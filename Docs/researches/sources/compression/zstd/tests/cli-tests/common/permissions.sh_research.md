# sources/compression/zstd/tests/cli-tests/common/permissions.sh

## Purpose

This shared shell helper asserts file permission modes in CLI tests.

## Important APIs, Types, and Functions

It sources `platform.sh`, selects `stat -c %a` by default or `stat -f %Lp` on Darwin/BSD, and defines `assertFilePermissions(file, expected)` plus `assertSamePermissions(file1, file2)`.

## Control Flow, State, and Persistence

Each assertion reads numeric modes and calls `die` on mismatch. No state is persisted.

## Dependencies and Integration Points

It depends on platform `stat` and `die`, and supports tests for `UTIL_setFileStat`/permission preservation behavior.

## Risks and Test Signals

Mode formatting differs across systems and umask can affect created files. Tests should set predictable permissions before assertions.
