# sources/cloud-native/containers-storage/pkg/archive/archive_110.go

## Purpose
This Go-version-specific file is compiled on Go 1.10 and newer. It tunes tar header handling for copy-pass archives and timestamp comparison fidelity.

## Important Functions
`copyPassHeader(hdr)` sets `hdr.Format = tar.FormatPAX`, enabling PAX behavior for copy-pass streams. `maybeTruncateHeaderModTime(hdr)` truncates `ModTime` to seconds only when `hdr.Format` is `tar.FormatUnknown`.

## Control Flow and State
The functions mutate a caller-provided `*tar.Header` and do not store state. They are called from `prepareAddFile` and `CopyFileWithTar` paths in `archive.go`.

## Dependencies and Integration Points
The file depends on `archive/tar` and `time`. It pairs with `archive_19.go`, which compiles on older Go versions and leaves both functions as no-ops.

## Risks and Edge Cases
The timestamp truncation behavior is subtle: it tries to avoid Go tar writer rounding surprises while retaining richer PAX timestamp precision when copy-pass mode has already set a concrete format. Incorrect changes here can cause false positives in directory diff comparisons.

## Test Signals
Round-trip tests in `archive_test.go`, especially no-change comparisons and timestamp determinism, indirectly validate this behavior on modern Go.
