# sources/distributed-fs/beegfs/meta/source/net/message/fsck/RetrieveDirEntriesMsgEx.cpp

## Purpose
Retrieves content directories, dentries, and inlined file inodes incrementally for fsck.

## Important APIs And Types
processIncoming uses hash/content offsets and currentContDirID to page through content dirs, skips buddy-mirrored retrieval on secondary/local group 0, references or temporarily creates DirInode, lists names, builds FsckDirEntry records with stat device/inode data, builds FsckFileInode records for inlined files including dynamic stat refresh fallback, emits contDir records when advancing dirs, and responds with cursors.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Read-only except temporary in-memory inode objects. It observes metadata dentries, inlined inode data, dynamic attribs, and stat device/inode numbers.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
readOutEntries is updated only when advancing to the next content dir, so maxOutEntries enforcement depends on entryNames size and loop structure. Damaged entries may be skipped with warnings. Secondary buddy nodes intentionally return empty.

## Test Signals
Test pagination across dirs, currentContDir resume, secondary buddy skip, missing parent temp inode, dynamic attribs outdated fallback, stat failure, inlined and non-inlined entries.
