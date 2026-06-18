# sources/distributed-fs/ceph/src/rgw/rgw_bucket_layout.cc

Purpose: implements string parsing, JSON conversion, and buffer encoding for bucket index/log layout and resharding state metadata.

Important APIs/types/functions: `to_string()/parse()` for `BucketIndexType`, `BucketHashType`, `BucketLogType`, and `BucketReshardState`; encode/decode/JSON functions for `bucket_index_normal_layout`, `bucket_index_layout`, `bucket_index_layout_generation`, `bucket_index_log_layout`, `bucket_log_layout`, `bucket_log_layout_generation`, and `BucketLayout`.

Control flow: each tagged layout encodes its type then conditionally encodes variant payload fields. Decode mirrors switch cases. `BucketLayout::decode()` has legacy behavior: for struct versions before logs existed, it synthesizes a log layout from current index when the index type is normal; version 3 adds `judge_reshard_lock_time`.

State/persistence: these functions define persisted bucket layout metadata, including current index generation, target reshard layout, log generations, and reshard status/time.

Dependencies/integration: used by bucket metadata, resharding code, and JSON/admin output. Depends on Ceph encoding, JSON decoder, `utime`, and Boost case-insensitive parsing.

Risks: unknown enum strings leave fields unchanged because parse return values are ignored in JSON decoders. `Indexless` layouts skip normal fields but some JSON output always includes `normal`, so consumers must tolerate unused data. Layout version changes affect existing buckets.

Test signals: binary compatibility for all struct versions, JSON parse case-insensitivity, legacy decode log synthesis, indexless decode/output, reshard state parse, and num-shard defaults.
