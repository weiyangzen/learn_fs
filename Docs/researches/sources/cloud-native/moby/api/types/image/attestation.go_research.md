<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/image/attestation.go -->
# sources/cloud-native/moby/api/types/image/attestation.go

## Purpose
AttestationStatement is a single in-toto statement attached to an image.

## Important APIs, Types, And Functions
- Exported types: AttestationStatement.
- `AttestationStatement` fields include Descriptor, PredicateType, Statement.
- Wire JSON fields include Descriptor, PredicateType, Statement.
- Source comments highlight: AttestationStatement is a single in-toto statement attached to an image.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `encoding/json`, `github.com/opencontainers/image-spec/specs-go/v1`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Uses OCI image-spec descriptors/platform structures, so it participates in registry and content-store interoperability.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- No direct test file is paired with this source; coverage is mostly integration-level through daemon/client API tests and compile-time use by downstream packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/image/attestation.go -->
