# Research: sources/cloud-native/moby/daemon/cluster/swarm.go

## sources/cloud-native/moby/daemon/cluster/swarm.go

Purpose: implements top-level swarm lifecycle and status APIs: init, join, inspect, update, unlock, leave, info, status, request validation, initial spec merge, and cleanup of node-owned containers on leave.

Important APIs: `Init`, `Join`, `Inspect`, `inspect`, `Update`, `GetUnlockKey`, `UnlockSwarm`, `Leave`, `Info`, `Status`, `validateAndSanitizeInitRequest`, `validateAndSanitizeJoinRequest`, `validateAddr`, `initClusterSpec`, and `listContainerForNode`. Init validates and resolves listen/advertise/data-path addresses, default address pools, and data-path port, starts a `nodeRunner`, waits for readiness, clears persistent state on failed fresh init, and merges user spec into the initial cluster spec. Join validates remote addrs, starts a node runner with join token, waits with timeout, and clears state on failure.

State is `Cluster.nr`, guarded by `controlMutex` and `mu`, plus persistent swarm state managed through node runner utilities. Unlock restarts the node runner with a parsed unlock key. Leave enforces manager quorum safeguards unless forced, stops the node, removes containers labeled for this node, clears swarm state, and notifies the daemon backend.

Dependencies include address resolution helpers, convert package, swarmkit control/CA APIs, encryption key formatting, manager quorum helpers, daemon backend container removal, errdefs, and gRPC. Risks include quorum-loss decisions, state cleanup after partial failures, address autodetection ambiguity, locked-swarm edge cases, and synchronous waits on node readiness. Test coverage here is largely integration-level.
