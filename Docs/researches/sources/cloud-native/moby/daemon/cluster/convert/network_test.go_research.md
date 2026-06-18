# sources/cloud-native/moby/daemon/cluster/convert/network_test.go

## Purpose
Tests that `BasicNetworkFromGRPC` preserves the swarmkit network creation timestamp in the Docker API network type.

## Important APIs, Types, And Functions
Defines `TestNetworkConvertBasicNetworkFromGRPCCreatedAt`.

## Control Flow
The test parses a fixed timestamp, converts it to protobuf timestamp form, embeds it in a minimal `swarmapi.Network`, converts with `BasicNetworkFromGRPC`, and compares `Created`.

## State And Persistence
No persistent state.

## Dependencies And Integration Points
Covers timestamp conversion in `network.go` using gogo protobuf timestamp helpers.

## Risks And Test Signals
Coverage is narrow and does not exercise IPAM, status extras, ports, or create conversion. Failure indicates metadata timestamp drift in network inspect/list output.
