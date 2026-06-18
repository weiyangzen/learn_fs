## sources/distributed-fs/beegfs/meta/source/storage/DirEntry.h

Purpose: declares the `DirEntry` class, which represents a directory entry copy containing user-visible name, on-disk dentry metadata, and optional inlined file-inode data.

Important APIs/types: constants define unlink modes for ID, filename, or both. Constructors create initialized entries or name-only load targets. Static APIs load/create entries from files and remove file/dir dentries. Mutators include `setOwnerNodeID`, `setFileInodeData`, buddy-mirror flag setters, dentry feature flag mutation, and `unsetInodeInlined`. Accessors expose entry ID, name, type, owner, feature flags, `EntryInfo`, and `FileInodeStoreData`. Serialization delegates to `DiskMetaData`.

Control flow: callers generally load a `DirEntry` copy, mutate it, and store it back; instances are not shared and have no internal mutex. `removeFileDentry` deletes by name first and only removes the ID file after successful name unlink to avoid racing with rename. `removeDirDentry` removes only the name path.

State and persistence behavior: persistent data is in `DentryStoreData` and optional `FileInodeStoreData`. `getEntryInfo` maps dentry flags to `ENTRYINFO_FEATURE_INLINED` and `ENTRYINFO_FEATURE_BUDDYMIRRORED`. Owner-node updates are disallowed for inlined inodes because ownership is stored in inode data instead.

Dependencies and integration points: friends `MetaStore`, `DirEntryStore`, `DirInode`, `FileInode`, debug and recreate message handlers. Depends on `StorageTkEx`, `DiskMetaData`, `MetadataEx`, and `FileInodeStoreData`.

Risks: no synchronization because dentries are copied per caller; correctness relies on external directory/inode locks. Friend classes can bypass encapsulation. Feature flags must remain consistent with serialized inode data; mismatches can break recovery or fsck.

Test signals: `EntryInfo` flag propagation, owner update rejection for inlined inode, unlink flag combinations, serialize/deserialize through `DiskMetaData`, hardlink/non-inlined conversion, and buddy-mirror flag inheritance.
