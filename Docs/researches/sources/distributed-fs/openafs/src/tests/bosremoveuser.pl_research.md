<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosremoveuser.pl -->
# sources/distributed-fs/openafs/src/tests/bosremoveuser.pl

## Purpose
Removes `testuser1` from the BOS superuser list and verifies only `admin` remains.

## Important APIs, Types, And Functions
Uses `AFS_bos_removeuser` and `AFS_bos_listusers`.

## Control Flow
Calls removeuser for `[testuser1]`, lists users, and exits `1` if any listed user is not `admin`.

## State And Persistence
Mutates UserList/superuser list.

## Dependencies And Integration Points
Completes the add/list/remove BOS user sequence.

## Risks And Test Signals
Assumes no extra administrative users. Exit `0` is a strong parser/state signal in the controlled test cell.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosremoveuser.pl -->
