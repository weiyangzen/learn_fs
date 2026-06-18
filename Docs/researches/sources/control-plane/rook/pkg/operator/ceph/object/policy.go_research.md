# sources/control-plane/rook/pkg/operator/ceph/object/policy.go

Purpose: provides a small S3 bucket-policy model and fluent helpers for constructing, reading, modifying, and applying bucket policies through `S3Agent`.

Important APIs/types: `action` constants for many S3 actions; `AllowedActions`; `effect`; `PolicyStatement`; `BucketPolicy`; `NewBucketPolicy`; `S3Agent.PutBucketPolicy`; `S3Agent.GetBucketPolicy`; `BucketPolicy.ModifyBucketPolicy`; `BucketPolicy.DropPolicyStatements`; `NewPolicyStatement`; fluent methods `WithSID`, `ForPrincipals`, `ForResources`, `ForSubResources`, `Allows`, `Denies`, and `Actions`.

Control flow: construction copies passed statements into a versioned policy. Put marshals the policy to JSON and sends `PutBucketPolicy` with `ConfirmRemoveSelfBucketAccess=false`. Get fetches policy JSON and unmarshals it into the local struct. Modify replaces the entire statement slice with the supplied statements. Drop removes the first matching statement for each SID. Fluent statement methods append AWS-style ARNs for Ceph users and buckets, set allow/deny only if no effect is already set, and set actions.

State and persistence: policy state exists in memory until pushed; `PutBucketPolicy` persists to RGW/S3 bucket policy; `GetBucketPolicy` reads persisted policy. No Kubernetes state is touched.

Dependencies and integration points: depends on `S3Agent` from `s3-handlers.go`, AWS SDK v2 S3 policy APIs, and Kubernetes JSON helpers. It is likely used by bucket/user controllers to grant access.

Risks: JSON marshal error is ignored; `GetBucketPolicy` assumes `out.Policy` is non-nil; `DropPolicyStatements` removes only the first statement for a SID per requested SID; `Allows` and `Denies` are first-writer-wins, so callers cannot change an existing effect through chaining. The `Principal` comment spells "Principle" in constants but the JSON key is correct.

Test signals: `policy_test.go` specifically locks down the newer replace-not-merge behavior of `ModifyBucketPolicy`, including duplicate SID replacement and preserving passed statement order.
