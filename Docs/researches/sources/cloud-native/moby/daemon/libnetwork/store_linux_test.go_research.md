## sources/cloud-native/moby/daemon/libnetwork/store_linux_test.go

Purpose: Linux-specific tests for the libnetwork local datastore backend and the `NetworkOptionPersist(false)` path.

Important APIs and functions: `TestBoltdbBackend` builds a temporary BoltDB path and delegates to `testLocalBackend`, exercising normal network and endpoint persistence. `TestNoPersist` creates a controller with a temp data directory, creates a host network with `NetworkOptionPersist(false)`, creates an endpoint, stops the controller, and creates a new controller over the same data directory.

Control flow and state: The test explicitly checks the store after restart by constructing `Network{id: nw.ID()}` and `Endpoint{network: nw, id: ep.ID()}` KV objects and calling `GetObject`. It expects `store.ErrKeyNotFound` and verifies `Exists()` stays false, proving both network and endpoint skipped persistent KV writes when the network is non-persistent.

Dependencies and integration points: Uses `config.OptionDataDir`, `New`, `NewNetwork`, `CreateEndpoint`, and the internal kvstore error contract. It depends on Linux datastore behavior and BoltDB availability.

Risks covered: Guards against accidentally persisting built-in or ephemeral networks when `persist=false` is requested. Also covers endpoint persistence inheritance from the parent network.

Test signals: Strong integration-style signal across controller construction, datastore reopen, network creation, endpoint creation, and object-level store reads.
