# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_log.cc

## Purpose
This file implements admin REST operations for RGW metadata logs, bucket index logs, and data change logs. It supports listing, info, shard info, trimming, locking/unlocking metadata log shards, notify wakeups, and sync status reads for multisite replication.

## Important APIs, Types, And Functions
- Metadata log operations: `RGWOp_MDLog_List`, `Info`, `ShardInfo`, `Delete`, `Lock`, `Unlock`, `Notify`, and internal `Status`.
- Bucket index log operations: `RGWOp_BILog_List`, `Info`, `Delete`, and internal `Status`.
- Data log operations: `RGWOp_DATALog_List`, `Info`, `ShardInfo`, `Delete`, `Notify`, `Notify2`, and internal `Status`.
- `RGWHandler_Log::{op_get,op_delete,op_post}` dispatches on `type=metadata`, `type=bucket-index`, or `type=data`, plus `id`, `info`, `status`, `lock`, `unlock`, `notify`, and `notify2` arguments.

## Control Flow
Metadata list/info/shard-info build `RGWMetadataLog` for the requested or current period and operate on a parsed shard id. Metadata delete trims to a marker and rejects legacy `start-time`, `end-time`, and `start-marker`; `end-marker` is accepted only when `marker` is absent. Metadata lock/unlock require period, shard id, duration or locker id, and zone id. Metadata notify reads up to 128 KiB of JSON, decodes updated shard ids, and wakes metadata sync shards.

Bucket-index log list loads a bucket by name or bucket instance, selects a log generation, streams the response header early, lists bilog entries until truncated or max count, and optionally emits version-2 metadata about truncation and the next log. Bilog info reads bucket stats against the latest log-derived index and returns retained generations. Bilog delete trims by generation, shard id, and marker range. Bilog status reads full and incremental bucket sync status for one pipe, or merges status across all local destinations when `options=merge`.

Data log list parses shard id and max entries, uses coroutine wrappers to list entries and read shard info, and returns marker, last update, truncation, and entries. Data notify variants decode updated shard maps and wake data sync shards. Data delete trims entries to a marker.

## State And Persistence Behavior
The operations read and mutate log objects stored in RADOS through metadata log services, bilog RADOS service, and datalog RADOS service. Trim operations permanently advance log retention markers. Lock/unlock stores cls lock state on mdlog shards. Notify operations do not persist log data directly but trigger in-memory sync processors via `driver->wakeup_meta_sync_shards()` and `driver->wakeup_data_sync_shards()`. Status operations read persistent sync status objects maintained by metadata and data sync managers.

## Dependencies And Integration Points
This file depends on JSON helpers, strict numeric parsing, async coroutine utilities, RGW sync and data sync types, mdlog and bilog services, datalog notify decoders, bucket parsing helpers, and SAL `RadosStore`. It integrates with multisite period history, bucket sync policy handlers, full and incremental bucket sync status helpers, and admin caps: `mdlog`, `bilog`, and `datalog` read/write.

## Risks And Edge Cases
Many endpoints parse numeric shard ids from free-form strings and return `-EINVAL` on parse errors. Several legacy time and marker parameters are rejected to avoid ambiguous trims. `RGWOp_DATALog_List::execute()` assigns `op_ret` after listing, then overwrites it with `get_info()`; a get-info failure can hide successful listing, and a list failure may still be followed by info read. Streaming bilog list sends headers before all list calls finish, so later list errors cannot be represented as a normal error response. Merge status requires equal shard counts across destinations or returns `-EINVAL`. Notify bodies are capped at 128 KiB.

## Test Signals
Tests should cover dispatch by `type`, cap enforcement, shard/max parsing errors, current-period fallback, legacy parameter rejection, mdlog lock busy mapping to `-ERR_LOCKED`, bilog generation selection and next-log response, streaming bilog truncation, bilog trim marker validation, data notify JSON v1 and notify2 formats, sync status merge with mismatched shard counts, and status behavior when sync managers are absent.
