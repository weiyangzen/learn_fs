<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/compare-inums -->
# sources/distributed-fs/openafs/src/tests/compare-inums

## Purpose
Tests directory entry inode reporting for many newly created files.

## Important APIs, Types, And Functions
Invokes `$objdir/create-files 100 0` and `$objdir/readdir-vs-lstat .`.

## Control Flow
Creates 100 empty numeric files, then validates every `readdir` inode against `lstat` for the current directory.

## State And Persistence
Leaves the 100 files unless the surrounding harness cleans them.

## Dependencies And Integration Points
Uses compiled helpers `create-files` and `readdir-vs-lstat`.

## Risks And Test Signals
Preexisting numeric files can conflict with `O_EXCL` in `create-files`. Success is zero exit from both helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/compare-inums -->
