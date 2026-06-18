<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bossalvagepart.pl -->
# sources/distributed-fs/openafs/src/tests/bossalvagepart.pl

## Purpose
Smoke-tests invoking BOS salvage for partition `a`.

## Important APIs, Types, And Functions
Calls `AFS_bos_salvage("localhost", "a", ...)`.

## Control Flow
Initializes AFStools, invokes salvage for a single partition, and exits `0` on wrapper success.

## State And Persistence
Runs salvager on partition `a`, potentially modifying volume metadata and salvage logs.

## Dependencies And Integration Points
Tests BOS salvager command integration in the configured cell.

## Risks And Test Signals
Destructive/repair operation on live test partition; should run only in disposable cell. Success is accepted BOS salvage output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bossalvagepart.pl -->
