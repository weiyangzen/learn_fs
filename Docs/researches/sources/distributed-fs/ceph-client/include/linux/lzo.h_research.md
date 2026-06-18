<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lzo.h -->
# sources/distributed-fs/ceph-client/include/linux/lzo.h

## Purpose
This header declares the kernel LZO1X and LZO-RLE compression/decompression interfaces and error code contract.

## Important APIs, Types, and Functions
It defines work-memory size `LZO1X_1_MEM_COMPRESS`, worst-case bound macro `lzo1x_worst_compress`, compressors `lzo1x_1_compress`, `lzo1x_1_compress_safe`, `lzorle1x_1_compress`, `lzorle1x_1_compress_safe`, decompressor `lzo1x_decompress_safe`, and result codes from `LZO_E_OK` through `LZO_E_INVALID_ARGUMENT`.

## Control Flow
Compression reads a source buffer into a caller-provided destination and work memory, returning output length and status. Safe variants add argument/bounds checking. Decompression validates encoded input and stops on overrun, EOF, or lookbehind errors.

## State and Persistence Behavior
No state is stored in the header. Work memory and output buffers are caller-owned; compressed bytes may be persisted by higher layers.

## Dependencies and Integration Points
It uses size types and integrates with kernel subsystems that support LZO compression, including filesystems, zram, and image formats.

## Risks and Test Signals
Risks include insufficient destination space, ignoring negative error codes, unsafe input trust assumptions, and incorrect worst-case sizing. Test signals are round-trip tests, malformed-stream tests, all error-code paths, and compression-bound boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lzo.h -->
