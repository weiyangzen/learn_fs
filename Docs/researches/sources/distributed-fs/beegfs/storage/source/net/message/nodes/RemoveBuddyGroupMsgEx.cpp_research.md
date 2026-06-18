## sources/distributed-fs/beegfs/storage/source/net/message/nodes/RemoveBuddyGroupMsgEx.cpp

### Purpose
`RemoveBuddyGroupMsgEx.cpp` processes requests to remove a storage mirror buddy group mapping from this node, optionally checking that the mirror chunk directory is empty first.

### Important APIs, Types, And Functions
The file defines recursive helper `checkChunkDirRemovable(int dirFD)`, which walks a directory FD and returns success only if it contains no non-directory entries. `processIncoming()` validates storage node type, determines whether the local node owns the primary or secondary target of the group, opens the target mirror directory, runs the removability check, honors `force` and `checkOnly`, and calls `MirrorBuddyGroupMapper::unmapMirrorBuddyGroup()`.

### Control Flow, State, And Persistence
If the directory is empty, or not empty but `force` is set, the handler returns success and may unmap the group unless `checkOnly` is set. Persistent state mutation is the buddy group unmapping; chunk files are not deleted here.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on mirror buddy mappers, target mapper, storage targets, directory FDs, and `RemoveBuddyGroupRespMsg`. Risks include recursive FD handling, not closing nested `openat()` FDs before recursion returns, forced unmap with remaining chunks, and local ownership resolution if mapper data is stale. Tests should cover non-storage type, group not mapped locally, missing target, empty tree, nonempty tree, force, checkOnly, and stat/open failures.
