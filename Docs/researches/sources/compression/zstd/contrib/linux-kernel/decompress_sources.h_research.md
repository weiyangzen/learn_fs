# sources/compression/zstd/contrib/linux-kernel/decompress_sources.h

Purpose: include-list header for kernel boot/decompression contexts that need all zstd decompression sources in one translation unit.

Important behavior: defines `ZSTD_DISABLE_ASM 1` so assembly Huffman code is excluded, then includes common debug/entropy/error/FSE/zstd common sources, decompression Huffman/DDict/decompress/block sources, and `zstd_decompress_module.c`.

State, dependencies, and integration: no runtime state. It depends on the generated kernel source layout under `lib/zstd` and is copied by the linux-kernel Makefile. It is used by kernel decompression code such as `lib/decompress_unzstd.c` where normal multi-object linking may not be available.

Risks and test signals: direct inclusion of `.c` files is sensitive to duplicate symbols, include order, and macro configuration. The linux-kernel test target validates that the generated source set remains buildable.
