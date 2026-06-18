<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boslistkeys.pl -->
# sources/distributed-fs/openafs/src/tests/boslistkeys.pl

## Purpose
Verifies the added test key appears in `bos listkeys` with an expected checksum.

## Important APIs, Types, And Functions
Calls `AFS_bos_listkeys(localhost)`.

## Control Flow
Lists keys, iterates returned hash keys, and if key version 250 is present, requires the checksum to match one of two accepted values.

## State And Persistence
Read-only.

## Dependencies And Integration Points
Depends on `bosaddkey.pl` having added kvno 250 and the wrapper parsing checksum output.

## Risks And Test Signals
The test does not fail if kvno 250 is absent because it only checks when seen. Success is therefore weak; meaningful signal is presence with accepted checksum.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/boslistkeys.pl -->
