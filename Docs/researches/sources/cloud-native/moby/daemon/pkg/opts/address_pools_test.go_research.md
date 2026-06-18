<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/address_pools_test.go -->
# sources/cloud-native/moby/daemon/pkg/opts/address_pools_test.go

## Purpose
Exercises basic `PoolsOpt.Set` behavior for daemon default address-pool flag input.

## Important APIs, Types, And Functions
`TestAddressPoolOpt` instantiates `PoolsOpt`, calls `Set` with `base=175.30.0.0/16,size=16`, then verifies a malformed multi-pool string returns an error.

## Control Flow
The test fails immediately on unexpected error from valid input and fails if invalid input is accepted.

## State, Dependencies, And Integration Points
No external state. It targets the address-pool parser used by daemon config and libnetwork setup.

## Risks And Test Signals
Coverage is shallow: it does not inspect parsed `Base`/`Size`, JSON decoding, missing keys, unknown keys, IPv6, or String/Value output. Its signal is mainly that CSV parsing rejects a common malformed comma-separated pair sequence.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/address_pools_test.go -->
