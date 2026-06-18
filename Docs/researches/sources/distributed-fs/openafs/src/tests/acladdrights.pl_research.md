<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/acladdrights.pl -->
# sources/distributed-fs/openafs/src/tests/acladdrights.pl

## Purpose
Checks that setting an existing/new positive ACL entry to broader rights (`rlidw`) is reflected by `fs listacl`.

## Important APIs, Types, And Functions
Uses `AFS_pts_createuser`, `AFS_fs_getacl`, and `AFS_fs_setacl` after AFStools initialization.

## Control Flow
Creates `user1`, creates the ACL test directory, captures original ACLs, sets `user1 rlidw`, reads ACLs again, and exits `1` if the matching entry has any rights string other than `rlidw`.

## State And Persistence
Adds or modifies `user1` on the positive ACL and leaves the directory/user in place.

## Dependencies And Integration Points
Tests the `OpenAFS::fs` ACL representation and the underlying `fs setacl/listacl` round trip.

## Risks And Test Signals
The script builds unused temporary arrays and does not restore original rights. Success is an exact rights-string parse from command output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/acladdrights.pl -->
