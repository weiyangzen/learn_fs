# sources/cloud-native/nydus-snapshotter/pkg/remote/unpack.go

## Purpose
Extracts a named file from a compressed tar stream and writes it to a target path.

## Important APIs, Types, And Functions
`Unpack(reader io.Reader, source, target string) error` is the only API.

## Control Flow
The function wraps the input with containerd compression auto-detection, iterates tar headers, and when `hdr.Name` equals `source`, creates the target file and copies the tar entry content into it. If iteration reaches EOF without a match, it returns a not-found error.

## State And Persistence
Writes one output file at `target` and closes both decompressor and file. It does not create parent directories.

## Dependencies And Integration Points
Uses Go `archive/tar`, `os.Create`, and containerd compression helpers. Likely used to pull specific files such as bootstrap/config artifacts from layer blobs.

## Risks And Edge Cases
Exact tar header-name matching means path normalization is caller responsibility. Existing target files are truncated. It does not validate regular-file type, size limits, path safety, permissions, or parent directory existence.

## Test Signals
No tests in this subset. Risk should be managed by callers controlling `source` and `target`.
