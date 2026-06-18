# sources/distributed-fs/openafs/src/WINNT/talocale/tal_alloc.cpp

## Purpose

`tal_alloc.cpp` implements the debug memory instrumentation backend declared in `tal_alloc.h`. In debug builds it tracks allocations made through `Allocate`/`Free` and `New`/`Delete`, records file/line/expression metadata, detects invalid frees, double frees, and overwritten trailing signatures, maintains aggregate allocation statistics, and optionally presents a Win32 list-view memory-manager window.

## Important APIs, Types, and Functions

- It forces `DEBUG` on and `NO_DEBUG_ALLOC` off for this implementation so the instrumentation itself is built.
- `MEMCHUNK` records one allocation: data pointer, size, expression, source file, line, allocation tick, optional trailing signature, C++/dynamic kind, hash links, freed/list/tared flags.
- `BUCKET` and `HASH()` implement a pointer-keyed hash table over `MEMCHUNK` entries.
- `ALLOCEXPANDARRAY` is a private segmented array that stores `MEMCHUNK` records in `GlobalAlloc()` heaps of 1024 elements each.
- `STATISTICS` tracks live C++ allocations, dynamic allocations, totals, and tared counts/bytes.
- `MemMgr_Initialize()` initializes the process-global critical section, chunk array, and default hash buckets.
- `MemMgr_TrackAllocation()` writes an optional end signature, creates or reuses a `MEMCHUNK`, links it into the hash table, updates stats, and posts UI refresh messages.
- `MemMgr_TrackDestruction()` finds the chunk, validates the pointer and trailing signature, warns on invalid/double free, marks the chunk freed, removes it from the UI list, and decrements stats.
- Public exports are `ShowMemoryManager()`, `WhileMemoryManagerShowing()`, `IsMemoryManagerMessage()`, `MemMgr_AllocateMemory()`, `MemMgr_FreeMemory()`, `MemMgr_TrackNew()`, and `MemMgr_TrackDelete()`.
- UI helpers include `MemMgr_DlgProc()`, `MemMgr_OnInit()`, `MemMgr_OnRefresh()`, `MemMgr_OnTare()`, `MemMgr_OnReset()`, `MemMgr_OnSort()`, and list insertion/removal helpers.

## Control Flow

Instrumentation starts lazily. A public allocate/new wrapper calls `MemMgr_TrackAllocation()`, which calls `MemMgr_Initialize()` if needed, enters the global critical section, grows/rebuilds hash buckets when the chunk count crosses the bucket threshold, writes the trailing `'Okay'` signature for `Allocate()`, fills a `MEMCHUNK`, links or reuses a record, updates live byte/count statistics, and schedules a manager-window refresh if the UI is open.

Free/delete calls flow through `MemMgr_TrackDestruction()`. The function locates the chunk by pointer hash, warns if the pointer is unknown, warns if the dynamic-allocation trailer was overwritten, warns if a chunk is already marked freed, then marks it freed and updates UI/statistics. With `TRACK_FREED` enabled, freed records remain in the metadata heap so future reuse of the same address can be detected and replaced.

The UI path begins with `ShowMemoryManager()`, which restores window/list settings from the registry and creates a top-level window by creating a `Static` window and replacing its window procedure with `MemMgr_DlgProc()`. `IDC_INITIALIZE` creates child controls, populates the list from non-tared live chunks, installs a timer, and refreshes statistics. Tare hides current live allocations from the list and moves counts into tared buckets; reset reverses that tare state. Column clicks resort by rebuilding the list in sorted insertion order.

## State and Persistence

The main state is the static `l` structure: critical section pointer, manager window handle, timer ID, expandable chunk heap, chunk count, bucket table, and live statistics. The static `lr` structure stores UI window bounds, column widths, sort column, and sort direction. `MemMgr_RestoreSettings()` and `MemMgr_StoreSettings()` persist `lr` under `HKLM\Software\Random\MemMgr\Settings`. Allocation metadata and stats are process-local and are not persisted.

## Dependencies and Integration Points

This file depends heavily on Win32 and common controls: `GlobalAlloc`, `GlobalFree`, critical sections, registry APIs, `CreateWindowEx`, list-view messages, timers, message boxes, and stock GUI fonts. It integrates with `tal_alloc.h` macros used by the TaLocale library and any other debug Windows code that includes the header. It also provides `FormatBytes`/`FormatTime` helpers local to the memory-manager UI, separate from similarly named TaLocale string exports.

## Risks and Edge Cases

- Pointer hashing uses `PtrToUlong()`/`DWORD`, which truncates pointer identity on 64-bit builds.
- The code stores numeric sort keys by casting integers and pointers to `LPTSTR`, and compares them by pointer subtraction; this is legacy Win32 C++ and risky on modern compilers.
- `MemMgr_TrackDestruction()` returns `TRUE` even after unknown or double frees, so `MemMgr_FreeMemory()` still calls `GlobalFree()` on the supplied pointer.
- Registry persistence uses `HKEY_LOCAL_MACHINE`, which may fail under normal user privileges.
- The manager window is implemented by subclassing a `Static` control rather than registering a dedicated class; behavior depends on Win32 message handling quirks.
- The UI and allocation tracking share state through posted messages and copied chunks; correctness depends on the global critical section and window lifetime checks.

## Test Signals

The code is testable through debug builds that use `Allocate`/`Free`/`New`/`Delete`, open the memory manager with `ShowMemoryManager()` or F8 through `IsMemoryManagerMessage()`, and intentionally exercise double free, bad pointer free, and trailer overwrite cases. The visible signals are MessageBox warnings, live list rows, aggregate stats, and stable process behavior during concurrent allocation.
