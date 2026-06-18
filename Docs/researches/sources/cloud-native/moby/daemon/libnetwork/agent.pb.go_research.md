# sources/cloud-native/moby/daemon/libnetwork/agent.pb.go

## Purpose
Generated gogo/protobuf implementation for `agent.proto`, defining the wire-compatible Go types and serialization code used in libnetwork gossip tables.

## Important APIs, Types, And Functions
Defines `PortConfig_Protocol` enum values `ProtocolTCP`, `ProtocolUDP`, and `ProtocolSCTP`; message structs `EndpointRecord` and `PortConfig`; getters; registration; `Marshal`, `MarshalTo`, `MarshalToSizedBuffer`, `Size`, `String`, `GoString`, and `Unmarshal` methods; varint helpers; unknown-field skipping; and generated errors for invalid lengths, integer overflow, and unexpected groups.

## Control Flow
Marshal methods write fields in reverse into sized buffers, omitting zero values. Unmarshal loops over wire fields, validates wire types and lengths, appends repeated fields, skips unknown fields, and returns EOF/overflow/length errors for malformed input.

## State And Persistence
No runtime state beyond message values. Serialized bytes are persisted or propagated through NetworkDB endpoint tables.

## Dependencies And Integration Points
Generated from `agent.proto` with gogo options and used by `agent.go`, diagnostics, tests, and any NetworkDB peers expecting the same schema.

## Risks And Test Signals
Manual edits would be overwritten by generation. Schema field numbers are compatibility-critical. Tests indirectly exercise marshal/unmarshal through `agent_test.go` and diagnostic decoding.
