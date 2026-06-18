# sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveFsIDsMsgEx.cpp

## Purpose
Retrieves dentry-by-ID files incrementally for fsck.

## Important APIs And Types
processIncoming pages through content dirs and #fSiDs# directories, skips buddy-mirrored retrieval on secondary/local group 0, references or temporarily creates DirInode, calls listIDFilesIncremental, stats each ID file, builds FsckFsID records, advances cursors, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Read-only except temporary in-memory inode creation. Observes #fSiDs# hard links and stat metadata.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
readOutIDs controls maxOutIDs. listRes errors are logged but already-read names are still processed. Secondary buddy skip must match fsck coordinator expectations.

## Test Signals
Test pagination, missing parent temp inode, list error, stat failure, buddy secondary skip, and cursor resume.
