<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/driverapi/driverapi_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/driverapi/driverapi_test.go

## Purpose
Tests `IPAMData` JSON round-trip, validation, and IPv6 detection behavior.

## Important APIs, Types, And Functions
`TestIPDataMarshalling` marshals/unmarshals an `IPAMData` with pool, gateway, and aux addresses. `compareAddresses` compares aux address maps. `TestValidateAndIsV6` checks `IsV6` and validation failures for mismatched IP versions and out-of-pool gateway/aux addresses.

## Control Flow
Tests construct IPv4 and IPv6 CIDRs, mutate fields to invalid states, and expect `Validate` to fail or pass at each step.

## State And Persistence
No state beyond test objects.

## Dependencies And Integration Points
Exercises `types.ParseCIDR`, `types.CompareIPNet`, JSON methods in `ipamdata.go`, and driver API validation semantics used by drivers.

## Risks And Edge Cases
Coverage does not check nil pool/gateway error messages, JSON type assertion panics on malformed JSON, or `IPAMConfig` conversion.

## Test Signals
Passing tests show stable IPAMData serialization and validation for the main IPv4/IPv6 congruence cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/driverapi/driverapi_test.go -->
