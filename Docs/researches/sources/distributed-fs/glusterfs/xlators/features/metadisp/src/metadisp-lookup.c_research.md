# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-lookup.c

## Purpose

`metadisp-lookup.c` implements two-stage lookup so regular files are verified in both metadata and data children.

## Important APIs, Types, and Functions

Functions are `metadisp_lookup`, `metadisp_lookup_cbk`, `metadisp_backend_lookup_resume`, and `metadisp_backend_lookup_cbk`.

## Control Flow

The top-level fop creates a lookup stub for the backend lookup, then winds lookup to `METADATA_CHILD`. If metadata lookup fails, the callback unwinds immediately. If metadata lookup finds a non-regular object, it also unwinds metadata result only. For regular files, it resumes the backend lookup stub. The backend resume builds a GFID path and winds lookup to `DATA_CHILD`; the backend callback maps backend `ENOENT` to `ENODATA` and unwinds the original lookup.

## State and Persistence Behavior

No long-lived state is stored. The code verifies consistency between persistent metadata and persistent data entries.

## Dependencies and Integration Points

It depends on `IA_ISREG`, `build_backend_loc`, metadata/data child separation, and default lookup unwind signatures.

## Risks and Edge Cases

Backend loc is not wiped in the resume function after winding, so lifetime depends on stack-wind or lower layers copying what they need. Metadata says regular but backend missing becomes `ENODATA`, which callers or healers must understand. The commented GFID copy in the metadata callback suggests earlier uncertainty about where GFID should be sourced.

## Test Signals

Tests should cover directory lookup, regular lookup with data present, metadata missing, data missing producing `ENODATA`, null/invalid GFID producing `EINVAL`, and consistency with stat/open flows.
