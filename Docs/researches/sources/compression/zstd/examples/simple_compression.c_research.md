# sources/compression/zstd/examples/simple_compression.c

Purpose: smallest one-shot compression example: read one file fully into memory, compress with `ZSTD_compress`, and save `<file>.zst`.

Important functions/APIs: `compress_orDie`, `createOutFilename_orDie`, `main`, `ZSTD_compressBound`, `ZSTD_compress`, `CHECK_ZSTD`, and common file/memory helpers.

Control flow: require exactly one input file, allocate an output name, load the input file, allocate `ZSTD_compressBound(input_size)` bytes, compress at level 1, save compressed bytes, print a summary, and free buffers.

State and persistence: all runtime state is local heap memory. Persistent side effect is the `.zst` output file.

Dependencies/integration: public zstd simple API and `common.h`; built and tested by examples Makefile.

Risks: whole-file memory use and blind output overwrite. It does not set frame checksum or advanced parameters. It is intentionally fatal-on-error.

Test signals: compress regular and zero-size files, decompress with `simple_decompression` or zstd CLI, and test missing/permission-denied input failures.
