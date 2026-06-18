# sources/distributed-fs/ipfs-kubo/core/node/libp2p/routingopt_test.go

Purpose: unit-tests delegated endpoint capability parsing and HTTP router address selection. Important tests are `TestDetermineCapabilities`, `TestEndpointCapabilitiesReadWriteLogic`, and `TestHttpRouterAddrFunc`.

Control flow: capability tests feed read/write endpoint sources with no path, trailing slash, IPNS path, providers path, peers path, write-only endpoint, and unsupported path, asserting base URL and capability booleans. The stub host implements `ConfirmedAddrs` and minimal `host.Host` methods. Address tests verify AutoNAT confirmed addresses win over `host.Addrs`, fallback works, Announce overrides both, AppendAnnounce is appended in all modes, and NoAnnounce filtering is assumed to happen upstream in `host.Addrs`.

State and persistence: no external state; all multiaddrs are parsed in-memory.

Dependencies/integration: autoconf capabilities, Kubo config, libp2p host interfaces, testify. It protects HTTP routing's read/write split and provider-address selection used for delegated routing records.

Risks signaled: publishing private/wildcard addresses to HTTP routers or enabling unsupported endpoint capabilities would harm retrieval and IPNS behavior.
