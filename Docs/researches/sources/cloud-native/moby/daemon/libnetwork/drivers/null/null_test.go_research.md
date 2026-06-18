# sources/cloud-native/moby/daemon/libnetwork/drivers/null/null_test.go

Purpose: Tests the null driver's single-network and undeletable-network contract.

Important APIs and functions: `TestDriver` checks `Type`, first `CreateNetwork`, stored id, forbidden second create, and forbidden delete for known/unknown ids.

Control flow: direct calls against a local `driver` value.

State and persistence: validates only in-memory state.

Dependencies and integration points: uses containerd errdefs to check permission-denied classification.

Risks: does not test registration capabilities or no-op endpoint/join methods.

Test signals: confirms the key invariants of the null driver.
