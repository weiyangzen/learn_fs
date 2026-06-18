# sources/distributed-fs/glusterfs/xlators/features/compress/src/cdc-helper.c

## Purpose
Implements zlib compression/decompression helpers for the CDC translator, including iobuf allocation, gzip-compatible trailer handling, CRC validation, and debug dumping.

## Important APIs, types, and functions
Public functions are `cdc_compress()` and `cdc_decompress()`. Helpers include `cdc_next_iovec`, little-endian trailer put/get, `cdc_init_gzip_trailer`, `cdc_alloc_iobuf_and_init_vec`, `cdc_flush_libz_buffer`, `do_cdc_compress`, `cdc_check_content_for_deflate`, `do_cdc_decompress`, and validation routines.

## Control flow
Compression creates an iobref, ensures xdata exists, initializes deflate with configured window/mem/level, compresses each input iovec into output iobufs, flushes with `Z_FINISH`, appends an 8-byte trailer containing CRC and original size, sets the `deflate` canary in xdata, and optionally dumps a gzip-debug file. Decompression first checks the canary, requires a single input iovec, extracts trailer CRC/length, inflates into output iobufs, recomputes CRC across output vectors, validates length, and returns inflated byte count.

## State and persistence behavior
State is per-call in `cdc_info_t` and zlib stream structs. Persistent data on the wire is compressed payload plus 8-byte validation trailer and xdata canary; debug mode writes `/tmp/cdcdump.gz`.

## Dependencies and integration points
Depends on zlib, GlusterFS iobuf/iobref pools, logging, sys_write, and dictionary xdata from `cdc.c`.

## Risks and test signals
Risks include only partially supporting multi-iovec decompression, output `MAX_IOVEC` overflow, memory cleanup on mid-stream failures, trailer assumptions, and passthrough behavior when canary is missing. Tests should cover small/large buffers, corrupt CRC/length, multiple iovecs, min-size bypass, debug dump, and zlib init/flush failures.
