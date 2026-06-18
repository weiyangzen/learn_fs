<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/driverapi/ipamdata.go -->
# sources/cloud-native/moby/daemon/libnetwork/driverapi/ipamdata.go

## Purpose
Implements serialization, validation, string rendering, and API conversion for `driverapi.IPAMData`.

## Important APIs, Types, And Functions
`MarshalJSON`, `UnmarshalJSON`, `Validate`, `IsV6`, `String`, and `IPAMConfig` convert between internal `net.IPNet` data, JSON strings, and public `network.IPAMConfig` using `netip` addresses.

## Control Flow
Marshal omits nil fields and stringifies networks. Unmarshal decodes a map, parses CIDR strings, and rebuilds aux address maps. Validate requires pool and gateway, checks gateway/aux address IP versions match the pool, and ensures gateway/aux addresses belong to the pool. `IPAMConfig` converts pool/gateway/aux data to API netip form.

## State And Persistence
Pure value transformations; no persistent state.

## Dependencies And Integration Points
Used by driver API JSON exchange, network inspect output conversion, and tests in `driverapi_test.go`.

## Risks And Edge Cases
`UnmarshalJSON` uses unchecked type assertions for expected JSON field types, so malformed input can panic. The validation error for aux address outside pool formats the gateway instead of the offending aux address in one message.

## Test Signals
Round-trip, validation, and API conversion tests are the key signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/driverapi/ipamdata.go -->
