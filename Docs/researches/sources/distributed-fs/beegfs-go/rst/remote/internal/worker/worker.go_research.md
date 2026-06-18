# sources/distributed-fs/beegfs-go/rst/remote/internal/worker/worker.go

## Purpose
This file defines the common worker-node interface and the shared base lifecycle used by all BeeRemote worker clients.

## Important APIs, Types, and Functions
`Worker` is the external interface for node identity, state, lifecycle, work submission, and work updates. `grpcClientHandler` is the internal connection/heartbeat/disconnect interface implemented by concrete node types. `baseNode` stores logger, state, config, node/RPC contexts, RPC wait group, node mutex, and error channel. `State` enumerates `UNKNOWN`, `OFFLINE`, and `ONLINE`. `Handle`, `connectLoop`, `Stop`, `GetID`, `GetState`, and `GetNodeType` provide shared behavior.

## Control Flow
`Handle` serializes lifecycle handling with `nodeMu`, repeatedly connects offline nodes, marks them online, monitors shutdown, unary RPC errors, and heartbeat readiness, then transitions offline, drains in-flight RPCs up to `DisconnectTimeout`, cancels the RPC context, and disconnects. `connectLoop` retries `connect` with exponential backoff and jitter until success, fatal error, or node shutdown.

## State and Persistence Behavior
No durable state is written. Runtime state is protected by mutexes and contexts. `nodeCtx` controls the overall node lifetime; `rpcCtx` is recreated on every connection so RPCs can resume after disconnect; `rpcWG` tracks in-flight unary calls so disconnect can be graceful.

## Dependencies and Integration Points
Concrete implementations in `beesync.go` and `mock.go` embed `baseNode`. `workermgr.Pool` reads `GetState`, calls `SubmitWork` and `UpdateWork`, and starts `Handle` through `Pool.HandleAll`.

## Risks and Edge Cases
Heartbeat and reconnect are central to avoiding stale stateless sync nodes, but prolonged RPCs can be forcibly cancelled after timeout. The unbuffered `rpcErr` channel requires nonblocking send discipline. `connectLoop` jitter can set the delay to slightly below `MaxReconnectBackOff`, but if max is configured too low behavior may be noisy. There is no persistence of online/offline state, so all recovery depends on config replay.

## Test Signals
This file has no direct tests in the subset. It is indirectly exercised whenever mock workers are started in manager tests, but heartbeat failure, reconnect backoff, RPC drain timeout, and shutdown races are not directly covered.
