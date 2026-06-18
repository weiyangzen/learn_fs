<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/docs/examples/kubo-as-a-library/main.go -->
# sources/distributed-fs/ipfs-kubo/docs/examples/kubo-as-a-library/main.go

## Purpose

This example is an executable tutorial for embedding Kubo as a Go library. It creates temporary repos, starts two in-process online IPFS nodes, connects them directly, adds local files and directories, reads them back through the CoreAPI, and demonstrates Bitswap retrieval from a peer without DHT or bootstrap discovery.

## Important APIs, Types, and Functions

`setupPlugins` initializes the plugin loader, including built-in plugins. `createTempRepo` creates an Ed25519 identity, configures a minimal loopback-only repo, disables QUIC/relay/web transports/autoconf/bootstrap/DHT, optionally toggles experimental features, and calls `fsrepo.Init`. `createNode` opens the repo and builds a `core.IpfsNode` with `libp2p.NilRouterOption`. `spawnEphemeral` uses `sync.Once` to load plugins only once, then returns `coreapi.NewCoreAPI`. `connectToPeers` parses `/p2p/` multiaddrs into grouped `peer.AddrInfo` entries and connects concurrently. `getUnixfsNode` adapts filesystem paths into `boxo/files.Node`.

## Control Flow, State, and Integration

`main` uses a two-minute context, starts node A and B, connects B to A via A's first local swarm address, adds content to node A, imports example file/directory content into node B, writes retrieved UnixFS nodes to a temporary output directory, then fetches node A's CID through node B. Persistent state is intentionally temporary: repos are created under the system temp directory, no bootstrap list is saved, and only the per-repo datastore retains added blocks during the process lifetime.

## Dependencies, Risks, and Test Signals

The example depends on Kubo core, CoreAPI, fsrepo, config, libp2p, multiformats multiaddrs, and boxo UnixFS files. Risks include relying on local example fixtures, assuming `peerAddrs[0]` exists, using temp repos without cleanup, and using `panic` instead of library-style error handling because this is tutorial code. The companion test runs `go run main.go` with reduced logging and checks for the final success banner; the Makefile also runs the example against published and local Kubo module replacements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/docs/examples/kubo-as-a-library/main.go -->
