# sources/distributed-fs/ceph/src/mon/Paxos.h

## Purpose
`Paxos.h` declares Ceph monitor Paxos, the replication substrate used by monitor services. It documents the monitor store layout: the Paxos prefix stores `first_committed`, `last_committed`, and one opaque encoded transaction per committed version. A committed Paxos value is also decoded and appended to the same `MonitorDBStore::Transaction` that records the Paxos version, so service state and Paxos metadata become durable atomically.

## Important APIs, Types, and Control Flow
The central type is `class Paxos`, owned by `Monitor` and friend to `PaxosService`. Its public surface includes election lifecycle (`init`, `restart`, `leader_init`, `peon_init`), message dispatch (`dispatch`), state sharing (`share_state`, `store_state`), read APIs (`is_readable`, `read`, `read_current`, `wait_for_readable`), write APIs (`is_writeable`, `get_pending_transaction`, `queue_pending_finisher`, `trigger_propose`), and trim/plug controls. The state machine constants cover recovery, active, updating, writing, refresh, and shutdown variants. Private handlers implement phase-1 collect/last handling, phase-2 begin/accept/commit handling, lease extension and timeout handling, and durable commit finish/abort paths.

## State and Persistence Behavior
Persistent state is version-based and stored through `MonitorDBStore`. Important volatile fields track proposal numbers, committed bounds, accepted proposal numbers, peer first/last committed versions, read lease expiry, pending and committing finishers, and timeout events. `decode_append_transaction()` is the key persistence helper: it decodes a service transaction from a bufferlist and appends it into a Paxos transaction. Trimming is guarded by config-derived minimums and `trimming`, while `extra_state_dirs` lets services such as OSD monitor register additional state areas.

## Dependencies and Integration Points
This header depends on monitor messaging (`MMonPaxos`, `MonOpRequest`), `MonitorDBStore`, Ceph contexts, perf counters, JSON formatting, clocks, config, and monitor types. It integrates with monitor elections, the monitor timer, monitor service transactions, peer state transfer, and perf counters identified by the `l_paxos_*` enum.

## Risks and Test Signals
Risks concentrate around state transitions, callback ordering, lease validity, atomic transaction composition, and trim safety. Tests should exercise single-monitor direct commits, multi-monitor collect/recovery with uncommitted accepted values, stale proposal rejection, lease timeout and lease ack timeout elections, read/write wait callbacks, durable transaction replay, and trim boundaries.
