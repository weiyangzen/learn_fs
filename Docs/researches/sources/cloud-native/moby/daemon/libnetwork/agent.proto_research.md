# sources/cloud-native/moby/daemon/libnetwork/agent.proto

## Purpose
Defines the protobuf schema for endpoint records and ingress port configs gossiped between libnetwork cluster nodes.

## Important APIs, Types, And Functions
`EndpointRecord` carries endpoint name, service name/id, virtual IP, endpoint IP, ingress ports, service aliases, task aliases, and `service_disabled`. `PortConfig` carries port name, protocol enum, target port, and published port. Gogo options request custom names, marshalers, unmarshalers, stringers, sizers, and GoString methods.

## Control Flow
There is no executable flow in the schema. Generated code serializes these fields into NetworkDB values consumed by `agent.go`.

## State And Persistence
The schema defines persistent/gossiped NetworkDB value layout. Field numbers are the compatibility contract across nodes and versions.

## Dependencies And Integration Points
Imported by protoc with `gogoproto`. `EndpointRecord` is stored in `endpoint_table`; `PortConfig` ingress data is used for service binding and diagnostics.

## Risks And Test Signals
Changing field numbers or semantics can break mixed-version clusters. `service_disabled` is treated specially by event logic as a state toggle that may not change endpoint equivalence. Tests cover generated records through event transition handling.
