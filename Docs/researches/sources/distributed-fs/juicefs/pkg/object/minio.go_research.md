# sources/distributed-fs/juicefs/pkg/object/minio.go


Purpose: implements MinIO/S3-compatible storage behind `!nos3`, registering `minio`.

Important APIs and flow: `minio` embeds the generic `s3client`, overriding `String` and multipart `Limits`. `newMinio` normalizes endpoints to HTTP, parses SSL and optional `region` query, falls back to `MINIO_REGION`, `MINIO_ACCESS_KEY`, and `MINIO_SECRET_KEY`, loads AWS SDK v2 config, builds an S3 client with custom base endpoint, path-style setting, shared HTTP client, unsigned payload middleware, and a single retry attempt. It extracts the bucket from the endpoint path, including a compatibility case for paths starting with `minio/`.

State and persistence: all persistent behavior is delegated to the remote MinIO bucket through `s3client`.

Dependencies and integration: uses AWS SDK v2 and package helpers `defaultPathStyle`, `httpClient`, and generic S3 code outside this subset.

Risks: missing bucket path is an error. Endpoint path parsing only uses the first path segment after optional `minio/`. All provider behavior beyond construction depends on `s3client`. Path-style defaults can be critical for MinIO deployments.

Test signals: `TestMinIO` is environment-gated on `MINIO_TEST_BUCKET`; when configured it runs `testStorage`.
