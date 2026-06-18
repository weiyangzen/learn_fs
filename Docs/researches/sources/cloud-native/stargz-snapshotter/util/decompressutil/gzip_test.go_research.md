<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/decompressutil/gzip_test.go -->
# sources/cloud-native/stargz-snapshotter/util/decompressutil/gzip_test.go

## Purpose
Tests gzip helper selection and decompression behavior for external and Go fallback helpers.

## Important APIs, Types, And Functions
- `TestGetGzipHelperFunc` detects available `gzip`, `pigz`, and `igzip` commands.
- Builds compressed test data with Go `gzip.Writer`.
- Resets `findCmdOnce` after the test to avoid leaking discovery state.

## Control Flow
The test skips if no helper command is available, builds cases for invalid helper, available helpers, and unavailable fallback helpers, obtains helper functions, reads decompressed output, and compares bytes.

## State And Persistence
Creates a temp file but primarily uses in-memory buffers. Mutates package globals for command path discovery and resets `sync.Once`.

## Dependencies And Integration Points
Depends on environment-installed gzip-family commands for full coverage and on `gzip.go` helper selection.

## Risks And Edge Cases
Coverage varies by CI environment depending on installed commands. A temp file is created but not central to the assertions.

## Test Signals
Passing means invalid names fail, available helpers decompress correctly, unavailable requested helpers return Go `*gzip.Reader`, and output matches original data.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/decompressutil/gzip_test.go -->
