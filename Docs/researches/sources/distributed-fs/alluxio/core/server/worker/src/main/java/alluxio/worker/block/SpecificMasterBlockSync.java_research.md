## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/SpecificMasterBlockSync.java

### Purpose
`SpecificMasterBlockSync` is the heartbeat executor for one specific block master in all-master registration mode. It asynchronously registers/re-registers the worker with that master, sends block heartbeat reports, handles master commands, and retries indefinitely on soft failures.

### Important APIs and Types
- Constructor takes `BlockWorker`, `BlockMasterClient`, and `BlockHeartbeatReporter`.
- `heartbeat(long)` performs registration if needed and sends heartbeat reports.
- `registerWithMasterInternal()` notifies worker id, obtains store meta, acquires registration lease, registers, updates state, and increments registration metric.
- `isRegistered()` exposes registration state.
- `handleMasterCommand(Command)` handles Free/Register/Nothing/Delete/Unknown commands.
- Nested `Metrics` contains registration success counter.

### Control Flow
When state is `NOT_REGISTERED`, heartbeat calls `registerWithMaster`, which clears pending heartbeat deltas and retries registration forever. Successful registration sets state to `REGISTERED`. For normal heartbeats, the sync generates and clears a report, calls helper heartbeat with current store meta and command callback, and updates last-success time on success. On heartbeat failure, if the report is too large it discards it and forces full re-registration; otherwise it merges the report back for retry. `Free` commands enqueue async block removal, while `Register` resets state.

### State and Persistence
State includes master address/client, worker id/address, worker state, async block remover, sync helper, last successful heartbeat timestamp, and heartbeat reporter. Persistent effects are through master registration/heartbeat RPCs and local block removals requested by master.

### Dependencies and Integration Points
Created by `BlockSyncMasterGroup`; uses `BlockMasterSyncHelper`, `AsyncBlockRemover`, `BlockWorker` metadata, master client RPCs, retry policies, and command protobufs.

### Risks
- Registration obtains full store metadata; TODO notes concurrent registration to all masters can cause OOM on large workers.
- Indefinite retries can block the heartbeat thread for a down master.
- On large failed reports, deltas are discarded and correctness relies on subsequent full registration.
- State is volatile but class is marked not thread-safe; external access should remain limited.

### Test Signals
`SpecificMasterBlockSyncTest` covers registration, heartbeat, re-registration, failure behavior, lease timeout behavior, and command handling. `TestSpecificMasterBlockSync` provides test hooks for heartbeat failure and registration counts.
