<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/bcm2835-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/bcm2835-mailbox.c

## Purpose
`bcm2835-mailbox.c` implements the Raspberry Pi/BCM2835 ARM-to-VideoCore mailbox channel. It exposes one mailbox channel that writes requests to mailbox 1 and receives replies from mailbox 0.

## Important APIs, Types, and Functions
`struct bcm2835_mbox` contains the MMIO base, a spinlock, and the controller. `bcm2835_send_data()` writes a 32-bit request, `bcm2835_mbox_irq()` drains received replies, `bcm2835_last_tx_done()` checks the TX FIFO-full bit, and startup/shutdown enable or disable receive interrupts.

## Control Flow
Probe allocates state, requests the DT IRQ with `IRQF_NO_SUSPEND`, maps registers, configures polling TX completion, allocates one channel, registers the mailbox controller, and logs that the mailbox is enabled. Startup writes `ARM_MC_IHAVEDATAIRQEN` to enable data interrupts. Send locks around the mailbox write and logs the request. The IRQ handler loops while the receive FIFO is not empty, reads each 32-bit word, and passes it to `mbox_chan_received_data()`. Shutdown clears interrupt enable.

## State and Persistence
The driver keeps no software queue. The spinlock serializes writes and TX status checks against concurrent clients. Hardware FIFO state is the source of truth for completion readiness.

## Dependencies and Integration Points
The driver uses OF IRQ/address helpers, platform MMIO mapping, the mailbox core, and compatible `brcm,bcm2835-mbox`. Clients typically use the firmware property interface format carried in the 32-bit mailbox word.

## Risks and Edge Cases
`send_data()` does not itself test FIFO fullness; the mailbox core is expected to call `last_tx_done()` and clients must tolerate busy behavior. IRQ request uses `irq_of_parse_and_map()` directly. Only one channel is exposed, and the OF xlate rejects any phandle arguments.

## Test Signals
Validate firmware property round trips, repeated IRQ draining of multiple replies, TX polling under full FIFO, startup/shutdown interrupt enable bits, no-suspend IRQ behavior, and invalid phandle argument rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/bcm2835-mailbox.c -->
