# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_timeline.c Research

Purpose: this file tests intel timeline synchronization and HWSP breadcrumb allocation in both mock and live modes. It covers cacheline reuse, sync-map wrap comparisons, benchmark characteristics, independent HWSP writes, seqno rollover, delayed GPU reads of HWSP, and breadcrumb slot recycling.

Important APIs/types/functions: mock helpers include `mock_hwsp_freelist()`, `igt_sync()`, and `bench_sync()`. Live helpers include `selftest_tl_pin()`, `checked_tl_write()`, `live_hwsp_engine()`, `live_hwsp_alternate()`, `live_hwsp_wrap()`, `live_hwsp_read()`, `live_hwsp_rollover_kernel()`, `live_hwsp_rollover_user()`, and `live_hwsp_recycle()`. `struct hwsp_watcher` manages a GPU-visible result buffer and request used to read delayed HWSP references.

Control flow: mock tests create timelines on a mock GEM device, pin HWSP allocations, insert cachelines into a radix tree to detect duplicates, shuffle/free histories, and exercise `__intel_timeline_sync_is_later()` across wrap cases. Live tests create thousands of timelines, emit GGTT store-dword requests to each HWSP slot, flush, and verify stored values. Wrap tests force `tl->seqno` near `UINT_MAX`, obtain new seqnos, and validate old/new HWSP cachelines remain valid. The delayed read test creates watcher requests with software fences, obtains HWSP addresses before/after timeline wrapping, and checks before reads are `< seqno` while after reads are `>= seqno`.

State and persistence: it allocates timelines, pins/unpins HWSP GGTT objects, mutates timeline seqnos for rollover simulation, temporarily assigns a user context to a shared timeline, creates large watcher VMAs, manipulates request timeline locks, disables heartbeats in rollover tests, and retires requests to recycle HWSP storage. All timelines and VMAs are released.

Dependencies/integration: dependencies include timeline allocation/sync internals, GEM ww locking, mock GEM device, engine PM, MI store/LRM/SRM commands, software fences, request retirement, and GT flush tests.

Risks and test signals: key risks are timeline lock ordering, stale HWSP references across wrap, duplicate cacheline allocation, and request retirement/recycling races. Pass signals include unique HWSP cachelines, expected sync comparison outcomes across `INT_MAX`/`UINT_MAX` wrap, correct per-timeline stored values, old HWSP retained over wrap, watcher comparisons passing, and completed pre-wrap requests for kernel and user timelines.
