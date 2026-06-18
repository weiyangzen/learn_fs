## sources/distributed-fs/beegfs/meta/tests/TestSerialization.cpp

Purpose: Exercises serialization round trips for session stores and several metadata/storage value types.

Important APIs/types/functions: `sessionSerialization` serializes a populated `SessionStore`, deserializes into a clone, and compares equality. `initSessionStoreForTests()` builds many `FileInode`, `FileInodeStoreData`, `StatData`, `EntryInfo`, striping patterns, and `SessionFile` instances with edge and random values. Additional tests call `testObjectRoundTrip()` for `DynamicFileAttribs`, `ChunkFileInfo`, `EntryLockDetails`, and `RangeLockDetails`. Helpers fill target vectors and target chunk block maps.

Control flow: Session test first uses an unbuffered `Serializer` to compute size, then serializes to a buffer, deserializes, and compares. Object tests serialize, deserialize, reserialize, and compare byte buffers.

State and persistence: No disk persistence. It constructs heap-owned session/inode structures that become owned by session store/session files according to BeeGFS ownership conventions.

Dependencies and integration: Uses BeeGFS serialization framework, session store, inode/stat data, striping patterns (`Raid0`, `Raid10`, `BuddyMirror`), lock details, random utilities, and GoogleTest.

Risks and test signals: Random values improve range coverage but can make failures less reproducible. The large hand-built fixture tests backward-compatible field ordering indirectly, but does not use golden byte streams. Add fixed seed or golden compatibility vectors for migration-sensitive serialization changes.
