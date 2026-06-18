# sources/distributed-fs/beegfs/meta/source/net/message/fsck/RecreateDentriesMsgEx.cpp

## Purpose
Recreates missing dentry-by-name links from existing dentry-by-ID files.

## Important APIs And Types
processIncoming iterates FsckFsID records, chooses local owner ID, builds ID and name paths, locks parent/name for mirrored entries, references parent dir, hard-links ID file to a name equal to the entry ID, reads the created DirEntry, builds FsckDirEntry and inlined FsckFileInode records if inode data is present, releases parent, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Persists hard links in the dentry namespace and reports reconstructed fsck objects.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
The original file name is lost and replaced with the ID. link failure can happen if target exists. Inlined inode data is expected because the ID file exists, but absence is only logged.

## Test Signals
Test successful recreation, missing parent, existing name, link failure, no inlined inode data, buddy-mirrored paths, and created inode fields.
