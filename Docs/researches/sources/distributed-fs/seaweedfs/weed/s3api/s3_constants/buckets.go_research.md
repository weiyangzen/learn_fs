# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/buckets.go

Purpose: defines the default filer path for S3 buckets.

Important APIs and values: `DefaultBucketsPath = "/buckets"`.

Control flow: no functions.

State and persistence: constant only. Actual bucket data persists under the configured buckets path in the filer.

Dependencies and integration: used by S3 server options and bucket path construction.

Risks: any code assuming this value without honoring configuration can diverge from deployments with custom bucket paths.

Test signals: no direct tests in this subset.
