# sources/compression/zstd/contrib/externalSequenceProducer/main.c

Purpose: executable example showing how to register an external sequence producer with a zstd compression context and validate round-trip compression.

Important behavior: expects one file path. It creates a `ZSTD_CCtx`, registers `simpleSequenceProducer` with an integer state pointer, enables `ZSTD_c_enableSeqProducerFallback`, reads the whole file into memory, allocates `ZSTD_compressBound(srcSize)` destination, compresses with `ZSTD_compress2`, decompresses with `ZSTD_decompress`, and compares source/validation buffers. `CHECK` prints zstd error names and returns failure.

State, dependencies, and integration: state is heap buffers and a compression context. It depends on `ZSTD_STATIC_LINKING_ONLY`, public/static zstd APIs, `zstd_errors.h`, and the local producer header.

Risks and test signals: file I/O uses `assert`, `ftell` result is stored in `size_t`, and all input is held in memory, so this is example code rather than robust CLI code. The success message and byte-for-byte comparison are its runtime test signal.
