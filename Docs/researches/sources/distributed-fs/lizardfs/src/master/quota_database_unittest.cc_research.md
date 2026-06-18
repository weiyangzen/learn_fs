# sources/distributed-fs/lizardfs/src/master/quota_database_unittest.cc

## Purpose

`quota_database_unittest.cc` provides GoogleTest coverage for `QuotaDatabase` set/get, remove, exceedance, boundary behavior, and checksum semantics. The source was read as a complete 159-line test file.

## Important APIs, Types, and Functions

The helper macro `EXPECT_ENTRY_EQ` checks used inode/size and soft/hard inode/size values for a quota entry. Tests are `SetGetQuota`, `RemoveQuota`, `IsExceeded`, `IsExceededCornerCase`, and `Checksum`.

## Control Flow

Each test creates a fresh `QuotaDatabase`, mutates quota limits/usage, and asserts direct entry layout or boolean/checksum results. The checksum test collects multiple distinct checksums after changing one field at a time, verifies they differ, then verifies rewriting the same limit and changing usage do not alter the checksum.

## State and Persistence Behavior

The tests operate purely in memory. They validate that usage is tracked for exceedance but excluded from metadata checksum.

## Dependencies and Integration Points

The file depends on GoogleTest and `master/quota_database.h`. It is created by the build system as part of quota/metarestore or master test suites depending on CMake collection.

## Risks and Edge Cases

Coverage is focused but does not directly test `getEntries`, `getEntriesWithStats`, negative `update` deltas, removal of all quota dimensions for user/group/inode, or overflow/underflow. It also assumes deterministic checksum behavior over unordered maps through order-independent checksum combination.

## Test Signals

Passing this suite is a strong signal for core quota semantics. Additional tests should target serialization ordering, stats enumeration, and delta edge cases.
