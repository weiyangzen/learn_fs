# sources/cloud-native/buildkit/exporter/verifier/platforms.go

Purpose: validates that the platforms requested by the frontend match the platforms actually represented in an export result, returning BuildKit vertex warnings rather than mutating results.

Important APIs: `CheckInvalidPlatforms` is the verifier entry point; `platformsString` formats deterministic sorted platform lists.

Control flow: request options are loaded from result metadata. A result with multiple refs must have platform metadata; empty results are ignored. Requested platforms are parsed, normalized, and checked for invalid or duplicate entries. Single requested/single produced platform gets special OSVersion tolerance. Multi-platform mismatches compare normalized sets and warn on cardinality or value differences; multiple requested platforms with a non-map result warn separately.

State and persistence: no mutation except local warning construction.

Dependencies and integration: depends on `exptypes.ParsePlatforms`, `client.VertexWarning`, and request metadata from `opts.go`.

Risks and test signals: risks include nil request metadata assumptions, OSVersion comparison edge cases, and warnings after invalid parse still appending a zero platform. Exporter/platform integration tests should exercise this.
