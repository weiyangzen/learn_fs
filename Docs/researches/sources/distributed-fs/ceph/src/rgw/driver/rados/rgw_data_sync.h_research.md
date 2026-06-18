# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_data_sync.h

## Purpose
This header defines the RADOS-backed RGW multisite data-sync status, context, and administrative interfaces. It is mostly declarations plus inline serialization for data sync state, bucket sync state, remote data-log access, bucket-pipe sync status, sync modules, and permission helpers used by the data sync coroutines implemented elsewhere. It connects remote zone REST access, local RADOS status objects, bucket index log state, sync policy routing, fairness, tracing, error logging, and admin progress reporting.

## Important APIs, Types, and Functions
`rgw_data_sync_obligation` is the in-memory work descriptor for a bucket shard, optional bilog generation, marker, timestamp, and retry flag. `rgw_datalog_info`, `rgw_data_sync_info`, `rgw_data_sync_marker`, and `rgw_data_sync_status` model remote data-log shard count and per-shard full or incremental sync progress. They provide Ceph buffer encoding, JSON dump/decode, and test-instance hooks.

`RGWDataSyncEnv` is the service bundle passed into sync coroutines: dpp, cct, `RadosStore`, services, async rados processor, HTTP manager, error logger, trace manager, sync module, perf counters, fairness bid manager, and optional pretty-print stream. `RGWDataSyncCtx` adds a REST connection and source-zone id, with `LatencyConcurrencyControl` to reduce concurrency when sync lock latency approaches fractions of the lease period.

`RGWRemoteDataLog` is a coroutine manager facade over remote data-log operations: read log info, list shard info and next entries, read/init/run sync status, read recovering or lagging shard state, and wake up specific shards with data notifications. `RGWDataSyncStatusManager` wraps that remote log for zone-level sync status and implements `DoutPrefixProvider`.

The bucket-specific half declares `rgw_bucket_shard_full_sync_marker`, `rgw_bucket_shard_inc_sync_marker`, `rgw_bucket_shard_sync_info`, `rgw_bucket_full_sync_status`, `BucketSyncState`, `rgw_bucket_sync_status`, `bilog_status_v2`, `store_gen_shards`, and `rgw_bucket_index_marker_info`. `RGWBucketPipeSyncStatusManager` manages sync status for one destination bucket and one or more source pipes, including full status, incremental status, object-status oid naming, remote bilog info, and `run()`. `rgw_read_remote_bilog_info()`, `rgw_read_bucket_full_sync_status()`, and `rgw_read_bucket_inc_sync_status()` are the public read helpers.

`RGWDefaultSyncModule` and `RGWArchiveSyncModule` declare module capabilities. `RGWUserPermHandler` asynchronously loads user ACL/IAM state and exposes a nested `Bucket` helper that validates bucket/object permissions during sync.

## Control Flow
The declared flow starts with a status manager initializing a `RGWRemoteDataLog` against a source zone and REST connection. Admin or sync code can read remote data-log info, initialize the local status object, then run sync. Bucket-pipe sync construction discovers matching source pipes, builds per-source `RGWDataSyncCtx` values, reads remote bucket index marker info, initializes status objects, then runs a `RGWBucketSyncCR`.

Serialization flow is versioned. Zone sync info has states `init`, `building-full-sync-maps`, and `sync`; shard markers switch from `full-sync` to `incremental-sync`; bucket shard status moves from init to full to incremental or stopped. JSON decoding maps unknown or missing state strings conservatively toward init.

Concurrency flow is adjusted by `LatencyConcurrencyControl::adj_concurrency()`. It compares average lock latency to `rgw_sync_lease_period / 12`, halves proposed concurrency in throttled state, drops to one operation in overloaded state, and logs state transitions only when the state changes.

## State and Persistence Behavior
Most types are durable status records stored in RGW metadata or per-shard RADOS objects. `rgw_data_sync_status` encodes only `sync_info`; shard markers are intentionally encoded separately. Bucket shard status uses attrs for state and incremental markers, and retains backward decode support for the older full marker embedded in v1. `rgw_bucket_sync_status` version 2 persists full state, incremental generation, and per-shard generation completion bits.

The header defines important oid naming contracts: zone sync status object ids, source shard status prefixes, bucket full-status ids, incremental-status ids, and per-object status ids. These names are integration contracts with admin commands and sync coroutines.

## Dependencies and Integration Points
The file depends on RGW coroutine, HTTP client, SAL Rados store, data log, sync module, sync trace, sync policy, bucket sync, fairness, JSON, Ceph encoding, and formatter infrastructure. It integrates with remote REST APIs, local RADOS metadata/status objects, sync error logging, `radosgw-admin bucket sync run` pretty output, IAM/ACL policy evaluation, and perf counters.

## Risks and Test Signals
Compatibility risks are concentrated in versioned encoders and JSON state strings: old shard status attrs, missing `instance_id`, and unknown bucket sync states should decode safely. Runtime risks include stale object-id naming, lock latency feedback reducing too aggressively, and permission handler initialization racing sync work. Tests should cover encode/decode round trips for every status type, old-version decode paths, JSON admin output, remote datalog reads with truncated markers, bucket-pipe full-to-incremental transitions, pause/stopped status, and permission checks with ACL plus IAM policy combinations.
