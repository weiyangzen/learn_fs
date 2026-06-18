# File Research: sources/block-storage/bcache-tools/bcache.h

This central header defines bcache magic, superblock versions, superblock constants, on-disk `cache_sb_disk`, in-memory `cache_sb`, bitfield accessors, cache/backing mode constants, CRC declaration, checksum macro, and feature flags.

It models the disk format as little-endian fields and keeps a separate native-endian in-memory struct because member order and sizes differ. It supports cache-device versions `0`, `3`, `5` and backing versions `1`, `4`, `6`, including feature-set-aware large bucket support. `SB_IS_BDEV` is the common discriminator used throughout the tools.
