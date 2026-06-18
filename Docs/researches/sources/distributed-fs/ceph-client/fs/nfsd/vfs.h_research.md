# sources/distributed-fs/ceph-client/fs/nfsd/vfs.h

## Purpose

`vfs.h` declares NFSD's internal VFS-facing service API and access flag vocabulary. It is the contract between protocol operation implementations and `vfs.c`, plus adjacent helpers such as the filecache and NFSv4 handlers.

## Important APIs, Types, and Functions

The `NFSD_MAY_*` constants define NFSD permission intents. The low bits intentionally match Linux `MAY_EXEC`, `MAY_WRITE`, and `MAY_READ`; extra bits express NFS-specific behavior such as setattr, truncate, lockd access, owner override, local device access, GSS bypass, lease-breaking suppression, read-if-exec, 64-bit readdir cookies, and localio tracing. `NFSD_MAY_CREATE` and `NFSD_MAY_REMOVE` compose common directory mutation masks.

`nfsd_filldir_t` is the callback shape for readdir encoding. `struct nfsd_attrs` bundles an input `iattr`, optional security label, access/default POSIX ACLs, and per-extension output errors. `nfsd_attrs_free()` releases ACL references and `nfsd_attrs_valid()` answers whether any attribute-like update is present.

The prototypes cover errno translation, lookup/mount traversal, setattr, create, access, commit, open, read/write, symlink/link/rename/unlink, readdir, statfs, permission checks, synchronous file close, NFSv4 xattr operations, and NFSv4.2 clone/fallocate helpers.

## Control Flow

Protocol handlers include this header to call a typed VFS operation after XDR decode and filehandle preparation. Typical flow is: decode request into an operation-specific struct, call a `vfs.h` function with `struct svc_rqst` and `struct svc_fh`, encode returned status and result fields, then release filehandles and attributes. The access flags guide `fh_verify()`, `nfsd_permission()`, `nfsd_open()`, and filecache acquisition.

## State and Persistence Behavior

The header itself stores no state. It exposes operations that mutate backing filesystems and NFSD runtime state in `vfs.c`. `struct nfsd_attrs` is an important lifetime carrier: ACL references and optional labels are decoded before VFS execution, consumed by `nfsd_setattr()` or create paths, and then released by callers.

## Dependencies and Integration Points

It depends on Linux `fs.h`, POSIX ACLs, NFSD filehandle definitions, and `nfsd.h`. Under `CONFIG_NFSD_V4`, it exposes xattr, clone, and fallocate helpers used by NFSv4 operation code. The permission constants are also mirrored by trace formatting in `trace.h`.

## Risks and Edge Cases

Because the low access bits must match VFS `MAY_*`, changing flag values would break permission checks. Callers must respect ownership rules documented in comments: many functions require `fh_put()` afterward and some creation paths transfer dentry references to release callbacks. Attribute callers must release ACLs and inspect per-field errors for labels/ACLs.

## Test Signals

Build coverage should catch mismatched prototypes and `CONFIG_NFSD_V4` guards. Runtime tests should validate that each protocol version calls the correct VFS entry point with the intended `NFSD_MAY_*` flags, especially write/truncate/create/remove, xattr, direct I/O, clone/fallocate, and readdir cookie behavior.
