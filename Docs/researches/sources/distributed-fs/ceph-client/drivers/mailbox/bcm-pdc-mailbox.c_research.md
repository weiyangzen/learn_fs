<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/bcm-pdc-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/bcm-pdc-mailbox.c

## Purpose
`bcm-pdc-mailbox.c` implements the Broadcom PDC/MDE/FA2 mailbox controller for SPU offload engines. It maps `BRCM_MESSAGE_SPU` scatterlists into paired TX and RX DMA descriptor rings and reports responses back through the mailbox framework.

## Important APIs, Types, and Functions
`struct pdc_state` is the central state object, holding platform state, DMA registers, descriptor rings, ring indexes, response metadata buffers, mailbox controller, work item, counters, and hardware type. Important functions include `pdc_probe()`, `pdc_hw_init()`, `pdc_ring_init()`, `pdc_send_data()`, `pdc_rx_list_init()`, `pdc_rx_list_sg_add()`, `pdc_tx_list_sg_add()`, `pdc_tx_list_final()`, `pdc_irq_handler()`, `pdc_work_cb()`, `pdc_receive()`, and `pdc_receive_one()`.

## Control Flow
Probe allocates state, sets a 39-bit DMA mask, creates DMA pools, reads DT properties (`brcm,rx-status-len`, optional `brcm,use-bcm-hdr`, compatible-selected hardware type), maps registers, creates response-header buffers, initializes DMA control registers, sets up bottom-half work and interrupts, registers a one-channel mailbox, and creates debugfs stats. Channel startup allocates and programs TX/RX descriptor rings for ringset 0. Send only accepts SPU messages, DMA maps source and destination scatterlists, checks ring capacity, posts a receive metadata descriptor plus destination descriptors, posts source descriptors, then writes RX and TX hardware pointer registers to start transfer. The hard IRQ disables and clears device interrupts, queues work, and the work callback reclaims available response frames and reenables interrupts.

## State and Persistence
Ring indexes (`txin`, `txout`, `rxin`, `rxout`, `last_rx_curr`) and per-message descriptor counts persist while the channel is active. `rx_ctx[]`, `src_sg[]`, and `txin_numd[]` tie completions to original scatterlists and opaque client context. Debugfs counters persist for the device lifetime but not across driver reload.

## Dependencies and Integration Points
The driver depends on Broadcom SPU message definitions, scatterlist DMA mapping, DMA pools, workqueues, debugfs, OF IRQ/resource APIs, and mailbox polling for backpressure (`last_tx_done()` checks descriptor headroom). Compatibles are `brcm,iproc-pdc-mbox` and `brcm,iproc-fa2-mbox`.

## Risks and Edge Cases
Ring-space checks must prevent partial descriptor sequences; however, several send-error paths after DMA mapping require careful unmap review. Response length/overflow handling differs for SPU-M headers. `last_tx_done()` uses conservative free-space thresholds and increments statistics when rings are low. The global debugfs root is shared across instances. Multiple descriptor splitting for buffers over 16 KiB must keep EOT/SOF/EOF/IOC flags correct.

## Test Signals
Exercise SPU request/reply with multi-entry scatterlists, buffers larger than `PDC_DMA_BUF_MAX`, RX overflow/zero-length responses, FA2 versus PDC lazy interrupt offsets, backpressure via `last_tx_done()`, channel startup/shutdown ring allocation, debugfs counters, and removal while deferred work may be queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/bcm-pdc-mailbox.c -->
