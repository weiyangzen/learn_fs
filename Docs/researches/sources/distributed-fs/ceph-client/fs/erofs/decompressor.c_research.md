<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor.c -->
# sources/distributed-fs/ceph-client/fs/erofs/decompressor.c

## Purpose
`decompressor.c` provides the common EROFS compressed-data decompressor registry, LZ4 implementation, plain shifted/interlaced transforms, compressed-size fixup, stream buffer switching support, compression config parsing, and decompressor subsystem init/exit.

## Important APIs, types, and functions
Important functions include `z_erofs_load_lz4_config`, `z_erofs_lz4_decompress`, `z_erofs_fixup_insize`, `z_erofs_transform_plain`, `z_erofs_stream_switch_bufs`, `z_erofs_parse_cfgs`, `z_erofs_init_decompressor`, and `z_erofs_exit_decompressor`. It defines the `z_erofs_decomp[]` algorithm table.

## Control flow
Mount-time config parsing either loads legacy LZ4 settings from the superblock or walks compression configuration records after the superblock, enabling only algorithms compiled into the kernel. LZ4 decompression prepares destination pages, decides whether contiguous direct mapping is possible, handles in-place overlap by direct reuse, vmapped input, or per-CPU bounce buffers, fixes leading zero padding to obtain exact compressed size, and invokes safe or partial LZ4 decode. Plain transform copies or moves shifted/interlaced data without decompression. Stream switching supplies input/output page transitions and overlap bounce logic for LZMA/DEFLATE/ZSTD.

## State and persistence
Runtime state includes superblock LZ4 limits, global decompressor registrations, temporary pagepool pages, and per-CPU/global buffers. Persistent state is only read from on-disk compression config records.

## Dependencies and integration points
It depends on LZ4, vm_map_ram, pagepool helpers, EROFS compressed map metadata, optional algorithm modules, and zdata/zmap callers that create requests.

## Risks and test signals
Risks include overlap corruption during in-place decompression, invalid zero-padding fixups, unsupported algorithm bits, huge pcluster limits, partial decode edge cases, and buffer lifecycle leaks. Test signals include LZ4 legacy and config-table images, shifted/interlaced pclusters, in-place and non-in-place I/O, sparse output gaps, partial reads, unsupported algorithms, and low-memory pagepool paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor.c -->
