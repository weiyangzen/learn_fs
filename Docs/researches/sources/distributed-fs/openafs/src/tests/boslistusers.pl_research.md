<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boslistusers.pl -->
# sources/distributed-fs/openafs/src/tests/boslistusers.pl

## Purpose
Checks BOS superuser list after adding `testuser1`.

## Important APIs, Types, And Functions
Calls `AFS_bos_listusers(localhost)`.

## Control Flow
Lists superusers and allows only `admin` and `testuser1`; any other listed user exits `1`.

## State And Persistence
Read-only.

## Dependencies And Integration Points
Depends on the UserList state from `afs-newcell.pl` and `bosadduser.pl`.

## Risks And Test Signals
Sites with extra legitimate superusers will fail. Exit `0` indicates list parsing and expected state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boslistusers.pl -->
