<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/bcm74110-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/bcm74110-mailbox.c

## Purpose
`bcm74110-mailbox.c` implements a Broadcom BCM74110 mailbox with an initialization service, link-training handshake, shared-memory setup, and service channels for PMC, SCMI, and DPFE notifications.

## Important APIs, Types, and Functions
Message layout is encoded by `struct bcm74110_mbox_msg` and `BCM_MSG_*` field macros. `struct bcm74110_mbox` stores TX/RX channel numbers, IRQ, init-message list, controller, and per-channel state. Key functions are `bcm74110_mbox_init()`, `bcm74110_mbox_link_training()`, `bcm74110_mbox_shmem_init()`, `bcm74110_mbox_tx_msg_and_wait_ack()`, `bcm74110_rx_process_msg()`, `bcm74110_mbox_send_data()`, and `bcm74110_mbox_of_xlate()`.

## Control Flow
Probe maps registers, reads `brcm,tx` and `brcm,rx`, masks and clears IRQs, requests the RX IRQ, creates four service-indexed channels, registers the controller, then initializes hardware. Initialization resets/enables the TX queue, unmasks not-empty IRQ, performs a three-code link-training sequence, and negotiates shared-memory TX/RX windows through synchronous INIT messages. Runtime RX interrupts clear IRQ status and drain RX FIFO messages. INIT messages are queued on a spinlock-protected list for synchronous waiters; PMC/SCMI/DPFE messages notify enabled mailbox channels. Sending on service channels writes a request message carrying service type and slot.

## State and Persistence
The init-message list persists queued handshake responses until consumed or flushed. Per-channel `en`, `slot`, and `type` track client startup and DT xlate state. Shutdown sends link-stop, masks/clears IRQs, disables queues, and frees any queued init messages.

## Dependencies and Integration Points
The driver depends on platform MMIO/IRQ, OF properties, Linux lists/spinlocks, mailbox core service channels, and compatible `brcm,bcm74110-mbox`. Client channels are selected by two-cell phandles `(service type, shared-memory slot)`.

## Risks and Edge Cases
Synchronous INIT waits poll for up to roughly 30 ms and can race with asynchronous RX delivery if message fields are unexpected. Slot validation currently compares against `BCM_MBOX_HAB_MEM_IDX_SIZE`, which is zero, so only slot 0 is accepted. RX service messages deliver `NULL` data and rely on shared memory outside this driver. Link training retries on malformed/missing responses, and shutdown proceeds even if link-stop ack fails.

## Test Signals
Test link-training success/failure, INIT message queuing and flushing, PMC/SCMI/DPFE channel enable gates, invalid phandle services/slots, FIFO-full transmit rejection, shutdown link-stop behavior, and IRQ drain of multiple messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/bcm74110-mailbox.c -->
