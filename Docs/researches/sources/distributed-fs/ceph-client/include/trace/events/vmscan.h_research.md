# sources/distributed-fs/ceph-client/include/trace/events/vmscan.h

Purpose: Defines memory reclaim tracepoints for kswapd, direct reclaim, memcg reclaim, slab shrinking, LRU isolation/shrink, writeback during reclaim, throttling, and hopeless-zone handling.

Important APIs/types/functions: Provides reclaim flag helpers (`RECLAIM_WB_*`, `show_reclaim_flags`, `show_throttle_flags`) and events including `mm_vmscan_kswapd_sleep`, `mm_vmscan_kswapd_wake`, `mm_vmscan_wakeup_kswapd`, direct/memcg reclaim begin/end templates, `mm_shrink_slab_start/end`, `mm_vmscan_lru_isolate`, `mm_vmscan_write_folio`, `mm_vmscan_reclaim_pages`, `mm_vmscan_lru_shrink_inactive/active`, `mm_vmscan_node_reclaim_begin/end`, `mm_vmscan_throttled`, `mm_vmscan_kswapd_reclaim_fail`, and `mm_vmscan_kswapd_clear_hopeless`.

Control flow: Reclaim code emits begin/end events around reclaim phases and point events for page isolation, writeback, throttling, and kswapd state changes. Assignments copy node/zone/order/gfp/memcg/reclaim counts and reason flags.

State/persistence: No reclaim state is owned; trace buffers persist samples from reclaim loops.

Dependencies/integration: Includes MM, memcontrol, and mmflags trace helpers; conditional memcg events depend on `CONFIG_MEMCG`.

Risks: These are high-frequency pressure paths. Field reads must be cheap and race-tolerant, and flag decoders must stay aligned with reclaim internals.

Test signals: Run memory pressure, memcg, and slab pressure tests with `vmscan:*`; verify begin/end pairing, count consistency, and no tracing-induced reclaim regressions.
