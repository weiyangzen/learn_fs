# Research: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/windows_store.go

Purpose: provides datastore serialization, restore, update, and delete behavior for the Windows HNS driver. Important constants are `windowsPrefix` and `windowsEndpointPrefix`; important APIs are `initStore`, `populateNetworks`, `populateEndpoints`, `storeUpdate`, `storeDelete`, and `datastore.KVObject` implementations for `networkConfiguration` and `hnsEndpoint`.

Control flow: initialization first lists stored network configs for the driver's HNS type and recreates in-memory `hnsNetwork` records, then lists stored endpoints, attaches each to its restored network, and deletes stale endpoint records whose network is gone. Store updates use `PutObjectAtomic`; deletes call `DeleteObject`. JSON methods encode stable fields such as HNS IDs, names, VLAN/VSID, DNS, endpoint profile IDs, MAC/IP/gateway, endpoint options, connectivity, and port mappings.

State and dependencies: this is the persistence bridge between libnetwork state and the generic datastore, while HNS remains the runtime source. Dependencies include JSON, `datastore`, `types.ParseCIDR`, and logging. Risks include unchecked type assertions during unmarshal, older saved records missing newer fields, and persistence warnings that do not always abort runtime changes. Test signal comes from Windows driver tests using a temp store.
