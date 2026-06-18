<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_database_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/io_limits_database_unittest.cc

## Purpose
Tests token-bucket semantics for the I/O limits database. The source was read completely for this report.

## Important APIs, Types, And Functions
Exercises `setLimits`, `getGroups`, and `request` using artificial `SteadyTimePoint` values.

## Control Flow
The tests configure groups, advance virtual time, issue requests, and assert exact granted byte counts, including partial and exhausted buckets.

## State And Persistence Behavior
No persistent state; each test owns its `IoLimitsDatabase` and fake time point.

## Dependencies And Integration Points
Depends on gtest and `time_utils.h`.

## Risks And Edge Cases
Coverage focuses on deterministic arithmetic. It does not cover missing group exceptions, reconfiguration removal, or integer overflow.

## Test Signals
Passing tests indicate correct KB-to-byte conversion, accumulation caps, and replenishment over time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_database_unittest.cc -->
