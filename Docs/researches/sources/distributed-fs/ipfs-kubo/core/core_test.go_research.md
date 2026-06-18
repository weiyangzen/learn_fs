# sources/distributed-fs/ipfs-kubo/core/core_test.go

Purpose: tests basic node construction and `IpfsNode.HasActiveDHTClient` behavior, especially typed-nil interface hazards.

Important APIs/types/functions: `TestInitialization`, `testIdentity`, `mockHostOption`, and `TestHasActiveDHTClient`.

Control flow: initialization tests create mock repos with good/bad config and expect `NewNode` success/failure. DHT-client tests cover nil interface, typed nil `*ddht.DHT`, typed nil `*fullrt.FullRT`, `routinghelpers.Null`, a valid dual DHT node built on mocknet, and a valid accelerated fullrt client.

State and persistence behavior: uses in-memory datastore/keystore and temporary filestore paths. Valid node cases construct live mocknet/libp2p nodes and close them after assertions.

Dependencies and integration points: integrates with `repo.Mock`, Kubo `NewNode`, libp2p DHT options, mocknet host option, filestore, keystore, and config identity/address setup.

Risks: tests depend on constructing DHT services under mocknet, so they are heavier than pure unit tests. They validate known nil/no-op types but not arbitrary custom routing clients.

Test signals: strong regression coverage for the typed-nil interface bug that affects DHT stats/version/routing commands.
