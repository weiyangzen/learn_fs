# sources/distributed-fs/seaweedfs/weed/s3api/s3_existing_object_tag_test.go

Purpose: tests S3 API integration for bucket policies that depend on `s3:ExistingObjectTag/<key>` using object metadata available after entry lookup.

Important APIs and functions: tests call `S3ApiServer.checkPolicyWithEntry`, `NewBucketPolicyEngine`, and `PolicyEngine.HasPolicyForBucket`. They use `s3_constants.AmzObjectTaggingPrefix` metadata keys and expect `s3err` outcomes.

Control flow: the allow-policy test checks public/missing/private tag cases and whether policy evaluation was decisive. No-policy and nil-engine tests assert graceful pass-through. Deny-policy tests verify explicit deny on confidential objects while allowing public/no-tag objects through an allow statement.

State and persistence: object tags are simulated as `map[string][]byte` entry metadata. Bucket policies are in-memory in the policy engine.

Dependencies and integration: validates the phase-two authorization path where an object entry is available, linking S3 handlers to `policy_engine.EvaluateConditions`.

Risks: existing-object-tag conditions cannot be fully evaluated before object metadata is loaded, so callers must ensure the second-phase `checkPolicyWithEntry` path is invoked for relevant operations.

Test signals: strong integration signal for tag-based allow/deny, no-policy fallback, nil policy-engine safety, and `HasPolicyForBucket`.
