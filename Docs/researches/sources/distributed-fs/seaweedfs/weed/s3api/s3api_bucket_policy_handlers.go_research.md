# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_policy_handlers.go

Purpose: Implements S3 bucket policy GET/PUT/DELETE APIs, policy validation/storage, IAM synchronization hooks, and not-implemented public access block endpoints.

Important APIs/types/functions: `BUCKET_POLICY_METADATA_KEY`, `ErrPolicyNotFound`, `GetBucketPolicyHandler`, `PutBucketPolicyHandler`, `DeleteBucketPolicyHandler`, `getBucketPolicy`, `setBucketPolicy`, `deleteBucketPolicy`, `validateBucketPolicy`, `validateResourceForBucket`, `updateBucketPolicyInIAM`, and public-access-block handlers.

Control flow: GET validates bucket existence then reads policy JSON from bucket extended attributes. PUT reads body, unmarshals JSON, validates core policy and bucket-specific constraints, stores policy, immediately loads it into the policy engine, and best-effort updates IAM integration. DELETE validates bucket and policy existence, removes metadata, immediately deletes engine entry, and best-effort removes IAM integration.

State and persistence: policy JSON is stored under `s3-bucket-policy` in bucket entry extended attributes. Storage uses filer `LookupDirectoryEntry` plus whole-entry `UpdateEntry`, preserving current entry content but potentially overwriting concurrent extended changes if stale. Policy engine and IAM updates are secondary in-memory/external side effects.

Dependencies and integration: uses filer RPCs, `policy_engine.ValidatePolicy`, S3 constants/errors, IAM integration (`S3IAMIntegration` and IAM manager), and bucket policy engine. Public access block APIs currently always return `NotImplemented`.

Risks: whole-entry update path is weaker than `patchBucketEntry` and can race with other extended-attribute writes. `removeBucketPolicyFromIAM` is a TODO-style no-op. PUT does not explicitly cap body size in this file. Validation permits simplified non-ARN resource forms but requires bucket match and `s3:` actions.

Test signals: policy public/status tests and ARN tests cover parts of behavior. End-to-end policy persistence, concurrent mutation, IAM sync, and public access block behavior need broader tests.
