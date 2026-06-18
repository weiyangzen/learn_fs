# sources/distributed-fs/ceph-client/fs/nfsd/vfs.c

## Purpose

`vfs.c` is NFSD's VFS execution layer. It translates already-decoded NFS requests into Linux VFS operations while enforcing export policy, NFS-specific permission semantics, write verifier rules, weak cache consistency attributes, stable-write/commit behavior, file-cache interaction, local I/O throttling, NFSv4 xattrs, and NFSv4.2 clone/copy/fallocate helpers.

## Important APIs, Types, and Functions

`nfserrno()` maps Linux negative errno values to network-order NFS status values and warns on unmapped errors. Lookup and traversal are handled by `nfsd_lookup_dentry()`, `nfsd_lookup()`, `nfsd_cross_mnt()`, `nfsd_lookup_parent()`, and `nfsd_mountpoint()`. Attribute operations are centered on `nfsd_setattr()`, `nfsd_sanitize_attrs()`, `__nfsd_setattr()`, `nfsd_get_write_access()`, `commit_metadata()`, and `commit_inode_metadata()`.

I/O entry points include `nfsd_read()`, `nfsd_splice_read()`, `nfsd_iter_read()`, `nfsd_direct_read()`, `nfsd_write()`, `nfsd_vfs_write()`, `nfsd_direct_write()`, and `nfsd_commit()`. Object operations include `nfsd_create()`, `nfsd_create_locked()`, `nfsd_create_setattr()`, `nfsd_readlink()`, `nfsd_symlink()`, `nfsd_link()`, `nfsd_rename()`, `nfsd_unlink()`, `nfsd_readdir()`, `nfsd_statfs()`, and `nfsd_filp_close()`. NFSv4-specific helpers include junction detection, xattr operations, `nfsd4_vfs_fallocate()`, `nfsd4_clone_file_range()`, and `nfsd_copy_file_range()`.

## Control Flow

Most operations start with `fh_verify()` to resolve and authorize a filehandle under a requested type and `NFSD_MAY_*` access mask. Lookup refuses symlink following, treats `.` and `..` specially, and conditionally crosses mountpoints only when export, v4root, nohide, or NFSv4 rules allow it. Creation and removal paths acquire write access with `fh_want_write()`, use VFS helpers such as `start_creating()`, `start_removing()`, and `start_renaming()`, fill pre/post WCC attributes, call the VFS mutation, then commit metadata for synchronous exports.

Reads acquire an `nfsd_file` from the filecache, prefer splice unless globally disabled or GSS integrity/privacy is active, and fall back to iterator reads. Direct reads expand the byte range to filesystem alignment requirements and then trim the returned NFS payload to the original request. Writes convert the incoming `xdr_buf` to bio vectors, set `IOCB_SYNC`/`IOCB_DSYNC` for stable writes, optionally split direct I/O into prefix/middle/suffix segments, check writeback errors, update stats, and reset the write verifier on durable-storage failures. `nfsd_commit()` clamps the client range to filesystem limits, fsyncs synchronous exports, checks writeback errors, and returns the current verifier.

## State and Persistence Behavior

This file changes filesystem state through VFS operations: metadata updates, file data writes, xattrs, links, renames, unlinks, directory creation, device/special creation, clone/copy, and fallocate. It also updates NFSD-visible transient state such as WCC pre/post attributes, request page vectors, file-cache references, I/O stats, and the per-network write verifier. Persistent durability is export-policy-sensitive: `EX_ISSYNC` forces metadata or data commit paths; unstable writes rely on later COMMIT and verifier stability.

## Dependencies and Integration Points

The implementation depends on core VFS, namei, exportfs, security hooks, xattrs, POSIX ACLs, writeback/error-sequence APIs, splice/iov_iter/direct I/O, fsnotify, SUNRPC request buffers, NFSD filecache, export policy, and NFSv3/NFSv4 XDR/state headers. It is the integration point between protocol operation handlers and underlying filesystems.

## Risks and Edge Cases

High-risk areas are mount crossing across namespaces, parent lookup at export roots, negative dentries, delegation retry loops on `-EAGAIN`, write verifier reset semantics, direct I/O alignment, partial direct writes, GSS MIC safety with splice, and cached file closing before unlink/rename for filesystems that request it. Permission behavior intentionally diverges from ordinary POSIX in owner-override and device-local-access cases. Xattr list/get paths must lock around probe-and-fetch to avoid size changes.

## Test Signals

Exercise NFSv2/v3/v4 lookup, crossmnt/nohide/v4root traversal, guarded setattr, chmod/chown with setuid/setgid clearing, synchronous and asynchronous writes, commit verifier behavior, direct and buffered I/O, GSS krb5i/krb5p reads, create/mkdir/mknod/symlink/link/rename/remove, readdir cookie sizing, xattr get/list/set/remove, clone/fallocate, and export read-only checks. Tracepoints in `trace.h`, writeback error injection, lockdep, KASAN, fsnotify behavior, and delegation recall tests are good validation signals.
