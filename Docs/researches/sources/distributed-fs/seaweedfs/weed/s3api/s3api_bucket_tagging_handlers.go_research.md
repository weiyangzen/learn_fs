# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_tagging_handlers.go

Purpose: Implements S3 bucket tagging GET/PUT/DELETE handlers.

Important APIs/types/functions: `GetBucketTaggingHandler`, `PutBucketTaggingHandler`, and `DeleteBucketTaggingHandler`.

Control flow: all handlers check bucket access. GET loads structured bucket metadata and returns `NoSuchTagSet` when the tags map is empty. PUT reads the request body limited by `ContentLength`, unmarshals XML into `Tagging`, converts to a map, validates tags, and persists via `UpdateBucketTags`. DELETE clears tags via `ClearBucketTags` and returns 204.

State and persistence: tags are stored in structured protobuf `BucketMetadata` in bucket entry content. Updates share `UpdateBucketMetadata` read-modify-write semantics with CORS/encryption.

Dependencies and integration: depends on XML tag helpers (`Tagging`, `FromTags`, `ValidateTags`), bucket metadata API, S3 constants/errors, and access checks. Integrated with lifecycle/object policy paths that may reference tags indirectly elsewhere.

Risks: using `io.LimitReader(r.Body, r.ContentLength)` can behave poorly when `ContentLength` is negative or absent. Structured metadata last-write-wins can lose concurrent CORS/encryption changes. GET maps metadata load failures to internal error rather than absent tag set.

Test signals: no direct tests in this subset; bucket metadata tests cover underlying data object, and broader S3 tagging tests likely cover XML behavior.
