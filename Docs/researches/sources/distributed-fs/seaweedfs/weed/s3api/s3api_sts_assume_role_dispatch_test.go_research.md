<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_assume_role_dispatch_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_assume_role_dispatch_test.go

Purpose: verifies that public `AssumeRoleWithWebIdentity` STS handling dispatches through `IAMManager` when available instead of directly calling the bare STS service.

Important APIs/functions: `TestAssumeRoleWithWebIdentity_DispatchesThroughIAMManager` directly exercises `STSHandlers.assumeRoleWithWebIdentity`.

Control flow: one subtest wires an uninitialized IAMManager and nil STS service, expecting an IAM-manager-not-initialized error. The other omits IAM integration and expects fallback to an uninitialized bare STS service error.

State and persistence behavior: no persistent state; the test relies on distinct initialization errors as behavioral evidence of dispatch choice.

Dependencies and integration: uses `integration.IAMManager`, `NewS3IAMIntegration`, and STS request types. It guards cross-account provider-scope and max-session-duration enforcement that live on IAMManager.

Risks: error-message-based assertions are fragile if initialization errors are reworded. The test does not build a full OIDC provider stack, so it validates dispatch path rather than successful assumption.

Test signals: passing test means web identity HTTP paths will not silently skip IAMManager-only validation when an IAM manager is configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_sts_assume_role_dispatch_test.go -->
