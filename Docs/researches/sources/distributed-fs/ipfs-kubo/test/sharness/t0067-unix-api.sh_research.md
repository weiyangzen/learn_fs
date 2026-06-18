## sources/distributed-fs/ipfs-kubo/test/sharness/t0067-unix-api.sh

Purpose: verifies that Kubo can expose and consume the HTTP API over a Unix domain socket.

Important APIs and helpers: uses `ipfs config Addresses.API`, `ipfs --api=/unix/... id -f=<id>`, `test_init_ipfs`, daemon launch/kill helpers, and `test_cmp`.

Control flow and state: initializes a repo, records the local peer ID, configures the daemon API address to a socket under a test directory, launches the daemon, and performs an explicit `--api` client call through the Unix socket.

Dependencies and integration points: covers multiaddr support for `/unix` API endpoints, daemon listener binding, client transport selection, and peer identity retrieval over the daemon API.

Risks and test signals: catches regressions in Unix socket path handling, endpoint serialization, or client API dialing. The test signal is equality between the configured peer ID and `ipfs id` fetched through the socket endpoint.
