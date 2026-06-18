<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/acladdgroup.pl -->
# sources/distributed-fs/openafs/src/tests/acladdgroup.pl

## Purpose
Smoke-tests adding a PTS group to a directory's positive ACL in the workstation cell.

## Important APIs, Types, And Functions
Calls `AFS_Init`, `AFS_fs_wscell`, `AFS_pts_creategroup`, `AFS_fs_getacl`, and `AFS_fs_setacl`.

## Control Flow
Initializes AFStools, finds the workstation cell, best-effort creates `group1`, creates `/afs/<cell>/service/acltest`, snapshots ACLs, adds `group1 rl`, reads ACLs again, and exits nonzero unless exactly one positive entry for `group1` is found.

## State And Persistence
Creates or reuses PTS group `group1`, creates an AFS directory, and mutates its positive ACL. It does not restore the original ACL or remove the group.

## Dependencies And Integration Points
Depends on the AFStools Perl modules, writable `/afs/<cell>/service`, PTS service, and cache manager ACL commands.

## Risks And Test Signals
The test assumes `service/acltest` can be created and that prior ACL state will not contain duplicate `group1` entries. Success is exit `0`; any missing positive ACL entry exits `1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/acladdgroup.pl -->
