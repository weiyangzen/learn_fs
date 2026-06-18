## sources/distributed-fs/beegfs/storage/source/net/message/nodes/SetMirrorBuddyGroupMsgEx.cpp

### Purpose
`SetMirrorBuddyGroupMsgEx.cpp` handles storage mirror buddy group mapping updates from management.

### Important APIs, Types, And Functions
`processIncoming()` ignores non-storage node type requests by returning success, then maps storage buddy groups with `MirrorBuddyGroupMapper::mapMirrorBuddyGroup(buddyGroupID, primaryTargetID, secondaryTargetID, localNodeID, allowUpdate, &newBuddyGroupID)`. It acknowledges or sends `SetMirrorBuddyGroupRespMsg`.

### Control Flow, State, And Persistence
The storage buddy group mapper is mutated for storage-node requests. The response includes the map result and possibly assigned new group ID.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `MirrorBuddyGroupMapper`, local node ID, common response message, and acknowledgement support. Risks include silently succeeding for meta buddy group requests on storage and caller interpretation of updated group IDs. Tests should cover initial map, allowed update, disallowed update, non-storage request, ackable request, and invalid target pairs.
