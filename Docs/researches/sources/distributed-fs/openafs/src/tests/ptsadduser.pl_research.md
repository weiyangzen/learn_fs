<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsadduser.pl -->
# sources/distributed-fs/openafs/src/tests/ptsadduser.pl

## Purpose
Exercises the OpenAFS protection-server wrapper `pts_add` as one step in the PTS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_pts_add; AFS calls/macros: AFS_Help, AFS_Init, AFS_pts_add

## Control Flow
Initializes the OpenAFS Perl environment with `AFS_Init`, invokes `AFS_pts_add`, and exits nonzero on mismatched state.

## State and Persistence Behavior
Mutates or queries the protection database through test users/groups such as `testuser1`, `testgroup1`, `admin`, and `system:administrators`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_pts_add; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 17 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/ptsadduser.pl -->
