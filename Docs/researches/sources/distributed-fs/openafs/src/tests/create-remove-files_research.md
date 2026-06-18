<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-remove-files -->
# sources/distributed-fs/openafs/src/tests/create-remove-files

## Purpose
Shell wrapper for repeated file create/unlink stress.

## Important APIs, Types, And Functions
Uses `$objdir/create-remove file 1000`.

## Control Flow
Skips when `FAST` is set; otherwise runs the compiled helper for 1000 create/unlink cycles.

## State And Persistence
No intended persistent files on success.

## Dependencies And Integration Points
Depends on `create-remove.c` helper.

## Risks And Test Signals
Failures can leave a `foo-...` file. Exit `0` means repeated create/unlink completed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-remove-files -->
