# Chunk Research: sources/os/darwin/xnu/bsd/vfs/vfs_syscalls.c lines 10624-15325

## Scope

This chunk covers the later VFS syscall helpers in Darwin XNU's `bsd/vfs/vfs_syscalls.c`, within the `sources/os/darwin/xnu` source tree included by `Docs/research_subset_a.md`. It starts inside the `rmdirat_internal()` retry/error path and then covers directory enumeration, `umask`, device revoke, HFS-style directory attribute/search syscalls, dataless namespace resolver machinery, filesystem control ioctls, extended attribute syscalls, path lookup by object id, stat/statfs structure munging, VFS purge, and filesystem snapshot operations.

## APIs and Entry Points

- `rmdir()` delegates to `rmdirat_internal()` with `AT_FDCWD`, user path input, and default flags. The visible `rmdirat_internal()` tail handles batched `ENOENT` retries, dataless directory remove fallback, AppleDouble cleanup, FSE/fileop/MAC notifications, and vnode/nameidata cleanup.
- `vnode_readdir64()` wraps `VNOP_READDIR()`, using native extended readdir when available or converting legacy `struct dirent` records to `struct direntry`.
- `getdirentries_common()`, `getdirentries()`, and `getdirentries64()` implement fd-based directory enumeration, offset locking, union traversal, EOF reporting, and 32/64-bit copyout.
- `revoke()`, `getdirentriesattr()`, `exchangedata()`, `searchfs()`, `fsctl()`/`ffsctl()`, xattr syscalls, `fsgetpath*()`, stat/statfs mungers, `vfs_purge()`, and `fs_snapshot()` are the major syscall surfaces in this chunk.
- Dataless file support under `CONFIG_DATALESS_FILES` defines resolver request tables, `vfs.nspace` sysctls, materialization policy, and `vfs_materialize_file()`, `vfs_materialize_dir()`, `vfs_materialize_reparent()`.

## Control Flow

Directory enumeration resolves fd to vnode, locks `fg_offset`, validates readable state and vnode consistency, creates user uios, invokes `VNOP_READDIR()` or `VNOP_READDIRATTR()`, updates offsets, and handles union mount lower-layer traversal.

The dataless resolver path inserts stack-allocated request records into a mutex-protected hash table, sends filecoordinationd Mach upcalls, waits interruptibly, and completes via `vfs.nspace.complete`. Completion can validate recursive generation count and APFS sync-root under mount rename locking before waking the caller.

`fsctl_internal()` normalizes compatibility commands, copies ioctl arguments through stack or heap storage, handles generic VFS commands, rejects selectors that should not pass through this path, delegates unknown commands to `VNOP_IOCTL()`, and copies output back to userspace.

Snapshot operations are dispatched by `fs_snapshot()` after entitlement checks and, for mutation/root/revert operations, device write authorization. Helpers validate snapshot names, obtain the unnamed snapshot directory, call create/remove/rename VNOPs, mount snapshots through `mount_common()`, and use VFS ioctls for revert/root.

## State and Data Flow

- Directory state flows through `fileproc`, `fg_offset`, `fp_set_data()`, vnode iocounts, and `uio` buffers.
- Dataless state includes resolver request hash buckets, outstanding request count, resolver process identity, per-process materialization policy, and per-thread override flags.
- Xattr state is vnode plus attribute name, with payload/list transfer via `uio`; protected filesec xattrs require private entitlement.
- Snapshot state flows through mount capabilities, snapshot directory vnodes, component names, snapshot VNOPs/VFS ioctls, and mount/device authorization.

## Dependencies

This chunk depends on XNU VFS primitives (`namei`, `NDINIT`, vnode/mount reference APIs, `build_path`, `mount_common`), VNOP/VFS operation vectors, MAC hooks, kauth/fileop authorization, FSE events, UIO/copy helpers, fd helpers, sysctl plumbing, Mach filecoordinationd resolver IPC, and config-gated features including union mounts, file leases, AppleDouble cleanup, searchfs, dataless files, routefs, exclaves, and root snapshots.

## Risks and Edge Cases

- The chunk begins mid-`rmdirat_internal()`; prior chunk context is needed for full remove/rmdir invariants.
- Legacy readdir conversion must defensively validate filesystem-provided record lengths; malformed records return `EIO`.
- Dataless resolver requests are stack allocated while visible to async completion; `RRF_COMPLETING` and removal ordering are critical.
- `handle_sync_volume()` intentionally drops the vnode iocount and clears `*arg_vp`; callers must honor that contract.
- `fsctl_internal()` mixes compatibility rewriting, generic handling, and VNOP passthrough, so new selectors can be routed incorrectly if not coordinated with fcntl paths.
- Snapshot revert/root build component names directly and rely on filesystem ioctl semantics for deeper validation.

## Cross-Chunk References

- Earlier lines define the start of `rmdirat_internal()`, remove helpers, FSE/path helpers, `vn_remove()`, `vn_rmdir()`, `chflags0()`, and support routines reused here.
- Earlier chunks likely contain `xattr_protected()`, package extension helpers, `test_fse_access_granted()`, and related fsctl/xattr support.
- Later code after line 15325 should be checked for syscall wrappers consuming `munge_statfs()` and stat munging helpers.
- The final per-file report should merge this chunk with the prior chunk because this report starts inside an active function.