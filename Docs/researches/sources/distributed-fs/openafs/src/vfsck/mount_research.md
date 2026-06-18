<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/mount -->
# sources/distributed-fs/openafs/src/vfsck/mount

## Purpose
Filesystem-type wrapper installed as `/sbin/fs/afs/mount` for HP-UX mountall integration. It strips the generic `-Fafs` selector and delegates the real mount operation to the HFS mount implementation.

## Important APIs, Types, And Functions
There are no functions; the script executes `/sbin/fs/hfs/mount $2 $3 $4 $5 $6 $7 $8 $9` and exits with that command’s status.

## Control Flow
The generic mount framework calls this script with the filesystem type as `$1`. The script ignores `$1`, forwards up to eight remaining positional arguments to HFS mount, and exits with the delegated status.

## State And Persistence
All persistent effects are produced by `/sbin/fs/hfs/mount`, which mounts the underlying server partition. The wrapper stores no state.

## Dependencies And Integration Points
This relies on AFS server partitions being HFS-compatible on the target HP-UX platform, while the boot framework refers to them as type `afs`.

## Risks And Test Signals
Risks include loss of arguments beyond `$9`, word-splitting of arguments with spaces, and hard-coded HFS path. Tests should verify mountall invocation with typical AFS fstab records and failure propagation from HFS mount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/mount -->
