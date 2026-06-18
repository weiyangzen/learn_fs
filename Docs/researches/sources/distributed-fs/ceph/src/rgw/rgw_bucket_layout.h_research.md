# sources/distributed-fs/ceph/src/rgw/rgw_bucket_layout.h

Purpose: declares the persisted description of bucket index layouts, bucket log layouts, and resharding status.

Important APIs/types/functions: enums `BucketIndexType`, `BucketHashType`, `BucketLogType`, `BucketReshardState`; structs `bucket_index_normal_layout`, `bucket_index_layout`, `bucket_index_layout_generation`, `bucket_index_log_layout`, `bucket_log_layout`, `bucket_log_layout_generation`, and `BucketLayout`; helpers `log_layout_from_index()`, `matches_gen()`, `log_to_index_layout()`, `num_shards()`, `current_num_shards()`, `current_min_layout_shards()`, `is_layout_indexless()`, `is_layout_reshardable()`, and `current_layout_desc()`.

Control flow: the header defines equality, stream operators, and helper conversions. `num_shards()` treats historical `num_shards=0` as one shard. Reshardability is limited to `Normal` index layouts.

State/persistence: `BucketLayout` carries current and target index generations, untrimmed log generations, resharding state, and `judge_reshard_lock_time`, all persisted by implementations in the `.cc`.

Dependencies/integration: low-level Ceph encoding and JSON; consumed by bucket metadata, resharding, bilog/datalog, and bucket index selection paths.

Risks: equality for `bucket_index_normal_layout` ignores `min_num_shards`, so comparisons may miss minimum-shard changes. Helpers assert normal layout in some paths. Current log/index conversion assumes `InIndex` log layout.

Test signals: helper semantics for zero shards, indexless buckets, reshardable checks, equality expectations including `min_num_shards`, log/index conversion, and generation matching.
