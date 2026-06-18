# sources/cloud-native/moby/daemon/libnetwork/agent_test.go

## Purpose
Tests the high-risk endpoint event logic in libnetwork agent gossip handling.

## Important APIs, Types, And Functions
`TestEndpointEvent_EquivalentTo` validates semantic equality rules for endpoint events, including unordered ingress ports and aliases while ignoring `ServiceDisabled`. `mockServiceBinder` records binding actions. `TestHandleEPTableEvent` builds `networkdb.WatchEvent` values with marshaled previous/current `EndpointRecord` data and asserts expected add/remove operations.

## Control Flow
Transition cases cover insert, update, delete, and replace for service endpoints and attachable-network containers with `ServiceDisabled` true/false combinations. Service transitions use `addServiceBinding` or `rmServiceBinding`; container transitions use add/delete name resolution.

## State And Persistence
All state is in memory. Protobuf marshal/unmarshal is exercised for event payloads.

## Dependencies And Integration Points
Uses `gogo/protobuf`, NetworkDB watch events, and `gotest.tools` assertions. It isolates agent event logic behind the `serviceBinder` interface.

## Risks And Test Signals
The tests do not start real NetworkDB or drivers. Their strong signal is preventing DNS/LB flapping and ensuring disabled endpoints remove bindings without fully deleting service records unless appropriate.
