# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/subunit.h

## Purpose
Small output helper for subunit-style PowerPC selftest reporting.

## Important APIs, Types, and Functions
Defines macros/functions for emitting test start, success, failure, skip, and error lines in a consistent format.

## Control Flow
No complex control flow; harness code calls these output helpers around child execution.

## State and Persistence
No state beyond stdout/stderr output.

## Dependencies and Integration Points
Integrated by `harness.c` for tests that use PowerPC custom harness rather than generic kselftest harness.

## Risks and Test Signals
Risk is reporting format drift affecting parsers. Test signal is readable subunit output from harnessed tests.
