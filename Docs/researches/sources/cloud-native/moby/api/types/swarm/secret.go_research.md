<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/secret.go -->
# sources/cloud-native/moby/api/types/swarm/secret.go

## Purpose
Secret represents a secret.

## Important APIs, Types, And Functions
- Exported types: Secret, SecretSpec, SecretReferenceFileTarget, SecretReference, SecretCreateResponse.
- `Secret` fields include ID, Spec.
- `SecretSpec` fields include Data, Driver, Templating.
- `SecretReferenceFileTarget` fields include Name, UID, GID, Mode.
- `SecretReference` fields include File, SecretID, SecretName.
- `SecretCreateResponse` fields include ID.
- Source comments highlight: Secret represents a secret. SecretSpec represents a secret specification from a secret in swarm SecretReferenceFileTarget is a file target in a secret reference

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `os`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- Package-level tests include `network_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/secret.go -->
