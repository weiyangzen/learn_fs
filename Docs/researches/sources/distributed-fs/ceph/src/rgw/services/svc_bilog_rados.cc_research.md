# sources/distributed-fs/ceph/src/rgw/services/svc_bilog_rados.cc

## Purpose

`svc_bilog_rados.cc` implements bucket-index log operations on top of the RADOS bucket-index service. It starts/stops bilog recording, trims bilog ranges, lists log entries across shards, and reads bilog status markers. The file was read as a complete 382-line implementation.

## Important APIs, Types, and Functions

Implemented methods are `RGWSI_BILog_RADOS::init()`, `log_trim()`, `log_start()`, `log_stop()`, `log_list()`, and `get_log_status()`. Internal pieces include `TrimWriter`, `StartWriter`, `StopWriter`, `build_bucket_index_marker()`, `LogReader`, and helper `bilog_list()`.

## Control Flow

Every operation converts a bucket log layout to its backing index layout with `rgw::log_to_index_layout()`, asks `RGWSI_BucketIndex_RADOS::open_bucket_index()` for shard oids, then fans out RADOS cls operations through `rgwrados::shard_io`. Start and stop are simple writes of `cls_rgw_bilog_start()`/`cls_rgw_bilog_stop()`. Trim parses start/end marker strings with `BucketIndexShardsManager`, calls `cls_rgw_bilog_trim()`, and retries until cls reports no more data. Listing parses the input marker, reads per-shard log lists, round-robins entries up to `max`, rewrites entry ids with shard prefixes for sharded indexes, updates per-shard markers, and reports truncation if cls or local merge state has remaining entries.

## State and Persistence Behavior

Bilog state is persisted inside bucket index RADOS objects through cls_rgw bilog methods. Markers are string state owned by callers and encoded/decoded by `BucketIndexShardsManager`. `get_log_status()` reads bucket index headers and returns each shard's `max_marker` keyed by shard.

## Dependencies and Integration Points

The file depends on `svc_bilog_rados.h`, `svc_bi_rados.h`, `rgw_asio_thread.h`, `driver/rados/shard_io.h`, `cls/rgw/cls_rgw_client.h`, and blocked async completion support. It is called by bucket index overwrite handling and by sync/admin paths that consume or trim bucket index logs.

## Risks and Edge Cases

Marker parsing errors abort list/trim. Multi-shard list merging is round-robin rather than globally timestamp-sorted, so consumers must rely on marker semantics rather than a total order. `log_trim()` retries until `ENODATA`; unexpected cls behavior could loop through shard_io retry handling. `get_log_status()` asserts header and instance-id counts match, so malformed results can abort in debug/asserting builds.

## Test Signals

Signals include RADOS cls integration tests for start/stop/trim/list/status, marker round-trip tests for sharded and unsharded logs, pagination/truncation tests, trim-to-ENODATA behavior, and bucket data-sync transition tests through `RGWSI_BucketIndex_RADOS::handle_overwrite()`.
