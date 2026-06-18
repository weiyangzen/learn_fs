# sources/distributed-fs/eos/mgm/tgc/RealClock.hh

## Purpose
`RealClock.hh` declares the production `IClock` implementation backed by `std::time()`.

## Important APIs, Types, And Functions
`RealClock` derives from `IClock` and overrides `getTime()`.

## Control Flow
Consumers call the interface method to retrieve current epoch seconds.

## State And Persistence
The class owns no state and is safe to construct cheaply.

## Dependencies And Integration Points
It depends on `IClock` and is used by `SmartSpaceStats`/`FreedBytesHistogram` in production.

## Risks And Edge Cases
It does not provide monotonic semantics. Any component needing duration measurement across clock adjustments should use a different clock implementation.

## Test Signals
Build tests with the real implementation and functional tests of consumers using dummy clocks for deterministic cases.
