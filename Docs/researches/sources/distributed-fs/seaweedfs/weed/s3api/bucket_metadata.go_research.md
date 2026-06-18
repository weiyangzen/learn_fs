# sources/distributed-fs/seaweedfs/weed/s3api/bucket_metadata.go

Purpose: maintains cached S3 bucket metadata from filer bucket entries, including ownership controls, ACL grants, owner identity, and table-bucket status.

Important APIs/types: `BucketMetaData`, `BucketRegistry`, `NewBucketRegistry`, `init`, `LoadBucketMetadata`, `buildBucketMetadata`, `RemoveBucketMetadata`, `GetBucketMetadata`, `LoadBucketMetadataFromFiler`, and cache helpers. `loadBucketMetadataFromFiler` is package-level for indirection/testing.

Control flow: initialization lists `option.BucketsPath`, skips hidden names, loads metadata, and warms bucket config cache. Metadata defaults to bucket-owner-enforced ownership and AccountAdmin owner, then validates extended ownership, resolves owners via `AccountManager`, and unmarshals ACL grants. `GetBucketMetadata` checks positive cache, negative cache, then serializes filer loading to avoid duplicate concurrent loads.

State and persistence: persistent metadata lives in filer entry `Extended` keys. Runtime state is `metadataCache` and `notFound`, protected by separate RW mutexes.

Dependencies and integration points: uses `filer_pb.List`, `S3ApiServer.getBucketEntry`, bucket config cache, AWS S3 owner/grant structs, `s3_constants`, `s3err`, and `s3tables`.

Risks: stale positive or negative cache can misrepresent filer changes until invalidated. Invalid extended metadata falls back with warnings, preserving availability but hiding drift.
