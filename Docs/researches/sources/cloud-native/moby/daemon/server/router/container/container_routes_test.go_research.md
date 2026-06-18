# sources/cloud-native/moby/daemon/server/router/container/container_routes_test.go

## Purpose
This test file validates backward-compatibility helpers used by the container create/update HTTP routes, especially fields whose wire behavior changed across Docker API versions.

## Important APIs, Types, And Functions
The tests exercise `handleMACAddressBC`, `epConfigForNetMode`, `rejectLegacyCapabilities`, and `handleSysctlBC`. They construct `container.HostConfig`, `network.NetworkingConfig`, and endpoint maps, then assert warnings, errors, migrated endpoint settings, and retained/deleted host sysctls.

## Control Flow
Each table-driven test mutates request-like config objects through the compatibility helper under test. MAC tests cover old container-wide MAC migration, endpoint-specific MAC conflicts, no-network conflicts, and API 1.52 rejection. Network-mode tests verify endpoint selection rules before and after API 1.44. Sysctl tests migrate `net.ipv6.conf.eth0.*` settings into `netlabel.EndpointSysctls` for supported API versions and reject unsupported placement for newer ones.

## State And Persistence
No daemon state is persisted. The tests verify in-memory mutation of request structs before those structs are handed to daemon creation logic.

## Dependencies And Integration Points
The tests depend on API container/network types, `netlabel.EndpointSysctls`, `maps.Copy`, and `gotest.tools` assertions. They protect behavior in `container_routes.go`, which is outside this work item but directly adjacent to the listed router files.

## Risks
The main risk is compatibility drift: changing request normalization can silently break old clients, reject valid legacy inputs, or accept fields that newer APIs should reject.

## Test Signals
The file is itself the test signal for container-router compatibility lanes around MAC address, endpoint identity, legacy `Capabilities`, and per-interface sysctls.
