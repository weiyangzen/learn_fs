# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/general.h

## Purpose
`general.h` declares the per-window interlocked counter helpers used by the UI refresh machinery.

## Important APIs, Types, And Functions
It exposes `LONG InterlockedIncrementByWindow(HWND hWnd)` and `LONG InterlockedDecrementByWindow(HWND hWnd)`.

## Control Flow
No logic is present in the header. Callers increment before starting work associated with a window and decrement when that work finishes.

## State And Persistence
No storage is declared. The implementation keeps process-local counters in `general.cpp`.

## Dependencies And Integration Points
The API depends on Win32 `HWND` and `LONG` types. Its main consumer is `display.cpp`.

## Risks And Test Signals
Risks are tied to lifecycle semantics: callers must balance increments and decrements or completion handlers will run too early or too late. Compile coverage and display-queue completion tests cover the header contract.
