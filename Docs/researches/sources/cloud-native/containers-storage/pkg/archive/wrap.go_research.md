<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/wrap.go -->
# sources/cloud-native/containers-storage/pkg/archive/wrap.go

Purpose: small testing/demo helper for generating in-memory tar archives from path/content string pairs.

Important APIs/types/functions: `Generate` and `parseStringPairs`.

Control flow: `parseStringPairs` groups variadic strings into `[name,content]` pairs, defaulting missing content to empty. `Generate` writes each pair as a tar regular file header and content into a `bytes.Buffer`, closes the tar writer, and returns the buffer as an `io.Reader`.

State/persistence: all state is in memory. No filesystem writes.

Dependencies/integration: useful for tests and examples that need simple tar streams without setting full metadata.

Risks: buffers the entire archive, sets minimal tar metadata, and treats incomplete pairs as empty files. It is not suitable for large archives or production metadata preservation.

Test signals: `wrap_test.go` validates empty-file and content-file generation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/wrap.go -->
