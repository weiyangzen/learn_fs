# sources/distributed-fs/seaweedfs/weed/s3api/s3err/s3api_errors.go

Purpose: central typed S3 API error catalog. It maps internal `ErrorCode` constants to AWS-compatible code strings, descriptions, and HTTP status codes, and defines the XML shape for error responses.

Important APIs/types: `APIError`, `RESTErrorResponse`, `ErrorCode`, the large `const` block from `ErrNone` through `ErrNoSuchConfiguration`, checksum message constants, `errorCodeResponse`, and `GetAPIError`.

Control flow: `RESTErrorResponse.Error()` returns explicit `Message` if present, otherwise looks up `Code` in `s3ErrorResponseMap`, otherwise returns a generic code message. `GetAPIError` performs a direct map lookup by `ErrorCode`; callers then write status and XML through `error_handler.go`.

State and persistence behavior: no persisted state. The map is process-global read-only after init. Its values are part of the public S3 protocol contract.

Dependencies and integration points: depends on `net/http`, XML tags, and shared constants. It is used by handlers, auth, multipart upload, object lock, SSE, lifecycle/configuration, listing validation, and error response writers.

Risks: `ErrNone` and any unmapped `ErrorCode` return the zero `APIError` if passed to `GetAPIError`, which can lead to HTTP status 0 and empty XML fields. The growing const block requires careful insertion because integer values are implicit. Some internal codes use non-AWS code strings like `ErrTooManyRequest`, which may not match client expectations. Drift between this map and `s3-error.go` is possible.

Test signals: no dedicated map completeness test in this subset. `error_handler_test.go` exercises `ErrNoSuchKey`; many other packages likely depend on specific constants. A useful future test would iterate all non-`ErrNone` constants expected to be public and assert non-empty code/status.
