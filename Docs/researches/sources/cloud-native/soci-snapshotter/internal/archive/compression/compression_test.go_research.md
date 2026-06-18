# sources/cloud-native/soci-snapshotter/internal/archive/compression/compression_test.go

Purpose: unit tests for configurable decompression-stream initialization, media-type lookup, and command-stream error propagation.

Important APIs/types/functions: `resetDecompressStreams` resets package globals for test isolation. `TestInitializeDecompressStreams` covers default, gzip, unsupported algorithm, and nonexistent executable configurations. `TestGetDecompressStream` checks lookups before initialization and after gzip setup. `TestCmdStream` and `TestCmdStreamBad` verify stdout capture and error formatting from subprocesses.

Control flow: tests reset globals, call `InitializeDecompressStreams`, then assert map cardinality and specific key presence. Lookup tests first assert no streams, initialize gzip, then assert Docker and OCI gzip media types are available. Command tests run small shell snippets through `cmdStream` and read from the returned pipe.

State and persistence: directly mutates package-level maps and `sync.Once`, which is intentional test-only access from the same package. It assumes `/usr/bin/gzip` exists for positive sanitizer validation and fake `/usr/bin/superfast*` paths do not.

Dependencies/integration points: uses `config.DecompressStream`, OCI media type constants, `os/exec`, `io.ReadAll`, and shell availability. It tests behavior that downstream unpackers rely on without invoking actual layer unpacking.

Risks: hard-coded `/usr/bin/gzip` can make the test environment-dependent. Resetting `sync.Once` is safe in tests but highlights that production cannot reinitialize. Command failure assertions compare exact error string including newline from stderr.

Test signals: high confidence around media-type registration and subprocess pipe behavior; no test directly decompresses gzip/zstd data or validates zstd success with a real binary.
