<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/compare-inum-mp -->
# sources/distributed-fs/openafs/src/tests/compare-inum-mp

## Purpose
Tests directory entry inode consistency across an AFS mount point.

## Important APIs, Types, And Functions
Uses `${FS}` for ACL and mount operations plus `$objdir/readdir-vs-lstat`.

## Control Flow
Grants `system:anyuser all` on current directory, creates a `root.cell` mount point, runs `readdir-vs-lstat` on `.` and the mount point, removes the mount point, and exits on first failure.

## State And Persistence
Temporarily changes ACLs and creates/removes a mount point.

## Dependencies And Integration Points
Requires the `fs` command, built `readdir-vs-lstat`, and a valid `root.cell` volume.

## Risks And Test Signals
ACL broadening may persist if cleanup fails. Success confirms readdir inode values match lstat across normal and mount-point directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/compare-inum-mp -->
