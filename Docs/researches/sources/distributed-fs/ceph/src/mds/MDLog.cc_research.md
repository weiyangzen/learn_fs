# sources/distributed-fs/ceph/src/mds/MDLog.cc

## Purpose

`MDLog.cc` implements the MDS journal manager declared in `MDLog.h`. It creates and recovers `Journaler` instances, queues and submits `LogEvent` objects, tracks log segments and major segment boundaries, replays events into `MDSRank`/`MDCache`, trims expired segments, reformats older journals, and maintains perf counters for journal positions and event/segment counts.

## Important Functions And Control Flow

Construction reads runtime config such as `mds_debug_subtrees`, `mds_log_events_per_segment`, `mds_log_max_segments`, `mds_log_max_events`, skip-corrupt flags, and trim decay; it starts `log_trim_upkeep`. `create_logger` registers counters for submitted, replayed, large, expiring, expired, trimmed events/segments and read/write/expire positions. `create` initializes a fresh journal inode, writes the journal head and `JournalPointer`, makes the journal writeable, and starts the submit thread. `open` starts the recovery thread and submit thread; `reopen` repeats recovery and then appends.

`submit_entry` locks `submit_mutex`, calls `_submit_entry`, performs `_segment_upkeep`, and wakes `_submit_thread`. `_submit_entry` increments `event_seq`, starts segments for `SegmentBoundary` events, updates touched inode `last_journaled`, associates the event with the current `LogSegment`, stamps it, snapshots up MDS feature bits, and appends it to `pending_events`. `_submit_thread` encodes each event with a header, appends to `Journaler`, updates segment offsets/end, registers a `MDSLogContextBase` flush callback, optionally flushes, and deletes the event.

Replay begins in `replay`; if the journal is non-empty it starts `_replay_thread`. `_replay_thread` loops over readable journal entries, decodes `LogEvent`s, reconstructs segment boundaries, requires a major segment before applying bounded events unless `mds_log_skip_unbounded_events` allows skipping, updates counters and segment end offsets, and calls `le->replay(mds)` under `mds_lock`. Corrupt entries either skip or damage the MDS depending on `mds_log_skip_corrupt_events`.

## State And Persistence Behavior

Persistent state is the RADOS journal plus `JournalPointer`; in-memory state mirrors it through `journaler`, `segments`, `major_segments`, `event_seq`, `num_events`, `safe_pos`, pending submit queues, and expiring/expired segment sets. `MDSLogContextBase` callbacks update `safe_pos` only after completion code runs. `write_head` persists journal expire position and queues `waiting_for_expire` callbacks until the head commit proves the expire position durable. `_reformat_journal` rewrites old journal streams into a new back journal, rewrites segment references in metablobs where necessary, zeros subtree-map `expire_pos`, atomically flips `JournalPointer`, erases the old journal, and resets the active `Journaler`.

Trim is conservative: `trim` only considers flushed segments (`safe_pos` beyond segment end and no pending events), asks each `LogSegment` to expire referenced objects through `try_expire`, moves them through `expiring_segments` to `expired_segments`, and only erases old segments up to a later major segment in `_trim_expired_segments`. `standby_trim_segments` follows another rank's `expire_pos` and drops expired standby segments while keeping at least one segment.

## Dependencies And Integration Points

The implementation depends on `MDSRank`, `MDCache`, `MDSContext`, `LogEvent`, `Journaler`, `JournalPointer`, and event types such as `ESubtreeMap`, `ESegment`, and `ELid`. It calls into `MDCache` for subtree maps, open-file-table commits, stray advancement, standby segment trimming, and cache trimming after replay. It reports severe write/recover errors by respawning or damaging the rank through `MDSRank`.

## Risks And Test Signals

Key risks are journal-ordering bugs, safe-position races, segment-boundary corruption, old-format rewrite mistakes, and deadlocks during shutdown or callbacks under `mds_lock`. Tests should crash around segment creation, event flush completion, journal head writes, trim expiry callbacks, `JournalPointer` front/back swaps, and standby replay while an active rank trims or rewrites the journal. Perf counters and `dump_replay_status` are operational signals; `is_trim_slow`, large-event counters, and replay percent estimates are useful regression signals.
