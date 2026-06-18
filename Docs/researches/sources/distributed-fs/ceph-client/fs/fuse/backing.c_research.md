# sources/distributed-fs/ceph-client/fs/fuse/backing.c

## Purpose
`backing.c` manages FUSE passthrough backing files registered by privileged userspace. It stores kernel `struct file` references in a per-connection IDR and returns integer backing IDs for direct-operation mapping.

## Important APIs, Types, and Functions
- `fuse_backing_files_init()` and `fuse_backing_files_free()` initialize and destroy `fc->backing_files_map`.
- `fuse_backing_open()` validates and registers a backing fd.
- `fuse_backing_close()` removes a backing id.
- `fuse_backing_lookup()` finds and refcounts a backing file under RCU.
- `fuse_backing_get()`/`fuse_backing_put()` manage `struct fuse_backing` lifetime.

## Control Flow
Open requires `fc->passthrough` and `CAP_SYS_ADMIN`, rejects flags/padding, obtains the raw fd, requires a regular non-directory file, checks stack depth against `fc->max_stack_depth`, allocates a `fuse_backing`, stores the file and prepared credentials, and allocates an IDR id starting at 1. Close performs the same feature/capability checks, removes the id under `fc->lock`, and drops the backing reference. Lookup uses RCU plus `refcount_inc_not_zero()` to return a stable object.

## State and Persistence
State is per-connection in an IDR. Each `fuse_backing` holds a file ref, credentials, refcount, and RCU lifetime. There is no disk state; persistence is the lifetime of the FUSE connection or until explicit close.

## Dependencies and Integration Points
This file is enabled by `CONFIG_FUSE_PASSTHROUGH`, called from `FUSE_DEV_IOC_BACKING_OPEN/CLOSE` in `dev.c`, and consumed by passthrough read/write/splice/mmap paths in other FUSE code. It integrates with `FS_STACK` stack-depth protection.

## Risks
The TODO notes CAP_SYS_ADMIN may be overly strict until backing files are visible to tools such as `lsof`. The stack-depth check prevents recursive stacking loops but relies on correct `max_stack_depth`. Prepared credentials must be released, and IDR removal must not race with lookup users, hence RCU freeing.

## Test Signals
Test ioctl registration/close, permission failures, non-regular fds, directory fds, stack-depth rejection, lookup while closing, connection teardown with live backings, and disabled `CONFIG_FUSE_PASSTHROUGH`.
