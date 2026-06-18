# sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_test.go

Purpose: Tests macvlan driver registration and type reporting.

Important APIs and functions: `driverTester` validates `RegisterDriver` receives `macvlan` and a `*driver`, while `RegisterNetworkAllocator` is unexpected. `TestMacvlanRegister`, `TestMacvlanNilConfig`, and `TestMacvlanType` cover registration, empty-store init, and `Type`.

Control flow: tests use a temp datastore and capture the registered driver.

State and persistence: uses empty temp store; no network records are created.

Dependencies and integration points: checks libnetwork registration contract.

Risks: no coverage for create/delete, endpoint, join, parent sharing, or store restore.

Test signals: verifies basic driver wiring only.
