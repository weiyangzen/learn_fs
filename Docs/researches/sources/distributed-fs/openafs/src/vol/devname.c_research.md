# sources/distributed-fs/openafs/src/vol/devname.c

Purpose: legacy non-NAMEI helper for mapping a mounted `/vicep*` partition's device number back to a block device basename and for deriving raw character-device paths. It is excluded under `AFS_NAMEI_ENV`.

Important APIs/types/functions: `vol_DevName(dev_t adev, char *wpath)` scans the platform mount database, filters for writable `/vicep` partitions, stats candidate mountpoints, compares `st_dev` with `adev`, and returns the device basename in static storage. If `wpath` is non-NULL, it also copies the parent directory of the device path. `afs_rawname(char *devfile)` walks backward through a device path, inserting `r` after each directory separator until it finds an existing character device.

Control flow: `vol_DevName` has separate mount-iteration branches for AIX `getmount`, Solaris `MNTTAB`, SGI/Sun/HPUX `getmntent`, and BSD-style `getfsent`. For each record it rejects read-only, remote, removable, non-UFS, or non-`/vicep` entries according to platform checks, then compares the root inode and device number. `afs_rawname` repeatedly builds candidate raw names and returns on the first `S_ISCHR` stat match.

State and persistence: both functions return pointers into static buffers (`pbuffer` and `rawname`), so callers must copy results before the next call. No files are modified. Mount-table and device-node state are external runtime dependencies.

Dependencies: platform mount headers, filesystem headers, `ihandle.h`, `partition.h`, `VICE_PARTITION_PREFIX`, `ROOTINO`, and `OS_DIRSEPC`. The code is deeply conditional for old server platforms.

Integration points: used by inode-based salvager and volume utilities that need raw device access for `ListViceInodes`. `listinodes.c` calls `afs_rawname` in generic non-NAMEI scanning. The `wpath` output is later used to rebuild raw device paths.

Risks: static buffers and `strcpy`/`strcat` assume short device paths and are not thread-safe. Mount-table filtering is conservative and old-platform-specific; newer filesystem naming can be missed. `vol_DevName` intentionally ignores non-`/vicep` partitions, which is correct for AFS partitions but surprising for generic callers. Failure paths may leak open mount table handles on early returns in some platform branches.

Test signals: platform-specific tests should mock or run against mount tables containing writable `/vicep` entries, read-only entries, non-AFS mounts, matching and non-matching `st_dev`, device names with and without directory separators, and raw-device candidates that exist only at different path depths.
