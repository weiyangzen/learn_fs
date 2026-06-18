# sources/distributed-fs/ceph/src/mds/MDLog.h

## Purpose

`MDLog.h` declares the MDS journal manager. It defines log perf-counter IDs, public journal lifecycle APIs, submit/flush/trim/replay controls, segment accessors, and thread classes for recovery, replay, and asynchronous submission.

## Important APIs And Types

The core class is `MDLog`. Public lifecycle methods are `create`, `open`, `reopen`, `append`, `replay`, `shutdown`, and `cap`. Submission and durability methods are `submit_entry`, `wait_for_safe`, `flush`, `is_flushed`, `set_write_iohint`, `kick_submitter`, and `finish_head_waiters`. Segment methods include `peek_current_segment`, `get_current_segment`, `get_segment`, `get_oldest_segment`, `get_last_major_segment_seq`, `get_last_segment_seq`, `trim_expired_segments`, `trim_all`, and `trim_to`.

`PendingEvent` pairs a `LogEvent*`, completion `Context*`, and flush flag. `ReplayThread`, `RecoveryThread`, and `SubmitThread` wrap the corresponding private methods. The class exposes `pending_exports` for replay state and `is_trim_slow` for beacon/health signaling.

## State And Persistence Behavior

The declaration shows the division between persistent journal positions and in-memory control state. `journaler` owns the RADOS journal stream; `safe_pos` records a position that is both durable and whose callbacks have run; `segments`, `major_segments`, `expired_segments`, and `expiring_segments` describe journal trimming boundaries. `pending_events` is protected by `submit_mutex`; `waiting_for_expire` is protected by `mds_lock`. Replay waiters, recovery completion, and submit queues are explicit because journal work runs outside normal request flow.

Runtime configuration is cached in `debug_subtrees`, `event_large_threshold`, `events_per_segment`, `max_events`, `max_segments`, `minor_segments_per_major_segment`, `pause`, corruption skip flags, `log_warn_factor`, and `log_trim_counter`. The upkeep thread uses `cond` and `upkeep_log_trim_shutdown` to perform periodic trim.

## Dependencies And Integration Points

`MDLog` depends on `Journaler`, `JournalPointer`, `LogEvent`, `MDSLogContextBase`, `MDSRank`, `MDSMap`, `LogSegment`, and `SegmentBoundary`. It grants friendship to replay/submit contexts, `ESubtreeMap`, and `MDCache` because replay, segment creation, and subtree-map events require tight coordination. `MDSLogContextBase` in `MDSContext.h` calls `MDLog::set_safe_pos`.

## Risks And Test Signals

The header highlights shared mutable state across three threads plus the rank lock, so lock-order tests and thread-shutdown tests are important. Public trim APIs should be covered by journal replay/trim integration tests, especially `trim_to` and `trim_expired_segments` waiters. The `pending_events` map by segment sequence is a critical invariant: segment creation, event sequence increments, and safe callbacks must stay aligned.
