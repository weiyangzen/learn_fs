# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_tlb_inval.c

Purpose: GuC-backed implementation of `xe_tlb_inval_ops`. It sends global, GGTT, ASID PPGTT, context PPGTT, range-selective, and page-reclamation invalidation requests through GuC CT, with MMIO fallback for GGTT invalidation when CT submission is unavailable.

Important functions: `send_tlb_inval`, `send_tlb_inval_all`, `send_tlb_inval_ggtt`, `send_tlb_inval_ppgtt`, `send_tlb_inval_asid_ppgtt`, `send_tlb_inval_ctx_ppgtt`, `normalize_invalidation_range`, `send_page_reclaim`, `xe_guc_tlb_inval_init_early`, and `xe_guc_tlb_inval_done_handler`.

Control flow: early init stores the GuC as `tlb_inval->private` and selects ASID or context ops based on `xe->info.has_ctx_tlb_inval`. Each send path allocates a seqno in the generic TLB invalidation layer, builds a GuC action, sends it with a one-message G2H reservation, then the done handler forwards the returned seqno to `xe_tlb_inval_done_handler`.

State/persistence: the algorithm assumes GuC processes invalidations in order. `seqno_lock` protects PPGTT issue ordering. Context invalidation temporarily moves active VM exec queues onto a local list while holding `vm->exec_queues.lock` and returns them before dropping refs. PRL requests use a suballocated buffer address and invalidate seqno only on the page reclamation message.

Dependencies/integration: integrates GuC CT, GT stats, forcewake/MMIO fallback registers, VM ASID lookup, exec queue activity callbacks, SA BO addresses for page reclamation, and generic `xe_tlb_inval` sequencing/waiting.

Risks/test signals: ordered seqno dependence is explicit and fragile if GuC ordering changes. Range normalization must avoid overflow and respect platform range invalidation constraints. Context invalidation must preserve VM exec queue list integrity on all errors. Test with CT enabled/disabled, wedged devices, SR-IOV VF fallback cancellation, high active queue counts forcing full invalidation, no-active-queue dummy GGTT invalidations, PRL requests, and malformed done messages.
