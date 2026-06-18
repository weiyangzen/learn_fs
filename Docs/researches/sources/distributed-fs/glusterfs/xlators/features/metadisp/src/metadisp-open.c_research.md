# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-open.c

## Purpose

`metadisp-open.c` opens both the metadata object and the backend data object for a regular file.

## Important APIs, Types, and Functions

Functions are `metadisp_open`, `metadisp_open_cbk`, and `metadisp_open_resume`.

## Control Flow

`metadisp_open` builds a backend loc from `loc->gfid`, creates an open resume stub for that backend loc, and winds open to `METADATA_CHILD`. The callback resumes the stub only if metadata open succeeds; the resume function winds open to `DATA_CHILD` using the same callback with a null cookie, so the second callback unwinds the final result.

## State and Persistence Behavior

Temporary state is the call stub and backend loc. Persistent state is limited to the open state each child associates with the fd.

## Dependencies and Integration Points

It depends on `build_backend_loc`, child open fops, `fd_t` sharing across child opens, and call-stub poison handling.

## Risks and Edge Cases

If metadata open succeeds and data open fails, metadata fd state may remain open without explicit rollback. A successful callback with null cookie on the first stage would unwind without setting an error. Backend loc lifetime and cleanup are implicit through the stub.

## Test Signals

Tests should cover successful dual open, metadata denial, data child missing or denied, null GFID/backend loc failure, and fd cleanup after partial failure.
