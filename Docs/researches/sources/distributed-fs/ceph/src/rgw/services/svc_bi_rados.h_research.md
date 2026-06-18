# sources/distributed-fs/ceph/src/rgw/services/svc_bi_rados.h

## Purpose

`svc_bi_rados.h` declares the RADOS implementation of the bucket-index service. It exposes helpers for opening bucket index pools/objects/shards and high-level methods for stats, resharding, index checking/rebuilding/listing, and overwrite handling. The file was read as a complete 191-line header.

## Important APIs, Types, and Functions

The class `RGWSI_BucketIndex_RADOS` derives from `RGWSI_BucketIndex` and is a friend of `RGWSI_BILog_RADOS`. It stores `librados::Rados* rados` and service dependencies in `Svc` (`RGWSI_Zone`, `RGWSI_BILog_RADOS`, `RGWDataChangesLog`). Static helpers include `shards_max()`, `shard_id()`, and `bucket_shard_index()` overloads. Public methods include index lifecycle overrides, RADOS-specific reshard/status/check/rebuild/listing helpers, bucket index opening helpers, and `cls_bucket_head()`.

## Control Flow

The header defines static shard selection logic: generic keys use `rgw_shard_id()`, while bucket-object keys use Linux string hashing with a bit-mixed value and multipart objects hash on the multipart base key. Implementations use `open_bucket_index_*()` before invoking cls or shard_io operations.

## State and Persistence Behavior

The class itself holds service pointers and the librados cluster handle. Persistent state is external in bucket index RADOS objects, bilog state, reshard logs, and datalog entries manipulated by the `.cc` implementation.

## Dependencies and Integration Points

Includes connect it to RADOS datalog/service/tools, `rgw_bucket.h`, the abstract `svc_bi.h`, and tier RADOS service types. It integrates closely with `RGWSI_BILog_RADOS`, `RGWSI_Zone`, bucket layout types, and cls_rgw return structures.

## Risks and Edge Cases

The shard hash functions are part of object placement compatibility; changing them would move object index entries. Public `open_bucket_index()` helpers are used by bilog and other services, so naming/layout bugs have broad impact. Service pointer initialization order must ensure `init()` runs before operations.

## Test Signals

Compile coverage, shard hash golden tests, multipart key shard tests, service initialization tests, and RADOS integration tests for every public method are relevant.
