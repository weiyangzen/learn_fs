# sources/distributed-fs/ceph-client/include/linux/pseudo_fs.h

Purpose: declares the setup helper and context data for simple pseudo filesystems that need an internal superblock rather than a full mountable disk-backed filesystem.

Important APIs and types: `struct pseudo_fs_context` carries superblock operations, export operations, xattr handlers, dentry operations, magic number, and superblock dentry flags. `init_pseudo()` initializes an `fs_context` for a pseudo filesystem and returns the pseudo context.

Control flow: a pseudo filesystem init path calls `init_pseudo(fc, magic)`, fills or uses the returned context, and VFS mount/setup code consumes those operations to create a pseudo superblock.

State and persistence: state is per mount/context and superblock runtime metadata. Pseudo filesystems normally expose kernel objects and do not persist data.

Dependencies and integration points: depends on VFS `fs_context`, superblock, dentry, export, and xattr operation structures. Used by internal filesystems that need VFS semantics without backing storage.

Risks and test signals: risks include wrong magic values, missing operation callbacks for expected VFS behavior, and lifetime bugs in context allocation. Test mount/init failure paths, superblock teardown, xattr/dentry behavior, and export operation users if configured.
