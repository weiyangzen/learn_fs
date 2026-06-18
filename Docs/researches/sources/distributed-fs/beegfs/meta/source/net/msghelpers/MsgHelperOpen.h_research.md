<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperOpen.h -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperOpen.h

## Purpose
Declares static open helpers for metadata file open operations.

## Important APIs, Types, and Functions
`MsgHelperOpen::openFile()` is public and returns a `MetaFileHandle` on success. Private helpers `openMetaFile()` and `openMetaFileCompensate()` wrap `MetaStore` open/close behavior. The class is non-instantiable.

## Control Flow, State, and Persistence
The public signature exposes quota, access-check bypass, message user ID, output inode handle, and secondary flag, making callers responsible for later session insertion and close.

## Dependencies and Integration Points
Includes `EntryInfo`, `MetaStore`, and `MetadataEx`. Used by lookup-intent, explicit open messages, and session recovery.

## Risks and Test Signals
Tests should verify output handle is set only on success and that callers close or transfer ownership after successful open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperOpen.h -->
