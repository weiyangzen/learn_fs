# sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sobj.h

## Purpose

`svc_bucket_sobj.h` declares the system-object-backed implementation of the bucket metadata service. The file was read as a complete 160-line header.

## Important APIs, Types, and Functions

`RGWSI_Bucket_SObj` derives from `RGWSI_Bucket`. It defines a private `bucket_info_cache_entry`, a `RGWChainedCacheImpl` pointer, private `do_start()`, `do_read_bucket_instance_info()`, and a `RGWBucketInfo`-based stats helper. Its `Svc` bundle stores dependencies on bucket service, bucket index, zone, sysobj, sysobj cache, mdlog, sync modules, and bucket sync. It overrides every abstract bucket metadata method from `RGWSI_Bucket`.

## Control Flow

The header defines service wiring and method contracts. Runtime flow is implemented in `svc_bucket_sobj.cc`: initialize dependencies, start cache, list/read/store/remove metadata objects, and delegate stats/sync/index side effects.

## State and Persistence Behavior

The class owns only cache state and service pointers. Persistent bucket metadata lives in zone domain-root system objects, while mdlog, bucket sync, and bucket index state are updated through dependent services.

## Dependencies and Integration Points

It includes `driver/rados/rgw_service.h`, `svc_bucket.h`, and `svc_bucket_sync.h`, and forward-declares zone/sysobj/cache/mdlog/sync-module classes. It integrates bucket metadata with cache, metadata log, bucket index, and sync policy handling.

## Risks and Edge Cases

Dependency initialization order matters because operations dereference several service pointers. Cache entry contents must stay aligned with `RGWBucketInfo` serialization and object attrs. The private read helper and public read methods need consistent version-refresh semantics.

## Test Signals

Compile coverage, service wiring tests, cache initialization tests, and concrete behavior tests through `svc_bucket_sobj.cc` are relevant.
