# sources/distributed-fs/ceph-client/drivers/char/applicom.c

## Purpose

`applicom.c` is a misc character driver for Applicom industrial communication boards, including PCI Applicom cards and parameter-specified ISA boards. It exposes `/dev/ac` for mailbox reads/writes and ioctl-based board status/control while coordinating with board shared memory and interrupts.

## Important APIs, Types, And Functions

- `struct applicom_board` tracks each board's physical shared-memory address, ioremapped RAM, receive/send waitqueue, IRQ, and spinlock.
- Module parameters: `irq` and `mem` support ISA board discovery.
- Board discovery/lifecycle: `ac_register_board()`, `applicom_init()`, and `applicom_exit()`.
- File operations: `ac_read()`, `ac_write()`, and `ac_ioctl()`.
- Interrupt path: `ac_interrupt()` scans all boards, clears board interrupt flags, validates ready bytes, and wakes read/write waiters.
- Helper: `do_ac_read()` copies a board mailbox into kernel buffers and writes acknowledgement fields back to board RAM.

## Control Flow

Init scans PCI devices of class `PCI_CLASS_OTHERS`, matches Applicom IDs, enables devices, maps BAR0 shared memory, validates the signature and board number, requests shared IRQs, and enables board interrupts. If `mem`/`irq` parameters are provided, it scans up to four ISA slots spaced by `LEN_RAM_IO`. After at least one board is registered it registers miscdevice minor `AC_MINOR` as `ac`.

`ac_write()` expects a packed `struct st_ram_io` plus `struct mailbox`, validates the board index with `array_index_nospec()`, waits until `DATA_FROM_PC_READY` becomes zero, writes mailbox bytes using byte accesses, fills ownership/destination fields, marks data ready, and interrupts the card. `ac_read()` scans boards until `DATA_TO_PC_READY == 2`, then reads the mailbox, acknowledges it to the card, copies data to userspace, and returns. `ac_ioctl()` implements legacy numeric commands for raw status, board identity, reset/interrupt manipulation, TIC updates, owner fields, board number setup, and diagnostic printing.

## State And Persistence Behavior

Persistent driver state includes the `apbs[]` board table, `numboards`, per-board waitqueues/spinlocks, mapped I/O memory, IRQ registrations, and error counters. Hardware state persists in the board shared-memory protocol bytes and mailboxes. The driver intentionally uses byte-wise MMIO because the board cannot handle word accesses.

## Dependencies And Integration Points

Dependencies include PCI enumeration, miscdevice, shared IRQs, waitqueues, spinlocks, `array_index_nospec()`, MMIO byte accessors, and UAPI structures from `applicom.h`. Integration is through `/dev/ac`, module parameters for ISA hardware, and board firmware's shared-memory protocol.

## Risks And Edge Cases

`ac_read()` computes `ret` from `do_ac_read()` but returns `tmp` after userspace copies; because `tmp` is `2`, successful reads appear to return 2 bytes rather than the full structure size, which is a notable behavioral risk unless legacy userspace expects it. PCI device references from `pci_get_class()` are not released for every continuing path in the scan loop. Sleep/wait setup in read/write manually manipulates task state and waitqueues; missed wakeups or signal paths require care. Ioctl command numbers are raw integers with broad hardware effects. Multiple ISA boards share one IRQ but only the first records it for free. Byte protocol fields above value 2 are treated as device errors.

## Test Signals

Build with Applicom support and verify PCI and ISA discovery paths. On hardware or a test shim, exercise exact-size read/write buffers, bad board numbers, interrupt wakeups for receive and send readiness, ioctl commands 0-6, and cleanup after failed registration. Static review should investigate the successful `ac_read()` return value, PCI refcounting, and waitqueue signal paths.
