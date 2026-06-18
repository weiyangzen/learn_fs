<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/umount -->
# sources/distributed-fs/openafs/src/vfsck/umount

## Purpose
Filesystem-type unmount wrapper installed as `/sbin/fs/afs/umount`. It represents AFS as not dynamically unmountable in this HP-UX integration path.

## Important APIs, Types, And Functions
There are no functions or external command calls. The script exits with status 1.

## Control Flow
When generic `umountall` invokes the script for `AFS /afs`, it performs no operation and immediately exits 1. The comments state reboot is the only supported way to unmount AFS.

## State And Persistence
No state is changed. The mounted AFS client filesystem remains mounted.

## Dependencies And Integration Points
This integrates with HP-UX `umountall` as the filesystem-specific handler for AFS. It intentionally does not call HFS unmount or detach the AFS client.

## Risks And Test Signals
Risks include callers treating exit 1 as an unexpected failure during shutdown and the spelling/comment drift indicating this path may be obsolete. Test signals are shutdown scripts tolerating this status and verifying no accidental unmount attempt occurs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/umount -->
