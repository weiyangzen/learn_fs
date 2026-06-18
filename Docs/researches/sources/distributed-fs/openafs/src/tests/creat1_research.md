<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/creat1 -->
# sources/distributed-fs/openafs/src/tests/creat1

## Purpose
Minimal shell test for creating an empty file and verifying it has zero size.

## Important APIs, Types, And Functions
Uses shell redirection, `test -f`, `test -s`, and `rm`.

## Control Flow
Truncates/creates `foobar`, fails if it is absent or nonempty, then removes it.

## State And Persistence
Temporarily creates `foobar` and deletes it.

## Dependencies And Integration Points
Basic filesystem create/stat/unlink smoke test.

## Risks And Test Signals
Very narrow coverage. Exit `0` confirms empty-file creation semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/creat1 -->
