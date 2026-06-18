# Research: sources/cloud-native/moby/daemon/cluster/noderunner.go

## sources/cloud-native/moby/daemon/cluster/noderunner.go

Purpose: manages the lifecycle of a SwarmKit node inside dockerd, including startup, readiness, control-socket changes, store watches, reconnects, persistent config, and state reporting.

Important types and APIs: `nodeRunner`, `nodeStartConfig`, `Ready`, `Start`, `start`, `handleControlSocketChange`, `watchClusterEvents`, `handleReadyEvent`, `handleNodeExit`, `Stop`, `State`, `enableReconnectWatcher`, and `nodeState` helpers. Startup builds a `swarmnode.Config` with control socket, remote listen/advertise addresses, network allocator config, state dir, join token, container executor, raft ticks, unlock key, plugin getter, and network provider. It starts the SwarmKit node, saves persistent state, then launches goroutines for node exit, readiness, and control socket updates.

Persistent state is `nodeStartConfig` serialized by `savePersistentState` in the swarm state dir. Runtime state is guarded by `nodeRunner.mu`: current node, gRPC connection/clients, error, ready/done channels, reconnect delay, and reconnect cancel function. Cluster watch messages are forwarded into `cluster.watchStream`.

Dependencies include container executor, cluster convert, libnetwork cluster events, cnmallocator provider, SwarmKit node/control/watch APIs, gRPC status handling, and network allocator config. Risks include reconnect loops after promotion/demotion failures, stale join addresses, goroutine/channel lifetime complexity, persistent state consistency during join, and watch-stream backpressure. Tests are mostly integration-level outside this subset.
