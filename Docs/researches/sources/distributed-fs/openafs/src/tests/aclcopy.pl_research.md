<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/aclcopy.pl -->
# sources/distributed-fs/openafs/src/tests/aclcopy.pl

## Purpose
Verifies copying one directory ACL to another through `fs copyacl`.

## Important APIs, Types, And Functions
Uses `AFS_fs_copyacl`, `AFS_fs_getacl`, `AFS_fs_wscell`, and setup calls.

## Control Flow
Creates `acltest` and `acltest2` under `/afs/<cell>/service`, reads ACLs from the source, calls `AFS_fs_copyacl($path, [$path2], 1)` to clear/copy to the target, reads target ACLs, and compares positive and negative ACL entry counts.

## State And Persistence
Creates two directories and overwrites the target ACL. No cleanup is performed.

## Dependencies And Integration Points
Exercises `OpenAFS::fs::AFS_fs_copyacl` and `fs listacl` parsing.

## Risks And Test Signals
The test checks only array lengths, not entry identity or rights. Exit `0` means target positive/negative ACL counts matched source counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/aclcopy.pl -->
