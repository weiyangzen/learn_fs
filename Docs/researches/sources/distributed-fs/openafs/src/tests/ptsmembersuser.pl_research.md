<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsmembersuser.pl -->
# sources/distributed-fs/openafs/src/tests/ptsmembersuser.pl

## Purpose
Exercises the OpenAFS protection-server wrapper `pts_members` as one step in the PTS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_pts_members, AFS_pts_add, AFS_pts_remove; AFS calls/macros: AFS_Help, AFS_Init, AFS_pts_members, AFS_pts_add, AFS_pts_remove

## Control Flow
Initializes the OpenAFS Perl environment with `AFS_Init`, invokes `AFS_pts_remove` and checks returned fields, and exits nonzero on mismatched state.

## State and Persistence Behavior
Mutates or queries the protection database through test users/groups such as `testuser1`, `testgroup1`, `admin`, and `system:administrators`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_pts_members, AFS_pts_add, AFS_pts_remove; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 35 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsmembersuser.pl -->
