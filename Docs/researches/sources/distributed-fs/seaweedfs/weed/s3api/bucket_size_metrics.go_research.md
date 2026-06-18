# sources/distributed-fs/seaweedfs/weed/s3api/bucket_size_metrics.go

Purpose: periodically collects bucket logical size, physical size, object counts, and quota status from master topology and filer bucket entries, then updates metrics and quota read-only flags.

Important APIs/types: `CollectionInfo`, `volumeKey`, `startBucketSizeMetricsLoop`, `collectAndUpdateBucketSizeMetrics`, `enforceBucketQuotas`, `collectCollectionInfoFromMaster`, `listBuckets`, `ecVolumeAgg`, and `collectCollectionInfoFromTopology`.

Control flow: a delayed loop acquires long-lived lock `s3.leader` and runs every minute only as leader. It fetches topology from a master, paginates bucket entries, maps buckets to collections, updates stats, and enforces quotas. Quota enforcement reads `filer.conf`, applies read-only flags by bucket prefix, and writes back only on change.

State and persistence: metrics are external Prometheus state; quota enforcement persists changed `filer.conf` inside filer. Aggregation is in-memory.

Dependencies and integration points: cluster lock client, master/filer protobuf clients, filer config helpers, stats package, and erasure-coding size helpers.

Risks: regular volumes must be deduped by collection/volume ID while physical replicas still sum. EC shards require physical all-shard size, logical data-shard size, max file count, and summed delete count. Missing filers disables collection.
