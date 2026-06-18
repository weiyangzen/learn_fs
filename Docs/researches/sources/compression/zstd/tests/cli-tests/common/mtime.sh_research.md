# sources/compression/zstd/tests/cli-tests/common/mtime.sh

## Purpose

This shared shell helper asserts file modification-time equality across platforms.

## Important APIs, Types, and Functions

It sources `platform.sh`, selects `stat -c %Y` by default or `stat -f %m` on Darwin/BSD, and defines `assertSameMTime(file1, file2)`.

## Control Flow, State, and Persistence

The assertion reads both mtimes, prints them, and calls `die` if they differ. It has no persistent state.

## Dependencies and Integration Points

It depends on platform `stat` syntax and the `die` helper. CLI tests that check metadata preservation source it.

## Risks and Test Signals

Timestamp granularity and filesystem behavior can differ by platform. Tests should account for platforms where compression/decompression may round or not preserve subsecond data.
