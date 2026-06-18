# Research: sources/distributed-fs/ipfs-kubo/cmd/ipfswatch/ipfswatch_test.go

Purpose: Unit coverage for hidden-directory detection in the `ipfswatch` helper command.

Important APIs/types/functions: `TestIsHidden` asserts that path components beginning with `.` are hidden except the current-directory marker `"."`.

Control flow, state, and persistence: No filesystem state is created; it only calls `IsHidden` with string paths.

Dependencies and integration points: Uses `testify/require`. The behavior protects `addTree` from recursively watching hidden directories such as `.git`.

Risks and test signals: The test is narrow; it does not cover watcher behavior, symlinks, recursive traversal, or errors from `os.Stat`. It does lock the special-case behavior for `"."`.
