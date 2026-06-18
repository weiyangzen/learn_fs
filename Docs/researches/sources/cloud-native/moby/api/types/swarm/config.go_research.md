<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/config.go -->
# sources/cloud-native/moby/api/types/swarm/config.go

## Purpose
Config represents a config.

## Important APIs, Types, And Functions
- Exported types: Config, ConfigSpec, ConfigReferenceFileTarget, ConfigReferenceRuntimeTarget, ConfigReference, ConfigCreateResponse.
- `Config` fields include ID, Spec.
- `ConfigSpec` fields include Data, Templating.
- `ConfigReferenceFileTarget` fields include Name, UID, GID, Mode.
- `ConfigReferenceRuntimeTarget` fields include File, Runtime, ConfigID, ConfigName.
- `ConfigCreateResponse` fields include ID.
- Source comments highlight: Config represents a config. ConfigSpec represents a config specification from a config in swarm ConfigReferenceFileTarget is a file target in a config reference

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
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/config.go -->
