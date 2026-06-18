# sources/distributed-fs/lizardfs/src/master/filesystem_xattr.cc

Purpose: implements in-memory extended attribute storage operations and checksum maintenance for master metadata.

Important APIs/types/functions: `xattr_setattr()` creates, replaces, or removes an xattr with create-only/replace-only/remove modes; `xattr_getattr()` returns a pointer and length for an attribute value; `xattr_listattr_leng()` returns list size and an inode-entry cookie; `xattr_listattr_data()` copies null-terminated names; `xattr_removeinode()` removes all xattrs for an inode; `xattr_recalculate_checksum()` rebuilds global xattr checksum; `xattr_checksum_add_to_background()` participates in background checksum updates.

Control flow: set operations validate value/name lengths, find or create the inode hash entry, find the data entry by `(inode,name)`, enforce mode semantics, update linked lists and aggregate name/value lengths, and adjust checksums. Removal unlinks from both inode-local and global data hash chains and deletes the entry. Listing first locates inode aggregate data, then copies each name plus null terminator.

State and persistence behavior: state lives in `gMetadata->xattr_inode_hash`, `gMetadata->xattr_data_hash`, per-entry allocation, per-entry checksum, and `gMetadata->xattrChecksum`. Persistence is handled by `xattr_store()`/`xattr_load()` in `filesystem_store.cc`.

Dependencies/integration: depends on checksum helpers, `gChecksumBackgroundUpdater`, hash combine logic, LizardFS xattr size constants, and metadata singleton. Filesystem operations call these helpers when servicing xattr client requests or deleting inodes.

Risks and test signals: values returned by `xattr_getattr()` are internal pointers, so callers must not outlive mutation/removal. `xattr_listattr_leng()` adds to `*xasize` rather than resetting it, so callers must initialize the output. Manual memory and two linked-list indexes require exact unlinking. Tests should cover create/replace/remove modes, empty values, max-name/list/value bounds, checksum changes and recalculation equality, inode deletion cleanup, and list buffer content.
