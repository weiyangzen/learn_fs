# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlay_test.go

Purpose: Tests Linux overlay driver registration and type reporting.

Important APIs and functions: `driverTester` validates `RegisterDriver` receives `overlay` and a `*driver`; plugin getter returns nil and network allocator registration is unexpected. `TestOverlayInit` checks registration succeeds. `TestOverlayType` checks `Type`.

Control flow: tests call `Register` with the fake registerer and inspect captured driver.

State and persistence: no kernel or datastore state.

Dependencies and integration points: verifies libnetwork registration contract for the overlay driver.

Risks: no coverage for network lifecycle, discovery, join, encryption, or peer events.

Test signals: basic smoke coverage for driver registration.
