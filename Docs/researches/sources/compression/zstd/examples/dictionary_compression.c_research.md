# sources/compression/zstd/examples/dictionary_compression.c

Purpose: demonstrates one-shot compression of multiple files using a pre-trained zstd compression dictionary loaded once into a `ZSTD_CDict`.

Important functions/APIs: `createCDict_orDie`, `compress`, `createOutFilename_orDie`, `main`, `ZSTD_createCDict`, `ZSTD_createCCtx`, `ZSTD_compress_usingCDict`, `ZSTD_freeCCtx`, `ZSTD_freeCDict`, and helpers from `common.h`.

Control flow: `main` expects one or more input files plus a final dictionary path. It creates a `ZSTD_CDict` at level 3, loops over inputs, creates `<input>.zst` names, loads each file, allocates a compression-bound buffer, compresses using the dictionary in a fresh CCtx, saves output, prints sizes, and frees per-file buffers.

State and persistence: the dictionary object persists for all files. Per-file input/compressed buffers and CCtx are transient. Persistent side effects are `.zst` output files beside the inputs.

Dependencies/integration: public zstd dictionary API, trained dictionary from `zstd --train` or zdict APIs, and `common.h` fatal helpers. The examples Makefile uses it in dictionary tests.

Risks: no dictionary training is performed here; invalid or mismatched dictionary content will surface as zstd errors. Output naming blindly appends `.zst` and can overwrite existing files. It creates a new CCtx per file even though the dictionary is reused; that is simpler but not optimal.

Test signals: compress several files with a trained dictionary, decompress with `dictionary_decompression.c`, verify dictionary ID presence, test invalid dictionary files, and confirm cleanup of output-name allocations.
