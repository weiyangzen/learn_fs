# sources/compression/zstd/examples/multiple_simple_compression.c

Purpose: shows efficient one-shot compression of many files by preallocating buffers and reusing one `ZSTD_CCtx`.

Important types/functions: `resources`, `createResources_orDie`, `freeResources`, `compressFile_orDie`, `main`, `ZSTD_createCCtx`, `ZSTD_compressCCtx`, `ZSTD_compressBound`, and common file helpers.

Control flow: resource creation scans all input arguments to find maximum file size and filename length, allocates one input buffer, one compressed buffer, an output filename buffer, and one CCtx. The main loop copies each input name into the reusable output-name buffer with `.zst`, loads the file into the reusable input buffer, compresses into the reusable compressed buffer, and writes the result.

State and persistence: reusable buffers and context persist for all files. Output files are written as `<input>.zst`. No cross-process state exists.

Dependencies/integration: public zstd simple compression API and `common.h`. It is part of examples Makefile tests.

Risks: all files must fit into memory and into `size_t`. Scanning all files before compression means any missing file aborts before producing outputs. Output naming may overwrite existing `.zst` files. The context is reused without explicit reset; `ZSTD_compressCCtx` handles one-shot context reuse under the public API.

Test signals: compress multiple files of different sizes, include zero-length file coverage, compare decompressed output, and test long filenames near the computed output-name capacity.
