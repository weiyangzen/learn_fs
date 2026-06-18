# sources/distributed-fs/seaweedfs/weed/s3api/s3_error_utils.go

Purpose: small helper file for consistent multipart operation error logging and return shape.

Important APIs and functions: `handleMultipartError` logs an operation-specific error and returns `(nil, errorCode)`. `handleMultipartInternalError` specializes it for `s3err.ErrInternalError`.

Control flow: callers pass an operation string, original error, and S3 error code. The helper logs through `glog.Errorf` and returns values compatible with multipart APIs that return an object plus `s3err.ErrorCode`.

State and persistence: no state.

Dependencies and integration: depends on SeaweedFS `glog` and `s3err`. Integrated by multipart handlers to reduce duplicated error handling.

Risks: logs include raw error text; callers should avoid passing sensitive details. The helper always returns nil payload, so it is only suitable for failure paths.

Test signals: no direct tests in this subset.
