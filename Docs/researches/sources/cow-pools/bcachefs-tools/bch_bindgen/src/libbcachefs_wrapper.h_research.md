# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/libbcachefs_wrapper.h

- Bindgen umbrella header for libbcachefs-facing Rust bindings.
- Includes format, error, option, btree, data, debug, init, fs, alloc, journal, superblock, tools, crypto, RAID, rust shim, Linux bio/blkdev, and FUSE shim headers.
- Defines `MARK_FIX_753` workaround constants so bindgen sees macro constants such as `BLK_OPEN_READ`, `BLK_OPEN_WRITE`, `BLK_OPEN_EXCL`, and `BLK_OPEN_CREAT`.
