<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/Range.h -->
# sources/compression/zstd/contrib/pzstd/utils/Range.h

## Purpose
`Range.h` implements a lightweight pointer/iterator range used for byte slices and string-like views in pzstd.

## Important APIs, Types, And Functions
It defines `Range<Iter>`, character-pointer detection helpers, aliases such as `ByteRange`/`StringPiece`, and methods for `begin`, `end`, `data`, `size`, `empty`, `advance`, and `subtract`.

## Control Flow
Constructors create begin/end pairs from pointers, arrays, or pointer+size. Mutators move the start or end inward, enabling cheap slice consumption.

## State And Persistence
State is just two iterators/pointers. It owns no memory and persists nothing.

## Dependencies And Integration Points
`Buffer`, `SkippableFrame`, file-system helpers, and tests use ranges to avoid copying byte/string data.

## Risks
Ranges are non-owning, so lifetime and boundary correctness belong to callers. Advancing beyond end would be a logic bug.

## Test Signals
`RangeTest.cpp` covers constructors, mutation, string conversion, and char-pointer behavior.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/Range.h -->
