# sources/cloud-native/moby/daemon/cluster/convert/netextra/network_extra.go

## Purpose
Converts Docker network extra options and status between API structs and protobuf `Any` messages, with forward-compatible unknown-type handling.

## Important APIs, Types, And Functions
Exports `OptionsFrom`, `StatusFrom`, and `MarshalStatus`.

## Control Flow
`OptionsFrom` returns zero options for empty or unknown type URLs, otherwise unmarshals `GetNetworkExtraOptions`. `StatusFrom` ignores nil or unknown `Any`, unmarshals `Extra`, converts binary subnet prefixes to `netip.Prefix`, and fills `network.Status.IPAM.Subnets`. `MarshalStatus` converts each subnet prefix to binary and marshals an `Extra` message into `Any`.

## State And Persistence
No local state. It serializes IPAM status maps into protobuf payloads; map iteration means marshaled order is not deterministic unless the protobuf layer enforces it.

## Dependencies And Integration Points
Used by network inspection conversion in `network.go`. Depends on gogo `types.Any`, generated netextra messages, `netip`, and Docker network status types.

## Risks And Test Signals
Invalid subnet binary data returns errors on inspect conversion. Unknown message types are silently ignored for compatibility. No direct tests here; network inspect tests should include status payloads.
