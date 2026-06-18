# sources/cloud-native/moby/daemon/libnetwork/ipams/remote/remote_test.go

## Purpose
Tests the remote IPAM plugin adapter against a local HTTP plugin simulation.

## Important APIs, Types, And Functions
- `handle` registers RPC endpoint handlers for `IpamDriver.<method>`.
- `setupPlugin` creates a plugin spec file and activation endpoint around an `httptest.Server`.
- `TestGetCapabilities`, `TestGetCapabilitiesFromLegacyDriver`, `TestGetDefaultAddressSpaces`, and `TestRemoteDriver` cover adapter behavior.

## Control Flow
Tests write temporary plugin specs in Docker's plugin directory, discover the plugin via `plugins.Get`, build a client with `getPluginClient`, then call the allocator. The test plugin decodes JSON request maps and emits expected response maps.

## State And Persistence
The tests mutate the system plugin spec directory (`/etc/docker/plugins` on Unix, ProgramData path on Windows) and clean it afterward. Server state is in-memory.

## Dependencies And Integration Points
Uses `httptest`, Moby `plugins`, and `ipamapi`. This is a relatively integration-style unit test because it exercises plugin discovery and HTTP transport.

## Risks
Writing under `/etc/docker/plugins` can require permissions or conflict in constrained environments. The overlap-loop behavior in `RequestPool` is not deeply tested here.

## Test Signals
Confirms endpoint names, JSON field names, capability conversion, metadata propagation, pool/subpool ID formatting by plugin, default address space strings, preferred address forwarding, and release payload validation.
