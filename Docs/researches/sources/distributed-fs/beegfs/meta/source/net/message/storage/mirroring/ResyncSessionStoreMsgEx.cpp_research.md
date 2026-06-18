<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncSessionStoreMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncSessionStoreMsgEx.cpp

## Purpose
Receives and installs a serialized mirrored session store during metadata buddy resync.

## Important APIs, Types, and Functions
`processIncoming()` calls `receiveStoreBuf()` with the short message timeout, handles out-of-memory and communication failures, clears `Program::getApp()->getMirroredSessions()`, deserializes the received buffer into the session store using `MetaStore`, and sends `ResyncSessionStoreRespMsg`.

## Control Flow, State, and Persistence
The operation replaces in-memory mirrored session state. It does not directly persist files, but deserialization references metadata inodes through `MetaStore`; failure after clearing means the secondary session store remains empty until another resync.

## Dependencies and Integration Points
Depends on `ResyncSessionStoreMsg` buffer helpers, `SessionStore::clear()` and `deserializeFromBuf()`, app config timeouts, mirrored sessions, `MetaStore`, and the resync response message.

## Risks and Test Signals
Risks include clearing good sessions before detecting bad serialized data, memory allocation failure, and metadata mismatches during session deserialization. Tests should cover receive failures, clear failure, bad buffer, successful restore, and behavior with open mirrored files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncSessionStoreMsgEx.cpp -->
