# sources/distributed-fs/seaweedfs/weed/s3api/s3_metadata_util.go

## Purpose
`s3_metadata_util.go` centralizes parsing of upload/copy request headers into SeaweedFS filer metadata. It captures S3 storage class, standard HTTP metadata, object tags, user metadata, SSE-C metadata, and ACL owner/grant markers for storage in `Entry.Extended`.

## Important APIs, Types, and Functions
The file exposes `ParseS3Metadata(r *http.Request, existing map[string][]byte, isReplace bool) (map[string][]byte, s3err.ErrorCode)`.

## Control Flow
The function creates a new metadata map, copies existing metadata unless the caller requested replacement, then selectively records `x-amz-storage-class`, `Content-Encoding`, `Cache-Control`, `Content-Disposition`, `Content-Language`, and `Expires`. It intentionally does not persist response override headers such as response content disposition. Object tags are parsed with `url.ParseQuery`, URL-decoded, checked for duplicate keys, and stored as `x-amz-tagging-<key>`. User metadata headers with the S3 metadata prefix are stored under their canonical Go header name with multiple values comma-joined. SSE-C algorithm and key MD5 are stored, but the customer key itself is not. ACL owner and grants are copied from SeaweedFS extension headers when present.

## State and Persistence Behavior
The returned map is intended for persistence in filer entry extended metadata. Existing metadata can be preserved across metadata updates when `isReplace` is false. Tag and ACL values become durable object metadata once written by the caller.

## Dependencies and Integration Points
The function depends on S3 constants, S3 error codes, Go HTTP header canonicalization, URL query parsing, and glog warnings. It feeds object PUT, copy, and multipart-create paths that later need metadata, ACL, tags, and SSE headers.

## Risks and Edge Cases
Header names are stored in canonicalized form for user metadata, which may matter for consumers expecting lower-case keys. Tag storage prefixes each key into separate metadata entries rather than preserving original tag order. Duplicate tag detection depends on `url.ParseQuery` grouping repeated keys. SSE-C stores only algorithm and MD5 here; IV storage is handled separately.

## Test Signals
Useful tests should cover replacement versus merge behavior, invalid or duplicate tags returning `ErrInvalidTag`, URL-decoded tag values, duplicate user metadata header values, non-persistence of response override headers, and SSE-C/ACL metadata preservation.
