<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosaddkey.pl -->
# sources/distributed-fs/openafs/src/tests/bosaddkey.pl

## Purpose
Tests adding a BOS server encryption key with key version number 250.

## Important APIs, Types, And Functions
Calls `AFS_bos_addkey(localhost, "\000...\007", 250)`.

## Control Flow
Initializes AFStools, submits an eight-byte binary key to `bos addkey`, and exits `0` on wrapper success.

## State And Persistence
Persists a key in the server KeyFile/key list.

## Dependencies And Integration Points
Follow-on `boslistkeys.pl` checks the key checksum and `bosremovekey.pl` removes it.

## Risks And Test Signals
Binary NULs in Perl string arguments and shell/exec handling are the key risk. Success means `bos addkey` accepted the key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/bosaddkey.pl -->
