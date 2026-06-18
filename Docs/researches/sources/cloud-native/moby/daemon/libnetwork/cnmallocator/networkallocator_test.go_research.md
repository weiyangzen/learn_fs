<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/networkallocator_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/cnmallocator/networkallocator_test.go

## Purpose
Unit tests for the CNM Swarm network allocator's network, service, task, and IPAM option behavior.

## Important APIs, Types, And Functions
`newNetworkAllocator` constructs a provider allocator. Tests cover invalid IPAM/driver names, double allocation, empty config default pool determinism, explicit subnet/gateway allocation, invalid gateways, `/32` support, multiple subnets, deallocation/reallocation, task address allocation/free, service VIP allocation, ingress VIP handling, service network updates, and custom `mockIpam`.

## Control Flow
Tests construct SwarmKit `api.Network`, `api.Task`, and `api.Service` objects, call allocator methods, and assert mutations to `IPAM.Configs`, `Gateway`, `Addresses`, `Endpoint.VirtualIPs`, and allocation predicates.

## State And Persistence
All state is in-memory. Some tests create two allocator instances to assert deterministic allocation order from identical inputs.

## Dependencies And Integration Points
Uses libnetwork default IPAM, SwarmKit API types, SwarmKit allocator interfaces, and `gotest.tools` assertions.

## Risks And Edge Cases
The tests mostly assert success/error presence rather than exact error types. They do not exercise concurrent allocation, remote plugins, release failure behavior, or node attachment allocation deeply. The mock IPAM's `RequestAddress` returns nil values, limiting coverage to pool option propagation.

## Test Signals
Passing tests strongly signal stable allocator mutation semantics and compatibility with SwarmKit service/task/network allocation flows.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/networkallocator_test.go -->
