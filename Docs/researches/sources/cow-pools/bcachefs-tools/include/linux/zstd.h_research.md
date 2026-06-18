# File Research: sources/cow-pools/bcachefs-tools/include/linux/zstd.h

Defines a kernel-style zstd API over upstream `zstd.h`. It aliases upstream parameter/context/buffer/header types and declares helpers for bounds, errors, levels, parameter selection, one-shot compression/decompression, streaming compression/decompression, and frame inspection.

This file is an API surface only; wrappers are implemented in zstd module source files.
