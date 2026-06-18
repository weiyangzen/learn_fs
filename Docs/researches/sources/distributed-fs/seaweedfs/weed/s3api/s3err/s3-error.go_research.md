# sources/distributed-fs/seaweedfs/weed/s3api/s3err/s3-error.go

Purpose: static map of S3 error code strings to human-readable default messages, derived from MinIO/AWS S3 responses.

Important APIs/types: `s3ErrorResponseMap map[string]string` keyed by AWS code strings such as `AccessDenied`, `BadDigest`, `NoSuchBucket`, `SignatureDoesNotMatch`, and `NoSuchCORSConfiguration`.

Control flow: no functions. `RESTErrorResponse.Error()` in `s3api_errors.go` consults this map when the response has no explicit `Message`.

State and persistence behavior: immutable process-local map; no persistence.

Dependencies and integration points: imports SeaweedFS `constants` for shared checksum digest text. It complements the typed `errorCodeResponse` map.

Risks: it is non-exhaustive and can drift from `errorCodeResponse`. Adding a new `APIError.Code` without adding a message here is usually acceptable because `RESTErrorResponse.Error()` falls back to a generic message, but user-facing diagnostics may degrade.

Test signals: no direct tests in this subset. Error response tests indirectly exercise mapped descriptions through `GetAPIError`, not necessarily this map's fallback path.
