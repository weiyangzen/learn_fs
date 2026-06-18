# sources/distributed-fs/lizardfs/src/mount/io_limit_group.h

## Purpose
This header declares cgroup-to-I/O-limit-group classification helpers and the exception type used when classification fails.

## Important APIs, Types, And Functions
`GetIoLimitGroupIdException` is declared with the project exception macro. `getIoLimitGroupId(std::istream&, subsystem)` parses `/proc/*/cgroup` formatted data. `getIoLimitGroupId(pid, subsystem)` reads the process file. `getIoLimitGroupIdNoExcept(pid, subsystem)` returns `kUnclassified` on error.

## Control Flow
No implementation is present. The API separates strict parsing from fallback classification so callers can choose error behavior.

## State And Persistence
No state is stored. Implementations read either a supplied stream or `/proc`.

## Dependencies And Integration Points
It depends on `common/exception.h` and `common/io_limit_group.h`. It is consumed by `global_io_limiter.cc` and tested by `io_limit_group_unittest.cc`.

## Risks And Test Signals
The contract depends on Linux cgroup text format. Tests should verify exact matching and fallback-to-unclassified behavior.
