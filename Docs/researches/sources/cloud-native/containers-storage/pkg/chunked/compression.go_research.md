<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compression.go -->
# sources/cloud-native/containers-storage/pkg/chunked/compression.go

Purpose: compatibility facade for chunked compression type constants and deprecated compressor entrypoint.

Important APIs/types/functions: type constants `TypeReg`, `TypeChunk`, `TypeLink`, `TypeChar`, `TypeBlock`, `TypeDir`, `TypeFifo`, `TypeSymlink`; deprecated `ZstdCompressor`.

Control flow: constants alias minimal metadata type strings. `ZstdCompressor` delegates to `pkg/chunked/compressor.ZstdCompressor`.

State/persistence: none.

Dependencies/integration: preserves public API compatibility for callers that imported `pkg/chunked` before the compressor moved to `pkg/chunked/compressor`.

Risks/test signal: removing or changing aliases would break external callers. No direct tests in this subset target this thin wrapper.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compression.go -->
