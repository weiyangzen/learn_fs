## sources/distributed-fs/beegfs/meta/source/storage/MkFileDetails.h

Purpose: Provides a compact value object carrying file-creation inputs through metadata create paths.

Important APIs/types/functions: `MkFileDetails` stores `newName`, optional `newEntryID`, `userID`, `groupID`, `mode`, `umask`, and `createTime`. The constructor initializes the normal create fields, while `setNewEntryID()` is used for mirrored secondary operations that must reuse the primary's entry ID.

Control flow: Header-only data carrier; callers build it before entering create logic.

State and persistence: It does not persist directly, but its fields become dentry/inode metadata and POSIX mode ownership on disk. `newEntryID` changes identity allocation behavior during mirroring.

Dependencies and integration: Used by metadata storage operations that create file dentries and inodes. It depends on standard strings and BeeGFS common typedefs via surrounding includes.

Risks and test signals: Misusing `newEntryID` on primaries or ignoring it on secondaries would break mirrored identity consistency. Tests should cover create on primary, mirrored replay on secondary, and mode/umask propagation.
