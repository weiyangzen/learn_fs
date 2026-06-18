<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/bcheckrc -->
# sources/distributed-fs/openafs/src/vfsck/bcheckrc

## Purpose
Boot-time HP-UX AFS filesystem check wrapper installed as `/sbin/fs/afs/bcheckrc`. It is intended to be called by the generic `/sbin/bcheckrc` path before AFS server partitions are mounted. Its job is to discover `/etc/fstab` entries whose filesystem type is `afs`, run the host HFS fsck in metadata-check mode, and invoke the AFS-specific fsck when a server partition is not clean.

## Important APIs, Types, And Functions
The script is a Bourne shell program with one local function, `afs_partitions_clean`. It uses `/sbin/awk` to parse `/etc/fstab`, `/sbin/fs/hfs/fsck -m -P` to test partition cleanliness, `/sbin/fs/afs/fsck -P -f` to repair AFS server partitions, `/sbin/stty` to establish a sane interactive terminal mode, and `ROOTSHELL=/sbin/sh` for manual repair fallback.

## Control Flow
Startup sets terminal modes, defines `ROOTSHELL`, then calls `afs_partitions_clean`. The function iterates over un-commented fstab records with field 3 equal to `afs`. For each matching device, it probes the partition with HFS fsck. A nonzero probe result triggers `fsck -P -f` through the AFS wrapper; success prints a fixed message, and any other result drops root into an interactive shell, then resumes the boot script after EOF. A flag records whether any AFS partitions were seen, and the script always exits 0 after the scan.

## State And Persistence
The script reads `/etc/fstab`, may repair on-disk AFS/HFS server partition metadata through the fsck binary, and may leave repair side effects on the checked devices. It does not persist its own state. The shell fallback can perform arbitrary manual changes because it runs as root during boot.

## Dependencies And Integration Points
This file integrates HP-UX boot sequencing, `/sbin/fs/afs/fsck`, the host HFS fsck, and OpenAFS server partition conventions. It assumes AFS partitions are listed in `/etc/fstab` with type `afs` but are physically compatible with HFS fsck probing.

## Risks And Test Signals
Risks include brittle whitespace parsing of fstab, unconditional final exit 0 even after manual repair failures, boot blocking on a root shell, and the hard-coded line break inside the warning text. Useful tests are boot-script dry runs with no AFS partitions, clean partitions, dirty partitions fixed automatically, and fsck failures that require manual mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/bcheckrc -->
