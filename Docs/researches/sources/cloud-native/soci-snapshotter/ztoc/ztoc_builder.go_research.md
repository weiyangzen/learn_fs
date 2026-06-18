# sources/cloud-native/soci-snapshotter/ztoc/ztoc_builder.go

## Purpose
`ztoc_builder.go` composes TOC building and zinfo building into a complete zTOC builder with default support for gzip and uncompressed tar.

## Important APIs, Types, and Functions
`Builder` stores a `TocBuilder`, per-algorithm `ZinfoBuilder` map, and build tool identifier. `NewBuilder` registers gzip, uncompressed, and unknown/tar handling. `WithCompression` configures build algorithm, `defaultBuildConfig` defaults to gzip, `BuildZtoc` creates a full zTOC, `RegisterCompressionAlgorithm` adds extensibility, and `CheckCompressionAlgorithm` verifies both TOC and zinfo support.

## Control Flow, State, and Persistence
`BuildZtoc` validates filename, applies options, checks algorithm support, builds compression info first, builds TOC second, and returns a populated `Ztoc` with version `0.9`. Builder state is in-memory registration maps; output state is the zTOC struct that can later be marshaled.

## Dependencies and Integration Points
It depends on the compression package and the local TOC/zinfo builder types. It is used in tests and any SOCI zTOC creation path.

## Risks and Test Signals
The unsupported compression error message says supported gzip even though uncompressed is also registered. Unknown is registered with tar providers/builders, so callers can build unknown as uncompressed-like data. Tests exercise default and explicit compression through ztoc generation suites.
