<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/utils_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/utils/utils_test.go

## Purpose

This test file validates general utility behavior across platform matching, archive extraction, retry classification, descriptor marshaling, filesystem-version annotations, retry loops, and hashing.

## Important APIs, Types, and Functions

Helpers `makePlatform`, `makeDesc`, `createArchive`, `addToArchive`, and `writerToSlice` support tests for `IsSupportedArch`, `IsNydusPlatform`, `MatchNydusPlatform`, `UnpackFile`, `HashFile`, `MarshalToDesc`, `WithRetry`, `RetryWithHTTP`, `GetNydusFsVersionOrDefault`, `RetryWithAttempts`, and `UnpackFileNotFound`.

## Control Flow

Tests construct OCI platform descriptors, in-memory or on-disk tar.gz archives, temporary files, and controlled retry closures. Assertions check boolean classification, expected digest values, error propagation, and cancellation behavior.

## State and Persistence Behavior

Some tests create files in the current working directory (`example.txt`, `output.tar.gz`, `output.txt`, `test`) and remove them with defers; others use temp files. The retry test performs an HTTP GET to localhost:5000 and expects connection refused.

## Dependencies and Integration Points

The test suite depends on OCI spec types, digest helpers, HTTP/syscall errors, gzip/tar primitives, and `testify/require`. It gives broad regression signals for utility functions used across nydusify.

## Risks and Test Signals

The tests cover many happy and error paths, but the localhost retry test is environment-sensitive if a service happens to listen on port 5000. `UnpackFile` parent-directory behavior and malformed tar loop behavior remain under-tested.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/utils_test.go -->
