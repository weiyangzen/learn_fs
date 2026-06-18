<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_config_loader_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/io_limits_config_loader_unittest.cc

## Purpose
Validates the I/O limits configuration grammar and loader state after parsing. The source was read completely for this report.

## Important APIs, Types, And Functions
Uses GoogleTest macros plus helpers `PAIR`, `LIMITS`, and `ASSERT_LIMITS_EQ` around `IoLimitsConfigLoader`.

## Control Flow
Each test constructs an in-memory string, feeds it through `std::istringstream`, and asserts either parsed subsystem/limits or `ParseException`.

## State And Persistence Behavior
No persistent state; each test creates a fresh loader.

## Dependencies And Integration Points
Depends on `common/exceptions.h`, `io_limits_config_loader.h`, and gtest.

## Risks And Edge Cases
The suite documents important edge cases but does not test loader reuse after a previous subsystem, negative limits, overflow, or CRLF handling.

## Test Signals
Passing tests are strong signals for directive parsing, duplicate detection, and the special unclassified-only case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_config_loader_unittest.cc -->
