<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/blocks-new-file.c -->
# sources/distributed-fs/openafs/src/tests/blocks-new-file.c

## Purpose
Checks that a newly created sparse-ish file reports nonzero allocated block count after a seek-and-write.

## Important APIs, Types, And Functions
Defines `doit` and `main`. Uses `open`, `lseek`, `write`, `close`, `stat`, `unlink`, and `st_blocks`.

## Control Flow
Creates/truncates a file, seeks to 1 MiB, writes three bytes, closes, stats, unlinks, and fails if `st_blocks == 0`.

## State And Persistence
Temporarily creates a target file (`foo` by default), then removes it.

## Dependencies And Integration Points
Exercises filesystem allocation/stat behavior after sparse writes in the current directory.

## Risks And Test Signals
Some filesystems legitimately report block counts differently, so this is a portability-sensitive test. Exit `0` confirms nonzero `st_blocks`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/blocks-new-file.c -->
