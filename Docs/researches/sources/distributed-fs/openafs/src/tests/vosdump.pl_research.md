<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosdump.pl -->
# sources/distributed-fs/openafs/src/tests/vosdump.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_dump` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_dump; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_dump

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_dump`, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_dump; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
uses `/tmp` scratch files; requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 19 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/vosdump.pl -->
