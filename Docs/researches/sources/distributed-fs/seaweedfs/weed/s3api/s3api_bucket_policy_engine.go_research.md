# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_policy_engine.go

Purpose: Wraps the generic policy engine with bucket-specific loading, caching, resource ARN building, action resolution, request-condition extraction, and multipart SSE inheritance.

Important APIs/types/functions: `BucketPolicyEngine`, `NewBucketPolicyEngine`, `LoadBucketPolicy`, `LoadBucketPolicyFromCache`, `DeleteBucketPolicy`, `HasPolicyForBucket`, `GetBucketPolicy`, `ListBucketPolicies`, and `EvaluatePolicy`.

Control flow: load methods read policy JSON from bucket extended attributes or cached `PolicyDocument`, marshal as needed, and call `policy_engine.SetBucketPolicy`; missing policy deletes the engine entry. `EvaluatePolicy` validates bucket/action, resolves SeaweedFS action to S3 action, builds a resource ARN, extracts request condition values and principal variables, injects JWT claims when provided, optionally inherits multipart SSE algorithm by upload ID, then maps engine result to `(allowed, evaluated, error)`.

State and persistence: this wrapper holds in-memory policy engine state only. Durable policy JSON is stored in bucket extended attributes by policy handlers and hydrated here from cache or filer entry.

Dependencies and integration: depends on `policy_engine`, bucket policy metadata key, filer entries, S3 action resolver, request condition extraction, and optional `MultipartSSELookup` installed by `S3ApiServer`. Used by auth paths such as public-read evaluation and IAM authorization.

Risks: policy engine staleness is possible if subscription/cache hydration misses updates, though handlers load/delete immediately after changes. `EvaluatePolicy` fails on empty bucket/action and should be called after routing. Multipart SSE inheritance depends on upload ID and lookup availability.

Test signals: ARN tests indirectly protect resource construction; policy handler and auth tests likely cover evaluation. Direct unit coverage of multipart condition inheritance is not in this subset.
