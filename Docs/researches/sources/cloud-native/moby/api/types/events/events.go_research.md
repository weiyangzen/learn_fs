<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/events/events.go -->
# sources/cloud-native/moby/api/types/events/events.go

## Purpose
Defines Docker event stream types, actions, actors, and message payloads.

## Important APIs, Types, And Functions
- Exported types: Type, Action, Actor, Message.
- Constants: BuilderEventType, ConfigEventType, ContainerEventType, DaemonEventType, ImageEventType, NetworkEventType, NodeEventType, PluginEventType, SecretEventType, ServiceEventType, VolumeEventType, ActionCreate, ActionStart, ActionRestart, ActionStop, ActionCheckpoint, and others.
- `Actor` fields include ID, Attributes.
- `Message` fields include Type, Action, Actor, Scope, Time, TimeNano.
- Wire JSON fields include scope, time, timeNano.
- Source comments highlight: Type is used for event-types. Action is used for event-actions. Actor describes something that generates events, like a container, or a network, or a volume.
- The constants provide the canonical vocabulary for daemon event publication and client-side filtering.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.

## Dependencies And Integration Points
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- No direct test file is paired with this source; coverage is mostly integration-level through daemon/client API tests and compile-time use by downstream packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/events/events.go -->
