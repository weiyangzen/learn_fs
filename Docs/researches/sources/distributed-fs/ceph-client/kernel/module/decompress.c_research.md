# sources/distributed-fs/ceph-client/kernel/module/decompress.c

## Purpose
Implements in-kernel decompression for compressed module files loaded through `finit_module` with `MODULE_INIT_COMPRESSED_FILE`. It supports exactly the compression algorithm selected at build time: gzip, xz, or zstd.

## Important APIs, Types, And Functions
External functions are `module_decompress` and `module_decompress_cleanup`. Allocation helpers are `module_extend_max_pages` and `module_get_next_page`. Algorithm-specific helpers are `module_gzip_decompress`, `module_xz_decompress`, and `module_zstd_decompress`. When sysfs is enabled, `compression_show` exposes the active format.

## Control Flow
`module_decompress` records compressed length for stats, preallocates a page pointer array, runs the selected decompressor into highmem pages, then `vmap`s the pages into `info->hdr` and sets `info->len` to decompressed size. Cleanup unmaps, frees pages, and frees the page array. `init_module_from_file` frees the original compressed buffer immediately after decompression.

## State And Persistence
Temporary state is stored in `load_info.pages`, `max_pages`, `used_pages`, `hdr`, and `len`. A read-only `/sys/module/compression` style attribute under the module kset is registered late when sysfs support exists.

## Dependencies And Integration Points
Depends on zlib, xz, or zstd libraries, highmem mapping, vmap/vunmap, sysfs, and module stats. It feeds the ordinary ELF validation path by producing the same `load_info.hdr` buffer shape as uncompressed reads.

## Risks And Edge Cases
Input magic and frame validation are critical. Gzip optional filename parsing, xz stream termination, zstd window limits, page array growth, and partial output pages are failure-prone. Cleanup must handle partially filled `load_info` after decompressor or allocation failure.

## Test Signals
Load valid and corrupt `.ko.gz`, `.ko.xz`, and `.ko.zst` files under matching configs. Verify decompression failures increment stats, cleanup leaves no leaks, sysfs reports the expected format, and signature verification still applies to the decompressed module content path.
