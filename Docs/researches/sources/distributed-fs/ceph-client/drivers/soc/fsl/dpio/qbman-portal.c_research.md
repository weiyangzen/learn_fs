# sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/qbman-portal.c

Purpose: DPAA2 QBMan software portal implementation. It programs software portal registers and implements enqueue, volatile dequeue, DQRR consumption, buffer release/acquire, FQ/channel management, state queries, and interrupt coalescing for both direct and memory-backed portal modes.

Important APIs and functions: portal lifecycle `qbman_swp_init()`/`qbman_swp_finish()`; interrupt helpers; management command helpers `qbman_swp_mc_start()`, `qbman_swp_mc_submit()`, `qbman_swp_mc_result()`; descriptor builders for enqueue, pull, and release; function-pointer-selected implementations for direct versus memory-backed enqueue/pull/DQRR/release; management commands `qbman_swp_acquire()`, `qbman_swp_alt_fq_state()`, `qbman_swp_CDAN_set()`, `qbman_fq_query_state()`, and `qbman_bp_query()`.

Control flow: init allocates `qbman_swp`, computes SDQCR defaults, selects DQRR size and valid bits from QMan revision, programs SWP configuration, enables memory-backed mode for QMan rev >= 5.0, switches global function pointers to memory-backed implementations, initializes EQCR producer/consumer tracking, and sets initial coalescing. Runtime operations fill cache-enabled command slots, use valid-bit protocols and DMA barriers, and write cache-inhibited trigger registers when memory-backed mode requires read-trigger semantics.

State and persistence: each `qbman_swp` tracks MMIO bases, valid bits, SDQCR, VDQ availability/storage, DQRR next index, EQCR ring producer/consumer state, access spinlock, and coalescing settings. Global function pointers change process-wide after a rev >= 5 portal is initialized.

Dependencies and integration: depends on DPAA2 frame/dequeue layouts, relaxed MMIO, DMA barriers, portal mapping attributes from `dpio-driver.c`, and the service layer. It is hardware-facing and has no firmware fallback except management command response codes.

Risks and test signals: risks include global function pointer mutation if mixed portal revisions existed, valid-bit/ring wrap mistakes, incomplete locking on multi-desc direct paths, memory-backed DQRR prefetch using direct offset in one path, and timeout-only management completion. Test signals are high-rate enqueue/dequeue, buffer pool acquire/release, FQ/BP count queries, QMan rev 4.x and 5.x coverage, IRQ coalescing limits, and stress under concurrent service users.
