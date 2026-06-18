<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/bcheckrc-hp_ux110 -->
# sources/distributed-fs/openafs/src/vfsck/bcheckrc-hp_ux110

## Purpose
HP-UX 11.0 variant of the AFS boot check wrapper. It performs the same `/etc/fstab` AFS partition discovery and repair orchestration as `bcheckrc`, but uses the HP-UX 11.0 HFS fsck invocation shape for its initial cleanliness probe.

## Important APIs, Types, And Functions
The only local function is `afs_partitions_clean`. It uses `/sbin/awk`, `/sbin/fs/hfs/fsck -m`, `/sbin/fs/afs/fsck -P -f`, `/sbin/stty`, and the interactive `ROOTSHELL` fallback. The significant delta from `bcheckrc` is that the probe command omits `-P` when calling `/sbin/fs/hfs/fsck -m`.

## Control Flow
The script initializes terminal settings, scans fstab for `afs` entries, and checks each partition with HFS fsck. Dirty or unclean partitions are repaired with AFS fsck in preen/force mode. If automatic repair returns nonzero, it prints an audible warning and opens `/sbin/sh` for root to run manual fsck, then continues.

## State And Persistence
Persistent effects are limited to filesystem repairs made by the invoked fsck command or by the manual root shell. The script’s own state is transient shell variables such as `serverPartition` and `name`.

## Dependencies And Integration Points
It is tied to HP-UX 11.0 boot scripts and HFS command behavior. The AFS fsck binary is expected at `/sbin/fs/afs/fsck`, and the generic boot script is expected to call this file as the filesystem-type-specific pre-mount hook.

## Risks And Test Signals
The main compatibility risk is command-line drift between HP-UX releases, which this variant addresses by changing the HFS probe. The same operational risks as `bcheckrc` remain: manual boot interruption, hard-coded paths, and always returning success to the caller. Test signals should compare HP-UX 11.0 clean/dirty fstab entries with the non-11.0 script behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/bcheckrc-hp_ux110 -->
