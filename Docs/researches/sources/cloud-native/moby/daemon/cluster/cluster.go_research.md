# sources/cloud-native/moby/daemon/cluster/cluster.go

## Purpose
Defines the core swarm `Cluster` object, its configuration, startup from persistent state, state-query helpers, manager action locking, shutdown behavior, and cluster event delivery.

## Important APIs, Types, And Functions
Defines constants for swarm directories, sockets, timeouts, and defaults; interfaces `NetworkSubnetsProvider`; structs `Config`, `Cluster`, and `attacher`; functions `New`, `Start`, `newNodeRunner`, status/address getters, `GetWatchStream`, `ListenClusterEvents`, `errNoManager`, `Cleanup`, `managerStats`, `detectLockedError`, `lockedManagerAction`, and `SendClusterEvent`.

## Control Flow
`New` normalizes runtime root and raft ticks, initializes channels and maps. `Start` creates state dirs, loads `docker-state.json`, starts a node runner when state exists, and waits up to 20 seconds for readiness. `newNodeRunner` validates backend compatibility, derives a local address if omitted, starts swarmkit, and notifies the backend. Manager actions take a read lock, verify active manager state, attach a timeout, and invoke a closure.

## State And Persistence
Persistent swarm state is under `<Root>/swarm`; runtime sockets live under `RuntimeRoot`. In-memory state includes `nr`, attachers, config event channel, and watch stream. Locking is explicit: `controlMutex` for lifecycle operations and `mu` for state visibility.

## Dependencies And Integration Points
Bridges daemon backends, swarmkit node/control clients, plugin controller, executor backends, libnetwork cluster events, and stack dump logging.

## Risks And Test Signals
`currentNodeState` assumes `nr` is usable while locked; callers must respect locking. Startup readiness failures are logged but may not always fail daemon startup. Quorum warnings in cleanup depend on manager stats. Tests elsewhere should cover init/join/leave, locked swarm, address derivation, and shutdown.
