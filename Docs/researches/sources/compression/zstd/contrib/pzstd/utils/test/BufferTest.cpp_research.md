<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/BufferTest.cpp -->
# sources/compression/zstd/contrib/pzstd/utils/test/BufferTest.cpp

## Purpose
This test verifies `Buffer` construction, ownership sharing, and slice mutation.

## Important APIs, Types, And Functions
It defines a custom deleter and tests constructors, `use_count`, `advance`, `splitAt`, `subtract`, `range`, and `size`.

## Control Flow
Tests allocate buffers, copy/split them, inspect shared ownership counts, mutate ranges, and assert resulting first/last bytes and sizes.

## State And Persistence
State is local heap buffers and shared pointers. No files are written.

## Dependencies And Integration Points
It depends on GoogleTest and `utils/Buffer.h`. It protects pzstd queue buffer behavior.

## Risks
Tests focus on normal boundaries; additional negative tests would be needed for invalid split/advance inputs.

## Test Signals
Passing tests support correctness of buffer slicing used by zstd stream adapters.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/BufferTest.cpp -->
