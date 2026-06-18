# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/header_test.go

Purpose: validates object-key normalization/path-safety helpers and request-context identity propagation.

Important APIs and functions: tests cover `NormalizeObjectKey`, `IsValidObjectKey`, `IsValidBucketName`, `IsValidPathSegment`, `removeDuplicateSlashes`, `EnsureIdentityHolder`, `SetIdentityNameInContext`, and `GetIdentityNameFromContext`.

Control flow: table tests check slashes, backslashes, leading/trailing slash behavior, dot segments, NUL bytes, and bucket/path segment rejection. Identity tests simulate outer middleware installing a holder, inner authentication setting identity on a request copy, and outer middleware reading the identity through the shared holder.

State and persistence: only request-scoped context state; no persistence.

Dependencies and integration: protects `header.go` behavior used by mux-based S3 routes, filer path construction, and audit/auth middleware.

Risks: object keys like `.hidden` and `..hidden` remain valid by design, while exact dot segments are invalid. Tests encode that distinction.

Test signals: strong unit coverage for path traversal prevention primitives and identity propagation across request copies.
