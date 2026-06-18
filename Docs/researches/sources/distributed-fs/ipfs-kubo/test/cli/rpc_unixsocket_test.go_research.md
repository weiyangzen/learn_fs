# sources/distributed-fs/ipfs-kubo/test/cli/rpc_unixsocket_test.go

Purpose: verifies the Kubo RPC client and daemon can communicate over a Unix socket API address.

Important APIs and functions: `TestRPCUnixSocket` constructs an API multiaddr by joining `/unix`, the node repo directory, and `sock`, writes it to `cfg.Addresses.API`, starts the daemon, builds a `multiaddr.Multiaddr`, and creates a client with `rpcapi.NewApi`.

Control flow: after daemon startup, the test issues RPC requests for `version` and `id` through the Unix socket client. Both responses must succeed and populate non-empty structs. The daemon is stopped at the end.

State and persistence: the API listen address is a config value set before daemon startup. The socket file lives under the temporary node directory during daemon runtime and is not inspected after shutdown.

Dependencies and integration points: integrates config address parsing, Unix socket listener creation, multiaddr parsing, the Go RPC client transport, and core API commands. It is Unix-specific in practice even though the file has no explicit build tag.

Risks and test signals: path length and platform support for Unix sockets can affect this test. Failures indicate daemon inability to bind Unix API addresses, client transport regression, or multiaddr format changes.
