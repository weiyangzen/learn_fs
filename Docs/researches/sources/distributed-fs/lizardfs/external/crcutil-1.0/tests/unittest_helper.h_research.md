<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/unittest_helper.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/unittest_helper.h

## Purpose
Minimal assertion macro support for crcutil tests when a richer test framework is not present.

## Important APIs, Types, and Functions
Defines `DEBUG_BREAK`, `CHECK(cond)`, `CHECK_GE(a,b)`, `CHECK_NE(a,b)`, and `CHECK_EQ(a,b)` unless `CHECK` is already defined. MSVC uses `__debugbreak()`; other builds call `exit(1)` after printing.

## Control Flow, State, and Persistence
`CHECK` evaluates a condition once, prints file, line, and failed expression to stderr, flushes, and breaks/exits. There is no persistent state.

## Dependencies and Integration Points
Depends on `std_headers.h` for C stdio/exit declarations and is included by `unittest.h` throughout verifier code.

## Risks and Test Signals
Risks include abrupt process termination that bypasses cleanup, no typed comparison diagnostics beyond the expression text, and macro namespace collision if consumers already define `CHECK`. Test signals are intentional failing assertions, successful preservation of an existing `CHECK` macro, and expected debugger break behavior under MSVC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/unittest_helper.h -->
