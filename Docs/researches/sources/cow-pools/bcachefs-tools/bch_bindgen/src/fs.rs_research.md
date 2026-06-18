# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/fs.rs

- High-level Rust wrapper around raw `bch_fs`.
- Provides RAII device references, superblock lock guard, borrowed raw view, open/start/exit, superblock access/mutation, and device iteration.
- Wraps online member traversal, btree root lookup, device get/existence/raw access, allocator mode setting, journal flushing, delete range, accounting reads, usage reads, time conversion, inode lookup, loglevel, and device add.
- Exposes read/write operations through `ReadOp` and `WriteOp`.
- Implements `Drop` by calling `bch2_fs_exit`.
- Includes standalone pure Rust helpers for bucket sizing, hashed writepoint, device targets, and allocator btree-id classification.
