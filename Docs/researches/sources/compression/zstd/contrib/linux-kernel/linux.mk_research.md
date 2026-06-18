# sources/compression/zstd/contrib/linux-kernel/linux.mk

Purpose: Linux kernel Kbuild makefile for generated zstd library objects.

Important behavior: declares `obj-$(CONFIG_ZSTD_COMPRESS)`, `obj-$(CONFIG_ZSTD_DECOMPRESS)`, and `obj-$(CONFIG_ZSTD_COMMON)`. It lists compression module/core objects, decompression module/core objects, and common debug/entropy/error/FSE/common objects in `zstd_compress-y`, `zstd_decompress-y`, and `zstd_common-y` respectively.

State, dependencies, and integration: no standalone state; Kbuild consumes it after `contrib/linux-kernel/Makefile` copies it to `linux/lib/zstd/Makefile` or an actual Linux tree. It integrates generated source files with kernel config symbols.

Risks and test signals: object lists must stay synchronized with upstream zstd source dependencies and generated module wrappers. Kernel import/build tests catch missing or obsolete objects.
