# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-unlink.c

## Purpose

`metadisp-unlink.c` removes both metadata and data objects while handling cases where the caller arrives without a GFID.

## Important APIs, Types, and Functions

Functions are `metadisp_unlink`, `metadisp_unlink_lookup_cbk`, `metadisp_unlink_cbk`, and `metadisp_unlink_resume`.

## Control Flow

If `loc->gfid` is null, `metadisp_unlink` creates a stub to retry unlink after lookup, winds lookup to `METADATA_CHILD`, and the lookup callback copies `buf->ia_gfid` into `loc->gfid` before resuming. With a GFID present, it filters root, builds a backend loc, creates a data unlink resume stub, and winds unlink to `METADATA_CHILD`. On metadata unlink success it resumes data unlink; backend `ENOENT` is treated as success to allow cleanup of metadata-only objects.

## State and Persistence Behavior

Persistent state is deleted in both children. Temporary state is held in stubs and rewritten loc GFID.

## Dependencies and Integration Points

It depends on root filtering, metadata lookup for GFID resolution, `build_backend_loc`, call stubs, and child unlink semantics.

## Risks and Edge Cases

Metadata unlink success followed by data unlink failure leaves partial deletion. The code mutates the caller's loc by copying GFID during lookup resume. The retry stub uses `metadisp_unlink` itself, so incorrect GFID resolution could loop or reuse stale state. Treating backend ENOENT as success hides missing-data conditions during unlink.

## Test Signals

Tests should cover unlink with and without initial GFID, root unlink filtering, data missing, metadata failure, data failure, and cleanup when lookup returns nonzero.
