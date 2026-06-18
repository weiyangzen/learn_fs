# sources/distributed-fs/lizardfs/src/mount/io_limit_group_unittest.cc

## Purpose
This unit test file validates parsing of `/proc/<pid>/cgroup`-formatted input into I/O limit group ids.

## Important APIs, Types, And Functions
Each GoogleTest case constructs a `std::stringstream` and calls `getIoLimitGroupId(input, "blkio")`. Tests expect either a returned path or `GetIoLimitGroupIdException`.

## Control Flow
The suite checks empty input, no matching subsystem, subsystem suffix/prefix false positives, a minimal `:blkio:/test` line, comma-separated subsystem lists, and matching on a later line.

## State And Persistence
State is test-local and in memory. It avoids reading real `/proc`.

## Dependencies And Integration Points
It depends on GoogleTest and `mount/io_limit_group.h`. It is the direct signal for parser behavior used by `LimiterProxy`.

## Risks And Test Signals
The tests do not cover malformed lines that partially match, cgroup v2 unified hierarchy, or the `pid` and no-throw overloads. Existing cases signal exact subsystem matching and line scanning behavior.
