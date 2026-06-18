# sources/compression/lz4/tests/decompress-partial-usingDict.c

## Purpose
This standalone regression test validates `LZ4_decompress_safe_partial_usingDict()` across no-dictionary, prefix-dictionary, and external-dictionary scenarios.

## Important APIs, Types, and Functions
`main()` compresses a static lorem source with `LZ4_compress_default()` and repeatedly calls `LZ4_decompress_safe_partial_usingDict()`. It allocates a large buffer to position output after prefix memory and a separate dictionary buffer for external dict cases.

## Control Flow, State, and Persistence
The test computes `srcLen`, compresses once into `cmpBuffer`, then loops `i` from `cmpSize` through `cmpSize + 9` so the decoder sees exact input and extra trailing bytes. Each mode checks nonnegative result, exact `srcLen`, and `memcmp()` equality. Heap buffers are process-local; the program returns `-1` on the first failure and `0` on success.

## Dependencies and Integration Points
It uses the public `lz4.h` block API plus libc allocation and assertions. It complements the broader fuzzer by making a focused dictionary partial-decode case easy to run from build scripts.

## Risks and Test Signals
The test intentionally does not free heap memory before exit, which is acceptable for a tiny executable but noisy under strict leak tools. Strong signals are the five dictionary layouts: none, small prefix, large prefix, small external, and large external.
