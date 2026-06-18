# sources/cloud-native/moby/daemon/libnetwork/netutils/utils_linux_test.go

## Purpose
Linux unit/integration tests for `netutils` random name, resolver parsing, MAC generation, and host-reserved network inference.

## Important APIs, Types, And Functions
`TestGenerateRandomName` checks invalid and valid lengths plus duplicate avoidance across 16 samples. `TestGetNameserversAsPrefix` validates parsing comments, search lines, IPv4, IPv6, and scoped IPv6 nameservers. `TestUtilGenerateRandomMAC` checks two generated MACs differ. `TestInferReservedNetworksV4`, `createInterface`, and `addRoute` verify link-scope route inclusion.

## Control Flow
The reserved-network test creates a dummy interface in an isolated namespace, adds two link-scope routes and one universe-scope route, then asserts only link-scope prefixes are present. Resolver parsing tests call the unexported helper directly with in-memory config strings.

## State And Persistence
Netlink state is created inside a test OS context and torn down by test utilities. Other tests use only in-memory values.

## Dependencies And Integration Points
Depends on `netnsutils`, vishvananda netlink, `netiputil`, and `gotest.tools`. It protects the behavior relied on by IPAM subnet exclusion.

## Risks
Tests that touch netlink require suitable privileges/capabilities in the test environment. Random uniqueness checks are probabilistic but low-risk at the sample size used.

## Test Signals
Strong signals for parsing edge cases and route-scope semantics; no direct test for `GenerateIfaceName` collision retry behavior in this file.
