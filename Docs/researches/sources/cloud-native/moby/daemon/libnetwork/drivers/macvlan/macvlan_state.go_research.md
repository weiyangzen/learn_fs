# sources/cloud-native/moby/daemon/libnetwork/drivers/macvlan/macvlan_state.go

Purpose: Provides concurrency-safe runtime state helpers for macvlan networks and endpoints plus id validation.

Important APIs and functions: `driver.network`, `addNetwork`, `deleteNetwork`, `getNetworks`, `network.endpoint`, `addEndpoint`, `deleteEndpoint`, `validateID`, and `driver.getNetwork`.

Control flow: driver methods lock `driver.mu`, network methods lock `network.mu`, and `getNetwork` returns typed libnetwork errors for public paths.

State and persistence: manipulates in-memory maps only; persistent state is handled in `macvlan_store.go`.

Dependencies and integration points: called by macvlan network, endpoint, and join paths.

Risks: missing-network `network` logs and returns nil, while `getNetwork` returns errors; inconsistent use can affect caller behavior. Endpoint object field mutation after lookup is not fully protected.

Test signals: no direct state tests in this subset.
