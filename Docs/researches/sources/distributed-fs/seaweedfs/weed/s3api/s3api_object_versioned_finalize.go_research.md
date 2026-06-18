# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_versioned_finalize.go

## Purpose

This file provides routed finalize and routed delete helpers for versioned objects.

## Important APIs, Types, and Functions

Key functions are `objectWriteOwner`, `latestPointerRecompute`, `routedVersionedFinalize`, `wormDeleteCondition`, `routedDeleteSpecificVersion`, `routedDeleteNullVersion`, and `versionedFinalize`.

## Control Flow

`latestPointerRecompute` builds a `RECOMPUTE_LATEST` mutation over `.versions`, copying latest metadata and optionally excluding a soon-deleted file or demoting the previous latest. Routed finalize and delete helpers send owner-filer `ObjectTransaction` requests under the object lock key. WORM delete conditions enforce legal hold and retention with governance bypass semantics.

## State and Persistence Behavior

The mutations update `.versions` directory latest-pointer metadata, cached latest fields, noncurrent timestamps, and delete version/null entries.

## Dependencies and Integration Points

The file depends on route-key helpers, version id format helpers, filer object transactions, Object Lock constants, and `putFinalize` used by versioned PutObject.

## Risks and Edge Cases

Risks include wrong scan direction for old/new version ids, wrong exclude filename, incorrect demotion, and incorrect WORM precondition mapping.

## Test Signals

Coverage is indirect through versioning and routed-write tests; end-to-end routed versioned PUT/delete tests would add confidence.
