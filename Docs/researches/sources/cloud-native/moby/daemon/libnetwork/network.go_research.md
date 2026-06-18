# sources/cloud-native/moby/daemon/libnetwork/network.go

## Purpose
Core implementation of libnetwork `Network`: a logical connectivity zone managed by a driver, persisted through the controller datastore, backed by IPAM allocations, endpoint lifecycle operations, service-discovery records, optional load-balancer sandbox, and distributed NetworkDB integration for swarm/dynamic networks.

## Important APIs, Types, And Functions
Key types are `EndpointWalker`, `IpamConf`, `IpamInfo`, `Network`, `NetworkOption`, and `NetworkDeleteOption`. Important methods include datastore `Key`, `Value`, `SetValue`, `CopyTo`, configuration validation/application, option setters, `Delete`, `CreateEndpoint`, endpoint walkers/lookups, service DNS record mutation, IPAM allocation/release/status, accessors, `ResolveName`, `ResolveIP`, `ResolveService`, and load-balancer sandbox creation/deletion.

## Control Flow
Network creation options populate fields and generic labels. Validation rejects invalid config-only/config-from combinations and platform-specific advertise-address settings. Endpoint creation locks by network ID, reloads the freshest network from the store, applies endpoint options, validates link-local addresses, allocates IPs, asks the network driver to create the endpoint, stores it, and rolls back IP/driver/store state on error. Deletion reloads the network, rejects active endpoints unless forced or only the LB endpoint remains, marks `inDelete`, persists, releases IPAM, leaves cluster/watch state, cleans service discovery/bindings, calls driver deletion, stops resolvers, deletes compatibility endpoint count, and removes the stored network.

## State And Persistence
`Network` implements `datastore.KVObject` with keys under `datastore.NetworkKeyPrefix`. JSON marshaling preserves persistent fields, including IPAM config/info encoded as nested JSON strings for compatibility. `dbIndex`, `dbExists`, and `persist` control datastore behavior. In-memory controller caches and `svcRecords` hold live network and DNS state. IPAM pool IDs, gateways, aux addresses, and deletion tombstone state are persisted enough for restore/delete semantics.

## Dependencies And Integration Points
Integrates with controller store/cache, driver API, IPAM registry, default IPAM, netlabel options, netutils reserved-prefix inference, networkdb peer visibility, service discovery/resolver code, OpenTelemetry tracing, errdefs, and platform methods in `network_unix.go`/`network_windows.go`.

## Risks
This file is a high-blast-radius lifecycle path. Risks include rollback gaps after datastore/driver/IPAM partial failures, stale network copies, lock-order regressions, JSON compatibility issues, nil/type assertion panics on malformed persisted data, and service DNS map races if controller locking is bypassed. IPAM release logs but continues on many failures. Load-balancer deletion notes an inconsistent-state boundary after recoverable checks.

## Test Signals
The Linux integration suite covers network/endpoint lifecycle, active endpoint/container errors, config-only/config-from, bridge/null/host behavior, DNS, plugin drivers, and parallel join/leave. Store-specific and Windows resolver tests cover adjacent behavior.
