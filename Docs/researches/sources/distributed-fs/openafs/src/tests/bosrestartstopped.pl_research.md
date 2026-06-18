<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosrestartstopped.pl -->
# sources/distributed-fs/openafs/src/tests/bosrestartstopped.pl

## Purpose
Tests restarting a stopped BOS bnode and verifying status counters/state.

## Important APIs, Types, And Functions
Uses `AFS_bos_restart` and `AFS_bos_status`.

## Control Flow
Restarts `sleeper`, reads long status, dereferences the `sleeper` info hash, and requires `num_starts == 2` and status text `temporarily enabled, currently running normally.`

## State And Persistence
Changes the runtime and BosConfig temporary state of the `sleeper` bnode.

## Dependencies And Integration Points
Assumes prior tests created and stopped/shutdown `sleeper` so the start count expectation is deterministic.

## Risks And Test Signals
Exact status string and start count are brittle. Exit `0` confirms restart and status parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosrestartstopped.pl -->
