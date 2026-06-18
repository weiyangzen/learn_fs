# sources/distributed-fs/eos/unit_tests/mgm/CtaUtilsTests.cc

## Purpose
Tests CTA/tape garbage collection utility helpers for numeric parsing, integer division rounding, binary time conversion, and bounded file descriptor reads.

## Important APIs, types, and functions
The file exercises `CtaUtils::toUint64`, `divideAndRoundToNearest`, `divideAndRoundUp`, `bufToTimespec`, and `readFdIntoStr`. It expects custom exceptions such as `EmptyString`, `NonNumericChar`, `ParsedValueOutOfRange`, and `BufSizeMismatch`.

## Control flow
Tests validate successful and failing integer parse inputs, exhaustive small-number rounding cases, binary serialization/deserialization of `timespec`, pipe-based reads with exact, truncated, and shorter-than-limit data, and a too-large max string length throwing `std::out_of_range`.

## State and persistence
All state is local to the test process. Pipe file descriptors are created for read tests; production callers may use the same helper to read proc or command output.

## Dependencies and integration points
Depends on MGM `CtaUtils.hh`, Google Test, `<limits>`, and POSIX `pipe`/`write`. It supports tape GC and CTA integration code.

## Risks and test signals
The tests cover many boundaries but do not close pipe fds explicitly, which is acceptable for short tests but not a production pattern. Additional tests should cover interrupted reads, nonblocking fds, negative divisors if allowed by type, and platform differences in `timespec` binary layout.
