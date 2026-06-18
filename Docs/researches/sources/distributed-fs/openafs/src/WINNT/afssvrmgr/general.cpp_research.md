# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/general.cpp

## Purpose
`general.cpp` provides a small synchronization utility that associates a `LONG` counter with an `HWND` and exposes interlocked increment/decrement operations for that counter. The display scheduler uses it to know when all outstanding updates for a window have completed.

## Important APIs, Types, And Functions
Public functions are `InterlockedIncrementByWindow` and `InterlockedDecrementByWindow`. The private helper `FindLongByWindow` lazily initializes `pcsWindowList`, searches `aWindowList`, and allocates entries in chunks of 16 using `REALLOC`.

## Control Flow
On each increment or decrement, the code finds or creates the row for the supplied window while holding a critical section, then calls the Win32 `InterlockedIncrement` or `InterlockedDecrement` primitive on the associated counter outside the table lock.

## State And Persistence
State is process-local: a grow-only static array of `{ HWND hWnd; LONG dw; }` records and one critical section. Entries are never removed when windows are destroyed.

## Dependencies And Integration Points
The main integration point is `display.cpp`, which increments before scheduling a display operation and decrements when the operation completes. It depends on Win32 handles, critical sections, and interlocked APIs.

## Risks And Edge Cases
The table leaks stale HWND entries for the process lifetime, which is acceptable for a small legacy GUI but can grow with many transient windows. Reuse of destroyed HWND values could associate a new window with an old nonzero counter if lifetimes overlap badly. Lazy critical-section initialization is not itself protected against simultaneous first callers.

## Test Signals
Test repeated increments/decrements for one window, many windows forcing `REALLOC`, concurrent access from display worker threads, zero return after balanced operations, and behavior after window destruction/recreation.
