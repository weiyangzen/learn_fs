<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/file_io.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/file_io.rs

Purpose: Async file data generation, write/read verification, checksum, and byte-by-byte comparison utilities for integration tests.

Important APIs/types: `DataSize(u64)` wraps byte sizes and provides constructors for bytes, KB, MB, GB, block counts, conversions, `Display`, and serde-as-u64 behavior. `set_test_buf_rng_seed()` fixes a global ChaCha8 seed. `test_write_to_file()` creates deterministic/random test buffers, writes repeated buffers at an offset, then seeks back and validates every byte. `compute_file_checksum()` streams MD5 over a file. `compare_files()` compares two files in 16 KiB chunks and reports size or byte mismatch.

Control flow: Tokio `OpenOptions`, async seek/read/write, and in-memory buffers are used throughout.

State and dependencies: global `OnceCell<ChaCha8Rng>` controls buffer seed and cannot be reset after first set. File contents are mutated by write tests.

Risks and test signals: cloning the RNG from `OnceCell` means repeated calls from the same seed create identical buffers, useful for reproducibility but surprising for randomness. `DataSize` conversions to `usize` can truncate on small platforms. Validation errors include exact offsets.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/file_io.rs -->
