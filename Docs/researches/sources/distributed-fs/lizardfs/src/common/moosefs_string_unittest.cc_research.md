<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/moosefs_string_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/moosefs_string_unittest.cc

## Purpose
Tests MooseFS-compatible string serialization for multiple length widths. The source was read completely for this report.

## Important APIs, Types, And Functions
Uses `MooseFsString<uint8_t/uint16_t/uint32_t>`, project serialize/deserialize helpers, and in/out pair macros.

## Control Flow
Builds long test strings, serializes substrings sized for each length width, deserializes, and checks equality and buffer size. Max-length test validates overflow rejection for 8-bit length.

## State And Persistence Behavior
No persistence beyond in-memory byte buffers.

## Dependencies And Integration Points
Depends on gtest and `unittests/inout_pair.h`.

## Risks And Edge Cases
Does not test deserializing into non-empty strings or malformed/truncated buffers except indirectly.

## Test Signals
Passing tests protect length-prefix sizing and round-trip compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/moosefs_string_unittest.cc -->
