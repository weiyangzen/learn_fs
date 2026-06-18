# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_cors_handlers.go

Purpose: Implements bucket CORS middleware adapters and S3 `GET/PUT/DELETE ?cors` handlers.

Important APIs/types/functions: fallback method/header variables, `S3BucketChecker`, `S3CORSConfigGetter`, `getCORSMiddleware`, `createFallbackCORSConfig`, `GetBucketCorsHandler`, `PutBucketCorsHandler`, and `DeleteBucketCorsHandler`.

Control flow: middleware wiring adapts `S3ApiServer.checkBucket` and `getCORSConfiguration` to the `cors` package. Bucket handlers first call `checkBucket`; GET loads cached CORS from bucket config and returns `NoSuchCORSConfiguration` when nil. PUT XML-decodes the request, validates via `cors.ValidateConfiguration`, then persists through `updateCORSConfiguration`. DELETE clears persisted CORS and returns 204.

State and persistence: bucket-specific CORS is stored in structured bucket metadata protobuf in `Entry.Content` through `UpdateBucketCORS`/`ClearBucketCORS`; cache is invalidated by the metadata write. Fallback CORS is in-memory from global `AllowedOrigins` and is not persisted.

Dependencies and integration: depends on `cors` package for validation/middleware, bucket config helpers, and S3 error/constant packages. Integrated into request handling for preflight/origin validation and bucket subresource API.

Risks: XML decoder reads directly from body without explicit size cap here. CORS storage shares the last-write-wins structured metadata path with tags/encryption. Fallback rules are broad (`AllowedHeaders: *`, many methods) and must be understood as a global compatibility mode.

Test signals: direct tests are not in this file, but bucket config conversion and CORS behavior are exercised through metadata tests and likely CORS package tests.
