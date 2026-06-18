# sources/cloud-native/moby/daemon/libnetwork/drivers/host/host_test.go

Purpose: Tests the minimal state and error contract of the host driver.

Important APIs and functions: `TestDriver` checks `Type`, successful first `CreateNetwork`, stored network id, forbidden second create, and forbidden `DeleteNetwork` for both existing and unknown ids.

Control flow: constructs the driver directly and calls public driver methods with a background context.

State and persistence: validates in-memory `driver.network`; no external state.

Dependencies and integration points: uses containerd errdefs to assert forbidden errors map to permission denied.

Risks: no coverage for register capabilities or endpoint/join no-op methods.

Test signals: confirms the key host-driver invariant: exactly one undeletable network.
