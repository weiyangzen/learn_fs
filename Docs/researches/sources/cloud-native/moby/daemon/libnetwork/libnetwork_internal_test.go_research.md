# sources/cloud-native/moby/daemon/libnetwork/libnetwork_internal_test.go

## Purpose
Provides internal libnetwork tests for JSON persistence, IPAM cleanup, service DNS records, endpoint labels, auxiliary address validation, SRV lookup, and failure rollback behavior.

## Important APIs, Types, And Functions
- `TestNetworkMarshalling` and `TestEndpointMarshalling` validate JSON round-trip of private network/endpoint fields.
- Comparison helpers check IPAM configs, IPAM info, endpoint interfaces, maps, and address lists.
- `TestAuxAddresses` validates aux-address ranges during `ipamAllocate`.
- `TestEndpointNameLabel` checks endpoint name is included in IPAM options.
- `TestUpdateSvcRecord`, `getSvcRecords`, `TestSRVServiceQuery`, and `TestServiceVIPReuse` cover service DNS record maps and resolver behavior.
- `TestIpamReleaseOnNetDriverFailures` verifies IPAM allocations are released after network or endpoint driver failures.
- `badDriver` simulates network driver failures.

## Control Flow
Tests create controllers with temp data directories and isolated network namespaces where needed, create networks/endpoints/sandboxes, mutate service records, resolve names/IPs/services, and assert expected cleanup. The bad driver first fails network creation, then endpoint creation, to verify different rollback paths.

## State And Persistence
Marshalling tests exercise JSON persistence of network/endpoint structs. Other tests create temporary controller state and modify in-memory service maps. Network namespace and bridge setup are external OS state isolated by test helpers.

## Dependencies And Integration Points
Integrates default IPAM, bridge driver behavior, service record `setmatrix`, netlabel constants, netutils reverse-IP logic, driver registry, and controller lifecycle.

## Risks
Tests are platform-sensitive and skip Windows for Linux-only bridge/namespace behavior. They rely on cleanup through `defer`; failures can leave transient network state. These tests also exercise private fields, making refactors visible.

## Test Signals
Strong signals include persistence compatibility for private fields, aux-address validation against pools/subpools, endpoint-name metadata reaching IPAM, v4/v6 DNS record add/delete, SRV target resolution, service VIP reference counting by service ID, and IPAM release after driver failures.
