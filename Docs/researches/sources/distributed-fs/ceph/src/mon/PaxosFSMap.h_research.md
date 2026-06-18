# sources/distributed-fs/ceph/src/mon/PaxosFSMap.h

## Purpose
`PaxosFSMap.h` provides a small mixin-style holder for the CephFS `FSMap` as managed by a Paxos-backed monitor service. It separates the current committed map from a leader-only pending map and keeps bounded in-memory history by epoch.

## Important APIs, Types, and Control Flow
`class PaxosFSMap` exposes `get_fsmap()` for committed state and `get_pending_fsmap()` for leader-only pending reads. Implementers must provide `is_leader()`. Protected helpers include `get_pending_fsmap_writeable()`, `create_pending()`, `prune_fsmap_history()`, `put_fsmap_history()`, history threshold setters/getters, `get_fsmap_history()`, and `decode()`. `create_pending()` copies the committed `fsmap`, increments its epoch, and returns it for mutation. `decode()` decodes a committed map, inserts it into history if within the retention window, and clears `pending_fsmap` to catch invalid post-commit access.

## State and Persistence Behavior
The class itself does not write to disk; persistence is provided by the owning Paxos service. Its state is the current `FSMap`, the next `pending_fsmap`, a map of historical `FSMap` instances keyed by epoch, and `history_prune_time`. Pruning intentionally keeps at least the newest history entry and preserves the map just before the retention threshold so "last seen" style queries remain meaningful.

## Dependencies and Integration Points
It depends on `mds/FSMap.h`, `mds/MDSMap.h`, Ceph assertions, and `real_clock`. It is intended for the MDS monitor/Paxos service path, where committed FSMap versions are decoded from Paxos values and leader updates work against `pending_fsmap`.

## Risks and Test Signals
Risks include accidental pending-map access on peons, history pruning that removes too much context, and epoch mutation outside the leader-only path. Tests should cover leader assertions, pending epoch increments, decode reset behavior, history insertion and pruning with multiple birth times, and retaining the last history element.
