# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_handlers.go

Purpose: Main bucket API implementation: list, create, delete, head, ACL, lifecycle, location, request payment, ownership controls, versioning, access helpers, auto-create, public-read auth, and bucket ARN helpers.

Important APIs/types/functions: `ListBucketsHandler`, `PutBucketHandler`, `DeleteBucketHandler`, `bucketHasUserObjects`, `checkBucket`, `existingBucketError`, `autoCreateBucket`, `AuthWithPublicRead`, ACL handlers, lifecycle handlers, ownership controls handlers, versioning handlers, `buildResourceARN`, and `isBucketOwnedByIdentity`.

Control flow: bucket listing filters hidden dirs and uses IAM identity/ownership or list permission. creation validates names, parses ACLs, rejects table-bucket conflicts, detects existing collections/directories, atomically stores owner/ACL/Object Lock/versioning in the created entry, and removes negative cache. deletion checks access, Object Lock active locks, non-empty rules, removes bucket directory before best-effort collection deletion, invalidates caches/metrics, and prunes IAM bucket-scoped actions. lifecycle PUT validates XML and rejects transition rules, cleans legacy day-TTL filer.conf entries, then stores canonical XML in bucket extended attributes.

State and persistence: bucket directories live under `option.BucketsPath`; collection names map to bucket storage. Extended attrs store owner, ACL, versioning, ownership controls, Object Lock, and lifecycle XML/header. Lifecycle also interacts with legacy filer.conf TTL entries. Metrics and bucket config caches are invalidated on delete/update. Some paths still use whole-entry `updateEntry` while newer config paths use `updateBucketConfig`.

Dependencies and integration: integrates IAM, bucket registry, filer RPC/list/update/delete, lifecycle XML, AWS SDK XML types, stats, object-lock utilities, public-read bucket policy evaluation, and S3 response helpers. It is the central route target for S3 bucket management.

Risks: mixed persistence styles can race if whole-entry updates overwrite concurrent extended mutations. `PutBucketAclHandler` includes a short sleep for propagation, indicating cache/subscription timing sensitivity. Delete treats collection deletion failure as non-fatal, leaving reusable/orphan cleanup state. Lifecycle transition support is explicitly rejected; lifecycle volume TTL stamping has irreversible semantics handled elsewhere.

Test signals: covered by misc handler tests, lifecycle response tests, policy ARN tests, metadata/config update tests, Object Lock tests elsewhere, and likely broader S3 integration tests. Edge cases for concurrent create/delete and collection orphan recovery need integration coverage.
