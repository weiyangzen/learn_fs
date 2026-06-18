# sources/distributed-fs/ceph-client/drivers/mailbox/arm_mhuv2.c

## Purpose
Implements the ARM MHUv2 mailbox controller for AMBA devices. It supports unidirectional sender or receiver frames and two device-tree-described transport protocols: doorbell and data-transfer.

## Important APIs, Types, And Functions
Packed register structs model sender and receiver frames. `struct mhuv2` stores the mailbox controller, mapped frame, frame type, IRQ, hardware window count, architecture minor revision, raw protocol table, and a doorbell pending spinlock. `struct mhuv2_mbox_chan_priv` records protocol ops, channel-window index, doorbell bit, data-transfer window count, and pending state. Protocol ops include doorbell startup/read/send/txdone and data-transfer startup/read/send/txdone. Top-level ops are `mhuv2_sender_*`, `mhuv2_receiver_*`, and `mhuv2_mbox_of_xlate()`.

## Control Flow
Probe maps the AMBA resource, selects TX init for `"arm,mhuv2-tx"` or RX init for `"arm,mhuv2-rx"`, reads implemented window count and architecture minor revision, parses `arm,mhuv2-protocols`, verifies total windows and protocol IDs, allocates mailbox channels, and registers the controller. TX frames request access from the receiver and use interrupts for minor version 1+ if available, otherwise polling. RX frames require an IRQ, mask all windows initially, and unmask per-channel during startup.

## State, Dependencies, And Integration
Runtime state is per controller and per generated mailbox channel. It depends on AMBA IDs for MHUv2 2.0/2.1, OF resource and protocol parsing, MMIO access, threaded IRQs, spinlocks, the mailbox framework, and `linux/mailbox/arm_mhuv2_message.h` for data-transfer payloads. Device-tree clients address channels by window offset and doorbell index.

## Risks And Test Signals
Several busy-wait loops spin until peer state changes (`access_ready`, data-transfer TX completion). Data-transfer requires the first word of each round to be nonzero so the receiver interrupt fires. Doorbell TX completion uses a pending bit under spinlock to distinguish newly completed bits from concurrent sends. `BUG_ON()` is used for impossible states and could hard-stop malformed hardware/logic cases. Test signals include protocol-table validation, channel count math, doorbell exact-channel IRQ decoding, combined interrupt versus status scanning by minor version, short data-transfer masking, TX interrupt fallback to polling, RX on unattached channels, and sender remove clearing `access_request`.
