## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/permissions_test.go

Purpose: unit-tests policy matching primitives and default-allow behavior for S3 Tables authorization.

Important tests: `TestMatchesActionPattern`, `TestMatchesPrincipal`, `TestEvaluatePolicyWithConditions`, and `TestCheckPermissionWithDefaultAllow`.

Control flow: table-driven tests assert exact, suffix, middle, question-mark, and combined wildcard behavior; direct, wildcard, array, and AWS-map principal matching; multi-operator condition evaluation over namespace, table name, request tags, and resource tags; and explicit deny overriding fallback allow.

State and dependencies: no persistence. The condition test marshals a `PolicyDocument` to exercise the same JSON path used by production.

Signals and risks: coverage is strong for matching semantics but does not test resource ARN arrays or every supported condition key. It confirms the move to `policy_engine` wildcard support for middle wildcards and protects the security rule that deny wins over `DefaultAllow`.
