# File Research: sources/cow-pools/bcachefs-tools/c_src/fuse_shims.c

- C shim layer for Rust FUSE support, compiled only when `BCACHEFS_FUSE` is defined.
- Initializes fuser worker threads for libbcachefs expectations around `current`, RCU, and percpu state.
- Wraps inline time/block/link-count functions.
- Implements FUSE-facing lookup, create, unlink, rename, link, setattr, post-write inode timestamp update, readdir callback bridging, statfs usage, and inode counting.
- Uses native bcachefs transaction macros and VFS-style helpers that bindgen cannot express directly.
