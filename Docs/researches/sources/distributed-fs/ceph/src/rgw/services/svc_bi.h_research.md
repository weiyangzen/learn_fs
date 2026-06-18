# sources/distributed-fs/ceph/src/rgw/services/svc_bi.h

## Purpose

`svc_bi.h` declares the abstract RGW bucket-index service interface. It separates bucket metadata services from the backend that initializes, cleans, reads, and reacts to changes in bucket index state. The file was read as a complete 49-line header.

## Important APIs, Types, and Functions

`RGWSI_BucketIndex` derives from `RGWServiceInstance` and declares pure virtual methods: `init_index()`, `clean_index()`, `read_stats()`, and `handle_overwrite()`. Inputs include `RGWBucketInfo`, bucket index layout generations, optional coroutine yield contexts, and a flag to probe log-record support during index initialization.

## Control Flow

The header has no implementation flow. Concrete services such as `RGWSI_BucketIndex_RADOS` implement shard creation/removal, stat reads, and overwrite side effects.

## State and Persistence Behavior

No state is stored here. Implementations own persistence details, typically RADOS bucket index objects and bucket index logs.

## Dependencies and Integration Points

It includes `driver/rados/rgw_service.h` and forward-declares `RGWBucketInfo`/`RGWBucketEnt`. `svc_bucket_sobj.cc` uses this interface for bucket stats and overwrite handling; RADOS-specific code implements it in `svc_bi_rados.{h,cc}`.

## Risks and Edge Cases

The interface assumes all implementations can map high-level bucket layouts to backend index operations. `handle_overwrite()` is part of metadata write flow, so failures can block bucket-info updates. `init_index()`'s `judge_support_logrecord` flag is backend-specific but exposed through the generic interface.

## Test Signals

Compile-time interface coverage, mock implementations for bucket metadata unit tests, and backend integration tests for index lifecycle and overwrite behavior are the main signals.
