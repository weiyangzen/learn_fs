# sources/distributed-fs/ceph-client/drivers/misc/hpilo.c

## Purpose
`hpilo.c` implements the character-device driver for HP iLO management processors. It maps PCI BARs, creates one device with multiple channel-control-block minors, allocates DMA-backed send/receive FIFOs per open channel, handles doorbells and interrupts, and exposes read/write/poll packet exchange to user space.

## Important APIs, Types, and Functions
File operations are `ilo_open()`, `ilo_close()`, `ilo_read()`, `ilo_write()`, and `ilo_poll()`. PCI/module lifecycle uses `ilo_init()`, `ilo_exit()`, `ilo_probe()`, and `ilo_remove()`. Queue/channel helpers include `fifo_enqueue()`, `fifo_dequeue()`, `fifo_check_recv()`, `ilo_pkt_enqueue()`, `ilo_pkt_dequeue()`, `ilo_ccb_setup()`, `ilo_ccb_open()`, `ilo_ccb_verify()`, `ilo_ccb_close()`, `ilo_isr()`, `ilo_map_device()`, and `ilo_unmap_device()`.

## Control Flow
Module init registers class, char-device range, and PCI driver. Probe filters a blacklist, clamps `max_ccb`, reserves a device slot, enables PCI, maps MMIO/shared RAM/doorbell BARs, clears pending device bits, requests a shared IRQ, enables interrupts, adds a cdev range, and creates `hpilo!d%dccb%d` nodes. Open either creates a new CCB for the minor or shares an existing one unless exclusive flags conflict. CCB setup allocates coherent memory for send/recv FIFOs and descriptor areas, writes a hardware view of the CCB to mapped shared memory, prequeues send and receive descriptors, and verifies iLO consumes a send entry. Write dequeues a send descriptor, copies user data, enqueues it, and rings the doorbell; read waits/retries for a receive descriptor, copies data to user, and returns the descriptor. ISR reads pending doorbell bits, marks all channels reset on reset bit, wakes affected wait queues, and clears handled bits.

## State and Persistence
Global module state tracks the major, max CCB count, and one occupied device slot. Per-device `ilo_hwinfo` stores BAR mappings, cdev, locks, PCI device, and active `ccb_data` pointers. Per-channel `ccb_data` stores software/hardware CCBs, coherent DMA memory, mapped device CCB pointer, wait queue, refcount, and exclusivity. Hardware reset state is mirrored in FIFO reset flags.

## Dependencies and Integration Points
The driver depends on PCI, cdev/device class, coherent DMA, wait queues, poll, shared IRQs, and the hardware layouts in `hpilo.h`. It supports Compaq/HP PCI IDs and avoids disabling the PCI device on remove due to shared interrupt-line behavior with a USB function.

## Risks and Edge Cases
Lock ordering is documented and important: open lock, allocation lock, then FIFO lock. Open failure paths must not leak coherent CCB memory. `ilo_read()` can block up to roughly two seconds via retry sleep even though poll exists. Device reset forces applications to close/reopen channels. `device_create()` errors are logged but do not unwind already created nodes. Shared CCB references rely on open_lock serialization.

## Test Signals
Test probe/remove on both BAR layouts, max/min `max_ccb` clamping, exclusive and shared opens, read/write packet lengths, poll wakeups, IRQ reset handling, close while active, failure injection for DMA allocation and IRQ request, and module unload with open channels.
