# sources/distributed-fs/eos/mgm/tgc/IClock.hh

## Purpose
`IClock.hh` declares the minimal clock interface used to decouple time-dependent tape-GC logic from wall-clock time.

## Important APIs, Types, And Functions
`IClock` has a virtual destructor and pure virtual `std::time_t getTime()`.

## Control Flow
Consumers call `getTime()` through the interface. Production and tests supply different implementations.

## State And Persistence
The interface owns no state. Implementations decide how time is sourced or stored.

## Dependencies And Integration Points
`FreedBytesHistogram` depends on `IClock` for current time. `RealClock` wraps `std::time(nullptr)` and `DummyClock` supplies deterministic test time.

## Risks And Edge Cases
The interface uses wall-clock seconds, not monotonic timestamps, so implementations can move backward. Callers need to tolerate clock skew or explicitly use a monotonic implementation if that becomes required.

## Test Signals
Tests should verify base-pointer deletion and correct substitution of dummy and real clocks in histogram code.
