<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/baduniq.pl -->
# sources/distributed-fs/openafs/src/tests/baduniq.pl

## Purpose
Regression test for restoring/salvaging a volume with problematic vnode uniquifier data and verifying a file is visible afterward.

## Important APIs, Types, And Functions
Uses `AFS_vos_restore`, `AFS_bos_salvage`, `AFS_fs_mkmount`, and `AFS_fs_rmmount`.

## Control Flow
Restores volume `badvol` on localhost partition `a` from `/tmp/t.uniq-bad` using id `100` and full overwrite, salvages it, mounts it at `badvol`, checks for `badvol/test`, removes the mount point, and exits `0` only if the file exists.

## State And Persistence
Creates/restores `badvol`, invokes salvage, creates/removes a mount point, and leaves the restored volume unless external cleanup removes it.

## Dependencies And Integration Points
Depends on a prepared dump file `/tmp/t.uniq-bad`, working VOS/BOS/FS wrappers, and a test cell.

## Risks And Test Signals
The dump path is absolute and external to the repository. The test does not remove the volume. Success indicates the salvaged volume exposes the expected file through a mount point.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/baduniq.pl -->
