# sources/distributed-fs/beegfs-go/rst/remote/internal/worker/config.go

## Purpose
This file defines worker-node configuration and factory logic for BeeRemote worker clients.

## Important APIs, Types, and Functions
`Type` enumerates supported worker pools: `Unknown`, `BeeSync`, and `Mock`. `Config` includes identity, address, TLS/proxy settings, reconnect/disconnect/retry/heartbeat timing, and embedded type-specific config. `BeeSyncConfig` is currently empty. `MockConfig` and `MockExpectation` define Testify expectations for mock worker nodes. `NewWorkerNodesFromConfig` builds all valid workers while accumulating errors. `newWorkerNodeFromConfig` applies timing defaults, builds base contexts/wait groups, and dispatches to BeeSync or mock constructors.

## Control Flow
The public factory loops over configs, attempts to create each node, appends valid workers, and returns a `types.MultiError` if any config failed. The single-node factory fills zero timing values with defaults, initializes `baseNode` as `OFFLINE`, and switches on worker type.

## State and Persistence Behavior
No persistent state is written. The function initializes in-memory lifecycle state: node context, RPC context, wait group, state mutexes, and RPC error channel. Created nodes must later be driven by `Handle`.

## Dependencies and Integration Points
The file depends on `common/types.MultiError`, zap logging, and worker implementations in `beesync.go`/`mock.go`. `workermgr.NewManager` uses it to populate node pools.

## Risks and Edge Cases
Unknown worker types are rejected but do not prevent other valid nodes from being returned. Defaults are hard-coded here pending centralized config defaults, so CLI/config docs must remain aligned manually. The unbuffered `rpcErr` channel relies on nonblocking sends in worker implementations to avoid RPC deadlocks.

## Test Signals
This subset has indirect coverage through job-manager and work-manager tests that create mock nodes. There is no direct table test for defaults, multi-error behavior, or unknown type rejection.
