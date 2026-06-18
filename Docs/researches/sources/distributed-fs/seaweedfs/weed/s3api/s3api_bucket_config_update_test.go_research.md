# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_config_update_test.go

Purpose: Verifies `updateBucketConfig` does not mutate cached bucket state when persistence fails.

Important APIs/types/functions: `TestUpdateBucketConfigDoesNotMutateCacheOnPersistFailure`, `newTestS3ApiServerWithMemoryIAM`, `NewBucketConfigCache`, `updateBucketConfig`, `BucketConfig`, and `s3_constants.ExtVersioningKey`.

Control flow: the test seeds a bucket config with empty versioning and no filer connection. It calls `updateBucketConfig` with a callback that sets versioning to `Enabled`. Persistence through `patchBucketEntry` fails, returning `ErrInternalError`; the test reloads the cached config and asserts versioning and extended attributes are unchanged.

State and persistence: deliberately simulates persistence failure before cache invalidation. The important state contract is copy-on-write: mutation happens on a cloned config, so failed writes cannot corrupt the live cache.

Dependencies and integration: integrates with the bucket config cache and filer-free in-memory IAM test server. It directly protects bucket versioning/ACL/Object Lock update paths that share `updateBucketConfig`.

Risks: does not simulate partial filer transaction success, concurrent updates, or mutation of nested pointer fields not deeply cloned. It also does not cover successful cache invalidation.

Test signals: high-value regression test for cache correctness and failed write isolation.
