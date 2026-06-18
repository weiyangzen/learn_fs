<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compression_linux_test.go -->
# sources/cloud-native/containers-storage/pkg/chunked/compression_linux_test.go

Purpose: tests tar-split size accounting and temporary file unlink behavior for chunked compression helpers.

Important APIs/types/functions: `TestTarSizeFromTarSplit` and `TestOpenTmpFile`.

Control flow: `TestTarSizeFromTarSplit` writes fixture tar entries, records actual tarball length, runs tar-split packing, and asserts `tarSizeFromTarSplit` reconstructs the same size. `TestOpenTmpFile` repeatedly opens temp files through both `openTmpFile` and fallback `openTmpFileNoTmpFile`, checks `/proc/self/fd/<fd>` contains `(deleted)`, and closes files.

State/persistence: temporary tar buffers and temp directory files that are unlinked immediately.

Dependencies/integration: uses tar-split `asm.NewInputTarStream`, `storage.NewJSONPacker`, and Linux `/proc/self/fd`.

Risks/test signal: protects the invariant that tar-split can be used to calculate layer tar size and that temporary tar-split data is not left visible on disk.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compression_linux_test.go -->
