<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/bcm-flexrm-mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/bcm-flexrm-mailbox.c

## Purpose
`bcm-flexrm-mailbox.c` turns Broadcom FlexRM hardware rings into mailbox channels for FlexSparx4 offload engines. Each ring is a channel that accepts Broadcom mailbox messages and writes FlexRM descriptor packets, with completions reported through MSI-backed ring completion queues.

## Important APIs, Types, and Functions
`struct flexrm_mbox` owns mapped ring registers, ring array, DMA pools, debugfs entries, and the mailbox controller. `struct flexrm_ring` tracks one ring's registers, IRQ, descriptor and completion buffers, request bitmap, in-flight messages, and counters. Descriptor helpers build header, null, next-table, SRC/DST/MSRC/MDST/IMM/TLAST descriptors. Message paths include `flexrm_sanity_check()`, `flexrm_dma_map()`, `flexrm_write_descs()`, `flexrm_new_request()`, `flexrm_process_completions()`, and mailbox callbacks `flexrm_send_data()`, `flexrm_startup()`, `flexrm_shutdown()`, and `flexrm_peek_data()`.

## Control Flow
Probe maps the register range, scans for rings by `RING_VER_MAGIC`, allocates ring state, sets a 40-bit or fallback 32-bit DMA mask, creates DMA pools, allocates platform MSIs, optionally creates debugfs `config` and `stats`, and registers one mailbox channel per ring. Startup allocates descriptor and completion rings, seeds next-table/null descriptors, requests the ring IRQ, programs ring base addresses/MSI settings, clears counters, and activates the ring. Send validates `brcm_message` content, allocates a request ID, DMA maps SPU scatterlists when needed, checks descriptor space against the hardware read pointer, writes descriptors, flips the first header toggle after a write barrier, and advances the software write offset. Completion processing reads the completion write pointer, decodes error status and request ID, unmaps DMA, releases the bitmap slot, returns the original message with `msg->error`, and updates stats.

## State and Persistence
Ring state is volatile and is rebuilt on channel startup. In-flight request pointers live in `ring->requests[]`, with allocation tracked by `requests_bmap`. Descriptor memory and completion memory are allocated from DMA pools per startup and freed on shutdown. Debugfs stats are runtime counters only.

## Dependencies and Integration Points
The driver depends on `linux/mailbox/brcm-message.h` message formats, DMA mapping and pools, platform MSI allocation, debugfs, OF compatible `brcm,iproc-flexrm-mbox`, and Linux mailbox callbacks. DT mailbox args select ring index, MSI count threshold, and MSI timer value.

## Risks and Edge Cases
Descriptor accounting is the main risk: packet extension headers, next-table descriptors, toggle bits, and wraparound must remain consistent. Completion descriptors with bad DME/RM status translate to `-EIO` or `-ETIMEDOUT`. Shutdown aborts in-flight messages with `-EIO`. The source contains duplicated declarations/log calls in a few locations that should be caught by compile testing. Batch messages can partially queue and return an error with `msgs_queued` updated.

## Test Signals
Test SPU and SBA message sanity checks, scatterlist DMA map/unmap, descriptor wraparound, MSI completion processing, batch partial failure, debugfs output, ring startup/shutdown/flush, invalid DT args, and error completion descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/bcm-flexrm-mailbox.c -->
