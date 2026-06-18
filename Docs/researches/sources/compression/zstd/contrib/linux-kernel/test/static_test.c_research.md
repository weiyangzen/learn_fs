<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/static_test.c -->
# sources/compression/zstd/contrib/linux-kernel/test/static_test.c

## Purpose
`static_test.c` is a small user-space test that verifies the static kernel-style decompression API can decode a known empty zstd frame.

## Important APIs, Types, And Functions
It defines a `CONTROL` assertion macro, the `kEmptyZstdFrame` byte sequence, `test_decompress_unzstd`, and `main`. The test exercises the unzstd/static decompression entry point through the linux-kernel shim.

## Control Flow
`main` calls the single decompression test. The test provides the embedded compressed frame, prepares output storage, invokes the static decompressor, and asserts that the result matches an empty payload and successful return status.

## State And Persistence
All state is stack/static test data. No files are written and no global state is persisted.

## Dependencies And Integration Points
It depends on the kernel-contrib test include tree and the zstd static decompression symbols compiled by the local Makefile. It complements `test.c`, which covers broader btrfs/f2fs-like flows.

## Risks
Because it only uses an empty frame, it mainly catches linkage/API regressions, not large-window or dictionary behavior.

## Test Signals
Successful process exit indicates that the static decompression wiring and an empty zstd frame path work.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/linux-kernel/test/static_test.c -->
