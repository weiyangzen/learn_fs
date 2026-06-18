<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosshutdown.pl -->
# sources/distributed-fs/openafs/src/tests/bosshutdown.pl

## Purpose
Tests `bos shutdown -wait` on the `sleeper` bnode and verifies temporary disabled status.

## Important APIs, Types, And Functions
Uses `AFS_bos_shutdown` and `AFS_bos_status`.

## Control Flow
Shuts down `sleeper`, reads status, requires `num_starts == 2` and status `temporarily disabled, currently shutdown.`

## State And Persistence
Stops the running bnode and marks it temporarily disabled.

## Dependencies And Integration Points
Part of sequential BOS lifecycle tests.

## Risks And Test Signals
Start-count expectations depend on exact test ordering. Exit `0` confirms shutdown and status parser behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosshutdown.pl -->
