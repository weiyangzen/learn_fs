# sources/distributed-fs/ceph-client/drivers/block/zram/backend_lz4.c

Purpose: zram backend adapter for LZ4 fast compression, with optional dictionary support.

Important APIs/types/functions: `struct lz4_ctx` holds either raw workspace memory or dictionary-capable compression/decode streams. `lz4_setup_params()` defaults acceleration and loads an optional dictionary into `params->drv_data`. `lz4_compress()` calls `LZ4_compress_fast()` or `LZ4_compress_fast_continue()`. `lz4_decompress()` calls safe LZ4 decode APIs.

Control flow and state: dictionary-less contexts allocate `LZ4_MEM_COMPRESS`; dictionary contexts allocate per-CPU stream structs and copy/reset dictionary state for each request. Params release frees the shared dictionary stream.

Dependencies and integration: depends on kernel LZ4 compression/decompression APIs and zcomp ops.

Risks: dictionary size must be fully accepted by `LZ4_loadDict()` or setup fails. Compression failure is normalized to `-EINVAL`. Dictionary stream reset correctness is central to reproducible compressed output.

Test signals: no-dictionary round trips, dictionary setup and repeated requests, invalid dictionary acceptance, acceleration levels, and decompression of malformed data.
