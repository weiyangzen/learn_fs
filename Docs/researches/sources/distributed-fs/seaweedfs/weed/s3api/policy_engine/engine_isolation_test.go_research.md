# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_isolation_test.go

Purpose: regression test for per-user folder isolation using dynamic resource variables and an explicit deny with `NotResource`.

Important APIs and functions: `TestIsolationPolicy` constructs a policy with `AllowOwnFolder`, `AllowListOwnPrefix`, and `DenyOtherFolders`. It evaluates `s3:GetObject` for Alice and Bob against their own and each other's prefixes.

Control flow: the test installs a bucket policy with `${aws:username}` in both `Resource` and `NotResource`. Matching own-folder requests hit the allow statement and do not hit the deny statement. Cross-folder requests fail the allow statement and match the deny statement because the requested resource is outside the substituted own-folder pattern.

State and persistence: uses an in-memory `PolicyEngine`; no persisted state.

Dependencies and integration: depends on dynamic pattern compilation in `types.go`, runtime substitution in `engine.go`, and `NotResource` evaluation.

Risks: this pattern is security-sensitive. If callers fail to populate `aws:username` consistently from the authenticated principal, the dynamic allow/deny boundary can become indeterminate or overly broad depending on policy shape.

Test signals: validates explicit deny precedence and dynamic `NotResource` for a common tenant-isolation policy.
