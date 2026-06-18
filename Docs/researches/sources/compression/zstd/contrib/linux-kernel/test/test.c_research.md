<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/test.c -->
# sources/compression/zstd/contrib/linux-kernel/test/test.c

## Purpose
`test.c` is the main user-space functional test for the linux-kernel zstd module port. It models filesystem consumer patterns such as btrfs compression/decompression, unzstd use, f2fs parameter queries, and stack usage checks.

## Important APIs, Types, And Functions
It defines `test_data_t`, `create_test_data`, `free_test_data`, `test_btrfs`, `test_decompress_unzstd`, `test_f2fs`, stack sentinel helpers, `test_stack_usage`, and `main`. It exercises workspace-bound queries, cctx/dctx creation, streaming APIs, and one-shot compression/decompression wrappers.

## Control Flow
`main` creates deterministic test data, runs each scenario, reports progress to stderr, then frees buffers. Compression tests allocate workspaces, compress sample data, decompress it back, and compare. Stack tests fill/check a sentinel area around calls.

## State And Persistence
State is heap-allocated input/compressed/output buffers plus temporary workspaces. There is no persistent storage.

## Dependencies And Integration Points
The file integrates with `linux_zstd.h`, shim kernel headers, and the exported symbols from `zstd_common_module.c`, `zstd_compress_module.c`, and `zstd_decompress_module.c`.

## Risks
The test relies on deterministic buffer sizing and approximate consumer behavior; it is not a fuzzer. Stack checks are compiler/optimization sensitive.

## Test Signals
Passing output covers workspace sizing, streaming reset/end behavior, static decompression, level bounds, and stack footprint regressions for kernel consumers.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/test.c -->
