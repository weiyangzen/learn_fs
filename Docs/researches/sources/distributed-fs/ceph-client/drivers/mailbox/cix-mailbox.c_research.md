<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/cix-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/cix-mailbox.c

## Purpose
`cix-mailbox.c` implements the CIX Sky1 mailbox controller. It supports four transfer types: doorbell, register-window messages, FIFO messages, and eight fast channels, with instances configured as either TX or RX side by device property.

## Important APIs, Types, and Functions
`struct cix_mbox_priv` holds device state, direction, MMIO base, channel array, and shared-memory offset mode. `struct cix_mbox_con_priv` records channel type and index. Send helpers are `cix_mbox_send_data_db()`, `_reg()`, `_fifo()`, and `_fast()`. ISR helpers mirror those channel types. Startup/shutdown functions request/free the shared IRQ and enable/disable the relevant interrupt bits.

## Control Flow
Probe maps the resource, detects whether the first `0x80` bytes are reserved as shared memory based on the resource start offset, reads `cix,mbox-dir` as `tx` or `rx`, initializes 11 channels by index, and registers the mailbox controller with IRQ-based TX completion. TX instances accept send requests and dispatch by channel type: doorbell writes the DB bit, register writes up to 32 words then rings the doorbell, FIFO writes words and enables empty interrupt, and fast writes one word to the fast register. RX and TX ack interrupts are handled by the same IRQ handler and dispatch to type-specific routines.

## State and Persistence
Runtime state is mostly hardware interrupt-enable bits plus per-channel type/index metadata. There is no software queue. FIFO startup resets FIFO state and sets the default watermark. `use_shmem` changes all register offsets for devices whose first register window is client shared memory.

## Dependencies and Integration Points
The driver uses platform MMIO/IRQ, device properties, mailbox core, and compatible `cix,sky1-mbox`. It currently relies on default mailbox channel indexing rather than an explicit OF xlate function.

## Risks and Edge Cases
All channels request the same IRQ independently, so multiple active channels rely on request/free semantics and unique dev_id values. Stack-allocated receive arrays are passed to mailbox clients synchronously; clients must not retain pointers. `cix_mbox_send_data()` ignores return values from type-specific helpers and returns success after some helper failures. FIFO overflow/underflow are logged and cleared but do not propagate mailbox errors.

## Test Signals
Validate TX and RX instances separately, all four channel types, shared-memory offset mode, FIFO watermark and empty completion, fast-channel interrupts, invalid direction strings, invalid fast indexes, and multi-channel startup/shutdown sharing one IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/cix-mailbox.c -->
