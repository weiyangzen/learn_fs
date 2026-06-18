<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/runtime.go -->
# sources/cloud-native/moby/api/types/swarm/runtime.go

## Purpose
RuntimeType is the type of runtime used for the TaskSpec

## Important APIs, Types, And Functions
- Exported types: RuntimeType, RuntimeURL, NetworkAttachmentSpec, RuntimeSpec, RuntimePrivilege.
- Constants: RuntimeContainer, RuntimePlugin, RuntimeNetworkAttachment, RuntimeURLContainer, RuntimeURLPlugin.
- `NetworkAttachmentSpec` fields include ContainerID.
- `RuntimeSpec` fields include Name, Remote, Privileges, Disabled, Env.
- `RuntimePrivilege` fields include Name, Description, Value.
- Wire JSON fields include description, disabled, env, name, privileges, remote, value.
- Source comments highlight: RuntimeType is the type of runtime used for the TaskSpec RuntimeURL is the proto type url NetworkAttachmentSpec represents the runtime spec type for network attachment tasks

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- Package-level tests include `network_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/swarm/runtime.go -->
