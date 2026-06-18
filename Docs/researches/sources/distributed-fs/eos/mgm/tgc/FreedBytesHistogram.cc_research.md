# sources/distributed-fs/eos/mgm/tgc/FreedBytesHistogram.cc

## Purpose
`FreedBytesHistogram.cc` implements a thread-safe circular histogram of bytes freed over time. Tape-GC uses it to estimate space that has been queued for deletion locally but may not yet be reflected in MGM filesystem statistics.

## Important APIs, Types, And Functions
Implemented methods include the constructor, `bytesFreed()`, `getNbBytesFreedInLastNbSecs()`, `getTotalBytesFreed()`, `getFreedBytesInBin()`, `setBinWidthSecs()`, `getBinWidthSecs()`, `getNbBins()`, private `alignHistogramWithNow()`, and `getFreedBytesPerSec()`.

## Control Flow
Construction validates bin count and width. Mutating and query methods lock `m_mutex`, align the histogram to current clock time, then update or total bins. Alignment computes elapsed seconds since last update, converts that to bins, rotates `m_startIndex`, zeroes newly current bins, and updates the timestamp. `setBinWidthSecs()` rebuilds a temporary histogram by sampling old bytes-per-second estimates into new bins.

## State And Persistence
State is an in-memory vector of byte counts, current start index, bin width, clock reference, and last update timestamp. It is protected by a mutex and has finite historical depth of `nbBins * binWidthSecs`.

## Dependencies And Integration Points
The file uses constants from `Constants.hh`, `IClock`/`RealClock` or `DummyClock`, and `CtaUtils` rounding helpers. `SmartSpaceStats` calls `bytesFreed()` and query methods to augment available bytes.

## Risks And Edge Cases
`alignHistogramWithNow()` uses rounded-to-nearest bin movement, not floor, so partial-bin time movement can clear/advance sooner than expected. Negative clock movement converts through unsigned `size_t` after rounding helper behavior, which should be tested. `setBinWidthSecs()` calls `getFreedBytesPerSec()` while already holding the lock, but that helper assumes the lock and does not lock. Totals can overflow `uint64_t` if extremely large byte counts accumulate.

## Test Signals
Tests should cover invalid constructor args, bytes in current and aged bins, too-far-back exceptions, total bytes after full rotation, bin index validation, bin-width changes preserving approximate totals, dummy-clock time jumps, and concurrent access.
