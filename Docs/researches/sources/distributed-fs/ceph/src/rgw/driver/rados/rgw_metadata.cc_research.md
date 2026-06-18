# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_metadata.cc

## Purpose
Implements shard-name helpers and the concrete `RGWMetadataLog` operations declared in `rgw_mdlog.h`. It is the bridge between metadata mutation callers and cls timelog objects in the zone log pool.

## Important APIs And Functions
The three `rgw_shard_name()` overloads compute prefixed shard object names from a key, a section/key pair, or an explicit shard id. `RGWMetadataLog::add_entry()` writes a single timelog entry when metadata logging is enabled. `store_entries_in_shard()` writes a batch asynchronously. `init_list_entries()`, `list_entries()`, and `complete_list_entries()` implement iterative list handles. `get_info()` and `get_info_async()` return timelog header marker/time information. `trim()`, `lock_exclusive()`, `unlock()`, `mark_modified()`, and `read_clear_modified()` implement maintenance and local modification tracking.

## Control Flow
Hash-based shard selection uses `ceph_str_hash_linux()` modulo `rgw_md_log_max_shards`. Section/key sharding xors the section and key hashes. `add_entry()` returns immediately when `need_to_log_metadata()` is false; otherwise it builds the shard oid, marks the shard modified under the local RW lock, timestamps the entry with `real_clock::now()`, and calls `svc.cls->timelog.add()`. Listing reads from one oid/time range, treats `-ENOENT` as an empty shard, and advances the marker returned by cls.

## State And Persistence
Persistent metadata log entries are cls timelog records under objects named with `meta.log.*` prefixes. `RGWMetadataLogInfo` serializes to JSON marker and last update time for admin/reporting paths. `modified_shards` is process-local, protected by `RWLock`, and consumed by `read_clear_modified()` to report and clear modified shard ids.

## Dependencies And Integration Points
The implementation depends on zone service configuration, cls timelog and lock service wrappers, librados async completions, `RGWMetadataLogInfoCompletion`, Ceph JSON helpers, and the zone log pool. It is used by metadata service and sync code that needs to replicate or trim metadata changes.

## Risks And Test Signals
The double-lock pattern in `mark_modified()` optimizes repeated inserts but requires the write lock to be the authoritative insertion path. `list_entries()` ignores `-ENOENT` and returns success, so callers must inspect `truncated` rather than expecting an error for empty shards. Async info holds a ref until completion; cancellation clears the callback but still releases the librados completion in the destructor. Test signals include deterministic shard ids, empty shard listing, modified set clear/swap behavior, and async completion callback/cancel races.
