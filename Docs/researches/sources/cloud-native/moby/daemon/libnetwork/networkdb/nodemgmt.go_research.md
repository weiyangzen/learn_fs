## sources/cloud-native/moby/daemon/libnetwork/networkdb/nodemgmt.go

Purpose: internal node state management for NetworkDB. It tracks movement of nodes between active, left, and failed sets, cleans entries when nodes leave or fail, and detects reincarnated nodes that reuse the same network address/port with a different name.

Important APIs/types/functions: `nodeState` constants model `nodeNotFound`, `nodeActiveState`, `nodeLeftState`, and `nodeFailedState`; `nodeStateName` supports logging; `findNode` searches `nodes`, `leftNodes`, and `failedNodes`; `changeNodeState` moves nodes across maps; `purgeReincarnation` marks old incarnations left; `estNumNodes` reads the atomic active-node estimate.

Control flow: `changeNodeState` finds the current map, no-ops if already in target state, deletes from old map, inserts into target map, updates `estNodes`, logs the transition, and for left/failed transitions sets `reapTime` and deletes node-owned network/table entries. `purgeReincarnation` scans active, failed, then left nodes for matching address/port and different name, then moves the old node to left.

State and persistence behavior: all state is in-memory NetworkDB membership maps and node reap timers. Entry cleanup triggers table/network tombstone behavior elsewhere. `estNodes` is an atomic derived count of active nodes.

Dependencies and integration points: uses `memberlist.Node` for address/port identity and `containerd/log` for transition logs. It relies on NetworkDB methods `deleteNodeFromNetworks` and `deleteNodeTableEntries`, which are outside this subset.

Risks: callers must hold appropriate locks when mutating maps; this file does not lock internally. Reincarnation detection by address/port can incorrectly retire a previous node if address reuse is ambiguous, but it is necessary for fast recovery after daemon/node ID changes. Unknown `nodeState` values are silently ignored after a TODO.

Test signals: `TestFindNode`, `TestChangeNodeState`, `TestNodeReincarnation`, `TestNetworkDBNodeLeave`, and island recovery tests validate map transitions, reaping timer setup, entry deletion, and address/port reincarnation handling.
