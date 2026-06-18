# sources/cloud-native/soci-snapshotter/ztoc/compression/gzip_zinfo_test.go

## Purpose
This test file exercises guard and deserialization behavior for the gzip zinfo wrapper.

## Important APIs, Types, and Functions
`TestNewGzipZinfo` covers nil/empty blobs, undersized headers, inconsistent checkpoint counts, zero-checkpoint v2-like blobs, and v1 compatibility. `TestExtractDataFromBuffer` validates nil/empty buffer errors, negative-size errors, and zero-size success. `TestExtractDataFromFile` validates negative-size and zero-size behavior.

## Control Flow, State, and Persistence
The tests are table-driven and run in parallel. They instantiate `GzipZinfo` directly for guard checks without building real gzip checkpoint state, relying on early returns before C extraction for most cases.

## Dependencies and Integration Points
They depend on the compression package and Go testing. Broader integration with real gzip data is covered in ztoc tests rather than here.

## Risks and Test Signals
The tests do not validate successful extraction from non-empty real gzip buffers or files. They do signal that malformed serialized checkpoint data must return errors rather than over-read, and that zero-byte extraction is a safe fast path.
