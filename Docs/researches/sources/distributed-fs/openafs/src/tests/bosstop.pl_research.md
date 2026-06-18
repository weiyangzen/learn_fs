<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosstop.pl -->
# sources/distributed-fs/openafs/src/tests/bosstop.pl

## Purpose
Tests stopping the `sleeper` bnode with wait semantics.

## Important APIs, Types, And Functions
Uses `AFS_bos_stop` and `AFS_bos_status`.

## Control Flow
Stops `sleeper`, reads status, and requires `num_starts == 1` plus `disabled, currently shutdown.`

## State And Persistence
Stops and disables the bnode.

## Dependencies And Integration Points
Part of the ordered BOS lifecycle smoke suite.

## Risks And Test Signals
Depends on initial start count and exact status strings. Exit `0` validates stop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosstop.pl -->
