## sources/cloud-native/containers-storage/pkg/chunked/internal/minimal/compression.go

Purpose: minimal, dependency-light zstd:chunked format definitions and manifest writing logic shared with consumers that should not import graph-driver code.

Important APIs/types/functions: `ZstdWriter`, `CreateZstdWriterFunc`, `TOC`, `FileMetadata`, chunk/file type constants, annotation keys, `GetType`, `TarSplitData`, `WriteZstdChunkedManifest`, `ZstdWriterWithLevel`, `ZstdChunkedFooterData`, `footerDataToBlob`, `timeIfNotZero`, and `NewFileMetadata`.

Control flow: `WriteZstdChunkedManifest` marshals a TOC with entries and tar-split digest, compresses it with caller-provided zstd writer, records checksum and position annotations, writes the compressed manifest and tar-split bytes as zstd skippable frames, then writes a binary footer frame. `NewFileMetadata` converts tar headers to JSON metadata and base64-encodes PAX xattrs.

State and persistence: writes zstd skippable frames to a destination stream and mutates the caller-provided metadata map with manifest/tar-split annotations. It does not read files or maintain global mutable state beyond constants.

Dependencies and integration points: consumed by chunked compressor and differ manifest readers/writers. Integrates with `archive.PaxSchilyXattr`, `jsoniter`, `klauspost/compress/zstd`, OCI digest parsing, and `tar-split` tar types.

Risks: callers must pass valid offsets that reflect bytes already written; `RegularFile` chunk metadata invariants are documented but not enforced here; digest security depends on annotation consumers verifying the compressed manifest digest; footer is explicitly not read by this implementation.

Test signals: `compression_test.go` checks binary footer round trip and magic validation. `zstdchunked_test.go` exercises manifest generation and reading through higher-level chunked code. Local test execution was blocked by missing `go`.
