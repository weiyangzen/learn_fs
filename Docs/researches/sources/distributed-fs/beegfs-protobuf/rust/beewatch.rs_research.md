# Research: sources/distributed-fs/beegfs-protobuf/rust/beewatch.rs

## Purpose

`beewatch.rs` is generated Rust code for the BeeGFS Watch subscriber protobuf service. It models filesystem event delivery from BeeGFS Watch and the acknowledgement/shutdown responses sent by subscribers. The module supports both legacy v1 events and newer v2 events inside a common event envelope.

## Important APIs, Types, and Functions

`Event` is the top-level message. It carries `seq_id`, metadata node id, optional mirror id, an event flags bitmask, and a oneof `EventData` containing either `V1Event` or `V2Event`. `V1Event` includes event type, dropped/missed sequence counters, path, entry id, parent entry id, target path, and target parent id. `V2Event` includes event type, link count, path and id fields, message user id, and timestamp.

`Response` contains `completed_seq` and `shutting_down`, allowing subscribers to acknowledge progress and request graceful shutdown. The generated `subscriber_client::SubscriberClient` exposes `receive_events`, a bidirectional streaming RPC where the request stream contains `Event` messages and the response stream contains `Response` messages. The generated `subscriber_server::Subscriber` trait defines the server implementation surface.

## Control Flow and State Behavior

The client converts an input stream into a tonic streaming request, sets the gRPC method extension for `beewatch.Subscriber/ReceiveEvents`, and opens a streaming RPC. The server dispatch path wraps the implementor in a `StreamingService<Event>`, producing a response stream of acknowledgements. There is no persistence in the generated code; sequence tracking is represented by `seq_id` on events and `completed_seq` in responses.

The comments describe compatibility intent: minor API updates should be additive and not change existing field meaning. V1 is the legacy BeeGFS v7 format; V2 was introduced in BeeGFS v8 and extends event coverage with open/write/lock/stripe events and timestamps.

## Dependencies and Integration Points

This module depends on tonic/prost generated runtime types and integrates with BeeGFS metadata/watch services and subscribers that consume filesystem change events. Event flags refer to constants in BeeGFS `EventContext.h`, so consumers need out-of-band knowledge to interpret the bitmask.

## Risks and Edge Cases

The event envelope has no minor-version field, so compatibility relies on protobuf additive-change discipline. Unknown enum values and absent oneof event data must be handled defensively. Sequence gaps, dropped/missed counters, mirrored metadata nodes, and graceful shutdown all require protocol-level handling outside this generated file. The event flags are an untyped `u32`, making incorrect bit interpretation possible if producer and consumer constants drift.

## Test Signals

Tests should include streaming client/server interoperability, v1 and v2 event round trips, unknown event-type behavior, ack sequence progression, shutdown signalling, and simulated gaps or dropped sequence counters. Integration tests should confirm consumers correctly interpret event flags against the BeeGFS native constants.
