<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncRawInodesMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncRawInodesMsgEx.h

## Purpose
Declares the serializable raw-inode resync stream message.

## Important APIs, Types, and Functions
`ResyncRawInodesMsgEx` derives from `NetMessageSerdes<ResyncRawInodesMsgEx>`, serializes `basePath`, `hasXAttrs`, and `wholeDirectory`, overrides `processIncoming()`, and declares helpers for stream, packet, inode, dentry, xattr, and cleanup processing.

## Control Flow, State, and Persistence
The message object carries stream scope (`basePath`) and mode flags. `inodesWritten` is transient state used only for whole-directory cleanup after all packets are processed.

## Dependencies and Integration Points
Includes `NetMessage`, `Path`, and `IncompleteInode`. It is part of the metadata buddy-resync protocol rather than normal mirrored message replay.

## Risks and Test Signals
Constructor/serialization compatibility is important because the rest of the payload is streamed manually after the message header. Tests should verify serialization of mode flags and that empty/default construction works for receive-side deserialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncRawInodesMsgEx.h -->
