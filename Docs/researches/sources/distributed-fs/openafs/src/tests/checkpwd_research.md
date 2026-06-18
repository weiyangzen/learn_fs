<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/checkpwd -->
# sources/distributed-fs/openafs/src/tests/checkpwd

## Purpose
Tiny wrapper that runs the `apwd` current-directory test binary.

## Important APIs, Types, And Functions
Invokes `$objdir/apwd`.

## Control Flow
No arguments or cleanup; exit status is inherited from `apwd`.

## State And Persistence
No direct persistent state.

## Dependencies And Integration Points
Integrates the shell test harness with the compiled `apwd.c` utility.

## Risks And Test Signals
Requires `$objdir` to point at built test binaries. Success is `apwd` exit `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/checkpwd -->
