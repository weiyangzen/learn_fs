<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/RangeTest.cpp -->
# sources/compression/zstd/contrib/pzstd/utils/test/RangeTest.cpp

## Purpose
This test validates `Range` constructors and mutating slice operations.

## Important APIs, Types, And Functions
It covers empty ranges, pointer/array/string-style constructors, `advance`, `subtract`, `data`, `begin`, `end`, `size`, and conversion to `std::string` for verification.

## Control Flow
Tests create ranges over static strings, move the begin/end boundaries, and compare contents against expected substrings.

## State And Persistence
Only stack/static string data is used. No persistence exists.

## Dependencies And Integration Points
It depends on GoogleTest and `utils/Range.h`. It protects non-owning views used by buffers, filesystem helpers, and skippable frames.

## Risks
It does not exercise invalid lifetime scenarios because those are caller responsibility.

## Test Signals
Passing tests indicate basic range math is stable.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/RangeTest.cpp -->
