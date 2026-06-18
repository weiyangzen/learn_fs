## sources/distributed-fs/ceph-client/include/linux/compaction.h

Purpose: This header declares the memory compaction policy and external interfaces used by the page allocator, kcompactd, NUMA node registration, and fragmentation reporting. It is a coordination contract for `CONFIG_COMPACTION` builds rather than an implementation file.

Important APIs, types, and functions: `enum compact_priority` orders direct-compaction effort from full synchronous through asynchronous. `enum compact_result` encodes the allocator-visible result states, including skipped, deferred, continued, complete, contended, and success. `compact_gap(order)` computes the extra order-0 free page reserve needed above a watermark so the free scanner has target pages while isolating migration pages. `current_is_kcompactd()` checks `PF_KCOMPACTD`. Under `CONFIG_COMPACTION`, the header exports fragmentation queries (`extfrag_for_order`, `fragmentation_index`), direct compaction (`try_to_compact_pages`), suitability checks, deferral reset, kcompactd lifecycle, and wakeup hooks. NUMA sysfs registration is separately gated by `CONFIG_SYSFS` and `CONFIG_NUMA`.

Control flow: Callers first ask suitability helpers whether compaction is worthwhile for a zone, allocation order, and watermark. The allocation path then calls `try_to_compact_pages()`, interpreting `compact_result` to retry allocation, continue reclaim, or give up. Background compaction is driven by `wakeup_kcompactd()`, while node hotplug invokes `kcompactd_run()` and `kcompactd_stop()`.

State and persistence: The header exposes no persistent storage, but its APIs manipulate per-zone and per-node compaction state in mm code: deferred compaction, isolation suitability, fragmentation measurements, and kcompactd thread state. Stub definitions under disabled configs deliberately preserve buildability while making compaction unavailable.

Dependencies and integration points: It depends on mm types such as `struct zone`, `pg_data_t`, `gfp_t`, `struct page`, `struct alloc_context`, and `struct node`, and it is coupled to trace state because `enum compact_result` comments require matching `include/trace/events/compaction.h`.

Risks and test signals: Risks include mismatched result enum trace decoding, incorrect suitability logic causing allocation latency or failures, and improper kcompactd wakeups. Test signals are high-order allocation stress, fragmentation-index checks, NUMA node hotplug, tracepoint result names, and builds with `CONFIG_COMPACTION` disabled.
