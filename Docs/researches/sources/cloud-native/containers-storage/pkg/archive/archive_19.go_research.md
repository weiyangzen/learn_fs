# sources/cloud-native/containers-storage/pkg/archive/archive_19.go

## Purpose
This compatibility file is selected for Go versions older than 1.10. It provides no-op implementations of tar header helpers that modern builds implement in `archive_110.go`.

## Important Functions
`copyPassHeader(hdr)` and `maybeTruncateHeaderModTime(hdr)` are both no-ops under the `!go1.10` build tag.

## Control Flow and State
There is no control flow beyond accepting the header pointer. No persistent or runtime state is modified.

## Dependencies and Integration Points
The file depends only on `archive/tar`. It keeps `archive.go` source-compatible across Go versions by providing the same helper names.

## Risks and Edge Cases
Older Go builds do not force PAX for copy-pass and do not apply the timestamp truncation workaround. This can affect metadata precision and change detection, but only for legacy toolchains.

## Test Signals
Current test runs on Go 1.10+ will not exercise this file. Its main signal is build compatibility for old Go versions.
