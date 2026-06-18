<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosremovehost.pl -->
# sources/distributed-fs/openafs/src/tests/bosremovehost.pl

## Purpose
Tests removing the hard-coded BOS host entry and verifying only the local host remains.

## Important APIs, Types, And Functions
Uses `AFS_bos_removehost` and `AFS_bos_listhosts`.

## Control Flow
Removes `128.2.1.2`, lists hosts, validates first item is the cell name and all remaining hosts equal local hostname.

## State And Persistence
Mutates CellServDB/BOS host list by removing the test host.

## Dependencies And Integration Points
Completes the add/list/remove host sequence.

## Risks And Test Signals
Assumes no other hosts in the cell. Exit `0` verifies removal and parser behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosremovehost.pl -->
