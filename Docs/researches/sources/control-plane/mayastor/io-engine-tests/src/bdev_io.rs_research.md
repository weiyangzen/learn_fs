<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/bdev_io.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/bdev_io.rs

Purpose: Direct in-process I/O helpers for tests using `UntypedBdevHandle` rather than gRPC or host device paths.

Important APIs: `write_some()` delegates to `write_blocks`; `write_blocks()` opens a bdev read/write, allocates DMA memory sized by block length and count, fills it with a byte, and writes at an offset; `read_some()` reads into DMA memory and asserts the first block matches the expected fill; `write_zeroes_some()` issues write-zeroes; `read_some_safe()` returns `Ok(false)` instead of panicking on byte mismatch.

Control flow: each helper opens a fresh handle by name and uses async SPDK handle methods. Buffer sizing is based on the target bdev block length.

State and dependencies: mutates bdev content. Depends on io-engine core DMA allocation and an initialized SPDK reactor context.

Risks and test signals: `read_some()` only checks the first 512 bytes, regardless of actual block size. Offsets are passed through as byte offsets to handle methods, so callers must match expected units. Useful test signals are exact read/write lengths and mismatch prints from `read_some_safe`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/bdev_io.rs -->
