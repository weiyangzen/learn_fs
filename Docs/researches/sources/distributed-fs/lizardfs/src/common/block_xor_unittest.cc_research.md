<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/block_xor_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/block_xor_unittest.cc

## Purpose

This GoogleTest file smoke-tests `blockXor()` across several offsets and sizes.

## Important APIs, Types, and Functions

It defines `TEST(BlockXorTests, BlockXor)` and calls `blockXor()` for sizes 6000, 32, and 5.

## Control Flow

Two 7000-byte vectors are allocated. Nested loops call `blockXor()` for offset values, but both pointers use `+ i`, so `j` does not affect the source offset.

## State and Persistence Behavior

Only local vectors are mutated. No persistence is involved.

## Dependencies and Integration Points

It depends on GoogleTest and `block_xor.h`.

## Risks and Edge Cases

The test asserts only that calls do not throw; it does not verify XOR results. Because the source offset ignores `j`, many intended alignment combinations are not exercised.

## Test Signals

Passing this test is a weak crash-safety signal. Correctness needs byte comparisons against expected XOR output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/block_xor_unittest.cc -->
