# sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan.go

Purpose: Defines the Linux ipvlan driver core constants, driver/network/endpoint state types, and registration entrypoint.

Important APIs and types: constants define interface name prefixes, `NetworkType`, option names (`parent`, `ipvlan_mode`, `ipvlan_flag`), modes (`l2`, `l3`, `l3s`), and flags (`bridge`, `private`, `vepa`). `driver` owns a datastore and a mutex-protected `networks` map. `endpoint` stores ids, MAC/IPs, source link name, and datastore metadata. `network` stores config and a mutex-protected endpoint map. `Register` initializes state from the datastore then registers with local data scope and global connectivity scope.

Control flow: registration builds the driver, calls `initStore` to repopulate networks/endpoints, and exposes the driver to libnetwork.

State and persistence: persistent state is owned by `ipvlan_store.go`; this file defines the objects holding runtime and DB metadata.

Dependencies and integration points: depends on `datastore`, `driverapi`, and libnetwork `scope`. Other ipvlan files implement the driverapi methods against these types.

Risks: driver registration fails if store restore fails. The driver has process-local runtime maps that must stay synchronized with datastore updates.

Test signals: `ipvlan_test.go` checks registration, nil-ish store initialization path, and type reporting.
