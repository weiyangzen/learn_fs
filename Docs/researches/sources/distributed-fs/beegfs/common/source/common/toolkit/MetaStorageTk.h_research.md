<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MetaStorageTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MetaStorageTk.h

Purpose: Provides metadata storage path helper functions.

Important APIs/types: `MetaStorageTk` exposes helpers to build inode paths, hash values, dentry paths, and dentry-ID paths using `StorageTk` hashing rules and metadata directory depth constants.

Control flow/state/persistence: Pure path computation; no disk IO in this header.

Dependencies/integration: Depends on `StorageTk` and metadata path constants. Used by metadata server storage layout code and tools.

Risks/test signals: Path hashing must match on-disk layout. Tests should use golden paths for representative inode and dentry IDs, including edge-length names and nested hash directory expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MetaStorageTk.h -->
