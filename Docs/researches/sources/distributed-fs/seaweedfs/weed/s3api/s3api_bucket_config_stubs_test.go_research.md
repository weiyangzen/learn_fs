# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_config_stubs_test.go

Purpose: Unit-tests stub bucket configuration endpoints for analytics, inventory, intelligent-tiering, and metrics.

Important APIs/types/functions: `TestBucketConfigStubs` creates an `S3ApiServer` with enabled IAM and a prefilled `BucketConfigCache`, then exercises the list and get handlers through mux bucket variables and `httptest`.

Control flow: list cases call each `List*Configurations` handler and assert HTTP 200, expected XML root element, and `<IsTruncated>false</IsTruncated>`. get cases call each `Get*Configuration` handler and assert HTTP 404 plus `<Code>NoSuchConfiguration</Code>`.

State and persistence: the test avoids filer I/O by placing a synthetic bucket config into cache. No persistent mutation is expected.

Dependencies and integration: depends on `gorilla/mux`, `httptest`, `filer_pb.Entry`, and `NewBucketConfigCache`. It validates that `stubBucketGuard` can succeed from cache and that XML/error response helpers produce AWS-shape payloads.

Risks: does not test missing bucket precedence, IAM denial, XML namespace on list responses, or request IDs/logging. Since it relies on cache, it does not cover filer-backed `checkBucket`.

Test signals: strong regression signal for SDK compatibility probes: list endpoints remain non-failing empty responses while get endpoints report absent configuration.
