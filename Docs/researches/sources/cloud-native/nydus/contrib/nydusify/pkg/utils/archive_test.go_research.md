<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/archive_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/utils/archive_test.go

## Purpose

This test file verifies tar/tar.gz packing and unpacking helpers, including security-sensitive path traversal behavior in the plain tar helper from `utils.go`.

## Important APIs, Types, and Functions

Tests cover `PackTargzInfo`, `UnpackTargz`, `UnpackFromTar`, path traversal rejection, parent directory creation, root directory entries, invalid streams, and compressed/uncompressed `PackTargz`.

## Control Flow

The tests build in-memory tar or gzip streams with `archive/tar` and `compress/gzip`, call the utility under test, then inspect created files and content. `TestPackTargzWithoutCompression` and `TestPackTargzCompressedStream` read the generated archive entries back to verify names and content.

## State and Persistence Behavior

All filesystem writes are under temporary directories, except temporary files created by `os.CreateTemp`. Traversal tests assert that escaped files are not created outside the target directory.

## Dependencies and Integration Points

The tests depend on Go archive primitives and `testify`. They validate both `archive.go` and the plain tar extraction helper in `utils.go`.

## Risks and Test Signals

The strongest signal is coverage for `../` traversal rejection in `UnpackFromTar`. The fixed digest in `TestPackTargzInfo` can be sensitive to gzip/tar metadata changes, and tests do not cover overlay whiteout conversion or umask restoration under error.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/archive_test.go -->
