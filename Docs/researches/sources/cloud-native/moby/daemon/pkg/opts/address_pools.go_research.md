<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/address_pools.go -->
# sources/cloud-native/moby/daemon/pkg/opts/address_pools.go

## Purpose
Implements a flag/JSON value for daemon default address pools used by libnetwork IPAM.

## Important APIs, Types, And Functions
`PoolsOpt` holds `[]*ipamutils.NetworkToSplit`. `UnmarshalJSON` decodes directly into `Values`. `Set` parses CSV fields with keys `base` and `size`; `Type`, `String`, `Value`, and `Name` support flag/config plumbing.

## Control Flow
`Set` reads one CSV record, lowercases each field, splits on `=`, parses `base` as `netip.Prefix` and `size` as integer, rejects unknown keys, and appends a `NetworkToSplit`.

## State, Dependencies, And Integration Points
State is in-memory `Values`. It depends on `encoding/csv`, `net/netip`, and daemon libnetwork `ipamutils`. The daemon config layer consumes the parsed pools.

## Risks And Test Signals
Case-insensitive keys are a documented TODO. `Set` permits missing base or size until later consumers validate semantics. The test covers one valid definition and an invalid combined string.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/address_pools.go -->
