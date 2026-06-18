<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/copy-and-diff-gnu-mirror -->
# sources/distributed-fs/openafs/src/tests/copy-and-diff-gnu-mirror

## Purpose
Large test that copies a GNU mirror subtree from AFS/local source into the current directory and verifies every copied file.

## Important APIs, Types, And Functions
Uses `FAST`, `LARGE`, `tar`, `find`, and `cmp`.

## Control Flow
Skips under `FAST` or without `LARGE`. Sets source to argv or `$AFSROOT/stacken.kth.se/ftp/pub`, streams `gnu` through tar into current directory, and compares every copied file against the original.

## State And Persistence
Creates a `gnu` subtree in the current directory.

## Dependencies And Integration Points
Requires a source mirror, enough space/time, and tar/cmp utilities.

## Risks And Test Signals
Large and environment-dependent. Success is all file comparisons returning equal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/copy-and-diff-gnu-mirror -->
