<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/copy-file -->
# sources/distributed-fs/openafs/src/tests/copy-file

## Purpose
Repeated simple copy test for file data stability.

## Important APIs, Types, And Functions
Uses here-document file creation and repeated `cp foo foo2`.

## Control Flow
Creates `foo` with fixed text and copies it to `foo2` many times, exiting on first failed copy.

## State And Persistence
Leaves `foo` and `foo2` in the current directory.

## Dependencies And Integration Points
Exercises file create, overwrite, and copy paths in the filesystem under test.

## Risks And Test Signals
No content comparison after copy, so it mainly catches command/write failures. Exit `0` means all repeated copies succeeded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/copy-file -->
