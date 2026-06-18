# sources/distributed-fs/beegfs/client_module/source/common/toolkit/MetadataTk.c

## Purpose
Implements metadata helper routines used by VFS-facing create and root-entry paths in the BeeGFS client module. `CreateInfo_init` normalizes create parameters, ownership, mode/umask, preferred targets, storage-pool defaults, and file-event pointers into a single request object. `MetadataTk_getRootEntryInfoCopy` constructs a heap-backed `EntryInfo` for the BeeGFS root directory using the metadata node store root owner.

## Important APIs and control flow
`CreateInfo_init` is compiled with different signatures for idmapped mounts, user namespace mounts, and legacy kernels. It computes `newMode`, maps current fsuid/fsgid through mount/superblock namespaces when enabled, applies SGID or BeeGFS `grpid` inheritance from the parent inode, fills preferred target lists from `App`, and initializes an invalid storage pool. `MetadataTk_getRootEntryInfoCopy` duplicates empty parent/name strings plus `META_ROOTDIR_ID_STR`, calls `EntryInfo_init`, and returns whether the root owner is valid.

## State, dependencies, integration
The file depends on `App`, mount config, Linux credential/idmap helpers, `NodeStoreEx`, `EntryInfo`, `StoragePoolId`, and `StringTk`. It does not persist data, but it prepares state later serialized into metadata messages.

## Risks and test signals
Ownership mapping is kernel-version-sensitive; tests should cover idmapped, userns, SGID, `grpid`, and legacy paths. Root entry callers must free duplicated `EntryInfo` values. `parentDirInode == NULL` falls back to creator gid and init/superblock namespace behavior, so create paths should ensure expected parent context.
