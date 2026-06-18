## sources/distributed-fs/beegfs/meta/source/session/SessionStore.cpp

Purpose: manages all client sessions for a metadata server, including persistence to disk, recovery, mirror/session synchronization, open-file cleanup, and file-inode lock-state save/restore.

Important functions: `referenceSession`, `releaseSession`, `syncSessions`, `getAllSessionIDs`, `serialize`, `deserialize`, `deserializeLockStates`, `deserializeFromBuf`, `loadFromFile`, `serializeToBuf`, `saveToFile`, `clear`, `removeSessionUnlocked`, and `operator==`. The file format starts with `SESSION_FORMAT_HEADER` and `SESSION_FORMAT_VERSION`.

Control flow: `referenceSession` optionally creates a session and returns a referenced object. `syncSessions` compares sorted current sessions with a sorted master node list, removing sessions not present and reporting referenced unremovable sessions. Serialization writes sessions first, then a placeholder count and deduplicated file-inode lock states collected from all open session files. `serializeToBuf` does a sizing pass and a writing pass. Loading reads the file into memory under the store mutex, deserializes sessions, relinks open inodes, then restores inode lock states.

State and persistence behavior: session maps are persisted to a session file, including each session's files and mirror process state. Live object references are not persisted. File inode lock state is separately serialized once per unique inode. Recovery relinks inodes through `MetaStore` before applying lock states. `clear` removes sessions and closes open files but intentionally avoids unlinking disposed files or storage-server chunks during mirror resync secondary cleanup.

Dependencies and integration points: uses `Program::getApp()` for `MetaStore`, POSIX file I/O, BeeGFS serialization, `ObjectReferencer`, `NodeHandle` master lists, and `EntryLockStore`.

Risks: `loadFromFile` returns false on empty file without closing the opened fd because it returns before `err_stat`; this is a descriptor leak in that branch. `clear` logs a referenced-session error using `sessionIt->first` after the iterator was post-incremented, which can report the wrong ID or risk end-iterator use. `deserializeLockStates` dereferences `inode` after `metaStore.referenceFile(&info)` without checking `referenceRes`/null, so corrupt or stale lock-state entries can crash. `saveToFile` truncates the target before serialization succeeds, so allocation/serialization failure can destroy the previous session file.

Test signals: round-trip session persistence with lock states, malformed header/version, empty session file descriptor behavior, missing inode in lock-state restore, duplicate inode lock-state deduplication, syncSessions with referenced/unreferenced sessions, and save failure after truncation.
