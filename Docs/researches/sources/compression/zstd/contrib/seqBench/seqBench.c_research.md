# sources/compression/zstd/contrib/seqBench/seqBench.c

Purpose: minimal experiment for zstd's static sequence APIs. It reads one input file, generates zstd sequences, compresses those sequences with explicit block delimiters, decompresses the result, and compares the output to the original.

Important APIs/functions: `main`, `ZSTD_createCCtx`, `ZSTD_sequenceBound`, `ZSTD_generateSequences`, `ZSTD_CCtx_setParameter(ZSTD_c_blockDelimiters, ZSTD_sf_explicitBlockDelimiters)`, `ZSTD_compressSequences`, `ZSTD_decompress`, `ZSTD_isError`, and `memcmp`.

Control flow: argument count must be exactly two. The program opens the input, uses `fseek/ftell` to determine size, reads it into memory, allocates a sequence array sized by `ZSTD_sequenceBound()`, allocates a compressed buffer with `ZSTD_compressBound()`, generates sequences, compresses from sequences, then decompresses into a validation buffer. It prints success or the first mismatching byte index.

State and persistence: all state is process-local heap memory plus the created `ZSTD_CCtx`. It does not persist outputs to disk; compressed bytes are only kept in memory for validation.

Dependencies/integration: depends on `ZSTD_STATIC_LINKING_ONLY` and therefore on unstable/static zstd APIs. It is built by the adjacent Makefile with the local static library. It uses libc file IO and assumes the whole file fits into `long` and memory.

Risks: there is little error checking for `fopen`, `fseek`, `ftell`, `malloc`, `fread`, sequence-generation return values, decompression errors, or context allocation. `ZSTD_generateSequences()` can produce fewer sequences than the bound, but this example passes the bound onward rather than an observed count, so behavior depends on the API contract. The `printf("ERROR: %lu")` format is not portable for `size_t`, and the bad-index loop uses `int` against a `long` size.

Test signals: use small, empty, and larger files; run under ASan/UBSan to catch unchecked allocation/IO failures; compare generated output against `ZSTD_decompress`; and rebuild when zstd static sequence APIs change.
