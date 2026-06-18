# sources/cloud-native/moby/daemon/cluster/convert/netextra/extra.pb.go

## Purpose
Generated gogo/protobuf implementation for network inspection extension messages carrying options and IPAM status data between Docker and swarmkit.

## Important APIs, Types, And Functions
Defines generated message types `GetNetworkExtraOptions`, `Extra`, and `IPAMStatus`, getters, `Reset/String/ProtoMessage/Descriptor`, marshal/unmarshal/size helpers, `skipExtra`, and generated error variables.

## Control Flow
Marshal methods write fields in reverse into sized buffers. Unmarshal methods parse protobuf wire types, append repeated `IPAMStatus` entries, copy subnet bytes, skip unknown fields for forward compatibility, and detect overflow/negative length/unexpected EOF.

## State And Persistence
No process state, but this file defines the wire format persisted or transported inside protobuf `Any` values. `IPAMStatus.Subnet` stores `netip.Prefix` binary bytes as defined by `network_extra.go`.

## Dependencies And Integration Points
Generated from `extra.proto`; used by `netextra.OptionsFrom`, `StatusFrom`, and `MarshalStatus`. Registered type names are under `docker.engine.netextra`.

## Risks And Test Signals
Manual edits would be overwritten by protoc. Compatibility depends on stable field numbers. There are no direct tests in this subset; conversion tests should exercise `Any` marshaling and unknown-type behavior.
