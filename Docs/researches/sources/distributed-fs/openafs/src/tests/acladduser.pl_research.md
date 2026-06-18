<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/acladduser.pl -->
# sources/distributed-fs/openafs/src/tests/acladduser.pl

## Purpose
Smoke-tests adding a PTS user to a positive ACL with read/list rights.

## Important APIs, Types, And Functions
Calls `AFS_Init`, `AFS_fs_wscell`, `AFS_pts_createuser`, `AFS_fs_getacl`, and `AFS_fs_setacl`.

## Control Flow
Initializes, creates `user1`, creates the common ACL test directory, sets `user1 rl`, then scans the positive ACL for one matching user entry.

## State And Persistence
Creates `user1`, creates `/afs/<cell>/service/acltest`, and leaves an ACL entry behind.

## Dependencies And Integration Points
Exercises PTS user creation and filesystem ACL mutation through the shared wrapper modules.

## Risks And Test Signals
Preexisting ACL state can mask or duplicate the target entry. Exit `0` is the only success signal; failures are by explicit exit `1` or wrapper exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/acladduser.pl -->
