<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-files.c -->
# sources/distributed-fs/openafs/src/tests/create-files.c

## Purpose
Creates a requested number of numeric files of a requested size for filesystem stress tests.

## Important APIs, Types, And Functions
Defines `creat_files`, `usage`, and `main`. Uses `open(O_CREAT|O_EXCL)`, repeated `write`, `close`, `strtol`, and `opr_min`.

## Control Flow
Parses count and file size, creates each file named `0`, `1`, etc., writes up to 8192-byte chunks until the requested size is reached, and exits on short write or close error.

## State And Persistence
Leaves created files in the current directory.

## Dependencies And Integration Points
Used by `compare-inums` and other tests requiring many file entries.

## Risks And Test Signals
The write buffer is uninitialized, which is acceptable for size stress but not deterministic content. Existing numeric files fail due to `O_EXCL`. Success confirms create/write/close paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-files.c -->
