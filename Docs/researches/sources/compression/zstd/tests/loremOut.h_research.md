<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/loremOut.h -->
## sources/compression/zstd/tests/loremOut.h

Purpose: Declares the large lorem-output generator API for zstd tests.

Important APIs and types: Declares `void LOREM_genOut(unsigned long long size, unsigned seed);`.

Control flow and integration: Test programs include this header and call `LOREM_genOut` when they want compressible bytes streamed directly to stdout instead of an in-memory buffer.

State and persistence: The declaration implies stdout side effects implemented in `loremOut.c`; the header owns no state.

Dependencies and integration points: Must remain in sync with `loremOut.c`. Uses only standard integer types available without including extra headers because `unsigned long long` and `unsigned` are built-in C types.

Risks: No include guard is present, though the header only contains one compatible declaration. Repeated inclusion is unlikely to break but is not ideal.

Test signals: Compile-time linkage should resolve `LOREM_genOut` exactly once from `loremOut.c`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/loremOut.h -->
