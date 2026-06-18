# sources/cloud-native/moby/daemon/libnetwork/libnetwork_linux_test.go

## Purpose
Linux-only integration and behavior tests for libnetwork controller, network, endpoint, sandbox, plugin, bridge, host/null, DNS, namespace, and IPAM paths. The suite uses temporary controller data dirs plus isolated test network namespaces to exercise real Linux plumbing without sharing host state.

## Important APIs, Types, And Functions
`newController` constructs a controller with bridge configuration and default local address pools. `createTestNetwork`, `getEmptyGenericOption`, and `getPortMapping` are common helpers. Tests cover `Controller.NewNetwork`, `NewSandbox`, `Network.CreateEndpoint`, endpoint `Join`, `Leave`, `Delete`, `Network.Delete`, lookup APIs, driver plugin discovery, sandbox `SetKey`, and bridge driver operational data. `parallelTester` drives concurrent join/leave loops across host and bridge endpoints.

## Control Flow
Most tests create a controller, create one or more networks, add endpoints, optionally join endpoints into sandboxes, assert state/error behavior, then clean up with deferred deletes. Config-network tests first validate forbidden combinations, then verify config-only networks cannot be deleted while referenced. Remote-driver tests stand up an HTTP plugin mock and write plugin specs under the platform-specific plugin path. `TestExternalKey` optionally exercises the reexec helper path for setting a sandbox namespace key. `TestParallel` switches OS namespace context per goroutine and repeatedly joins/leaves endpoints to stress locking.

## State And Persistence
The tests rely on controller data dirs created by `t.TempDir` and on libnetwork datastore persistence through network/endpoint creation and deletion. Network namespace state is isolated by `netnsutils.SetupTestOSContext`. `TestResolvConf` writes origin and target `resolv.conf` files and verifies generated resolver content and file mode. Remote plugin tests mutate `specPath` and remove it after execution.

## Dependencies And Integration Points
The file integrates with the bridge, null IPAM, default IPAM, plugin registry, netlink namespace helpers, reexec, and containerd errdefs. It depends on Linux netns/netlink availability, IPv6 listenability, and bridge driver behavior.

## Risks
The tests are environment-sensitive: they require namespace operations and may depend on kernel IPv6 support, plugin spec filesystem permissions, and cleanup order. Several assertions note TODOs around error classification. Parallel join/leave tests can expose race regressions in controller, endpoint, or sandbox locking.

## Test Signals
Strong coverage exists for invalid names, duplicate endpoints, active endpoint/container protection, config-only/config-from constraints, host/null special drivers, bridge port mapping, DNS file generation, external namespace key handoff, plugin implementation validation, and null IPAM failures.
