# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-create.c

## Purpose

`metadisp-create.c` implements split create semantics: create metadata first, then create the backend data inode addressed by requested GFID.

## Important APIs, Types, and Functions

Functions are `metadisp_create`, `metadisp_create_cbk`, `metadisp_create_resume`, and `metadisp_create_dentry_cbk`. It uses `RESOLVE_GFID_REQ` to fetch `gfid-req`, `build_backend_loc` to create the data child loc, and `fop_create_stub` to defer the data create until metadata create succeeds.

## Control Flow

`metadisp_create` resolves the requested GFID from xdata, builds `backend_loc`, stores a create resume stub, and winds `create` to `METADATA_CHILD`. The metadata callback unwinds on error, destroys poisoned stubs, or resumes the stub. The resume function winds the backend create to `DATA_CHILD`, and the final dentry callback unwinds the original create result.

## State and Persistence Behavior

Metadata and data are persisted in separate children. Temporary state is a call stub containing the backend loc and create arguments. `frame->local = loc` is assigned but not used meaningfully in this file.

## Dependencies and Integration Points

The file depends on Gluster call stubs, xdata `gfid-req`, metadata/data child ordering, and `build_backend_loc`. It assumes metadata child enforces ACLs before data child creation.

## Risks and Edge Cases

If backend creation fails after metadata creation succeeds, the code unwinds the failure but does not roll back the metadata inode. Missing `gfid-req` or backend loc construction failure returns `EINVAL`. Stub poisoning is handled, but backend loc lifetime depends on the stub copying loc data safely.

## Test Signals

Tests should cover create success in both children, metadata ACL denial preventing data creation, missing `gfid-req`, data-child failure after metadata success, and orphan metadata recovery or healing expectations.
