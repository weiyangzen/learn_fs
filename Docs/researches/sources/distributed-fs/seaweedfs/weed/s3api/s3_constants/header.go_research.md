# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/header.go

Purpose: defines S3 and SeaweedFS header constants plus request/path helper behavior for bucket/object extraction, object-key safety, response header pass-through, internal-header filtering, and authenticated identity context propagation.

Important APIs and values: large constant groups cover S3 namespace, object key length, metadata/tagging/ACL/object-lock/checksum/conditional/SSE headers, internal SSE metadata keys, internal filer headers, trusted principal/session headers, and non-standard identity constants. Functions include `GetBucketAndObject`, `IsValidObjectKey`, `IsValidBucketName`, `IsValidPathSegment`, `NormalizeObjectKey`, `GetPrefix`, `IsSeaweedFSInternalHeader`, `EnsureIdentityHolder`, `SetIdentityNameInContext`, `GetIdentityNameFromContext`, `SetIdentityInContext`, and `GetIdentityFromContext`.

Control flow: object keys are normalized by converting backslashes, collapsing duplicate slashes, and trimming leading slash. Validation rejects NUL and literal `.`/`..` path segments. Identity propagation installs a mutable holder pointer in request context so inner auth handlers can set identity visible to outer middleware holding earlier request copies.

State and persistence: header constants define HTTP and extended metadata contracts. Identity state is request-scoped, using `atomic.Pointer[string]` in the holder.

Dependencies and integration: uses Gorilla mux path vars, `net/http`, `context`, and `sync/atomic`. Used by S3 handlers, auth middleware, audit logging, metadata parsing, encryption, and policy tag handling.

Risks: `NormalizeObjectKey` alone does not reject traversal; callers must also call `IsValidObjectKey`. Internal principal/session headers are trusted only after auth layers scrub client-supplied values.

Test signals: header tests cover normalization, path validation, duplicate slash removal, and identity-holder propagation.
