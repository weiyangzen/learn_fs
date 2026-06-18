# sources/distributed-fs/seaweedfs/weed/s3api/bucket_size_metrics_test.go

Purpose: unit tests for bucket metrics topology aggregation across erasure-coded and mixed regular/EC volumes.

Important tests: `TestCollectCollectionInfoFromTopologyEC`, `TestCollectCollectionInfoFromTopologyMixed`, and `TestCollectCollectionInfoFromTopologyECFileCountMaxDedupe`.

Control flow: tests construct `master_pb.TopologyInfo` trees directly. EC-only coverage expects physical size to sum all shards, logical size to sum data shards, file count to use max reporter value, delete count to sum, and volume count to dedupe to one. Mixed coverage requires regular and EC volumes in one collection to accumulate. Slow `.ecx` coverage requires a nonzero reporter to win over zero.

State and persistence: in-memory only.

Dependencies and integration points: exercises `collectCollectionInfoFromTopology` and `CollectionInfo` using master protobuf messages.

Risks and test signals: protects a regression where EC conversion caused bucket metrics to drop to zero. It does not cover gRPC fetching, locking, Prometheus writes, or quota persistence.
