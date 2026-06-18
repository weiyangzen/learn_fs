# sources/distributed-fs/ceph-client/lib/zstd/decompress_sources.h

## Purpose
`decompress_sources.h` is an aggregation header that includes every C source needed for Zstd decompression in a single translation unit. It is intended for kernel decompression users that need source inclusion rather than normal module linkage.

## Important APIs, types, and functions
The file defines `ZSTD_DISABLE_ASM` before including dependencies, then includes common debug, entropy, error, FSE, Zstd common, Huffman decompression, DDict, frame decompression, block decompression, and the Linux decompressor module wrapper.

## Control flow
There is no direct runtime control flow. At compile time, inclusion order assembles a complete decompressor implementation. The ASM Huffman path is disabled so that all required code comes from included C sources.

## State and persistence
The header creates no state itself, but the included files define the decompressor context, static tables, exported wrappers, and any module metadata present in the included sources.

## Dependencies and integration points
It integrates with `lib/decompress_unzstd.c` and similar early/standalone decompression paths. Because it includes `.c` files directly, it is sensitive to include ordering, macro environment, and duplicate symbol exposure.

## Risks and test signals
Risks include duplicate definitions if included alongside normal objects, incorrect macro leakage, missing source inclusion after upstream Zstd updates, and disabled ASM changing performance characteristics. Test signals are kernel decompression builds, initramfs or compressed-kernel boot tests, link checks for duplicate symbols, and decompression tests under configurations without module-loaded Zstd objects.
