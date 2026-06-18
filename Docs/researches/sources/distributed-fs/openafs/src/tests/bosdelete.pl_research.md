<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosdelete.pl -->
# sources/distributed-fs/openafs/src/tests/bosdelete.pl

## Purpose
Deletes the `sleeper` BOS bnode after lifecycle tests.

## Important APIs, Types, And Functions
Calls `AFS_bos_delete(localhost, sleeper)`.

## Control Flow
Initializes AFStools, invokes delete, and exits `0` if the wrapper succeeds.

## State And Persistence
Removes the `sleeper` BosConfig instance; it does not uninstall the script file.

## Dependencies And Integration Points
Requires a stopped/removable bnode created by `boscreate.pl`.

## Risks And Test Signals
Bareword `sleeper` relies on old Perl semantics. Deleting a running bnode is separately tested to fail in `bosdeleterunning.pl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosdelete.pl -->
