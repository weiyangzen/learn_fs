# sources/distributed-fs/ceph-client/lib/lz4/Makefile

Purpose: kernel build fragment for LZ4 compression/decompression objects.

Important APIs/types/functions: Kbuild variables `ccflags-y`, `obj-$(CONFIG_LZ4_COMPRESS)`, `obj-$(CONFIG_LZ4HC_COMPRESS)`, and `obj-$(CONFIG_LZ4_DECOMPRESS)`.

Control flow: Kbuild adds `-O3` for this directory and includes `lz4_compress.o`, `lz4hc_compress.o`, and/or `lz4_decompress.o` according to configuration symbols.

State/persistence: no runtime state; build configuration only.

Dependencies/integration: integrated by the kernel build system and Kconfig symbols controlling LZ4 support.

Risks: forcing `-O3` can expose compiler-specific behavior or increase build time/code size, but is likely chosen for compression performance. Missing config dependencies would omit required objects.

Test signals: build matrix with compress, high-compress, and decompress configs verifies object selection; runtime compression tests validate linked implementations.
