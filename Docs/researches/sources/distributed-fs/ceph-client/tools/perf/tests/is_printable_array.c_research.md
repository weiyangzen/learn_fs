# sources/distributed-fs/ceph-client/tools/perf/tests/is_printable_array.c

## Purpose
Tests `is_printable_array()` classification for NUL-terminated printable byte arrays and non-printable or non-terminated inputs.

## Important APIs, Types, and Functions
- `test__is_printable_array()` defines a table of buffer pointer, length, and expected return value.
- Uses two explicit buffers containing control byte `4` in different positions.
- Calls `is_printable_array((char *)t[i].buf, t[i].len)` for each row.

## Control Flow
The test iterates the table and returns `TEST_FAIL` immediately on the first mismatch, logging the row index. Cases include a full `"krava"` array with NUL, the same string without NUL in the length, an empty string with and without NUL, a NULL pointer with length zero, and arrays containing non-printable bytes.

## State and Persistence
No mutable state escapes the stack-local buffers and table. No allocations or file operations occur.

## Dependencies and Integration Points
Depends on `print_binary.h` for `is_printable_array()`, Linux `ARRAY_SIZE`, perf debug output, and `DEFINE_SUITE("is_printable_array", is_printable_array)`.

## Risks and Edge Cases
- The table asserts that length must include the terminating NUL for a printable string to return true.
- It only covers a small ASCII-like input set and one control byte.

## Test Signals
Passing confirms expected truth values for printable, empty, NULL, unterminated, and non-printable buffer cases.
