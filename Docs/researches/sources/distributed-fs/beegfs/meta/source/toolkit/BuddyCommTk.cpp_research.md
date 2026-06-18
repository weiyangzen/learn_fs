## sources/distributed-fs/beegfs/meta/source/toolkit/BuddyCommTk.cpp

Purpose: Implements metadata-server mirror-buddy communication helpers, especially persistent "buddy needs resync" state and primary-side resync start decisions.

Important APIs/types/functions: Internal state uses `.buddyneedsresync` as a `PreallocatedFile<uint8_t>` with flags for required/not-required and unacknowledged changes. Public functions are `prepareBuddyNeedsResyncState()`, `checkBuddyNeedsResync()`, `setBuddyNeedsResync()`, and `getBuddyNeedsResync()`. Internal `setBuddyNeedsResyncComm()` sends `SetTargetConsistencyStatesMsg` to mgmtd and schedules retries through `TimerQueue`.

Control flow: `setBuddyNeedsResync()` writes an unacked state to disk, cancels pending retry, and immediately tries mgmtd communication. On failure, a five-second timer calls `retrySetBuddyNeedsResyncComm()`. `checkBuddyNeedsResync()` runs on primaries, confirms the local node is `GOOD`, reads the buddy state, and starts a metadata `BuddyResyncer` when the online buddy is `NEEDS_RESYNC`.

State and persistence: Persistent byte file survives restart and carries unacknowledged mgmtd updates. Global lock protects the file and retry handle. On restart, `prepareBuddyNeedsResyncState()` enqueues immediate retry if the file has an unacked flag.

Dependencies and integration: Uses `Program::getApp()` to reach mgmt nodes, meta buddy group mapping, meta state store, internode syncer, timer queue, and buddy resyncer. It sends management-node target consistency messages and depends on `PreallocatedFile`.

Risks and test signals: Global state makes tests/order sensitive. `setBuddyNeedsResync(const std::string& path, ...)` ignores `path`, which is harmless but misleading. Failure modes include stale unacked file state, retry callback lifetime issues, and incorrect local primary detection. Tests should simulate mgmtd failures/retries, restart with unacked state, primary/secondary role changes, and external resync completion.
