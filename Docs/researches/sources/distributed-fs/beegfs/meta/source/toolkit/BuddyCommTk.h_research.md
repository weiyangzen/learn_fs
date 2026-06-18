## sources/distributed-fs/beegfs/meta/source/toolkit/BuddyCommTk.h

Purpose: Declares metadata mirror-buddy communication utilities.

Important APIs/types/functions: `prepareBuddyNeedsResyncState(Node&, const MirrorBuddyGroupMapper&, TimerQueue&, NumNodeID)` initializes persistent resync state. `checkBuddyNeedsResync()` polls state and starts resyncs. `setBuddyNeedsResync(const std::string&, bool)` requests mgmtd state changes. `getBuddyNeedsResync()` returns the local persisted flag.

Control flow: Header only declares the operations implemented in the cpp.

State and persistence: API exposes operations around the `.buddyneedsresync` persistent file and mgmtd consistency states.

Dependencies and integration: Requires BeeGFS `Node`, `MirrorBuddyGroupMapper`, `TimerQueue`, `NumNodeID`, and storage error types. Used by metadata app startup, internode sync, and mirroring code.

Risks and test signals: The unused `path` parameter on `setBuddyNeedsResync()` suggests an API inherited from storage-side code. Tests should verify callers do not expect per-path behavior.
