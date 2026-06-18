# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/DeleteObjectsResult.java

## Purpose
`DeleteObjectsResult` is the XML response model for S3 multi-object delete. It records successful deletions and per-object errors.

## Important APIs, Types, and Functions
The root element is `DeleteResult`. It exposes unwrapped repeated XML `Deleted` and `Error` lists through `getDeleted`, `setDeleted`, `getErrored`, and `setErrored`. Nested `DeletedObject` models `Key`, `DeleteMarker`, `DeleteMarkerVersionId`, and `VersionId`. Nested `ErrorObject` models `Key`, `Code`, `Message`, and `VersionId`.

## Control Flow, State, and Persistence
Both lists default to empty `ArrayList`s. Nested objects are simple XML DTOs. There is no persistence or control flow beyond getters and setters.

## Dependencies and Integration Points
It is serialized by S3 delete-object handling and depends on Jackson XML annotations. It mirrors AWS response field names sufficiently for non-versioned and partially versioned responses.

## Risks
Nested classes are package-private, so external tests may need package access. Quiet delete behavior must be implemented by callers because this model always has both lists available. `ErrorObject` fields are public as well as exposed by accessors, which allows mutation outside setters.

## Test Signals
Signals should verify XML serialization with no wrapper around repeated elements, success-only, error-only, mixed results, and quiet-mode omission behavior in the caller.
