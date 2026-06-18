# sources/distributed-fs/eos/mgm/tgc/DummyClock.hh

## Purpose
`DummyClock.hh` provides a controllable `IClock` implementation for deterministic unit tests of time-dependent tape-GC components such as `FreedBytesHistogram`.

## Important APIs, Types, And Functions
`DummyClock` has constructor `DummyClock(std::time_t initialTime)`, override `getTime()`, and setter `setTime(std::time_t)`.

## Control Flow
`getTime()` returns the stored timestamp. Tests move time forward or backward by calling `setTime()`, then exercise consumers.

## State And Persistence
The class stores one in-memory `std::time_t`. There is no locking, so it is intended for single-threaded tests or externally synchronized use.

## Dependencies And Integration Points
It derives from `IClock` and is used by tests for histogram aging and bin-width behavior. Production code uses `RealClock`.

## Risks And Edge Cases
The class does not prevent negative timestamps, backward time movement, or concurrent modification. That is useful for tests but would be unsafe as a production clock.

## Test Signals
Tests should verify construction, `getTime()`, `setTime()`, and consumer behavior when time advances across multiple histogram bins.
