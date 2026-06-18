# sources/distributed-fs/ceph-client/include/trace/events/oom.h

Purpose: Provides OOM and memory-reclaim tracepoints for score adjustment, reclaim retry decisions, victim marking, OOM reaper activity, skipped reaping, and compaction retry decisions.

Important APIs/types/functions: Events include `oom_score_adj_update`, `reclaim_retry_zone`, `mark_victim`, `wake_reaper`, `start_task_reaping`, `finish_task_reaping`, `skip_task_reaping`, and `compact_retry`. Fields capture task names/PIDs, order, priority, zone watermarks, reclaimable/scanned pages, OOM flags, MM pointers, and compaction retry metadata.

Control flow: Memory-management code emits these events during allocation failure handling: reclaim retry evaluation, OOM victim selection, reaper wake/start/finish/skip, and compaction retry logic. The tracepoints snapshot task and zone values at decision points.

State and persistence: No persistent state. Observed state lives in tasks, mm structs, zones, watermarks, reclaim counters, and OOM reaper queues.

Dependencies and integration points: Depends on tracepoints and `trace/events/mmflags.h`; integrates with page allocator, reclaim, compaction, memcg/global OOM, and task lifecycle.

Risks and test signals: Risks include racing task exit, stale mm pointers, interpreting zone counters under concurrent reclaim, and excessive output during memory pressure. Test forced OOM, memcg OOM, reaper disabled/skipped paths, compaction retry cases, high-order allocation failures, and tracepoint build coverage.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/oom.h` completely for this pass (223 lines, 5066 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/oom.h_research.md`.
