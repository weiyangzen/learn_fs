# sources/cloud-native/containers-storage/pkg/archive/archive_windows_test.go

## Purpose
This Windows-only test file validates Windows archive path canonicalization and documents a skipped invalid-destination copy case.

## Important Tests
`TestCanonicalTarNameForPath` checks that plain names pass, Unix-style `foo/bar` fails, and Windows-style `foo\bar` converts to `foo/bar`. `TestCanonicalTarName` verifies directory names receive trailing slashes after conversion. `TestCopyFileWithInvalidDest` is skipped with a note that it currently fails and needs investigation.

## Control Flow and State
The active tests are pure path-conversion checks. The skipped copy test would create temp files and attempt a copy to `c:dest`, but it is not executed.

## Dependencies and Integration Points
The file depends on Windows implementation functions in `archive_windows.go` and generic `canonicalTarName` in `archive.go`.

## Risks and Edge Cases
The skipped test is an explicit gap in Windows copy error coverage. The canonicalization tests do not cover long-path prefix behavior or permission normalization.

## Test Signals
The main signal is that Windows relative archive paths must be converted to POSIX tar names and forward slashes in Windows inputs are rejected.
