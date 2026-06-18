# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_routed_write.go

## Purpose

This file implements owner-routed object write helpers for PUT, multipart completion, metadata replacement, and eligible deletes.

## Important APIs, Types, and Functions

Important functions include `objectRouteKey`, `routableWriteOwner`, `routedObjectOwner`, `routeWriteCondition`, `buildWriteCondition`, `buildDeleteCondition`, `singleStrongETag`, `objectTxnOnFiler`, `routedPut`, `routedMkFile`, `writeMultipartObject`, `routedDelete`, and `routedMetadataReplace`.

## Control Flow

Writes hash `s3.object.write:<filer path>` to an owner filer. Simple strong ETag/existence preconditions are reduced into `filer_pb.WriteCondition`; complex or time-based conditions fall back to the gateway lock path. Routed PUTs send a PUT plus optional finalize mutations in one object transaction. Metadata replacement patches managed extended keys instead of rewriting the whole entry.

## State and Persistence Behavior

Persistent changes are owner-filer object mutations: PUT, DELETE, and PATCH_EXTENDED. Route keys allow filer-side forwarding if the gateway's ring view is stale.

## Dependencies and Integration Points

The file depends on filer object transactions, conditional-header parsing, route ownership, `pb.WithFilerClient`, S3 constants/errors, and metadata-copy helpers. It integrates with PutObject, multipart completion, DeleteObject, CopyObject metadata replacement, and versioned finalize.

## Risks and Edge Cases

Risks include routing conditions that require full gateway evaluation, stale owners, transaction response errors, metadata delete-list mistakes, and bypassing versioning/Object Lock restrictions.

## Test Signals

Companion tests cover condition reduction, ETag parsing, date parsing, delete conditions, and unique-version routing restrictions.
