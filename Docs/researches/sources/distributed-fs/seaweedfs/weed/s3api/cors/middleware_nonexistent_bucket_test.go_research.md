# sources/distributed-fs/seaweedfs/weed/s3api/cors/middleware_nonexistent_bucket_test.go

Purpose: tests CORS behavior for non-existent buckets and global fallback policy.

Important tests: `TestMiddlewareNonExistentBucket` and `TestMiddlewareConsistentBehavior`.

Control flow: missing-bucket preflight with wildcard or matching fallback should return 200 with origin header. Actual missing-bucket requests should keep downstream 404 while applying CORS headers. Non-matching origins and no fallback return forbidden preflight without origin headers. Existing and non-existing buckets should produce the same fallback preflight result.

State and persistence: in-memory mocks and httptest recorders.

Dependencies and integration points: mock bucket/config getters, Gorilla mux vars, fallback `CORSConfiguration`, and S3 error codes.

Risks and test signals: documents the deliberate security choice to avoid disclosing bucket existence via CORS. Real behavior depends on production config getter errors matching the mocked assumptions.
