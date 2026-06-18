# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/compress_types.h

Defines the filesystem compression runtime state.

Key contents:
- `struct bch_fs_compress` contains read/write bounce mempools.
- Per-compression-option workspace mempools are indexed by `BCH_COMPRESSION_OPT_NR`.
- Stores computed zstd compression workspace size.

Dependencies and interactions:
- Embedded in `struct bch_fs`.
- Initialized and torn down by `compress.c`.
