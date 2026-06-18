<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindLinkOwnerMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindLinkOwnerMsgEx.cpp

## Purpose
Implements a legacy reverse-lookup helper that tries to find the parent/owner information for an entry ID, primarily for `fhgfs-ctl` reverse lookup mode.

## Important APIs, Types, and Functions
`processIncoming()` reads `entryID`, tries `MetaStore::referenceLoadedFile()` first, then `MetaStore::referenceDir()`, sends `FindLinkOwnerRespMsg(result, parentNodeID, parentEntryID)`, and releases any referenced object.

## Control Flow, State, and Persistence
This is a read-only lookup. It does not scan unloaded file metadata and has TODO comments noting limitations: the old caller does not send a parent ID, buddy mirroring is not handled, and the mode may no longer be used.

## Dependencies and Integration Points
Depends on `Program`, `MetaStore`, loaded file handles, directory parent info, and `FindLinkOwnerRespMsg`. It is separate from normal path lookup and does not update op counters.

## Risks and Test Signals
The function can produce incomplete results for unloaded files and buddy-mirrored metadata. Tests should treat it as best-effort legacy behavior, covering loaded file success, directory success, missing entry, and mirrored-entry limitations if retained.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindLinkOwnerMsgEx.cpp -->
