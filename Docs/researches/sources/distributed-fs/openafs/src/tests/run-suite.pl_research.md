<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/run-suite.pl -->
# sources/distributed-fs/openafs/src/tests/run-suite.pl

## Purpose
Bootstraps an end-to-end local OpenAFS test cell, starts server/client services, creates volumes and mount points, then runs the front-end test harness.

## Important APIs, Types, and Functions
Perl calls/subs: mkvol, uudecode

## Control Flow
Requires root, rejects already-running AFS mounts, stops/starts services, writes ThisCell/CellServDB, seeds the protection database, creates bos/vl/pt/ka/fileserver instances, creates root/user/service/replicated volumes, authenticates, runs `pagsh -c './test-front.sh ...'`, and unwinds registered cleanup commands.

## State and Persistence Behavior
Mutates system-wide AFS configuration, databases, volumes, `/afs`, `/usr/vice/cache`, test dumps, and service state; cleanup is managed through an unwind stack and END block.

## Dependencies and Integration Points
OpenAFS Perl modules (`OpenAFS::util`, `afsconf`, `fs`, `pts`, `vos`, `bos`)

## Risks and Test Signals
Destructive and environment-sensitive; requires root, a valid KeyFile, available partitions, service paths from Dirpath, and careful cleanup to avoid leaving partial cells or running services.

## Source Notes
Read as Perl OpenAFS command test; 302 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/run-suite.pl -->
