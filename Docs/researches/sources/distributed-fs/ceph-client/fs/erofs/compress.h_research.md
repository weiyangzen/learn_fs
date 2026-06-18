<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/compress.h -->
# sources/distributed-fs/ceph-client/fs/erofs/compress.h

## Purpose
`compress.h` defines the internal decompression request and decompressor operation interface used by EROFS compressed data paths.

## Important APIs, types, and functions
Key types are `struct z_erofs_decompress_req` and `struct z_erofs_decompressor`. A request carries input/output page arrays, page offsets, input/output sizes, algorithm id, in-place/partial/fill-gap flags, superblock, and GFP flags. A decompressor supplies optional `config`, `decompress`, `init`, `exit`, and a name.

## Control flow
The header has no runtime flow. Compressed read paths construct requests, select a decompressor from the algorithm table in `decompressor.c`, and call the common function pointers declared by this interface.

## State and persistence
No state lives in the header. It describes transient decompression work and algorithm-global lifecycle hooks.

## Dependencies and integration points
It includes `internal.h` for EROFS types and is used by LZ4, LZMA, DEFLATE, ZSTD, and crypto decompressor implementations.

## Risks and test signals
Risks include request fields not being initialized consistently, algorithm implementations disagreeing about NULL output pages or partial decoding, and lifecycle hooks not matching Makefile/Kconfig combinations. Test signals include compressed reads for every algorithm, in-place I/O, partial decode, sparse output gaps, and low-memory allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/compress.h -->
