# sources/distributed-fs/openafs/src/vol/xfs_size_check.c

## Purpose
Implements a platform-specific utility that checks whether mounted `/vicep*` XFS partitions have inode sizes large enough for OpenAFS XFS attributes.

## Important APIs And Functions
On `AFS_SGI_XFS_IOPS_ENV`, `VerifyXFSInodeSize` tries to set the OpenAFS XFS attribute, inspects `F_FSGETXATTRA`, returns `VERIFY_OK`, `VERIFY_FIX`, or `VERIFY_ERROR`, and removes the temporary attribute. `CheckPartitions` scans mounted read-write filesystems via `setmntent`/`getmntent`, filters AFS partition prefixes and XFS filesystems, and accumulates partitions needing remake. `main` enforces root execution, prints `mkfs` guidance for bad partitions, and exits nonzero when fixes are needed. On other platforms, `main` prints that the utility only runs on XFS platforms.

## Control Flow And State
State is a dynamically grown global `partList` with `nParts` and `nAvail`. The utility treats inability to set attributes or inspect fsxattr as a verification error, but only `VERIFY_FIX` adds a partition to the remediation list.

## Persistence And Integration
It temporarily writes and removes `AFS_XFS_ATTR` on partition roots. It depends on mount-table APIs, XFS attribute syscalls, AFS partition naming, and `xfsattrs.h`.

## Risks And Test Signals
Risks include root-only behavior, reliance on SGI/XFS-specific fields such as `st_fstype` and `fsx_nextents`, old-style implicit `int main`, and possible stale `errno` reporting after cleanup. Test signals include running as non-root, mocked mount entries for non-AFS and read-only partitions, XFS partitions with/without inline attribute capacity, allocation growth tests, and non-XFS build behavior.
