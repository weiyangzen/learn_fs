<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/common.go -->
# sources/cloud-native/moby/api/types/swarm/common.go

## Purpose
Version represents the internal object version.

## Important APIs, Types, And Functions
- Exported types: Version, Meta, Annotations, Driver, TLSInfo.
- Exported functions/methods: String.
- `Version` fields include Index.
- `Meta` fields include Version, CreatedAt, UpdatedAt.
- `Annotations` fields include Name, Labels.
- `Driver` fields include Name, Options.
- `TLSInfo` fields include TrustRoot, CertIssuerSubject, CertIssuerPublicKey.
- Wire JSON fields include Labels.
- Source comments highlight: Version represents the internal object version. Meta is a base object inherited by most of the other once. Annotations represents how to describe an object.

## Control Flow
- Runtime behavior is limited to helper methods such as validators, stringers, comparison functions, sort methods, or error adapters.
- String/error methods expose compact human-readable representations without mutating receiver state.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `strconv`, `time`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Carries timestamp or duration fields that must remain JSON-compatible across daemon/client boundaries.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.
- Duration and timestamp fields need stable units and timezone/zero-value behavior across API versions.

## Test Signals
- Package-level tests include `network_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/common.go -->
