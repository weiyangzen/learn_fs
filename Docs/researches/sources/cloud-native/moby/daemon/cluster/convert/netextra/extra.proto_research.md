# sources/cloud-native/moby/daemon/cluster/convert/netextra/extra.proto

## Purpose
Declares the protobuf schema for Docker network extra request options and status payloads.

## Important APIs, Types, And Functions
Defines package `docker.engine.netextra`, Go package `netextra`, messages `GetNetworkExtraOptions`, `Extra`, and `IPAMStatus`, and a `go:generate` path in the companion Go file.

## Control Flow
No executable control flow. Field numbers assign `WithIPAMStatus = 1`, repeated `IPAMStatus = 1`, and IPAM status fields `Subnet = 1`, `IPsInUse = 2`, `DynamicIPsAvailable = 3`.

## State And Persistence
This schema is the persistent/wire contract for network extra `Any` payloads. `Subnet` is documented as a binary-marshaled `netip.Prefix`.

## Dependencies And Integration Points
Source for `extra.pb.go` and consumed by `network_extra.go`.

## Risks And Test Signals
Changing field numbers or package/type names breaks compatibility with stored or transported `Any` values. Regeneration consistency is the main validation signal.
