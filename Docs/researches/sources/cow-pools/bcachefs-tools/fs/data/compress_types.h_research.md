# File Research: sources/cow-pools/bcachefs-tools/fs/data/compress_types.h

Defines per-filesystem compression state.

Key responsibilities:
- `struct bch_fs_compress` stores read/write bounce mempools, per-compression-option workspace mempools, and cached zstd workspace size.

Important interactions:
- Allocated and released by `bch2_fs_compress_init()` / `bch2_fs_compress_exit()` in `compress.c`.
- Used by compression and decompression paths to avoid blocking allocations in data I/O paths.
