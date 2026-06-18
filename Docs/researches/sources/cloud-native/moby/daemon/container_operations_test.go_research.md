# sources/cloud-native/moby/daemon/container_operations_test.go

## Purpose
Tests focused pure functions in container networking: DNS name ordering for endpoints, static IP range validation, and endpoint IPAM normalization/validation.

## Important APIs, Types, And Functions
- `TestDNSNamesOrder` drives `updateNetworkConfig` and expects container name, alias, truncated ID, and hostname order.
- `buildNetwork` constructs a libnetwork `Network` from JSON test config.
- `TestEndpointIPAMInfoWithOutOfRangeAddrs` validates static addresses against libnetwork IPAM pools.
- `TestEndpointIPAMConfigWithInvalidConfig` validates malformed IPv4/IPv6/link-local addresses and unmapped normalization.

## Control Flow
Tests build small network and endpoint objects in memory, call the production validation/config functions, then compare returned error strings and mutated `EndpointSettings` fields. Error cases join multiple validation errors and assert each expected substring is present.

## State And Persistence
No persistent daemon state is used. The IPAM normalization test mutates the supplied endpoint config in place, mirroring production behavior.

## Dependencies And Integration Points
Uses API container/network types, libnetwork network JSON unmarshalling, driver IPAM data, and `gotest.tools`. It directly guards helper behavior used by `connectToNetwork` and `updateNetworkConfig`.

## Risks And Edge Cases
The tests do not instantiate real sandboxes, so they do not cover endpoint create/join rollback or checkpointing. Error-string assertions can be brittle if wording changes while semantics remain correct.

## Test Signals
Failures indicate DNS records may be generated in an order that breaks PTR assumptions, static IPs may be accepted outside subnets, or invalid IP forms may leak into endpoint settings.
