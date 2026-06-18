# sources/distributed-fs/lizardfs/src/nfs-ganesha/context_wrap.c

## Purpose
Provides credential-aware wrapper functions around the LizardFS C client API for the NFS-Ganesha FSAL.

## Important APIs, Types, And Functions
Exports `liz_cred_*` helpers for lookup, mknod, open, read, write, flush, getattr, opendir/readdir, mkdir, rmdir, unlink, setattr, fsync, rename, symlink, readlink, link, chunk info, ACL get/set, and POSIX byte-range lock get/set. Each wrapper creates a `liz_context_t` with `lzfs_fsal_create_context`, calls the corresponding `liz_*` API, destroys the context, and returns the result.

## Control Flow
Every wrapper follows the same pattern: create context from `liz_t` instance and `struct user_cred`, return failure on context allocation failure, invoke the underlying client call, then destroy the context. Read/write/open wrappers return pointer or byte counts; most others return integer status.

## State And Persistence Behavior
Wrappers do not own persistent state beyond transient contexts. Persistent effects are delegated to the LizardFS client instance and remote master/chunkserver operations.

## Dependencies And Integration Points
Depends on `lzfs_internal.h` for context creation and on `mount/client/lizardfs_c_api.h` declarations via the header. Used throughout FSAL export, handle, DS, ACL, and MDS files to preserve NFS request credentials.

## Risks And Edge Cases
`liz_cred_getlk` creates a context but does not destroy it before returning, unlike all other wrappers; that is a likely context leak. Passing `cred == NULL` intentionally creates root-like context in `lzfs_fsal_create_context`, used by pNFS DS paths. Errors are usually `-1`/`NULL` plus `liz_last_err`, so callers must convert immediately.

## Test Signals
No direct unit test. Coverage should come from FSAL request tests validating that operations run under expected UID/GID/group credentials and from leak checks around lock probing.
