# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_datalog.h

## Purpose
This header declares the RGW data changes log model and service interface. It defines the durable entry formats, notification records, generation-aware backend manager, bucket-generation key type, and the `RGWDataChangesLog` class that producers, sync readers, admin commands, and tests use to add, list, trim, recover, and observe bucket change logs.

## Important APIs, Types, and Functions
`DataLogEntityType` currently distinguishes bucket entries from unknown entries. `rgw_data_change` is the encoded change payload and includes entity type, bucket shard key, timestamp, and bilog generation. Its encoder uses compat version 1 when `gen == 0` and requires version 2 when a generation is present. `rgw_data_change_log_entry` adds backend log id and log timestamp. `RGWDataChangesLogInfo` exposes a max marker and last update time, while `RGWDataChangesLogMarker` carries cross-shard listing position.

`rgw_data_notify_entry` is the per-bucket notification key plus generation, ordered by key then gen. `DataLogBackends` derives from `logback_generations` and a flat map of generation backends. It declares listing, trimming entries, trimming empty generations, and generation lifecycle callbacks.

`BucketGen` combines `rgw_bucket_shard` and generation into a lexicographically sortable key. Its parser decodes `tenant/name:instance:shard:gen` style keys, accepts buckets without tenants or bucket ids, and throws `boost::system_error` on malformed generations or shards. Equality, ordering, stream output, and `std::hash` are provided.

`RGWDataChangesLog` owns RADOS access, backend generations, async strands/futures for renew/watch/recovery, modified notification state, coalescing status, semaphore state, and public methods for lifecycle, entry production, entry listing, trimming, format changes, recovery, shutdown, and admin semaphore operations. `RGWDataChangesBE` is the abstract backend API implemented by omap and FIFO in the `.cc` file.

## Control Flow
The public interface supports blocking and coroutine start paths. Producers call one of the `add_entry()` overloads with bucket info, bucket log layout generation, and shard id. Sync readers call shard-specific or cross-shard `list_entries()`, then `trim_entries()` after replication. Background code calls `renew_run()`, `watch_loop()`, and `recover()` through start options. Administrators call `admin_sem_list()` and `admin_sem_reset()` to inspect or repair semaphore state.

The backend abstraction normalizes write preparation, batched push, yielding push, list, info, trim, max marker, and empty checks across cls log and FIFO. The generation manager ensures callers can list and trim through a single marker namespace even while backing generations change.

## State and Persistence Behavior
The header encodes persistence contracts for data changes and log entries. `rgw_data_change` versioning is important because older decoders do not understand nonzero generations. `RGWDataChangesLog` object names are declared as methods rather than constants because generation ids and shard ids are part of the durable namespace. In-memory coalescing state uses `ChangeStatus` entries with expiration, sent time, pending flag, condition variable, and sync policy reference.

## Dependencies and Integration Points
Dependencies include neorados, Ceph async conditions/yield contexts, spawn groups, LRU map, cls log types, sem_set, RGW basic types, sync policy, trim bilog helpers, zone config, and log backing generation support. Integration points are RGW bucket mutation paths, multisite data sync readers, metadata generation migration, admin commands, unit tests via `DataLogTestBase`, and optional bucket change observers.

## Risks and Test Signals
Header-level risks include marker compatibility, `BucketGen` parse ambiguity between bucket id and shard id, generation version compatibility, lock ordering around `modified_lock` and `lock`, and backend interface mismatches when adding a new log type. Tests should cover `BucketGen` round trips for tenant/no-tenant, bucket-id/no-bucket-id, shard, and malformed strings; encode/decode of v1 and v2 changes; marker truthiness and clearing; backend polymorphic list/trim contracts; and `max_marker()` ordering against real backend markers.
