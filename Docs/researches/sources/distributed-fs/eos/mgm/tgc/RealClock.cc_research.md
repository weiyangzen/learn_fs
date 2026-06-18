# sources/distributed-fs/eos/mgm/tgc/RealClock.cc

## Purpose
`RealClock.cc` implements the production clock for tape-GC time calculations.

## Important APIs, Types, And Functions
It defines `RealClock::getTime()`.

## Control Flow
The method returns `std::time(nullptr)` each time it is called.

## State And Persistence
There is no stored state or persistence.

## Dependencies And Integration Points
`SmartSpaceStats` owns a `RealClock` before its `FreedBytesHistogram`, giving the histogram a production wall-clock source.

## Risks And Edge Cases
`std::time()` is wall-clock time and can jump backward or forward due to system time changes. Histogram code must tolerate those jumps.

## Test Signals
Compile/link coverage plus integration with `FreedBytesHistogram` is sufficient; deterministic behavior should use `DummyClock`.
