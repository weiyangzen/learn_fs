<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-mpfs.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-mpfs.c

## Purpose
`mailbox-mpfs.c` implements the Microchip PolarFire SoC system-controller mailbox. It sends service requests through MSS system controller registers or syscon regmaps and returns service responses from a mailbox data window.

## Important APIs, Types, and Functions
`struct mpfs_mbox` stores controller state, IRQ, control/mailbox bases, optional syscon regmaps, current response pointer, and response offset. Core functions are `mpfs_mbox_busy()`, `mpfs_mbox_last_tx_done()`, `mpfs_mbox_send_data()`, `mpfs_mbox_rx_data()`, `mpfs_mbox_inbox_isr()`, startup/shutdown, and probe helpers for new syscon and old DT formats.

## Control Flow
Probe first tries syscon lookup for `microchip,mpfs-control-scb` and `microchip,mpfs-sysreg-scb`; if that fails it falls back to old-format direct MMIO resources. It obtains an IRQ, configures one polling-completion mailbox channel, and registers the controller. Startup requests the inbox IRQ. Send stores the response pointer and response offset from `struct mpfs_mss_msg`, checks the system controller busy bit, writes optional command data into the mailbox window with byte handling for non-word tails, composes the option select from mailbox offset and opcode, and writes service control request/notify bits. The IRQ clears the message interrupt and reads the response window into the client response buffer. `last_tx_done()` also extracts failed service status from the status register after busy clears.

## State and Persistence
The active response pointer and response offset are stored in the controller state for the single outstanding request. Register access mode (`regmap` versus direct MMIO) is selected at probe and remains fixed. There is no persistent queue.

## Dependencies and Integration Points
The driver depends on mailbox core, platform IRQ/MMIO, regmap/syscon, MFD syscon lookup, and public Microchip service message types in `soc/microchip/mpfs.h`. Compatible is `microchip,mpfs-mailbox`.

## Risks and Edge Cases
Only one channel and one saved response pointer are supported, so concurrent clients must rely on mailbox serialization. Failed services may not interrupt, so `last_tx_done()` reads status as a workaround. Old DT fallback maps resources differently and may derive mailbox base from control base plus offset. Non-word command tails require careful read-modify-write.

## Test Signals
Test syscon and old-format probe paths, busy rejection, command data writes with unaligned byte counts, interrupt response reads, service failure status via polling, null response buffer error logging, and startup/shutdown IRQ lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/mailbox-mpfs.c -->
