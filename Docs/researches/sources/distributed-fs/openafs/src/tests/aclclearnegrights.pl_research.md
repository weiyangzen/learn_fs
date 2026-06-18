<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/aclclearnegrights.pl -->
# sources/distributed-fs/openafs/src/tests/aclclearnegrights.pl

## Purpose
Tests changing/clearing negative ACL rights for `user1` and comparing the resulting ACL shape.

## Important APIs, Types, And Functions
Uses `AFS_pts_createuser`, `AFS_fs_getacl`, and `AFS_fs_setacl` with negative ACL input.

## Control Flow
Creates `user1`, creates the ACL test directory, reads initial ACLs, sets negative `user1 r`, verifies the read-back rights are `r`, then compares reconstructed negative/positive ACL arrays with prior state and exits nonzero on mismatch.

## State And Persistence
Mutates the directory's negative ACL. It leaves the PTS user and directory present.

## Dependencies And Integration Points
Depends on negative ACL support in `fs setacl` and list parsing in `OpenAFS::fs`.

## Risks And Test Signals
Array comparisons use Perl scalar array length, not deep ACL equality, so the check is weak. Success signals only that the target negative rights were parsed as `r` and counts matched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/aclclearnegrights.pl -->
