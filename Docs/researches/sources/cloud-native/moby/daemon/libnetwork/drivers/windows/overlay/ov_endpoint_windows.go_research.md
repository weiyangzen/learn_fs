# sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/ov_endpoint_windows.go

Purpose: Implements Windows overlay endpoint create/delete and operational info through HNS endpoint APIs and Windows port allocation/policy helpers.

Important APIs and types: `endpoint` stores id, network id, HNS profile id, remote flag, MAC, IP, gateway-disable flag, and port mappings. State helpers manage the network endpoint map and stale endpoint removal. `CreateEndpoint` validates ids, deletes stale same-id HNS endpoint, validates IP/subnet, parses DNS and endpoint connectivity options, allocates host ports, constructs an `hcsshim.HNSEndpoint` with PA, outbound NAT, and port-binding policies, posts it to HNS, records profile/MAC/port policy state, and adds runtime endpoint. `DeleteEndpoint` releases ports, removes runtime endpoint, and deletes HNS endpoint. `EndpointOperInfo` returns HNS id, DNS flag, and copied port mappings.

Control flow: port allocation is rolled back via defer if creation fails before success. If HNS returns a generated MAC, it is propagated to `InterfaceInfo`. On policy parse failure after HNS create, the HNS endpoint is deleted.

State and persistence: runtime endpoint map, Windows port allocator state, and HNS endpoint state. No libnetwork datastore in this file.

Dependencies and integration points: depends on `hcsshim`, Windows driver DNS/port helpers, libnetwork endpoint options, and HNS policies.

Risks: HNS operations are external side effects and can partially fail. Endpoint deletion returns errors for missing endpoint instead of treating it as idempotent. Gateway is always disabled after endpoint creation.

Test signals: no direct tests in this subset.
