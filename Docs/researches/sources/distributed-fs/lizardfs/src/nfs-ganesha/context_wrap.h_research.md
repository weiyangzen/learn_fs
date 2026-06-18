# sources/distributed-fs/lizardfs/src/nfs-ganesha/context_wrap.h

## Purpose
Declares the credential-wrapped LizardFS C API used by the NFS-Ganesha plugin.

## Important APIs, Types, And Functions
The header exposes all `liz_cred_*` wrappers for namespace operations, file I/O, directory I/O, attributes, ACLs, chunk info, and locking. It includes Ganesha `fsal_types.h` for `user_cred` and the LizardFS C API for `liz_t`, `liz_fileinfo_t`, inode, ACL, and lock types.

## Control Flow
Consumers call these functions instead of raw `liz_*` calls when an operation must be executed under `op_ctx->creds` or an explicit credential pointer.

## State And Persistence Behavior
No direct state. The header establishes a convention that contexts are temporary and wrapper-owned.

## Dependencies And Integration Points
Integrated by `handle.c`, `export.c`, `ds.c`, `lzfs_acl.c`, `mds_export.c`, `mds_handle.c`, and `main.c`.

## Risks And Edge Cases
The API mirrors raw LizardFS return conventions, so callers must handle `NULL` vs negative integer failures consistently. As a C header without include guards beyond implicit compiler behavior, duplicate inclusion is tolerated by declarations but not explicitly protected.

## Test Signals
Compilation of all FSAL files confirms declaration compatibility; functional credential behavior needs integration testing.
