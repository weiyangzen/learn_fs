# sources/distributed-fs/ipfs-kubo/test/cli/harness/harness.go

Purpose: top-level test harness for Kubo CLI integration tests. It creates temporary workspaces, locates the built `cmd/ipfs/ipfs` binary, manages nodes, temp files, shell execution, stub DHT bootstrap, and cleanup.

Important APIs/types/functions: `Harness` stores `Dir`, `IPFSBin`, `Runner`, `NodesRoot`, `Nodes`, and optional `stubPeers`. `NewT` registers cleanup with testing, `New` initializes paths, `BootstrapWithStubDHT` wires local DHT peers, `NewNode`/`NewNodes` allocate repos, `WriteToTemp`, `TempFile`, `WriteFile`, `Mkdirs`, `WaitForFile`, `Sh`, `Cleanup`, and `ExtractPeerID` support tests.

Control flow: `New` walks up to `go.mod`, sets the binary path, creates a temp root, and applies options. Node creation delegates to `BuildNode`. Cleanup stops all daemons, closes stub peers, and removes temp dirs.

State and persistence: all state lives under a temporary directory and node repo directories. Cleanup is destructive for the harness temp root.

Dependencies/integration: imports Kubo testutils, go-log, libp2p peer IDs, and multiaddr. It is the primary integration point used by almost every CLI test in this subset.

Risks: `osEnviron` splits on every `=`, which can truncate env values containing `=`. `h.stubPeers.Close()` is called without a nil guard at the call site, relying on the method receiver check. Test signals are clean temp setup, successful command runs, and daemon teardown.
