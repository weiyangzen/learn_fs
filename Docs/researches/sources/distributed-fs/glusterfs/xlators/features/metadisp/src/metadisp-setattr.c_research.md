# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-setattr.c

## Purpose

`metadisp-setattr.c` applies setattr to metadata first and, for regular files, applies corresponding backend attributes to the data child.

## Important APIs, Types, and Functions

Functions are `metadisp_setattr`, `metadisp_setattr_cbk`, `metadisp_backend_setattr_resume`, and `metadisp_backend_setattr_cbk`.

## Control Flow

The top-level fop creates a backend setattr stub, winds setattr to `METADATA_CHILD`, and resumes the backend stub only when metadata setattr succeeds and the resulting type is regular. The backend resume builds a GFID path and winds setattr to `DATA_CHILD`. Backend `ENOENT` is mapped to `ENODATA`.

## State and Persistence Behavior

The persistent effect is attribute mutation in one or both children. Non-regular objects are only updated in metadata.

## Dependencies and Integration Points

It depends on `IA_ISREG`, `build_backend_loc`, child setattr support, and call stubs.

## Risks and Edge Cases

Metadata setattr can succeed while backend setattr fails, leaving divergent attributes. If `statpost` is null on a nominal success, `IA_ISREG(statpost->ia_type)` would dereference null. Backend loc cleanup is implicit.

## Test Signals

Tests should cover regular and directory setattr, backend missing mapped to `ENODATA`, metadata failure, data failure after metadata success, valid mask propagation, and null/invalid stat buffers in fault injection.
