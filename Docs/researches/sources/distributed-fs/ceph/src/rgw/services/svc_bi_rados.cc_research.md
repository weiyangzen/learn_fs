# sources/distributed-fs/ceph/src/rgw/services/svc_bi_rados.cc

## Purpose

`svc_bi_rados.cc` implements the RADOS-backed bucket-index service. It maps `RGWBucketInfo` and bucket index layout generations to RADOS index objects, performs asynchronous shard fan-out for index lifecycle/read/list/status operations, and coordinates bilog/datalog updates when bucket data-sync flags change. The file was read as a complete 1048-line implementation.

## Important APIs, Types, and Functions

Public methods implemented include `init()`, `open_pool()`, `open_bucket_index_pool()`, `open_bucket_index_base()`, several `open_bucket_index()` overloads, `get_bucket_index_object()`, `open_bucket_index_shard()`, `cls_bucket_head()`, `init_index()`, `clean_index()`, `read_stats()`, `get_reshard_status()`, `set_reshard_status()`, `trim_reshard_log()`, `set_tag_timeout()`, `check_index()`, `rebuild_index()`, `list_objects()`, and `handle_overwrite()`.

Internal helpers include `bucket_obj_with_generation()`, `bucket_obj_without_generation()`, `get_bucket_index_objects()`, `get_bucket_instance_ids()`, and shard_io reader/writer structs such as `IndexHeadReader`, `IndexInitWriter`, `IndexCleanWriter`, `ReshardStatusReader`, `ReshardStatusWriter`, `ReshardTrimWriter`, `TagTimeoutWriter`, `CheckReader`, `RebuildWriter`, and `ListReader`.

## Control Flow

Index object lookup starts by opening an index pool. Explicit bucket placement index pools win; otherwise the service uses the zonegroup default placement when a bucket lacks a placement rule, then looks up that placement in local zone params. Bucket index object names are `.dir.<bucket_id>` for unsharded indexes, `.dir.<bucket_id>.<shard>` for legacy generation 0 sharded indexes, and `.dir.<bucket_id>.<gen>.<shard>` for generated layouts.

Shard fan-out operations build a shard-id-to-oid map, create an appropriate `rgwrados::shard_io` reader/writer, then run either on the caller coroutine executor (`optional_yield`) or on a system executor with `ceph::async::use_blocked`. `init_index()` uses `RadosRevertibleWriter` so partial shard creation is reverted on failure. `list_objects()` handles `RGWBIAdvanceAndRetryError` by retrying with an advanced shard marker. `handle_overwrite()` compares old/new data-sync flags, starts or stops bilog as needed, then writes datalog entries for all log shards.

## State and Persistence Behavior

Persistent state is in RADOS bucket index objects and their omap headers/CLS-managed contents. CLS operations include bucket index initialization, head reads, reshard status get/set, reshard log trim, tag timeout updates, index checks, rebuild, and bucket listing. `read_stats()` aggregates main-category stats from bucket index headers. `handle_overwrite()` persists bilog start/stop state in index objects and writes data changes through `RGWDataChangesLog`.

## Dependencies and Integration Points

The file depends on `svc_bi_rados.h`, `svc_bilog_rados.h`, `svc_zone.h`, `rgw_asio_thread.h`, `rgw_zone.h`, `driver/rados/rgw_datalog.h`, `driver/rados/shard_io.h`, `cls/rgw/cls_rgw_client.h`, and async/error helpers. It integrates with local zone placement state, RADOS IoCtx creation, cls_rgw object-class methods, bilog service, datalog service, bucket layout helpers, and coroutine/blocking execution paths.

## Risks and Edge Cases

Empty bucket ids return `-EIO` because index object names cannot be formed. Placement-rule lookup failures return `-EINVAL` and block index access. Shard id checks use `std::cmp_greater(shard_id, num_shards)` or `shard_id > num_shards`; off-by-one behavior around `num_shards` deserves scrutiny because valid shard ids are zero-based. `cls_bucket_head()` ignores missing index objects but decode failures become `-EIO`. `init_index()` ignores `EEXIST` per shard but still aims for all-or-nothing for other failures. `handle_overwrite()` returns the final datalog result and treats datalog errors as fatal after bilog changes, so partial side effects are possible.

## Test Signals

Signals include unit tests for shard object naming with/without generations, shard selection for normal and multipart object keys, RADOS integration tests for index create/clean/head/list/check/rebuild, reshard status/log tests, coroutine and blocking execution coverage, data-sync flag transition tests that verify bilog and datalog writes, and error-injection tests for placement lookup, empty bucket ids, decode failures, and partial shard failures.
