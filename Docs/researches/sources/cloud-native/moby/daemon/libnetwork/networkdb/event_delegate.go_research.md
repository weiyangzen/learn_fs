# sources/cloud-native/moby/daemon/libnetwork/networkdb/event_delegate.go

## Purpose
Memberlist event delegate for node join/leave notifications and local watcher broadcasts.

## Important APIs, Types, And Functions
`eventDelegate` implements `NotifyJoin`, `NotifyLeave`, and `NotifyUpdate`. `broadcastNodeEvent` converts a node IP into a `NodeAddr` watch event. `nodeEventOp` distinguishes join and leave event payload direction.

## Control Flow
On join, it logs, broadcasts a node table add event, moves a known failed/left node back to active if present, purges reincarnations by IP, and inserts new active node state. On leave, it logs, broadcasts a node table delete event, finds the node, and moves active nodes to failed state; graceful left state is driven by node gossip events. `NotifyUpdate` is currently a no-op.

## State And Persistence
Mutates in-memory node state maps and `estNodes`; emits watcher events. No disk persistence.

## Dependencies And Integration Points
Used by memberlist config in `clusterInit`. Integrates with node management helpers, `NodeTable` watchers, and cluster reconnect/reap paths.

## Risks
Memberlist leave can indicate failure rather than graceful leave, so state transitions are conservative. Reincarnation handling is necessary when a new node ID appears at the same IP. Missing nodes on leave are logged but otherwise ignored.

## Test Signals
No direct tests in this subset.
