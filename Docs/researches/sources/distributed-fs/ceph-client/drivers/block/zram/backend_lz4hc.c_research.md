# sources/distributed-fs/ceph-client/drivers/block/zram/backend_lz4hc.c

Purpose: zram backend adapter for high-compression LZ4HC, including dictionary-capable operation.

Important APIs/types/functions: `struct lz4hc_ctx` stores either `LZ4HC_MEM_COMPRESS` workspace or HC/decode streams. `lz4hc_setup_params()` defaults compression level. `lz4hc_compress()` uses `LZ4_compress_HC()` or resets/loads a dictionary into `LZ4_streamHC_t` before `LZ4_compress_HC_continue()`. `lz4hc_decompress()` mirrors LZ4 safe decompression.

Control flow and state: setup has no shared driver data; per-CPU context owns all mutable stream/workspace state. Dictionary mode reloads the provided dictionary each request.

Dependencies and integration: depends on kernel LZ4HC/LZ4 APIs and zcomp.

Risks: higher compression may increase CPU latency in zram write paths. Dictionary load mismatch returns `-EINVAL`. Allocation failures currently return `-EINVAL` in create error handling rather than `-ENOMEM`.

Test signals: default and explicit compression levels, dictionary and no-dictionary round trips, compression failure with too-small destination, and malformed input decode.
