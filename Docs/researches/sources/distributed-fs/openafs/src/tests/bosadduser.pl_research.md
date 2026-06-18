<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosadduser.pl -->
# sources/distributed-fs/openafs/src/tests/bosadduser.pl

## Purpose
Adds `testuser1` to the BOS superuser list.

## Important APIs, Types, And Functions
Calls `AFS_bos_adduser(localhost, [testuser1])`.

## Control Flow
Initializes AFStools, calls the BOS wrapper, and exits on success.

## State And Persistence
Mutates the server UserList/superuser list.

## Dependencies And Integration Points
Used with `boslistusers.pl` and `bosremoveuser.pl` to verify list mutation.

## Risks And Test Signals
Uses bareword `testuser1`; under this non-strict script it becomes a string. Success is later list output containing `testuser1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosadduser.pl -->
