# sources/distributed-fs/ipfs-kubo/test/cli/daemon_test.go

Purpose: daemon lifecycle regression tests for null API config and graceful shutdown while operations are active.

Important APIs/types/functions: `TestDaemon`, `infiniteReader.Read`, `StartDaemon`, `StartDaemonWithReq`, `StopDaemon`, `Runner.Run`, `multiaddr.NewMultiaddr`, `manet.ToNetAddr`, and gateway HTTP client.

Control flow: one subtest starts `ipfs daemon` with `Addresses.API = nil`. The larger subtest enables pubsub, P2P HTTP proxy, gateway-over-libp2p, and GC, starts continuous stdin `ipfs add` plus a slow gateway CAR read, sleeps briefly, stops the daemon, asserts shutdown under ten seconds, ensures background operations terminate, and restarts the repo.

State/persistence: daemon config changes, repo lock lifecycle, gateway addresses, background processes/goroutines, and random blockstore content.

Dependencies/integration: daemon startup/shutdown, repo locking, command cancellation, gateway streaming, experimental components, and GC-enabled daemon paths.

Risks/test signals: good deadlock/shutdown signal. Timing is synthetic and could be flaky under very slow CI; background goroutines intentionally ignore expected shutdown errors.
