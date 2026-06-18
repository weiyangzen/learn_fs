<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/dump/dump.go -->
# sources/cloud-native/containers-storage/pkg/chunked/dump/dump.go

Purpose: generates a composefs-info-compatible textual dump from a chunked minimal TOC.

Important APIs/types/functions: escape flags `ESCAPE_STANDARD`, `NOESCAPE_SPACE`, `ESCAPE_EQUAL`, `ESCAPE_LONE_DASH`; helpers `escaped`, `escapedOptional`, `getStMode`, `dumpNode`; public `GenerateDump`.

Control flow: escaping converts non-printable/non-graph bytes, backslash, newline, tab, carriage return, optional equals, spaces, and lone dash into expected textual forms. `dumpNode` normalizes paths, recursively synthesizes missing parent directories, de-duplicates identical entries, writes path, size, mode/type, link count, UID/GID, rdev, timestamp, payload path/link target, inline placeholder, verity digest, and decoded xattrs. `GenerateDump` type-checks TOC, starts a pipe goroutine, computes hardlink counts, emits a root entry for empty TOCs, skips chunk entries, and dumps all non-chunk entries.

State/persistence: streaming in-memory output through an `io.Pipe`; no filesystem writes.

Dependencies/integration: uses minimal TOC metadata, chunked internal path helpers, OCI digest validation, base64 xattr decoding, Unix mode bits, and optional verity digest map.

Risks: output must match composefs expectations exactly. Duplicate path mismatch is an error. Xattrs must be valid base64. Missing-parent synthesis can introduce inferred directories with default mode/time.

Test signals: `dump_test.go` covers escaping, duplicate entries, files, dirs, symlinks, hardlinks, missing parents, xattrs, and expected line formatting.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/dump/dump.go -->
