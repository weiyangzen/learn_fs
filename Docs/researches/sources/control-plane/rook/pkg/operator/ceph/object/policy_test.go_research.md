# sources/control-plane/rook/pkg/operator/ceph/object/policy_test.go

Purpose: focused unit tests for `BucketPolicy.ModifyBucketPolicy`.

Important APIs/tests: `TestModifyBucketPolicy` has subtests for duplicate SID replacement, full statement replacement, and preserving the order of newly supplied statements.

Control flow: each subtest builds a `BucketPolicy` with one or more `PolicyStatement`s using fluent helpers, calls `ModifyBucketPolicy`, then asserts statement count, SID, and effect.

State and persistence: all state is in memory. No S3 calls or serialization paths are invoked.

Dependencies and integration points: uses the policy builder API in `policy.go` and `stretchr/testify/assert`.

Risks: the test only covers modify semantics. It does not cover JSON shape, ARN formatting, put/get S3 integration, `DropPolicyStatements`, or first-writer-wins behavior in `Allows`/`Denies`.

Test signals: the file clearly documents intended behavior after a semantic change: modification replaces the statement list, rather than merging by SID.
