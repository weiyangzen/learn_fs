# sources/cloud-native/moby/daemon/libnetwork/drivers/ipvlan/ipvlan_state.go

Purpose: Provides concurrency-safe runtime state accessors for ipvlan networks and endpoints plus shared id validation.

Important APIs and functions: `driver.network`, `addNetwork`, `deleteNetwork`, `getNetworks`, `network.endpoint`, `addEndpoint`, `deleteEndpoint`, `validateID`, and `driver.getNetwork`.

Control flow: driver-level methods lock `driver.mu` around `networks`. Network-level methods lock `network.mu` around `endpoints`. `network` logs and returns nil when missing; `getNetwork` returns typed libnetwork errors.

State and persistence: manipulates in-memory maps only. Persistent state is handled separately in `ipvlan_store.go`.

Dependencies and integration points: called throughout network, endpoint, and join/leave paths. Uses `types.InvalidParameterErrorf` and `types.NotFoundErrorf` for public error semantics.

Risks: there are two lookup styles with different error behavior. Callers must choose carefully. Some endpoint field mutations after lookup are not protected by the map lock.

Test signals: no direct state tests; behavior is indirectly exercised by registration and higher-level driver operations.
