# Research: sources/distributed-fs/seaweedfs/weed/s3api/iam_batch_delete_test.go

## sources/distributed-fs/seaweedfs/weed/s3api/iam_batch_delete_test.go

Purpose: regression tests for IAM authorization of S3 multi-object delete requests. The core behavior is that each key in a batch delete must be authorized against its object ARN, not only against the bucket-level ARN.

Important tests: `TestAuthorizeBatchDeleteKey_AwsCanonicalPolicy` creates a policy granting `s3:DeleteObject` on `arn:aws:s3:::bucket/*`, attaches it to an identity, and checks that deleting `objects/a.txt` in the bucket succeeds while another bucket is denied. `TestAuthorizeBatchDeleteKey_PrefixScopedPolicy` grants only `bucket/safe/*` and checks per-key allow/deny.

State and dependencies: tests build in-memory `IdentityAccessManagement` with `isAuthEnabled=true`, use `PutPolicy`, synthetic `Identity`/`Credential`, and `httptest` requests. Integration point is the delete handler loop that calls `AuthorizeBatchDeleteKey` for each object. Risk covered: a bucket-level precheck would reject valid AWS-style object policies or allow a whole batch based on one broad decision. Test signal is focused on object ARN construction and prefix scoping.
