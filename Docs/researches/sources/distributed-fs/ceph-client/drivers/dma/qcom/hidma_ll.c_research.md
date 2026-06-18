# sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_ll.c

Purpose: low-level HIDMA hardware driver responsible for TRE/EVRE ring allocation, MMIO setup, channel enable/disable/reset, interrupt cause handling, completion extraction, and callback handoff to the DMAEngine layer.

Important APIs/types/functions: exported-to-internal functions include `hidma_ll_init`, `hidma_ll_uninit`, `hidma_ll_setup`, `hidma_ll_request`, `hidma_ll_free`, `hidma_ll_set_transfer_params`, `hidma_ll_queue_request`, `hidma_ll_start`, `hidma_ll_disable`, `hidma_ll_enable`, `hidma_ll_status`, `hidma_ll_inthandler`, `hidma_ll_inthandler_msi`, and `hidma_cleanup_pending_tre`. Internal helpers include `hidma_ll_reset`, `hidma_handle_tre_completion`, `hidma_post_completed`, and `hidma_ll_tre_complete`.

Control flow: initialization allocates a TRE pool, pending-TRE table, coherent TRE ring, coherent EVRE ring, and handoff FIFO, aligns ring bases, programs hardware via `hidma_ll_setup`, and enables IRQs. Requests reserve TRE slots atomically and seed fixed configuration bits. Queueing copies local TRE words to the next ring slot, records the pending TRE, increments pending count, and advances the write offset. `hidma_ll_start` rings the TRCA doorbell. IRQ handling masks status with enabled bits; error causes disable hardware and synthesize error completions for all pending TREs, while normal causes clear interrupts and consume EVREs up to the hardware write pointer. Completions map ordered EVREs back to pending TREs by processed offset, update error code/info, enqueue to the FIFO, and schedule a tasklet that invokes requester callbacks.

State/persistence: runtime state is ring offsets, pending table entries, pending count, low-level channel states, enabled/MSI flag, and per-TRE allocation/error fields. No persistence survives device removal.

Dependencies/integration: used by `hidma.c`; depends on coherent DMA memory, `readl_poll_timeout`, Linux kfifo/tasklets, and hardware ordering guarantees documented in the ISR comments.

Risks: comments explicitly rely on HIDMA-specific interrupt ordering and relaxed MMIO assumptions. `hidma_ll_request` reserves only `nr_tres - 1` entries to keep one ring slot empty. Error cleanup loops until pending count reaches zero and depends on offset/table consistency. `hidma_ll_init` calls setup before initializing `lock` and tasklet, so changes around setup/IRQ enable order need care.

Test signals: ring alignment on varied DMA addresses, queue wraparound, normal completion ordering, MSI cause bit handling, wired IRQ status clearing, injected hardware error bits, disable/enable/reset polling timeouts, and synthesized completions during terminate/error paths.
