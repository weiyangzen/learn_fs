# Research: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_issue_9103_test.go

## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_issue_9103_test.go

Purpose: regression tests for issue #9103, where Iceberg clients need correct bucket routing and S3 FileIO configuration.

Important tests: `TestGetBucketFromPrefix_WarehouseQueryFallback` verifies `getBucketFromPrefix` uses `?warehouse=s3://bucket/` when no route prefix is present, ignores warehouse subpaths for routing, and falls back to `warehouse` on malformed or missing input. `TestBuildFileIOConfig` checks an empty endpoint yields no config and a configured endpoint advertises `s3.endpoint`, `s3.path-style-access=true`, and a non-empty region.

State and dependencies: tests use `httptest.NewRequest` and simple `Server{s3Endpoint: ...}` state. Integration points are `/v1/config`, load-table responses, DuckDB attach flows, and S3 direct file access by clients. Risks covered include clients landing on the wrong table bucket or requiring an external AWS region setting. Test signal directly targets helper behavior.
