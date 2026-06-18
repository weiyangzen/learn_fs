# sources/distributed-fs/lizardfs/src/protocol/directory_entry.h

Purpose: Defines serializable directory listing entries used in master-to-client getdir responses. It keeps both a legacy format and a newer indexed format.

Important APIs/types/functions: `legacy::DirectoryEntry` with `inode`, `name`, and `Attributes`; non-legacy `DirectoryEntry` with `index`, `next_index`, `inode`, `name`, and `Attributes`; `LIZARDFS_DEFINE_SERIALIZABLE_CLASS`.

Control flow: There is no executable control flow beyond generated serialization methods. Consumers deserialize vectors of entries from packet payloads.

State and persistence: Represents transient directory entries in network messages. It mirrors metadata attributes but is not a persistence format by itself.

Dependencies and integration: Depends on `common/attributes.h` and serialization macros. Used by `matocl::fuseGetDirLegacy` and `matocl::fuseGetDir` responses in `matocl.h`.

Risks and test signals: Compatibility risk is between legacy and indexed response versions; callers must select the correct packet version before deserializing. No direct unit test in this subset targets this struct alone.
