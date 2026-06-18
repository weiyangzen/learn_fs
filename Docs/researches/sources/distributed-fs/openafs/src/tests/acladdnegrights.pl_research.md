<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/acladdnegrights.pl -->
# sources/distributed-fs/openafs/src/tests/acladdnegrights.pl

## Purpose
Verifies adding negative ACL rights for a PTS user.

## Important APIs, Types, And Functions
Uses `AFS_Init`, `AFS_fs_wscell`, `AFS_pts_createuser`, `AFS_fs_getacl`, and `AFS_fs_setacl`.

## Control Flow
Creates `user1` if possible, makes `/afs/<cell>/service/acltest`, records ACLs, calls `AFS_fs_setacl` with an empty positive ACL and negative `user1 rl`, then scans the returned negative ACL for exactly one `user1` entry.

## State And Persistence
Persists PTS user `user1`, directory creation, and a negative ACL entry. No cleanup is attempted.

## Dependencies And Integration Points
Requires the protection database, `fs setacl -negative`, and a writable service volume.

## Risks And Test Signals
Preexisting negative entries can affect the exact count. The test does not validate rights string beyond presence. Exit `0` means the negative ACL entry was found once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/acladdnegrights.pl -->
