# sources/distributed-fs/ceph-client/include/trace/events/compaction.h

## Purpose
`compaction.h` traces memory compaction isolation, migration, suitability, deferral, and kcompactd wake/sleep behavior.

## Important APIs, types, and functions
Event classes are `mm_compaction_isolate_template`, `mm_compaction_suitable_template`, `mm_compaction_defer_template`, and `kcompactd_wake_template`. Events include isolate migrate/free/fast-free pages, migratepages, begin/end, try-to-compact-pages, finished/suitable, deferred/defer/reset, kcompactd sleep, and kcompactd wakeup/wake.

## Control flow
Compaction code emits isolation events as PFN ranges are scanned, begin/end around a compaction run, migratepages after migration attempts, suitability/deferral decisions per zone/order, and daemon sleep/wake events. Some events are only compiled under `CONFIG_COMPACTION`.

## State and persistence behavior
The header stores no state. Records snapshot PFN ranges, scan/take counts, compact control cursors, sync mode, gfp mask, priority, node/zone/order, compaction status, deferral counters, and kcompactd wake parameters.

## Dependencies and integration points
It depends on MM zone/compaction types, `<trace/events/mmflags.h>` for GFP/zone/status formatting, and tracepoints. It integrates with page allocator and memory-fragmentation diagnostics.

## Risks and test signals
Risks include ABI constraints on printed names such as `classzone_idx`, event availability depending on `CONFIG_COMPACTION`, and overhead on hot memory-management paths. Test signals are high-order allocation stress, compaction success/failure cases, deferred compaction behavior, and kcompactd wake/sleep traces.
