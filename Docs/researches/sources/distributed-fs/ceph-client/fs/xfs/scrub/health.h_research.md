<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/health.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/health.h

Purpose: Declares the scrub health-state interface used to map scrub outcomes to XFS sick/healthy flags and cross-reference gating.

Important APIs, types, and functions: Declares `xchk_health_mask_for_scrub_type()`, `xchk_update_health()`, `xchk_ag_btree_del_cursor_if_sick()`, `xchk_mark_healthy_if_clean()`, `xchk_file_looks_zapped()`, and `xchk_health_record()`.

Control flow: Scrub setup and teardown code query masks, scrub runners call `xchk_update_health()` after checks and repairs, and cross-reference setup calls `xchk_ag_btree_del_cursor_if_sick()` to avoid trusting known-bad secondary structures.

State and persistence: No state is defined in the header. It exposes operations that mutate in-core health state but not durable metadata.

Dependencies and integration points: Depends on `struct xfs_scrub` and btree cursors. It is a shared boundary between scrub implementations, repair code, and XFS health reporting.

Risks and test signals: Prototype drift or misuse can cause health flags to be updated at the wrong time. Test build coverage for all scrub types and runtime cases where repair changes `sick_mask` before final health update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/health.h -->
