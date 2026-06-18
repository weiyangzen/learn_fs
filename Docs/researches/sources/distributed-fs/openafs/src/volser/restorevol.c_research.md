# sources/distributed-fs/openafs/src/volser/restorevol.c

## Purpose
Implements the standalone `restorevol` utility, which reads a `vos dump` stream and recreates a filesystem tree outside AFS using normal directories, files, and symlinks.

## Important APIs And Functions
`readvalue`, `readchar`, and `readdata` parse raw dump bytes from `dumpfile`. `ReadDumpHeader` and `ReadVolumeHeader` parse dump metadata. `ReadVNode` handles directory, file, and symlink vnode records, reconstructing names through directory pages. `WorkerBee` implements command-line behavior for `-file`, `-dir`, `-extension`, `-mountpoint`, and `-umask`; `main` registers the command syntax.

## Control Flow And State
The utility reads a dump header to choose the restore root, then loops through volume-header and vnode sections until dump end. Directory vnodes are parsed to create real directories plus temporary root-level `AFSDir-<vnode>` symlinks. File entries first create temporary `AFSFile-<vnode>` symlinks in parent dirs; file vnode records resolve those symlinks and write data. Missing parents or files become `__ORPHANEDIR__.<vnode>` or `__ORPHANFILE__.<vnode>`. Incremental dumps trigger cleanup of leftover `AFSFile-` symlinks; all runs remove `AFSDir-` links at the end.

## Persistence And Integration
It writes to the local filesystem using `mkdir`, `symlink`, `rename`, `open`, `write`, and `unlink`. It depends on `dump.h`, vnode constants, AFS directory-page layout assumptions, and command parsing.

## Risks And Test Signals
Risks include old parser assumptions, limited unknown-tag handling, fixed-size buffers for names/MOTD/ACL, directory-page trust from input dumps, path/symlink collisions, partial output after errors, and no ACL restoration. Test signals include full and incremental dump extraction, orphan reconstruction, mountpoint symlink rewriting, long names/path overflow, truncated file data, and cleanup idempotence.
