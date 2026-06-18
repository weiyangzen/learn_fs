# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_config.go

Purpose: Implements SeaweedFS S3 bucket configuration state: cached bucket entries, structured bucket metadata, CORS conversion, versioning/ownership helpers, Object Lock and bucket policy cache hydration, lifecycle TTL fast-path derivation, and per-bucket KMS data-key caching.

Important APIs/types/functions: `BucketConfig`, `BucketConfigCache`, `BucketKMSCache`, `BucketMetadata`, `getBucketConfig`, `populateBucketConfigDerivedFields`, `updateBucketConfig`, `patchBucketEntry`, `getBucketMetadata`, `setBucketMetadata`, `UpdateBucketTags`, `UpdateBucketCORS`, `UpdateBucketEncryption`, lifecycle/CORS conversion helpers, and versioning/object-lock helpers.

Control flow: reads first consult negative cache, then positive cache, then filer bucket entry lookup. `populateBucketConfigDerivedFields` is the central mapper from `Entry.Extended` and `Entry.Content` into cached fields, then syncs bucket policy into the policy engine. Updates clone the cached config, apply the caller mutation, compute extended-attribute set/delete deltas, persist through `ObjectTransaction`, then invalidate cache instead of trusting a potentially stale clone.

State and persistence: extended attributes store versioning, ownership, ACL, owner, Object Lock, lifecycle XML/header values, public-read derivation source, and policy JSON. Protobuf `Entry.Content` stores structured `s3_pb.BucketMetadata` for tags, CORS, and encryption. `patchBucketEntry` uses a lock/route key to serialize bucket config writes through the owning filer; structured metadata remains read-modify-write with documented last-write-wins semantics.

Dependencies and integration: depends on filer protobufs, `proto`, AWS S3 grant types, KMS data key responses, CORS/lifecycle/policy packages, S3 constants/errors, `objectWriteLockClient`, and the bucket policy engine. It is consumed by bucket handlers, CORS/tagging/encryption handlers, Object Lock, lifecycle, ACL/public-read auth, and write-path lifecycle TTL resolution.

Risks: structured metadata updates can overwrite concurrent changes to different fields. Negative cache staleness can briefly hide newly created buckets until invalidated. Policy storage here and policy handlers both manipulate `BUCKET_POLICY_METADATA_KEY`, so whole-entry updates elsewhere can lose unrelated extended keys. KMS cache zeroing only knows the concrete `*kms.GenerateDataKeyResponse` type. CORS `MaxAgeSeconds` nil becomes zero in protobuf round trips.

Test signals: covered by bucket metadata tests, update-failure cache immutability test, lifecycle response tests, CORS/tagging/handler tests indirectly, and policy/ACL behavior tests. High-risk concurrency and filer transaction failure paths are mostly integration-tested rather than unit-tested.
