# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_tlb.c Research

Purpose: this live selftest verifies that GT TLB invalidation revokes active PTE translations. It forces a spinning GPU batch to observe a remapped PTE and requires a full invalidate to make the updated physical backing visible.

Important APIs/types/functions: `pte_tlbinv()` builds the core scenario. `mem_tlbinv()` allocates paired memory objects and runs the scenario across engines and page sizes. `tlbinv_full()` calls `intel_gt_invalidate_tlb_full()`, `invalidate_full()` runs system-memory and LMEM variants, and `intel_tlb_live_selftests()` iterates GTs.

Control flow: for each memory type, `mem_tlbinv()` creates objects A and B, maps them WC, creates a PPGTT, and replaces a context VM with that PPGTT. For each supported page size it first sanity-checks that a self-mapped VMA can end the conditional batch, then maps VMA A at a random aligned offset, aliases VMA B onto the same PTE node, writes `-1` through A and `0` through B, starts a `MI_CONDITIONAL_BATCH_BUFFER_END` loop, swaps PTE entries to B with `insert_entries()`, calls the invalidate callback, and waits for the request to complete.

State and persistence: it creates internal or LMEM objects, pins VMAs into a private PPGTT, temporarily edits `vb->node` to overwrite the same PTE, creates command batches, writes object mappings directly, changes context VM ownership, updates PTEs, and invalidates GT TLB. It restores VMA node state, unpins/unbinds, releases PPGTT, and flushes tests.

Dependencies/integration: it depends on GEM memory regions, PPGTT creation, page-size runtime info, VMA resource descriptors, PAT/PTE flags including `PTE_LM`, MI conditional batch semantics, engine request submission, and TLB sequence APIs. It skips pre-Gen8 because TLB invalidation is not implemented.

Risks and test signals: risks include large LMEM allocation limits, Small BAR sizing, 64K-page alignment rules requiring 2M PT coverage, slow OTHER_CLASS engines, and aliasing `vb->node` carefully. Pass signal is that the spinning request does not complete before remap/invalidate, then completes within timeout after invalidate; unexpected early completion or no completion is a failure.
