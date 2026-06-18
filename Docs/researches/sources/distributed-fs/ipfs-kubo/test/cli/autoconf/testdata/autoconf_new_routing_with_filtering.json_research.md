# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/autoconf_new_routing_with_filtering.json

Purpose: AutoConf fixture for testing path filtering on a delegated `NewRoutingSystem`. It intentionally mixes supported and unsupported read/write paths.

Important fields: the system declares delegated support for `/routing/v1/providers`, `/routing/v1/peers`, `/routing/v1/ipns` reads and `/routing/v1/ipns` writes. `DelegatedEndpoints` includes `supported-new.example.com` with valid provider/peer read and IPNS write paths, `unsupported-new.example.com` with custom unsupported paths, and `mixed-new.example.com` with both valid and invalid paths.

Control flow is data-only. Tests load and serve the fixture, then require expansion to include only supported provider/peer/IPNS URLs and exclude custom paths such as `/custom/v0/read`, `/api/v1/nonstandard`, and `/invalid/path`. State is endpoint capabilities. Dependencies are Kubo's supported-path filter and URL construction rules. Risks include adding new supported delegated-routing paths without updating this fixture/test. Test signal validates path-level filtering without discarding an entire mixed endpoint that has at least one valid path.
