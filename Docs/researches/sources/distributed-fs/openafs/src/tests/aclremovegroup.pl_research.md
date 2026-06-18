<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/aclremovegroup.pl -->
# sources/distributed-fs/openafs/src/tests/aclremovegroup.pl

## Purpose
Attempts to remove `group1` from the positive ACL on the common ACL test directory.

## Important APIs, Types, And Functions
Uses `AFS_fs_getacl` and `AFS_fs_setacl` after AFStools initialization.

## Control Flow
Reads current positive ACL, scans for `group1`, builds a string that resembles an ACL list for remaining entries, exits `1` if `group1` was absent, and calls `AFS_fs_setacl` with the constructed value.

## State And Persistence
Mutates `/afs/<cell>/service/acltest` ACL if the wrapper accepts the generated list. Leaves directory in place.

## Dependencies And Integration Points
Depends on prior `acladdgroup.pl` state and the `OpenAFS::fs` ACL setter.

## Risks And Test Signals
`$listref` is a string, not an array reference matching `AFS_fs_setacl`'s API, so this script may fail or behave unexpectedly. Success is weak because it does not verify that the group was actually removed after the call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/aclremovegroup.pl -->
