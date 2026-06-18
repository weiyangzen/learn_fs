# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-fsync.c

## Purpose

`metadisp-fsync.c` implements fsync across both metadisp children, syncing metadata first and data second.

## Important APIs, Types, and Functions

Functions are `metadisp_fsync`, `metadisp_fsync_cbk`, and `metadisp_fsync_resume`. It uses `fop_fsync_stub` and `default_fsync_cbk`.

## Control Flow

`metadisp_fsync` creates a resume stub for the data child and winds fsync to `METADATA_CHILD` with the stub as cookie. If metadata fsync fails, the callback destroys the stub and unwinds the metadata result. If it succeeds, it resumes the stub, which winds fsync to `DATA_CHILD` and unwinds through the default callback.

## State and Persistence Behavior

The only temporary state is the call stub. Persisted effects are whatever fsync guarantees each child provides for metadata and data storage.

## Dependencies and Integration Points

It depends on the child fops implementing fsync and on Gluster call-stub poisoning semantics.

## Risks and Edge Cases

If data fsync fails after metadata fsync succeeds, the final result reflects the data failure but metadata has already been flushed. A null stub is not explicitly guarded before `stub->poison` when the metadata callback succeeds and cookie is absent.

## Test Signals

Tests should inject metadata fsync failure, data fsync failure, stub allocation failure, and successful two-child fsync ordering.
