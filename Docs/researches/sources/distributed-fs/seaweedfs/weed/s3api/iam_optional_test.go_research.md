# Research: sources/distributed-fs/seaweedfs/weed/s3api/iam_optional_test.go

## sources/distributed-fs/seaweedfs/weed/s3api/iam_optional_test.go

Purpose: tests for optional IAM behavior when the gateway starts without an IAM config or identities. The target is zero-config S3 usability with advanced IAM plumbing present but not enforcing authentication.

Important APIs and tests: `resetMemoryStore` clears the shared memory credential store when it implements `Reset`. `TestLoadIAMManagerWithNoConfig` checks `NewIdentityAccessManagementWithStore` succeeds with an empty `Config`. `TestLoadIAMManagerFromConfig_EmptyConfigWithFallbackKey` checks no anonymous identity exists when not configured. `TestSetIAMIntegrationKeepsAuthDisabledWithoutConfig` covers issue #9557: calling `SetIAMIntegration` must not enable auth enforcement by itself; `EnableAuthEnforcement` is the explicit opt-in.

State and dependencies: tests mutate global credential stores, build `S3ApiServerOption`, and inspect `iam.isEnabled`. Dependencies are the credential package and testify. Integration points are `weed mini`, Docker default startup, and S3 server setup that installs advanced IAM integration. Risks: global in-memory store pollution can make tests order-sensitive; production risk is accidentally returning AccessDenied for anonymous zero-config deployments. Test signal is concise but important for startup defaults.
