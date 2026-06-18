<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/largeDictionary.c -->
## sources/compression/zstd/tests/largeDictionary.c

Purpose: Stress test for streaming compression with a very large window/dictionary-like history and immediate round-trip decompression of emitted chunks.

Important APIs and functions: `compress()` wraps `ZSTD_compressStream2` with `ZSTD_inBuffer`, `ZSTD_outBuffer`, `ZSTD_decompressStream`, and `ZSTD_EndDirective`. `main()` configures `ZSTD_CCtx` and `ZSTD_DCtx` using `ZSTD_CCtx_setParameter` and `ZSTD_DCtx_setParameter`, generates data with `RDG_genBuffer`, and cleans up contexts and buffers.

Control flow: The program allocates a 2 GiB source buffer, a 1 GiB round-trip buffer, and an output buffer sized by `ZSTD_compressBound(1 GiB)`. It sets `windowLog=31`, one worker, maximum overlap, checksum, `btopt`, and tuned low hash/chain/search values, then sets decoder `windowLogMax=31`. It generates deterministic data and compresses ten 1 GiB chunks with `ZSTD_e_continue`, then a final 1 GiB chunk with `ZSTD_e_end`; every compressed output chunk is immediately fed to the streaming decoder and the final call must finish the frame.

State and persistence: Heavy heap allocation is the main state. Compression and decompression contexts persist across all chunks until cleanup. No files are written.

Dependencies and integration points: Requires static-linking-only zstd parameters, `datagen.h`, and enough memory/address space for multi-gigabyte allocations. It exercises multithreaded compression settings and large window decode limits.

Risks: Very high memory use makes this unsuitable for normal CI unless gated. The comment says "Compress 30 GB" but the visible loop compresses eleven 1 GiB chunks total. Round-trip validation checks decoder errors and frame completion but does not compare decoded bytes against the original buffer.

Test signals: Stderr progress messages for each GiB and final `Success!`; exit `0` on success, `1` on allocation, parameter, compression, decompression, or incomplete-frame failure.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/largeDictionary.c -->
