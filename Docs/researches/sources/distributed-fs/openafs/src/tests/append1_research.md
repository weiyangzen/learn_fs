<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/append1 -->
# sources/distributed-fs/openafs/src/tests/append1

## Purpose
Shell smoke test for append redirection and file content preservation.

## Important APIs, Types, And Functions
Uses `$objdir/echo-n`, shell redirection, `cat`, `test`, and `rm`.

## Control Flow
Writes `hej` without newline to `foo`, verifies exact content, appends `hopp`, verifies `hejhopp`, and removes the file.

## State And Persistence
Creates and deletes `foo` in the current test directory.

## Dependencies And Integration Points
Depends on the built `echo-n` helper and a shell running in the filesystem under test.

## Risks And Test Signals
Backtick command substitution strips trailing newlines, which is acceptable because `echo-n` suppresses them. Exit `0` confirms basic append semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/append1 -->
