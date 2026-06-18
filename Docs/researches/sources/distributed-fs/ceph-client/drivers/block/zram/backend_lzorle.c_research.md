# sources/distributed-fs/ceph-client/drivers/block/zram/backend_lzorle.c

Purpose: zram backend adapter for LZO-RLE compression with LZO-compatible safe decompression.

Important APIs/types/functions: mirrors the LZO backend with `lzorle_create()`, `lzorle_destroy()`, `lzorle_compress()` using `lzorle1x_1_compress()`, `lzorle_decompress()` using `lzo1x_decompress_safe()`, and `backend_lzorle` named `lzo-rle`.

Control flow and state: no params; per-CPU context owns the LZO workspace. Compression/decompression return zero on `LZO_E_OK`, otherwise library code.

Dependencies and integration: depends on `linux/lzo.h`, zcomp, and the LZO backend Kconfig option.

Risks: same error-code normalization concern as LZO. Compatibility relies on standard LZO decompressor accepting LZO-RLE output.

Test signals: round-trip RLE-heavy and random pages, malformed input, and allocation failure.
