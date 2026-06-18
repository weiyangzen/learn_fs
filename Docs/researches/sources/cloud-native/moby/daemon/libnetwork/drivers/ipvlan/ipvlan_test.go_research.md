# sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_test.go

Purpose: Tests ipvlan driver registration and basic type behavior.

Important APIs and functions: `driverTester` validates `RegisterDriver` receives name `ipvlan` and a `*driver`, and fails if a network allocator is unexpectedly registered. `TestIpvlanRegister`, `TestIpvlanNilConfig`, and `TestIpvlanType` exercise registration, store initialization, and `Type`.

Control flow: each test uses `storeutils.NewTempStore`, calls `Register`, and inspects the captured driver.

State and persistence: uses an empty temporary datastore; does not create networks.

Dependencies and integration points: verifies integration with libnetwork registration and temp datastore utilities.

Risks: no coverage for network lifecycle, endpoint lifecycle, join routing, or datastore restore with populated records.

Test signals: confirms the driver wires into registration correctly and can initialize with an empty store.
