# sources/distributed-fs/ceph-client/lib/lzo/Makefile

## Purpose
`lib/lzo/Makefile` wires the kernel LZO library objects into Kbuild. It groups the shared compressor implementations into a composite compression object and the safe decompressor into a composite decompression object, then includes them conditionally based on kernel configuration.

## Important APIs, types, and functions
The file defines `lzo_compress-objs := lzo1x_compress.o lzo1x_compress_safe.o` and `lzo_decompress-objs := lzo1x_decompress_safe.o`. It adds `lzo_compress.o` under `CONFIG_LZO_COMPRESS` and `lzo_decompress.o` under `CONFIG_LZO_DECOMPRESS`.

## Control flow
There is no runtime control flow. At build time, Kbuild uses the composite-object variables to link the unsafe and safe compressor translation units into `lzo_compress.o`, and the decompressor translation unit into `lzo_decompress.o`. The parent `lib/Makefile` descends into this directory when the corresponding config symbols are enabled.

## State and persistence
The file does not manage runtime state. Its persistent effect is the build graph: enabling or disabling the config symbols changes which exported LZO symbols exist in the kernel image or module build.

## Dependencies and integration points
This Makefile integrates with the public prototypes in `include/linux/lzo.h`, the compression users in `crypto/lzo.c`, `crypto/lzo-rle.c`, Btrfs, SquashFS, and boot decompression code. It relies on Kbuild naming conventions where `foo-objs` lists the object files linked into `foo.o`.

## Risks and test signals
Risks are mostly build-configuration risks: omitting `lzo1x_compress_safe.o` would break callers of `_safe` compressor symbols, and omitting the decompressor object would break all LZO decode users. Test signals are `CONFIG_LZO_COMPRESS=y/m` producing both `lzo1x_1_compress*` and `lzorle1x_1_compress*` symbols, `CONFIG_LZO_DECOMPRESS=y/m` producing `lzo1x_decompress_safe`, and allmodconfig or crypto compression self-tests linking without unresolved symbols.
