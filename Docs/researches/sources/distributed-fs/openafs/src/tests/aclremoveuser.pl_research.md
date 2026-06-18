<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/aclremoveuser.pl -->
# sources/distributed-fs/openafs/src/tests/aclremoveuser.pl

## Purpose
Attempts to remove `user1` from the positive ACL on the common ACL test directory.

## Important APIs, Types, And Functions
Uses AFStools initialization, `AFS_fs_wscell`, `AFS_fs_getacl`, and `AFS_fs_setacl`.

## Control Flow
Scans the positive ACL for `user1`, constructs a list-like string of other entries, fails if `user1` was not found, calls `AFS_fs_setacl`, and exits `0` without confirming the postcondition.

## State And Persistence
Intended to mutate the ACL by removing `user1`, but leaves all other test state intact.

## Dependencies And Integration Points
Depends on state produced by earlier ACL user tests and on `OpenAFS::fs` accepting a correctly structured positive ACL argument.

## Risks And Test Signals
The same string-vs-array-reference bug as `aclremovegroup.pl` likely invalidates the setter call. A meaningful test signal would require a post-call `getacl` check for absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/aclremoveuser.pl -->
