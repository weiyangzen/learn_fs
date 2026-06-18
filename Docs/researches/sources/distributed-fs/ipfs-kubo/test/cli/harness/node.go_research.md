# sources/distributed-fs/ipfs-kubo/test/cli/harness/node.go

Purpose: core harness abstraction for a single Kubo repo and daemon. It owns process execution, repo config, daemon lifecycle, API readiness, swarm connectivity, gateway/API clients, and offline datastore helpers.

Important APIs/types/functions: `Node`, `BuildNode`, file/config helpers, `IPFS`/`RunIPFS`/pipe variants, `Init`, `StartDaemonWithReq`, `StartDaemon`, `StopDaemon`, `APIAddr`, `APIURL`, `checkAPI`, `PeerID`, `WaitOnAPI`, `IsAlive`, swarm address/connection helpers, `PeerWith`, `Disconnect`, `GatewayURL`, client constructors, and datastore diagnostics.

Control flow: `BuildNode` creates `IPFS_PATH` and runner env. `Init` runs `ipfs init` and rewrites config for local random ports, disabled bootstrap, disabled telemetry, mDNS choice, and test routing behavior. `StartDaemonWithReq` starts `ipfs daemon`, stores the process result, then polls `/api/v0/id`. Shutdown escalates from SIGTERM to SIGQUIT/SIGKILL with Windows handling.

State and persistence: each node has a repo directory containing config, version, api/gateway files, datastore, blocks, and optional resource-manager overrides. Daemon state is a running OS process.

Dependencies/integration: uses Kubo config serialization, libp2p peer IDs, multiaddr/manet conversion, HTTP API checks, and the harness `Runner`.

Risks: many methods panic on errors, which is intentional for tests but reduces recoverability. `ExitCode` assumptions can break for still-running processes. Swarm connect methods sometimes ignore failures for resilience, which can hide setup issues. Test signals are API id responses, peer IDs, swarm peers, gateway file URLs, and datastore command output.
