<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/md5.cc -->
# sources/distributed-fs/lizardfs/src/common/md5.cc

## Purpose
Implements MD5 digest routines plus LizardFS challenge-response and hex digest parsing helpers. The source was read completely for this report.

## Important APIs, Types, And Functions
`md5_init`, `md5_update`, `md5_final`, `md5_challenge_response`, and `md5_parse` are exported; internal helpers encode/decode little-endian words and run the MD5 transform rounds.

## Control Flow
MD5 update accumulates bit counts, buffers partial blocks, transforms complete 64-byte blocks, finalizes with padding and length, then zeroes the context. Challenge response hashes first half of challenge, data string, then second half.

## State And Persistence Behavior
State is caller-owned `md5ctx`; finalization clears it. No persistence.

## Dependencies And Integration Points
Used by authentication/password paths. Depends on fixed-width types and `md5.h`.

## Risks And Edge Cases
MD5 is cryptographically weak and should be treated as compatibility authentication only. `md5_parse` resizes output before validating and assumes NUL-terminated input.

## Test Signals
Needs known MD5 vector tests, challenge-response vectors, and invalid hex length/character tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/md5.cc -->
