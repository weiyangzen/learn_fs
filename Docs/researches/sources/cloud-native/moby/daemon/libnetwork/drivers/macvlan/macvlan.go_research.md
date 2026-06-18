# sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan.go

Purpose: Defines the Linux macvlan driver constants, runtime types, and registration entrypoint.

Important APIs and types: constants define `NetworkType`, interface prefixes, macvlan modes (`private`, `vepa`, `bridge`, `passthru`), and option labels. `driver` owns datastore and mutex-protected networks. `endpoint` stores ids, MAC/IPs, source name, and datastore metadata. `network` stores config and endpoint map. `Register` restores datastore state and registers the driver with local data scope and global connectivity.

Control flow: registration mirrors ipvlan: construct driver, `initStore`, register driver.

State and persistence: runtime maps are defined here; datastore format is in `macvlan_store.go`.

Dependencies and integration points: integrates with `driverapi`, `datastore`, and scope constants. Sibling files implement lifecycle behavior.

Risks: runtime maps and datastore must remain consistent across partial failures. Macvlan mode and parent sharing rules are enforced outside this core file.

Test signals: `macvlan_test.go` covers registration and type reporting.
