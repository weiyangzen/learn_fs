<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/ast2700-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/ast2700-mailbox.c

## Purpose
`ast2700-mailbox.c` implements the ASPEED AST2700 IPC mailbox with four fixed channels and 32-byte messages. It exposes RX interrupt delivery and TX polling completion through the mailbox framework.

## Important APIs, Types, and Functions
`struct ast2700_mbox_data` describes channel count and message size. `struct ast2700_mbox` holds the controller, TX/RX MMIO regions, message size, and an RX-enable spinlock. `ast2700_mbox_irq()` receives messages, `ast2700_mbox_send_data()` writes data and triggers TX, and `ast2700_mbox_startup()`/`shutdown()` update per-channel RX enable bits.

## Control Flow
Probe reads match data, allocates channels and a per-channel receive buffer stored in `chan->con_priv`, maps named `tx` and `rx` resources, requests the shared IRQ, enables TX-done polling, and registers the controller. Startup sets the channel bit in RX `IPCR_ENABLE`; shutdown clears it. Send checks that the TX channel is enabled, verifies the previous TX is done by testing `IPCR_STATUS`, writes eight 32-bit words into the channel data window, and writes `IPCR_TX_TRIG`. The IRQ path masks status with enabled channels, copies each pending channel's data into its private buffer, calls `mbox_chan_received_data()`, and clears the status bit after the FIFO is empty.

## State and Persistence
The only persistent runtime state is the per-channel receive buffer, MMIO enable bits, and the lock protecting read-modify-write updates to `IPCR_ENABLE`. No messages are queued in software.

## Dependencies and Integration Points
The driver integrates with OF compatible `aspeed,ast2700-mailbox`, named MMIO resources, platform IRQs, and the mailbox core. It uses poll-based TX completion (`txpoll_period = 5`) rather than TX interrupts.

## Risks and Edge Cases
`send_data()` assumes the caller supplies at least `msg_size` bytes. RX status is limited by `RX_IRQ_MASK`, so data and hardware match data must agree on the number of channels. Clients must handle `-ENODEV` for disabled channels and `-EBUSY` while previous TX data is still pending. IRQ clearing depends on the FIFO-empty condition described in the source comment.

## Test Signals
Validate all four channels independently, concurrent startup/shutdown RMW locking, fixed 32-byte payload transfer, TX busy behavior, RX IRQ handling only for enabled channels, and DT/resource failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/ast2700-mailbox.c -->
