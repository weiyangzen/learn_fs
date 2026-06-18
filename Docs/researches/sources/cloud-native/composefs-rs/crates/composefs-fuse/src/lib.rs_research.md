# sources/cloud-native/composefs-rs/crates/composefs-fuse/src/lib.rs

Purpose: implements a read-only FUSE filesystem view over a `composefs::tree::FileSystem`, serving external file data from a `Repository`.

Important APIs/types/functions: public entry points are `open_fuse`, `FuseMountOptions::set_allow_other`, `mount_fuse`, and `serve_tree_fuse`. Internal structures are `InodeMap`, `InodeRef`, `OpenHandle`, and `TreeFuse`. `InodeMap` assigns stable FUSE inode numbers eagerly from directories and leaf IDs so hardlinked leaves share inode numbers. `InodeRef` converts composefs metadata into `fuser::FileAttr`.

Control flow: callers open `/dev/fuse`, create a detached FUSE mount with `mount_fuse`, and then run a blocking `fuser::Session` through `serve_tree_fuse`. On lookup/readdir, `TreeFuse` registers inodes and caches attributes. `open` accepts only regular files; external files become object fds via `repo.open_object`, and inline files become in-memory byte slices. `read` serves either `pread` from the object fd or slices inline data. Symlinks, xattrs, directory listing, getattr, release, and statfs are implemented; mutation operations are absent.

State and persistence: runtime state is per-session maps for inode references, cached attrs, open handles, and a file-handle counter. The crate does not write repository content. `mount_fuse` creates a read-only FUSE mount object with `default_permissions`, optional `allow_other`, fixed root mode/user/group, and the supplied device fd.

Dependencies and integration points: bridges `fuser` callbacks to `composefs` tree types and `rustix` fd/mount syscalls. It relies on `composefs::repository::Repository` object lookup and `FileSystem::nlinks` for hardlink counts. Higher-level mount commands can use this when kernel composefs mounting is unavailable or when serving from userspace is desired.

Risks: `read` casts negative offsets to `u64`/`usize`, relying on FUSE not to issue invalid negative offsets; defensive checks would be safer. Directory inode identity uses raw directory pointers, valid only because the tree is immutably borrowed for the session lifetime. Attribute TTL is very long, which is fine for immutable trees but wrong if a future mutable mode is added. `blocks` is hard-coded to 1 and `statfs` returns zeros, so disk-usage semantics are approximate. Serving is blocking and single-session; callers must handle threading/lifetime.

Test signals: privileged CLI mount tests validate visible filesystem content, overlay upper/work behavior, bootable OCI mount differences, and plain mount sanity. Direct FUSE-specific xattr, hardlink inode, statfs, and error-path coverage is not shown in this subset.
