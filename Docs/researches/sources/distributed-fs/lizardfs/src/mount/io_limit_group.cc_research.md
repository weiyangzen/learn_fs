# sources/distributed-fs/lizardfs/src/mount/io_limit_group.cc

## Purpose
This file parses Linux `/proc/<pid>/cgroup` data to classify a process into an I/O limit group for a configured cgroup subsystem.

## Important APIs, Types, And Functions
`skipHierarchy()` skips the hierarchy id up to the first colon. `searchSubsystems()` scans comma-separated subsystem names and returns true only on exact subsystem matches followed by comma or colon. `getIoLimitGroupId(std::istream&, subsystem)` parses lines until it finds the subsystem and returns the group path after the second colon, otherwise throws `GetIoLimitGroupIdException`. `getIoLimitGroupId(pid, subsystem)` opens `/proc/<pid>/cgroup`. `getIoLimitGroupIdNoExcept()` catches classification errors and returns `kUnclassified`.

## Control Flow
The parser processes each line with a `stringstream` configured to throw on EOF while parsing structural fields; parse failures become `GetIoLimitGroupIdException` unless the underlying input is truly exhausted. The no-throw wrapper is used by `LimiterProxy` so missing cgroup information falls back to an unclassified group.

## State And Persistence
No persistent state is stored. The only external state read is `/proc/<pid>/cgroup`.

## Dependencies And Integration Points
It depends on C++ streams, `/proc`, `common/io_limit_group.h` for `IoLimitGroupId` and `kUnclassified`, and the exception helper. It integrates with `global_io_limiter.cc` process classification.

## Risks And Test Signals
Risks include blocking or malformed stream parsing loops, Linux-specific `/proc` assumptions, exact subsystem matching, and cgroup v2 format differences. `io_limit_group_unittest.cc` covers empty input, no match, prefix/suffix non-matches, minimal valid lines, comma lists, and second-line matches.
