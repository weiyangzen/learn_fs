# sources/distributed-fs/ipfs-kubo/core/coreapi/test/api_test.go

Purpose: adapts Kubo CoreAPI to the shared `coreiface/tests` suite by providing in-memory/mocknet node swarms.

Important APIs/types/functions: `NodeProvider.MakeAPISwarm` and `TestIface`.

Control flow: for each requested node, it generates full identities when requested or uses a fixed peer ID, builds a config with swarm address, filestore enabled, AutoTLS disabled, and provider strategy `roots`, creates a mock repo with map datastore/mem keystore/filestore, constructs `core.NewNode` with mock host and DHT server option, enables pubsub, wraps it with `coreapi.NewCoreAPI`, links all mocknet peers, and bootstraps non-first nodes to the first when online. `TestIface` passes the provider to the shared API test suite.

State and persistence behavior: test-only in-memory repo state plus temporary filestore directory. Network state lives in mocknet and is linked/bootstraped per test.

Dependencies and integration points: covers broad CoreAPI behavior across UnixFS, block, dag, name, key, pin, object, swarm, pubsub, and routing through `coreiface/tests`.

Risks: shared tests only cover behavior represented in the external interface suite. Mocknet differs from real transports/NAT/resource-manager behavior. Full identities are optional, so tests relying on private keys must request them.

Test signals: primary integration signal for CoreAPI conformance.
