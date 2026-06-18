# sources/distributed-fs/beegfs/meta/source/net/message/fsck/RecreateFsIDsMsgEx.cpp

## Purpose
Recreates dentry-by-ID hard links from existing dentry-by-name files.

## Important APIs And Types
processIncoming iterates FsckDirEntry records, computes ID and name paths, locks parent/name/file IDs, unlinks any old ID link unless ENOENT, creates a hard link from name to ID, collects failed entries, and responds.

## Control Flow
Handlers run synchronously in processIncoming: read inherited request fields, take buddy-mirror locks where needed, call MetaStore/filesystem/worker helpers, collect failed or created fsck objects, send the matching response, and return true unless protocol-invalid input is detected.

## State And Persistence
Persists hard links under #fSiDs# directories.

## Dependencies And Integration Points
Depends on Program/App MetaStore access, fsck model classes, MetaStorageTk path helpers, EntryLockStore locks for buddy-mirrored metadata, response message types, and in some cases worker fan-out to storage targets.

## Risks And Edge Cases
The code locks even non-buddy entries using entryLockStore, unlike many fsck handlers that lock only mirrored entries. A missing name file fails recreation. Removing an old faulty link is destructive but intended.

## Test Signals
Test successful relink, old ID link absent/present, unlink error, name link missing, buddy and non-buddy entries, and response failures.
