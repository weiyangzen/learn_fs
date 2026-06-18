# sources/cloud-native/moby/daemon/libnetwork/ipbits/ipbits_test.go

## Purpose
Tests IP address arithmetic helpers used by IPAM allocation logic.

## Important APIs, Types, And Functions
- `TestAdd` validates IPv4 and IPv6 shifted additions.
- `BenchmarkAdd` measures IPv4/IPv6 add performance.
- `TestField` verifies bitfield extraction across byte and wider boundaries.
- `TestSubnetsBetween` validates subnet counts for IPv4 and IPv6 gaps.

## Control Flow
Table-driven tests compare pure function outputs against known addresses or integer values.

## State And Persistence
No state.

## Dependencies And Integration Points
Uses `netip` and `gotest.tools`. The expected values mirror default IPAM gap-detection needs.

## Risks
Tests do not cover invalid argument behavior for `Field`, which is explicitly undefined. Overflow behavior is not asserted.

## Test Signals
Confirms IPv6 128-bit arithmetic works for high-bit shifts and large subnet counts such as `/64` gaps.
