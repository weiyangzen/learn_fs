<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/voslistvol.pl -->
# sources/distributed-fs/openafs/src/tests/voslistvol.pl

## Purpose
Exercises the OpenAFS volume-server wrapper `vos_listvol` as one step in the VOS integration suite.

## Important APIs, Types, and Functions
Perl calls/subs: AFS_Init, AFS_vos_listvol; AFS calls/macros: AFS_Help, AFS_Init, AFS_vos_listvol

## Control Flow
Initializes OpenAFS Perl modules, invokes `AFS_vos_listvol` and validates returned volume/partition fields, and relies on wrapper failure or explicit checks to fail the test.

## State and Persistence Behavior
Mutates or queries test volumes/partitions such as `testvol`, `testvol3`, `rep`, `service`, `localhost`, partition `a`, and partition `b`.

## Dependencies and Integration Points
AFS interfaces AFS_Help, AFS_Init, AFS_vos_listvol; OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
requires a configured local OpenAFS cell with expected test users, groups, volumes, and partitions; explicit Perl exits or wrapper failures are the primary test signal.

## Source Notes
Read as Perl OpenAFS command test; 24 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/voslistvol.pl -->
