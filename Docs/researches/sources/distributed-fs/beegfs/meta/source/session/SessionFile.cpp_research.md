## sources/distributed-fs/beegfs/meta/source/session/SessionFile.cpp

Purpose: implements equality and recovery relinking for a single open file session.

Important functions: `operator==` compares access flags, session ID, entry info, and async cleanup marker. `relinkInode` reopens the file through `MetaStore::openFile` with access-check bypass and stores the resulting `MetaFileHandle`.

Control flow: during session recovery, `SessionFileStore::relinkInodes` calls `SessionFile::relinkInode`. On success the in-memory handle is restored; on failure an error is logged and the session file can be removed by the caller.

State and persistence behavior: serialized `SessionFile` state omits the live `MetaFileHandle`; recovery reconstructs it from `EntryInfo` and access flags. `useAsyncCleanup` persists as a marker.

Dependencies and integration points: depends on `Program`, `MetaStore`, and storage file handle types. It integrates session persistence with metadata inode stores.

Risks: bypassing access checks is intentional for recovery, especially files in disposal directories, but it means recovery relies on stored session state being trusted. Equality does not compare the live inode handle.

Test signals: relink success/failure, disposal-directory locked file recovery, equality before/after serialization, and behavior when `EntryInfo` points to missing metadata.
