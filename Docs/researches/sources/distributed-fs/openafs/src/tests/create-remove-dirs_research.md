<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-remove-dirs -->
# sources/distributed-fs/openafs/src/tests/create-remove-dirs

## Purpose
Shell wrapper for repeated directory create/remove stress.

## Important APIs, Types, And Functions
Uses `$objdir/create-remove dir 1000`.

## Control Flow
Skips when `FAST` is set; otherwise asks the compiled helper to create and remove one directory name 1000 times.

## State And Persistence
No intended persistent files on success.

## Dependencies And Integration Points
Depends on `create-remove.c` helper and current directory filesystem semantics.

## Risks And Test Signals
Failures can leave the temporary directory. Exit `0` means 1000 mkdir/rmdir cycles completed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-remove-dirs -->
