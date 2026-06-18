# sources/distributed-fs/ceph-client/scripts/kconfig/tests/preprocess/variable/__init__.py

## Purpose
This pytest module validates Kconfig variable and user-defined function semantics.

## Important APIs, Types, and Functions
It calls `conf.oldaskconfig()` and `conf.stderr_matches('expected_stderr')`.

## Control Flow
Parsing should complete successfully and emit deterministic warnings.

## State and Persistence
No persistent state beyond captured stderr.

## Dependencies and Integration Points
Depends on `preprocess.c` and expected stderr fixture.

## Risks and Edge Cases
Whitespace in appended variables and function output is significant.

## Test Signals
Pass means simple/recursive/append/function expansion matches expectations.
