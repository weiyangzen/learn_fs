## sources/distributed-fs/beegfs/meta/source/session/SessionFile.h

Purpose: defines the persisted and live state for one open file within a client session.

Important APIs/types: constructor stores a `MetaFileHandle`, access flags, and `EntryInfo`. Serialization covers `accessFlags`, `sessionID`, `entryInfo`, and `useAsyncCleanup`, but not the live inode handle. Methods expose access flags, session ID, inode handle access/release, async-cleanup marking, entry info, parent-entry update, equality, and `relinkInode`.

Control flow: normal open paths create `SessionFile` with a live inode. Close/removal paths may release the inode and perform cleanup. Recovery creates default `SessionFile`, deserializes fields, then relinks the inode.

State and persistence behavior: `sessionID` is the file-handle ID within a client session. `useAsyncCleanup` marks that a close/removal happened while the file was referenced and cleanup must run after the final release. The inode pointer is process-local and must be rebuilt.

Dependencies and integration points: uses `Path`, `EntryInfo`, `DirInode`, `FileInode`, `MetaFileHandle`, and `MetaStore`.

Risks: `getUseAsyncCleanup`/`setUseAsyncCleanup` are intentionally unsynchronized because the flag only transitions false-to-true; callers must preserve that invariant. `releaseInode` moves the handle out and leaves the object without a valid inode.

Test signals: serialization round trip, async cleanup transition, parent ID updates after rename, move/release of inode handles, and recovery relinking.
