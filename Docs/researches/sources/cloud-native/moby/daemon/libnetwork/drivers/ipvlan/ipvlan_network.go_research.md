# sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_network.go

Purpose: Implements ipvlan network create/delete, option parsing, IPAM processing, parent interface provisioning, and gateway allocation policy.

Important APIs and functions: `CreateNetwork` enforces kernel >= 4.2, rejects empty IPv4/IPv6 pools when enabled, parses options, processes IPAM, supplies a dummy parent when none is configured, calls `createNetwork`, and persists configuration. `createNetwork` rejects reuse of the same parent by a different network, creates dummy or VLAN parent links if missing, and adds runtime state. `GetSkipGwAlloc` always returns true for both families. `DeleteNetwork` deletes driver-created parent links, deletes endpoint links and datastore records, removes runtime state, and deletes the network config. `parseNetworkOptions`, `parseNetworkGenericOptions`, `newConfigFromLabels`, and `processIPAM` define config ingestion.

Control flow: create separates config parsing from link provisioning and datastore update; datastore failure rolls back only runtime network state, not necessarily created links. Existing same-id/same-parent restore returns an internal maskable error. Delete is best-effort for kernel cleanup but fails if network config deletion from datastore fails.

State and persistence: persists `configuration` and endpoint records in `ipvlan_store.go`; creates/deletes dummy and VLAN netlink devices when `CreatedSlaveLink` is true.

Dependencies and integration points: integrates with kernel version parser, netlabel flags, libnetwork IPAM data, netlink parent setup helpers, and `errdefs.InvalidParameter`.

Risks: parent uniqueness is stricter than macvlan and disallows sharing a parent across ipvlan networks. Type assertions on `EnableIPv4`/`EnableIPv6` assume booleans. Link creation may outlive datastore rollback.

Test signals: setup tests cover helper parsing and modes; no direct network create/delete tests in this subset.
