# sources/distributed-fs/seaweedfs/weed/s3api/auth_credentials_policy_sync_test.go

Purpose: Regression tests for synchronizing runtime S3 IAM policies from `IdentityAccessManagement` into the advanced `integration.IAMManager` policy engine.

Important APIs, types, and functions: `newTestIAMManager` creates a memory-backed IAM manager with STS and policy engines. Tests exercise `SetIAMIntegration`, `PutPolicy`, `DeletePolicy`, `resyncIAMManagerPolicies`, and `integration.IAMManager.IsActionAllowed`.

Control flow and state: Each test installs policy JSON into `iam.policies`, attaches an IAM integration, and asks the manager whether named policies allow `s3:PutObject` on matching resources. The stale-snapshot test mutates `iam.policies` directly under lock, calls `resyncIAMManagerPolicies`, and verifies the manager converges to the current map.

State and persistence behavior: All state is in-memory. The tests model the production behavior where `SyncRuntimePolicies` is a full desired-state replacement, so ordering and snapshot freshness matter.

Dependencies and integration points: Depends on `weed/iam/integration`, `policy`, `sts`, protobuf IAM policies, and `testify/require`. It specifically covers the bridge implemented in `auth_credentials.go` between legacy policy storage and the advanced IAM manager.

Risks and test signals: The tests pin three risks: `PutPolicy` must immediately grant through the IAM manager, `DeletePolicy` must remove grants, and `SetIAMIntegration` must flush policies loaded before integration attachment. The final test protects against concurrent update races that could resurrect deleted policies or drop new ones.
