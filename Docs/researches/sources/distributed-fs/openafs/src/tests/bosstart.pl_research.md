<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosstart.pl -->
# sources/distributed-fs/openafs/src/tests/bosstart.pl

## Purpose
Tests starting the `sleeper` bnode and verifying normal running status.

## Important APIs, Types, And Functions
Uses `AFS_bos_start` and `AFS_bos_status`.

## Control Flow
Starts `sleeper`, fetches its status, and requires `num_starts == 2` plus `currently running normally.`

## State And Persistence
Starts an existing disabled/stopped bnode.

## Dependencies And Integration Points
Assumes prior stop state and deterministic start counter.

## Risks And Test Signals
Exact status string and start count are brittle. Exit `0` confirms start command and parser.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosstart.pl -->
