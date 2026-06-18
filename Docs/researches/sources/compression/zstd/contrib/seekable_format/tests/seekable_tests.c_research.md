<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/tests/seekable_tests.c -->
# sources/compression/zstd/contrib/seekable_format/tests/seekable_tests.c

## Purpose
`seekable_tests.c` is the main unit/regression test for zstd seekable format compression, decompression, seek-table access, and hang regressions.

## Important APIs, Types, And Functions
It defines a custom buffer-backed file wrapper with `readBuffWithTotal` and `seekBuffWithTotal`, then tests seekable cstream/dstream APIs, seek-table APIs, malformed inputs, empty compression header behavior, and repeated seek/decompress calls.

## Control Flow
`main` runs numbered tests using `assert` and `goto _test_error` failure exits. It compresses buffers, initializes seekable objects from memory or custom callbacks, validates frame metadata, checks malformed data returns errors rather than hanging, and verifies repeated forward/backward range reads.

## State And Persistence
State is heap buffers and in-memory compressed seekable data. It writes no persistent files.

## Dependencies And Integration Points
It depends on `zstd_seekable.h` and the seekable compress/decompress implementations. It is the primary regression signal for the contrib format.

## Risks
Assertions disappear under `NDEBUG`. Test data is small, so huge-frame and file-backed edge cases need additional coverage.

## Test Signals
Success messages confirm round-trip, metadata access, malformed input handling, empty stream header, and efficient repeated decompression behavior.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/tests/seekable_tests.c -->
