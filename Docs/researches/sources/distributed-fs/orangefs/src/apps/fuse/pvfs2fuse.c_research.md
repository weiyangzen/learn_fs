# sources/distributed-fs/orangefs/src/apps/fuse/pvfs2fuse.c

## Purpose
`pvfs2fuse.c` implements a FUSE 2.7 userspace mount frontend for OrangeFS/PVFS. It translates common VFS/FUSE operations into `PVFS_sys_*` calls, either using the default OrangeFS mount table configuration or a user-provided `-o fs_spec=...` URI. It is an alternate client path to the kernel module, useful where FUSE deployment is preferred.

## Important APIs, Types, and Functions
`pvfs_fuse_handle_t` stores a `PVFS_object_ref` and per-open `PVFS_credential`. Global `struct pvfs2fuse pvfs2fuse` stores `fs_spec`, `mntpoint`, `fs_id`, and a `PVFS_sys_mntent`. `SET_FUSE_HANDLE`/`GET_FUSE_HANDLE` hide pointer storage differences between 32-bit and 64-bit FUSE file handles.

Credential generation is centralized in `pvfs_fuse_gen_credential()`, which uses `fuse_get_context()` UID/GID values and `PVFS_util_gen_credential()`. `lookup()` resolves FUSE paths through `PVFS_sys_lookup()` and populates a handle. Attribute translation is in `pvfs_fuse_getattr_pfhp()`, mapping `PVFS_sys_attr` into `struct stat` including object type, permissions, size, timestamps, fsid, and handle-as-inode.

The `pvfs_fuse_oper` table registers handlers for getattr/fgetattr, readlink, mkdir, unlink/rmdir, symlink, rename, chmod/chown, truncate, utime, open, read, write, statfs, release, fsync, readdir, access, and create. `main()` parses FUSE options, initializes OrangeFS system state, creates a mount entry for explicit `fs_spec`, injects FUSE options (`direct_io`, zero attr timeout, `max_write`, optional `allow_other`, `-s` single-threading), and calls `fuse_main()`.

## Control Flow
Most operation handlers follow the same pattern: derive parent/name or lookup path, generate/use credentials, call a `PVFS_sys_*` operation, clean credentials, and convert OrangeFS errors to negative errno via `PVFS_ERROR_TO_ERRNO_N()`. File reads/writes create contiguous memory requests and invoke `PVFS_sys_read()`/`PVFS_sys_write()` with `PVFS_BYTE` file requests. Directory reads page through `PVFS_sys_readdir()` until `PVFS_READDIR_END`.

Startup has two branches. Without `fs_spec`, it uses `PVFS_util_init_defaults()`, obtains the default fsid, copies the mount entry, and disables name/attribute cache timeouts. With `fs_spec`, it manually initializes the sysint layer, parses comma-separated config-server URIs, constructs a `PVFS_sys_mntent`, and registers it with `PVFS_sys_fs_add()`.

## State and Persistence
Persistent filesystem state is managed remotely by OrangeFS servers through sysint calls. Local process state includes the global mount descriptor, per-open `pvfs_fuse_handle_t` objects stored in FUSE `fi->fh`, generated credentials, and FUSE argument mutations. No local file cache is maintained; `direct_io`, zero attr timeout, and single-threaded mode intentionally reduce caching and concurrency assumptions.

## Dependencies and Integration Points
The file depends on libfuse, OrangeFS compatibility/util/security headers, `PVFS_sys_*`, `PVFS_util_*`, `PINT_*` path helpers, request APIs, and management constants such as `PVFS2_BUFMAP_DEFAULT_DESC_SIZE`. It integrates with the FUSE mount lifecycle and with OrangeFS mount table parsing or explicit URI parsing.

## Risks and Edge Cases
Several error paths leak credentials or allocations. `pvfs_fuse_read()` and `pvfs_fuse_write()` do not free `mem_req` when the sysint I/O call fails. `pvfs_fuse_create()` transfers `dir_pfh.cred` into the returned file handle but does not clearly clean `dir_pfh` on all failure paths after `PVFS_sys_create()`. `pvfs_fuse_rename()` calls `lookup(todir, ...)` without assigning its return to `rc`, so failure may be missed and `todir_pfh` may be used uninitialized. `pvfs_fuse_readlink()` sets `buf[len] = '\0'` after possibly truncating `size`, which can write beyond the supplied buffer when `len >= size`. `pvfs_fuse_access()` returns success for any one requested permission bit rather than requiring all bits in `mask`, and it does not release fetched sys attrs. URI parsing mutates `fs_spec` with `strsep()`/slash replacement. Many handlers ignore `path` when `fi` already has a handle, which is normal for FUSE but should be tested around renames/unlinks.

## Test Signals
Smoke tests should mount with default config and explicit `fs_spec`, then exercise create/read/write/truncate/chmod/chown/utime/readdir/statfs/symlink/readlink/rename/unlink/rmdir. Run under ASan or Valgrind for request and credential leaks on both success and injected sysint failures. Permission tests should check combined masks such as `R_OK|W_OK`. Buffer tests should target short `readlink()` buffers. URI tests should cover multiple config servers, mismatched fs names, invalid slash counts, and root/non-root `allow_other` behavior.
