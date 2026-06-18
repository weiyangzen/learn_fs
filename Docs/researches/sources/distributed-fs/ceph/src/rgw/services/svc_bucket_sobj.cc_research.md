# sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sobj.cc

## Purpose

`svc_bucket_sobj.cc` implements bucket metadata storage on top of RGW system objects. It reads and writes bucket entrypoints and bucket instance records in the local zone's domain root, maintains a chained bucket-info cache, completes metadata-log entries after writes, updates bucket sync hints, and delegates stats to the bucket-index service. The file was read as a complete 579-line implementation.

## Important APIs, Types, and Functions

Important helpers include `instance_meta_key_to_oid()` and `instance_oid_to_meta_key()` for `.bucket.meta.` object-name translation, `BucketEntrypointLister`, and `BucketInstanceLister`. Implemented service methods include `init()`, `do_start()`, lister creation, `read_bucket_entrypoint_info()`, `store_bucket_entrypoint_info()`, `remove_bucket_entrypoint_info()`, `read_bucket_instance_info()`, `do_read_bucket_instance_info()`, `read_bucket_info()`, `store_bucket_instance_info()`, `remove_bucket_instance_info()`, `read_bucket_stats()` overloads, and `read_buckets_stats()`.

## Control Flow

Startup initializes a `RGWChainedCacheImpl` for bucket info using the system object cache. Entrypoint listing scans the zone domain root with an empty prefix and filters out object names that start with `.`, while instance listing scans `.bucket.meta.` and converts oids back to metadata keys. Reads first consult the cache, validate refresh versions when supplied, and fall back to system-object reads plus decode. Logical bucket reads first load the entrypoint; if it contains embedded old bucket info, that is returned, otherwise the referenced bucket instance is read.

Writes encode metadata into bufferlists and store through `rgw_put_system_obj()`. Entrypoint writes/removes complete an mdlog entry with section `bucket`. Instance writes may fetch prior info, call `svc.bi->handle_overwrite()` when overwriting, write the instance object, complete mdlog section `bucket.instance`, and call `svc.bucket_sync->handle_bi_update()`. Instance removal deletes the system object and calls `handle_bi_removal()`, treating sync hint cleanup failures as nonfatal. Stats load bucket info then call the bucket-index service.

## State and Persistence Behavior

Bucket entrypoints are persisted as system objects in `zone_params.domain_root` under logical bucket keys. Bucket instances are persisted in the same pool under `.bucket.meta.<key>` oids, with tenant separator conversion between metadata key `tenant/bucket:instance` and object oid `tenant:bucket:instance`. The service caches bucket info and attrs/mtime with chained invalidation tied to system object cache entries. Object version trackers are stored in decoded `RGWBucketInfo` after instance reads and passed to write/delete operations.

## Dependencies and Integration Points

The implementation depends on zone, sysobj, sysobj cache, bucket index, mdlog, sync modules, bucket sync, bucket types, metadata listers, string utilities, RADOS tools, and zone config. It is a central integration point among bucket metadata persistence, mdlog replication, bucket sync policy indexes, bucket index logging, and cache coherency.

## Risks and Edge Cases

Cache inconsistency warnings trigger invalidation and recovery reads, but stale cache behavior remains high risk. The tenant separator conversion assumes bucket instance oids cannot contain optional shard suffixes and only rewrites the first colon when another colon exists. `store_bucket_instance_info()` must correctly distinguish exclusive creates, absent prior info, and fetched prior info; mistakes can skip `handle_overwrite()` or incorrectly reject races. `-EEXIST` on exclusive instance store is treated as success for multisite race tolerance. Metadata log completion happens after system object writes, so mdlog failures can make writes return errors after persistence has happened.

## Test Signals

Signals include unit tests for key/oid translation, lister filtering and marker behavior, cache hit/refresh/invalidation paths, read paths for embedded old bucket info versus instance objects, write paths with all `orig_info` variants, mdlog failure injection, bucket sync hint update/removal tests, multisite exclusive-create race tests, and stats delegation tests.
