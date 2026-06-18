# sources/distributed-fs/eos/mgm/tgc/IClock.cc

## Purpose
`IClock.cc` provides the out-of-line virtual destructor for the tape-GC clock interface.

## Important APIs, Types, And Functions
The file defines `IClock::~IClock()`.

## Control Flow
There is no runtime behavior beyond allowing polymorphic destruction of `IClock` implementations.

## State And Persistence
No state is owned or persisted.

## Dependencies And Integration Points
This definition supports `DummyClock`, `RealClock`, and any other clock injected into `FreedBytesHistogram`.

## Risks And Edge Cases
If this file is omitted from a build target, users of `IClock` can hit unresolved vtable/destructor symbols. The destructor is empty and intentionally non-throwing by behavior, though not explicitly marked `noexcept`.

## Test Signals
Compile/link tests that construct and delete `IClock` implementations through base pointers are sufficient.
