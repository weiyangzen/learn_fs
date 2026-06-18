# sources/distributed-fs/seaweedfs/weed/s3api/s3_granular_action_security_test.go

Purpose: security-focused tests demonstrating that context-aware action resolution fixes coarse-action authorization gaps.

Important APIs and functions: helper `createTestRequestWithQueryParams` builds requests and extracts bucket/object. Tests include `TestGranularActionMappingSecurity`, `TestBackwardCompatibilityFallback`, `TestPolicyEnforcementScenarios`, `TestDeleteObjectPolicyEnforcement`, `TestFineGrainedPolicyExample`, and `TestCoarseActionResolution`.

Control flow: tests construct HTTP methods, paths, and query parameters, call `ResolveS3Action`, and assert precise AWS action strings. Cases cover DELETE object, ACL reads, tagging, multipart initiation, bucket policy updates, multipart upload listing, batch delete, and coarse `ACTION_WRITE` resolution.

State and persistence: no persisted state; tests are pure resolver checks.

Dependencies and integration: protects `s3_action_resolver.go` and `s3_constants` action strings. It documents intended security policy scenarios such as append-only buckets and metadata-only roles.

Risks: several tests log policy examples but do not run full policy evaluation. They prove action mapping, not end-to-end enforcement.

Test signals: high-value regression coverage for the critical bug class where `ACTION_WRITE` previously mapped DELETE operations to `s3:PutObject`.
