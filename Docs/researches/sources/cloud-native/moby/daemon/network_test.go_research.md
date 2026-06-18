# sources/cloud-native/moby/daemon/network_test.go

## Purpose
This file tests validation of network IPAM configuration.

## Important APIs, Types, And Functions
`TestValidateIPAM` calls unexported `validateIpamConfig` with table-driven `network.IPAMConfig` inputs and expected error substrings.

## Control Flow
Each subtest runs in parallel, calls validation with IPv6 enabled/disabled flags, expects nil for valid cases, or asserts the joined error contains `invalid network config` and each detailed expected error.

## State, Persistence, And Dependencies
No persistent state. Dependencies include `net/netip`, Docker API network types, and gotest assertions.

## Integration Points
The tests protect `CreateNetwork` validation behavior for IPv4/IPv6 IPAM input supplied through Docker API/CLI.

## Risks And Edge Cases
Tests include IPv6 subnet ignored when IPv6 is disabled for upgrade compatibility, mismatched address families, IP ranges larger than subnets, host bits in subnet/IP range, out-of-range gateways/aux addresses, empty IPAM, and a valid case.

## Test Signals
Strong focused signal for IPAM validation error messages and multierror aggregation; it does not cover conversion into libnetwork IPAM config.
