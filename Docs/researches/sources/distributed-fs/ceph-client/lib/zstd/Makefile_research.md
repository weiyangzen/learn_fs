# sources/distributed-fs/ceph-client/lib/zstd/Makefile

Purpose: Kbuild recipe for the in-kernel Zstandard compressor, decompressor, and common support objects.

Important entries:
- `obj-$(CONFIG_ZSTD_COMPRESS) += zstd_compress.o`.
- `obj-$(CONFIG_ZSTD_DECOMPRESS) += zstd_decompress.o`.
- `obj-$(CONFIG_ZSTD_COMMON) += zstd_common.o`.
- `zstd_compress-y` lists FSE/HUF and compressor strategy modules.
- `zstd_decompress-y` lists HUF and frame/block decompressor modules.
- `zstd_common-y` includes common debug, entropy, error, FSE decompression, and common API code.

Control flow: Build-time composition. The common object is shared by compressor/decompressor code and selected independently.

State and persistence: No runtime state. Kconfig controls which API surface is linked.

Dependencies and integration:
- Kernel consumers include crypto zstd, AppArmor rawdata compression, firmware decompression, initramfs/kernel image tools, and other zstd users through `<linux/zstd.h>`.

Risks:
- Missing common objects cause unresolved symbols for both compression and decompression.
- Updating upstream zstd files requires keeping the Makefile object split aligned with kernel module wrappers.

Test signals:
- Build all combinations of `CONFIG_ZSTD_COMMON`, `CONFIG_ZSTD_COMPRESS`, and `CONFIG_ZSTD_DECOMPRESS`.
- Link checks for exported zstd APIs.
