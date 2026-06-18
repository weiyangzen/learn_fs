<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_assume_role_empty_arn_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_assume_role_empty_arn_test.go

Purpose: regression test that `AssumeRoleWithWebIdentity` no longer rejects missing `RoleArn` at the HTTP handler layer.

Important APIs/functions: `TestAssumeRoleWithWebIdentity_AllowsEmptyRoleArn` invokes `handleAssumeRoleWithWebIdentity` with `RoleArn` omitted.

Control flow: the form includes action, web identity token, and session name. The handler runs and the test asserts the body does not contain a pre-STS "RoleArn is required" rejection.

State and persistence behavior: no persistent state. It uses a test STS service and in-memory request/response recorder.

Dependencies and integration: relies on the shared test STS setup and `STSHandlers`. It protects claim-based policy mode where role ARN can be derived from token claims/policy.

Risks: the test asserts absence of one error string rather than a full successful claim-based flow. Downstream STS failures are acceptable and not differentiated.

Test signals: passing test indicates the HTTP layer allows empty RoleArn to reach STS service validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_assume_role_empty_arn_test.go -->
