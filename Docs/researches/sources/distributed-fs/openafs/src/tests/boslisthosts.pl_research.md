<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boslisthosts.pl -->
# sources/distributed-fs/openafs/src/tests/boslisthosts.pl

## Purpose
Verifies BOS host list contains the workstation cell name, local hostname, and optionally the added hard-coded host.

## Important APIs, Types, And Functions
Uses `AFS_fs_wscell` and `AFS_bos_listhosts`.

## Control Flow
Gets local hostname and cell, lists hosts from localhost, checks first returned item equals the cell name, then accepts each host only if it is the local hostname or `128.2.1.2`.

## State And Persistence
Read-only.

## Dependencies And Integration Points
Follows `bosaddhost.pl` and validates `OpenAFS::bos` output parsing.

## Risks And Test Signals
Hostname canonicalization differences can fail the test. Exit `0` confirms parsed host list contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boslisthosts.pl -->
