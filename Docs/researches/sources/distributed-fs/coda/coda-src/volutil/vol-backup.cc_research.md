## sources/distributed-fs/coda/coda-src/volutil/vol-backup.cc

Purpose: `vol-backup.cc` implements server-side backup-volume creation and refresh. It can create a new backup clone or update an existing backup clone in place to match a locked read-write/non-replicated volume.

Important APIs/types/functions: main RPC `S_VolMakeBackups` coordinates the operation. Helpers include `MakeNewClone`, `ModifyIndex`, `purgeDeadVnodes`, `updateBackupVnodes`, `deleteDeadVnode`, `cleanup`, and debug `checklists`. It reuses `VUCloneVolume`/`CloneVnode` from clone logic.

Control flow: `S_VolMakeBackups` initializes volutil, attaches the original, verifies type and that volutil holds the volume lock, then tries to attach the existing backup id. If no valid backup exists, `MakeNewClone` allocates/creates/clones a backup volume, deletes/renumbers old backup if present, and sets backup metadata. If a backup exists, it marks it unblessed/destroy-me, updates small and large vnode indexes to match the RW volume, copies the RW version vector, then blesses and updates both volumes. It releases volumes and unlocks the original at the end.

State and persistence behavior: heavily mutates RVM volume headers, vnode list structures, directory inode references, inode reference counts, backup id/date, blessed/destroyMe flags, and hash tables. Vnode updates are batched in transactions limited by `MaxVnodesPerTransaction`; inode decrements are delayed until after transaction commit to avoid abort inconsistencies.

Dependencies/integration points: depends on volutil initialization, volume locks, RVM transaction APIs, vnode index/list structures, inode operations (`idec`), directory inode refcounts, volume hash functions, `CloneVnode`, and Coda server globals.

Risks: correctness depends on the `cloned` bit and version-vector comparisons accurately identifying changed data and metadata. Many paths use `CODA_ASSERT`, so production corruption can abort. Lock identity is a magic IP address value (`5`). In-place update manipulates shared vnode structures and inode refcounts; transaction/inode ordering bugs can leak or prematurely delete data. Debug output may write `/vicepa/dcstest`.

Test signals: backup RW and non-replicated volumes with file creation/deletion/modification, directory changes, metadata-only changes, barren inodes, grown vnode lists, existing/absent old backups, and crash/restart around unblessed/destroyMe states. Verify inode refcounts, vnode counts, backup readability, and unlock behavior on errors.
