# sources/cloud-native/soci-snapshotter/internal/archive/compression/compression.go

Purpose: configurable decompression stream registry for unpacking compressed image layers. It adapts containerd archive decompression interfaces so SOCI can invoke configured external decompressors for gzip and zstd media types.

Important APIs/types/functions: `DecompressStream` mirrors containerd's stream signature. `InitializeDecompressStreams` validates configured executable paths and registers stream functions for Docker gzip, OCI gzip, and OCI zstd media types. `GetDecompressStream` looks up a stream by layer media type. Internal types include `decompressionKey`, `readCloserWrapper`, `decompressor`, `gzipDecompressor`, `zstdDecompressor`, `decompress`, and `cmdStream`.

Control flow: initialization runs once via `sync.Once`; each configured algorithm is sanitized with `internal/os.SanitizeExecutablePath`, copied into a sanitized config, and mapped to one or more OCI/Docker media types. A returned stream starts an `exec.CommandContext`, connects input to stdin and stdout to an `io.Pipe`, and exposes a read closer whose close cancels the command context.

State and persistence: global mutable state is `decompressStreams`, `initDecompressors`, and `initDecompressorsErr`. Once initialization is attempted, later calls return the first result and do not reconfigure streams unless tests reset internals. Runtime state is an external decompressor process per stream invocation.

Dependencies/integration points: depends on `config.DecompressStream`, `internal/os` path sanitization, containerd archive compression identifiers, OpenContainers layer media types, `exec.CommandContext`, and containerd logging for unsupported algorithms. It plugs into layer unpack paths that need custom decompression.

Risks: singleton initialization can preserve a failed or partial configuration for process lifetime. Unsupported algorithms are logged but ignored. The path sanitizer rejects shell metacharacters and requires executable files, but arguments are passed directly to the binary and must still be configured correctly. `cmdStream` only reports process failures to readers, so callers must read to observe stderr/exit errors.

Test signals: companion tests cover empty config, gzip mapping to two media types, unsupported algorithm ignore behavior, missing gzip/zstd executable failures, lookup before/after initialization, and `cmdStream` success/failure propagation including stderr text.
