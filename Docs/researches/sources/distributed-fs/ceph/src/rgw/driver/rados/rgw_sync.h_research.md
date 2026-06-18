# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync.h

## Purpose
This header declares metadata sync data structures and coroutine interfaces for the RADOS driver: remote mdlog response models, sync error logging, backoff helpers, sync environment wiring, remote metadata log management, status management, ordered marker tracking, and factory functions used by mdlog trimming.

## Important APIs, Types, and Functions
- `rgw_mdlog_info`, `rgw_mdlog_entry`, and `rgw_mdlog_shard_data` model remote metadata log info, entries, and list responses.
- `RGWSyncErrorLogger` creates sharded error log object names and returns error-writing coroutines.
- `rgw_sync_error_info` is the encoded/dumped payload for sync error records.
- `RGWSyncBackoff` and `RGWBackoffControlCR` provide reusable retry behavior.
- `RGWMetaSyncEnv` carries store, REST connection, async RADOS processor, HTTP manager, error logger, sync tracer, and bid manager pointers.
- `RGWRemoteMetaLog` owns remote mdlog access and top-level sync execution.
- `RGWMetaSyncStatusManager` exposes status initialization, reads, master shard info reads, run, wakeup, stop, and logging-prefix behavior.
- `RGWOrderCallCR`, `RGWLastCallerWinsCR`, and `RGWSyncShardMarkerTrack<T,K>` coordinate ordered marker writes while entries process concurrently.

## Control Flow
`RGWMetaSyncStatusManager` delegates remote work to `RGWRemoteMetaLog`. `RGWRemoteMetaLog` initializes `RGWMetaSyncEnv`, reads remote log info, initializes local status, and runs the main sync loop. Shard workers process entries concurrently while `RGWSyncShardMarkerTrack` flushes high-water markers only when earlier pending entries are complete. `RGWBackoffControlCR` repeatedly allocates child coroutines and optionally runs a finisher after success.

## State and Persistence Behavior
The declared objects track sync status, marker windows, retry sets, child coroutine pointers, shard object mappings, clone markers, and timestamp-to-shard state. Persistent state is represented by RADOS object names returned from `RGWMetaSyncEnv::status_oid()` and `shard_obj_name()`, error log shards, and marker writes implemented by subclasses.

## Dependencies and Integration Points
The header includes coroutine, HTTP client, metadata, meta sync status, SAL, RADOS SAL, sync trace, mdlog, and sync fairness headers. It integrates with mdlog trimming through the remote mdlog factory functions.

## Risks
- Marker tracking assumes markers are strictly orderable and that the lowest pending marker determines the safe high-water mark.
- `RGWBackoffControlCR` stores a raw child coroutine pointer protected by a mutex; ownership and cancellation paths are delicate.
- `RGWMetaSyncEnv` is a raw-pointer dependency bag; all pointed services must outlive active coroutines.

## Test Signals
Runtime signals include marker-order tests under concurrent entry replay, backoff reset behavior, sync error logging, status read/init APIs, and wakeup behavior for specific shards.
