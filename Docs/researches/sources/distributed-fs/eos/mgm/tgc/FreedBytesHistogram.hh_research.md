# sources/distributed-fs/eos/mgm/tgc/FreedBytesHistogram.hh

## Purpose
`FreedBytesHistogram.hh` declares the circular freed-byte histogram abstraction and its validation exceptions.

## Important APIs, Types, And Functions
The class declares exceptions `InvalidNbBins`, `InvalidBinWidth`, `TooFarBackInTime`, and `InvalidBinIndex`; constructor `FreedBytesHistogram(uint32_t nbBins, uint32_t binWidthSecs, IClock&)`; public methods `bytesFreed()`, `getNbBytesFreedInLastNbSecs()`, `getTotalBytesFreed()`, `getFreedBytesInBin()`, `setBinWidthSecs()`, `getBinWidthSecs()`, and `getNbBins()`; private methods `alignHistogramWithNow()` and `getFreedBytesPerSec()`.

## Control Flow
The header defines the contract: callers notify freed bytes, then query finite time windows. Bin 0 is the youngest bin relative to now after alignment. Requests deeper than the histogram capacity throw `TooFarBackInTime`.

## State And Persistence
Private state is a mutex, vector of counters, start index, bin width, clock reference, and last update timestamp. The clock reference must outlive the histogram.

## Dependencies And Integration Points
It depends on EOS namespace macros, `IClock`, standard vectors, mutexes, and time types. `SmartSpaceStats` owns one histogram per space-GC statistics object.

## Risks And Edge Cases
The header documents `getFreedBytesPerSec(0)` as always returning zero. Because the class uses a reference clock and mutable mutex, copy/move semantics would be problematic; they are implicitly disabled by mutex/reference members. Consumers must size query periods to fit finite capacity.

## Test Signals
Header-level tests should compile exception types, public API signatures, and ownership with dummy and real clocks. Runtime tests should validate finite-depth behavior and exception messages used by operator diagnostics.
