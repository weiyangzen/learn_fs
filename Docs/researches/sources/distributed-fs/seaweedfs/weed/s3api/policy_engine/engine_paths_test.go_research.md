# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_paths_test.go

Purpose: tests extraction of principal variables from IAM and STS ARNs that include path components.

Important APIs and functions: `TestExtractPrincipalVariablesWithPaths` verifies IAM user, IAM role, and assumed-role ARN parsing. Expected variables include `aws:PrincipalAccount`, `aws:principaltype`, `aws:username`, and `aws:userid` where applicable.

Control flow: the test calls `ExtractPrincipalVariables` and compares returned maps to expected values. User and role paths are reduced to the final role/user name. Assumed-role paths use the final session-name segment for username/userid.

State and persistence: no persisted state.

Dependencies and integration: protects the `strings.Split` parsing logic in `engine.go`, which feeds policy variables used by resource patterns and conditions.

Risks: ARN parsing is intentionally simple and assumes AWS-style colon and slash layout. Edge cases such as escaped characters or unusual partition/service forms are not covered.

Test signals: provides path-aware regression coverage for principal-derived variables used in multi-tenant policies.
