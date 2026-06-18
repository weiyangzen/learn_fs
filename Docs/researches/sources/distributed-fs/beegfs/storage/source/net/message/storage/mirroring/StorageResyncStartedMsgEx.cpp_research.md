<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.cpp

### Purpose
Responds to notification that storage resync started by dropping all mirrored local-file sessions for the target so stale mirror handles are not reused.

### Important APIs, Types, And Functions
processIncoming() reads targetID via getValue(), calls deleteMirrorSessions(), and replies with StorageResyncStartedRespMsg. deleteMirrorSessions() walks SessionStore session IDs, references each Session, and calls SessionLocalFileStore::removeAllMirrorSessions(targetID).

### Control Flow
Control flow is a best-effort sweep over sessions. It tolerates sessions disappearing between getAllSessionIDs() and referenceSession().

### State, Persistence, And Dependencies
Runtime session state is mutated by erasing mirror sessions for the target. No session store file is directly persisted here, though later session persistence will reflect the removal. Depends on Program/App, SessionStore, Session, SessionLocalFileStore, NumNodeIDList, and common mirroring response message.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include removing sessions without closing underlying handles in removeAllMirrorSessions(), depending on store semantics, and racing with in-flight IO that still holds shared pointers to SessionLocalFile objects.

### Test Signals
Test signals include multiple client sessions, disappearing sessions during sweep, only mirrored sessions removed, non-mirrored sessions preserved, and subsequent mirror writes opening fresh handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.cpp -->
