# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_config_stubs.go

Purpose: Provides AWS-compatible stub endpoints for bucket subresources SeaweedFS does not persist: analytics, inventory, intelligent-tiering, and metrics.

Important APIs/types/functions: `s3XMLNamespace`, XML response structs for list operations, `stubBucketGuard`, `GetAnalyticsConfiguration`, `ListBucketAnalyticsConfigurations`, `GetInventoryConfiguration`, `ListBucketInventoryConfigurations`, `GetIntelligentTieringConfiguration`, `ListBucketIntelligentTieringConfigurations`, `GetMetricsConfiguration`, and `ListBucketMetricsConfigurations`.

Control flow: every handler first runs `stubBucketGuard`, which extracts the bucket and delegates to `checkBucket`. Missing/inaccessible buckets return the normal S3 bucket error before any subresource behavior. `Get*Configuration` endpoints return `NoSuchConfiguration`; `List*Configurations` endpoints return empty, well-formed XML with `IsTruncated=false`.

State and persistence: no persistent state is read or written except normal bucket existence/access checks through bucket config. The response structs encode only namespace and truncation status.

Dependencies and integration: uses `s3_constants` for bucket extraction, `s3err` for S3 error mapping, and common XML response helpers. These routes support SDKs and tools that probe optional bucket configuration APIs during discovery.

Risks: intentionally incomplete feature support can surprise clients that expect to create or mutate these subresources. The guard preserves bucket precedence, but it does not distinguish unsupported get by ID versus absent configuration beyond `NoSuchConfiguration`.

Test signals: `s3api_bucket_config_stubs_test.go` verifies successful empty list XML for all four list endpoints and 404 `NoSuchConfiguration` for all get endpoints against a cached existing bucket.
