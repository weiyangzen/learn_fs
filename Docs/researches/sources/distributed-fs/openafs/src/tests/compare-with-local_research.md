<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/compare-with-local -->
# sources/distributed-fs/openafs/src/tests/compare-with-local

## Purpose
Compares copy/move/cat file operations between the filesystem under test and a local temporary directory.

## Important APIs, Types, And Functions
Defines shell function `compare` using `cmp` and `diff`. Uses `cp`, `mv`, `cat`, `test`, and `${objdir}/rm-rf`.

## Control Flow
Creates `$TMPDIR/compare-with-local-$$`, writes a reference file, copies/moves/cats it into and out of the current directory with content comparisons, repeats with slightly different content to test overwrite behavior, removes the temp directory, and exits `0`.

## State And Persistence
Creates transient files in both local temp and current directory; local temp is removed on success.

## Dependencies And Integration Points
Exercises standard POSIX file data operations against AFS and local disk as oracle.

## Risks And Test Signals
Uses `function` syntax, which is not strictly POSIX `/bin/sh`. Cleanup only happens on success; failures can leave temp files. Signal is all `cmp` checks passing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/compare-with-local -->
