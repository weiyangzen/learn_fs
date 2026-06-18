<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/massert.h -->
# sources/distributed-fs/lizardfs/src/common/massert.h

## Purpose
Defines project assertion/abort macros with syslog diagnostics and optional exception throwing for tests. The source was read completely for this report.

## Important APIs, Types, And Functions
`massert`, `passert`, `sassert`, `eassert`, `zassert`, `mabort`, and `ABORT_OR_THROW` are the primary macros.

## Control Flow
Each macro checks a condition/status, logs a formatted error through `lzfs_pretty_syslog`, and aborts or throws depending on `THROW_INSTEAD_OF_ABORT`.

## State And Persistence Behavior
No persistent state; side effects are logs and process termination/exception.

## Dependencies And Integration Points
Depends on `mfserr.h` and `slogger.h`. Used throughout low-level code for invariants and system-call assertions.

## Risks And Edge Cases
Macros evaluate expressions in-place and terminate the process in production, so they must not guard recoverable external input. `errno` capture is handled in error macros but callers must preserve it when needed.

## Test Signals
Tests usually exercise this indirectly; dedicated tests can define `THROW_INSTEAD_OF_ABORT` to assert failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/massert.h -->
