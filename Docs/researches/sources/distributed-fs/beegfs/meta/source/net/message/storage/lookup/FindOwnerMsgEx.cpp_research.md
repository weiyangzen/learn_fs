<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindOwnerMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindOwnerMsgEx.cpp

## Purpose
Handles path-component owner discovery for metadata clients, returning the deepest known `EntryInfoWithDepth` and status so clients can route later operations to the correct metadata node or buddy group.

## Important APIs, Types, and Functions
`processIncoming()` special-cases depth zero as root owner lookup, otherwise calls `findOwner()`, sends `FindOwnerRespMsg`, and updates `MetaOpCounter_FINDOWNER`. `findOwner()` iterates path components from `currentDepth` to `searchDepth`, references each current directory, calls `MetaStore::getEntryData()`, updates `outInfo`, and stops once ownership leaves the local node/local buddy group.

## Control Flow, State, and Persistence
This is read-only. It follows local path components until it either reaches a missing entry, a nonlocal owner, or the requested depth. `DYNAMICATTRIBSOUTDATED` is accepted as a successful lookup for routing purposes. If a previously claimed local directory cannot be referenced, it returns success if a prior component was found, otherwise `PATHNOTEXISTS`.

## Dependencies and Integration Points
Depends on `RootDir`, `MetaStore`, `EntryInfoWithDepth`, `Path`, buddy group mapping, node op stats, and common find-owner response messages.

## Risks and Test Signals
Risks include races with deletes during traversal, stale ownership after concurrent moves, and correct mirrored owner comparison against group ID rather than node ID. Tests should cover root lookup, missing root owner, partial local traversal, remote handoff, dynamic-attrib success, and deleted-directory race behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindOwnerMsgEx.cpp -->
