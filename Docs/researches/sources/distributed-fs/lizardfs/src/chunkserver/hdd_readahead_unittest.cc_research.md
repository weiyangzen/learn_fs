# sources/distributed-fs/lizardfs/src/chunkserver/hdd_readahead_unittest.cc

## Purpose
This GoogleTest file verifies KiB-to-block conversion and setter/getter behavior for `HDDReadAhead`.

## Important APIs, Types, And Functions
- Helper `testHDDReadAhead` tests both max read-behind and read-ahead setters for one input.
- `TEST(HDDReadAheadTests, HDDReadAhead)` checks zero, just-under-one-block, exact one block, just-under-two-blocks, exact two blocks, and 17 blocks.

## Control Flow
Each helper invocation creates fresh `HDDReadAhead` instances, sets one value, and checks the corresponding getter.

## State And Persistence
No persistent state. Tests use local instances and do not touch `gHDDReadAhead`.

## Dependencies And Integration Points
It depends on GoogleTest, `hdd_readahead.h`, and `MFSBLOCKSIZE`.

## Risks
The test does not cover overflow, default constructor values, concurrent reads/writes, or the global instance.

## Test Signals
This is direct evidence that truncating KiB-to-block conversion is expected for common boundary values.
