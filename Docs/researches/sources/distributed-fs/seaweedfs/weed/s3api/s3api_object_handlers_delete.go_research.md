# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_delete.go

Purpose: implements S3 DeleteObject and DeleteObjects, including versioned delete markers, suspended null-version behavior, object-lock enforcement, conditional If-Match deletes, routed owner fast paths, per-key authorization for batch delete, audit logging, and delete metrics.

Important APIs and types include `deleteMutationResult`, `ObjectIdentifier`, `DeleteObjectsRequest`, `DeleteError`, `DeleteObjectsResponse`, `validateDeleteObjectIdentifier`, `resolveDeleteConditionalEntry`, `checkDeleteIfMatch`, `deleteVersionedObject`, `deleteUnversionedObjectWithClient`, `DeleteObjectHandler`, and `DeleteMultipleObjectsHandler`.

Control flow for single delete resolves bucket/object/version, validates table-bucket paths, gets versioning state, checks `If-Match`, then tries routed delete paths when safe. Versioned deletes with no version create delete markers; specific version deletes remove the named version; suspended deletes remove the null version and create a null delete marker. If routing is unavailable, mutation happens under `withObjectWriteLock` after rechecking conditions. Successful responses set version/delete-marker headers and return 204.

Batch delete reads XML, enforces the 1000-key limit, validates each object key and version ID, authorizes each key because the route cannot know body keys in middleware, and performs each mutation under a per-object write lock. It records deleted objects unless quiet mode is enabled and accumulates per-key errors instead of aborting the whole request.

State and persistence include filer entries, version files and latest pointers, delete markers, null versions, object-lock metadata, and volume chunk deletion behavior. `deleteUnversionedObjectWithClient` translates `metadataOnly` into `IsDeleteData=false`, allowing lifecycle TTL paths to remove metadata without enqueueing chunk delete RPCs.

Dependencies include `filer_pb`, object version helpers, object lock helpers, IAM batch authorization, routed owner APIs, S3 XML/errors, stats counters, and util path joining. Risks include path traversal through keys or version IDs, stale conditional checks around routed paths, object-lock bypass handling, and consistency between version directory state and visible latest object. Companion tests cover identifier validation, unsafe version rejection, metadata-only delete plumbing, path construction, and traversal rejection.
