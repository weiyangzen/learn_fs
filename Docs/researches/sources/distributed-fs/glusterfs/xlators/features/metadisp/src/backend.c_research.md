# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/backend.c

## Purpose

`backend.c` contains the metadisp helper for translating a user-visible location into the data-backend namespace. Metadisp stores metadata in one child and file data in another; the data child addresses file data by GFID-style paths.

## Important APIs, Types, and Functions

The single exported function is `build_backend_loc(uuid_t gfid, loc_t *src_loc, loc_t *dst_loc)`. It validates source and destination locs, copies the source loc, overwrites parent GFID with root, builds a `/<gfid>` path string using `uuid_utoa_r`, and updates `path` and `name` in the destination loc.

## Control Flow

The helper copies `src_loc`, frees the copied path because it is replaced, formats the supplied GFID into a newly allocated path, assigns `dst_loc->path`, and derives `dst_loc->name` from the final slash when the source had a name. Validation failure returns `-1`.

## State and Persistence Behavior

The function allocates path memory with `GF_CALLOC`; ownership is transferred to `dst_loc` and expected to be released by `loc_wipe`. It does not persist data beyond the loc structure.

## Dependencies and Integration Points

It depends on `metadisp.h`, Gluster loc helpers, UUID formatting, GFID buffer size constants, and common memory types. It is used by data-child fops such as lookup, open, stat, setattr, create, unlink, and generated dataloc operations.

## Risks and Edge Cases

Allocation failure is not explicitly checked after `GF_CALLOC`, so a null path could be dereferenced. The function assumes the supplied GFID is valid; callers must reject null GFIDs where necessary. Any loc copied into `dst_loc` must be wiped by the caller to avoid leaking references and path memory.

## Test Signals

Tests should verify root parent GFID replacement, expected `/<uuid>` path construction, name extraction, loc cleanup with `loc_wipe`, invalid input handling, and callers' behavior with null or missing GFIDs.
