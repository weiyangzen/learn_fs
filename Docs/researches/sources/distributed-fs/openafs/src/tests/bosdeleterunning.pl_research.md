<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosdeleterunning.pl -->
# sources/distributed-fs/openafs/src/tests/bosdeleterunning.pl

## Purpose
Negative test ensuring BOS refuses or errors when deleting a running `sleeper` bnode.

## Important APIs, Types, And Functions
Uses `eval { AFS_bos_delete(...) }` to inspect wrapper exceptions.

## Control Flow
Initializes AFStools, attempts to delete `sleeper`, exits `1` if no exception was raised, and exits `0` if an exception occurred.

## State And Persistence
Intended not to mutate state; if deletion unexpectedly succeeds, the bnode is removed and the test fails.

## Dependencies And Integration Points
Depends on `sleeper` being running from previous BOS lifecycle setup.

## Risks And Test Signals
The signal is inverted: success means a wrapper error was thrown. Any output-format change that hides the BOS error could invalidate the test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosdeleterunning.pl -->
