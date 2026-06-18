# sources/compression/zstd/examples/streaming_compression.c

Purpose: demonstrates streaming compression of one file with configurable compression level and worker count, checksum enabled, and recommended zstd stream buffer sizes.

Important functions/APIs: `compressFile_orDie`, `createOutFilename_orDie`, `main`, `ZSTD_createCCtx`, `ZSTD_CCtx_setParameter`, `ZSTD_c_compressionLevel`, `ZSTD_c_checksumFlag`, `ZSTD_c_nbWorkers`, `ZSTD_compressStream2`, `ZSTD_e_continue`, and `ZSTD_e_end`.

Control flow: parse `FILE [LEVEL] [THREADS]`, open input/output, allocate recommended buffers, create CCtx, set parameters, optionally request workers, then read chunks. For each chunk, choose end directive based on EOF, repeatedly call `ZSTD_compressStream2` until input is consumed or final frame is complete, and write each produced output buffer.

State and persistence: CCtx and buffers exist for one file. Output persists as `<input>.zst`.

Dependencies/integration: public zstd streaming API, optional multithread support in the linked library, `common.h` IO helpers. It is included in example tests.

Risks: `atoi` rejects level/thread value `0`, so level 0/default cannot be requested through this example. If linked libzstd lacks multithreading, worker setting emits a note and continues. Output overwrite is unchecked.

Test signals: compress with default and explicit level/thread values, decompress output, test exact-buffer-size and empty inputs, and run against both multithread-enabled and single-thread libraries.
