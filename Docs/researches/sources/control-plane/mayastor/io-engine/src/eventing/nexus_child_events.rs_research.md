# sources/control-plane/mayastor/io-engine/src/eventing/nexus_child_events.rs

## Purpose
Generates nexus child add/remove event messages from gRPC request types.

## Important APIs, Types, and Functions
- Implements `Event` for `AddChildNexusRequest`.
- Implements `Event` for `RemoveChildNexusRequest`.
- Both use `with_nexus_child_data(&self.uri)` metadata.

## Control Flow and State
When an add or remove child request is accepted, callers can emit an event with the request object. The event category is `Nexus`, target is the nexus UUID from the request, and metadata identifies the child URI and node name.

No state is persisted here.

## Dependencies and Integration Points
Depends on `io_engine_api::v1::nexus` request types, `events_api`, and `MayastorEnvironment`. Integrated into nexus gRPC request handling.

## Risks and Test Signals
Events are based on request data rather than post-operation object state, so they may include the requested URI even if later normalization occurs elsewhere. Tests should assert add/remove parity, target UUID, and URI metadata.
