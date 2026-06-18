<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/dump/dump_test.go -->
# sources/cloud-native/containers-storage/pkg/chunked/dump/dump_test.go

Purpose: tests composefs dump escaping and node formatting.

Important APIs/types/functions: `TestEscaped` and `TestDumpNode`.

Control flow: `TestEscaped` checks plain strings, control characters, backslashes, equals escaping, lone dash escaping, space handling, and UTF-8 bytes rendered as hex escapes. `TestDumpNode` builds metadata for root, regular file, duplicate roots, directory, symlink, hardlink, and missing-parent cases, then calls `dumpNode` and compares exact output or expected errors.

State/persistence: in-memory buffers only.

Dependencies/integration: exercises `escaped`, `dumpNode`, base64 xattr decoding, digest-to-physical path conversion, and Unix mode formatting.

Risks/test signal: exact-string assertions protect format compatibility but may be brittle to intentional formatting changes. Tests do not cover full `GenerateDump` pipe error propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/dump/dump_test.go -->
