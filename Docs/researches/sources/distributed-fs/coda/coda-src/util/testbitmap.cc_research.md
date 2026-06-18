# sources/distributed-fs/coda/coda-src/util/testbitmap.cc

## Purpose
Provides a small manual test program for the original `bitmap` class.

## Important APIs, Types, And Functions
The program defines `RvmType = 3` for VM mode, allocates/deletes a `bitmap`, prints it, sets and frees indexes, grows the bitmap, repeatedly calls `GetFreeIndex()`, and deletes the object.

## Control Flow
Execution exercises construction/destruction, print, `SetIndex`, `FreeIndex`, `Grow`, and free-index allocation until exhaustion. It also contains an invalid-looking `delete[100] c` expression in the source snapshot.

## State And Persistence
All state is transient heap state in VM-mode `rvmlib`.

## Dependencies And Integration Points
Depends on `bitmap.h` and a compatible C++ compiler/runtime. It is not listed in `util/tests` but is part of the utility source list.

## Risks
The program uses old K&R-style `main()` without return type and questionable array delete syntax, so it is more historical smoke test than modern unit test. It does not assert expected values automatically.

## Test Signals
Modernize or compile with legacy-tolerant flags, run under ASAN/Valgrind, and compare printed maps against expected allocation/free/grow sequences.
