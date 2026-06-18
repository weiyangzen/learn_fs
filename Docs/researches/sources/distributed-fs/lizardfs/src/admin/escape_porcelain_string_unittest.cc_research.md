<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/escape_porcelain_string_unittest.cc -->
# sources/distributed-fs/lizardfs/src/admin/escape_porcelain_string_unittest.cc

## Purpose
GoogleTest unit tests for porcelain string escaping.

## Important APIs, Types, and Functions
Defines `TEST(EscapePorcelainStringTests, EscapePorcelainString)` with expectations for empty strings, plain strings, goal-like punctuation, single/double/triple backslashes, quotes, surrounding slashes, and strings containing spaces.

## Control Flow, State, and Persistence
The test directly calls `escapePorcelainString` and compares exact raw-string outputs. It has no external state.

## Dependencies and Integration Points
Depends on `admin/escape_porcelain_string.h`, `common/platform.h`, and GTest. It is picked up by the admin CMake unit-test macro.

## Risks and Test Signals
The test suite is a strong signal for current quote/backslash behavior but does not cover tabs, newlines, non-ASCII, or round-trip parsing by a consumer. Any change to escaping must update both helper and tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/escape_porcelain_string_unittest.cc -->
