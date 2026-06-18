# sources/distributed-fs/openafs/src/WINNT/talocale/tal_alloc.h

## Purpose

`tal_alloc.h` exposes TaLocale's optional debug allocation instrumentation. It lets callers replace raw `GlobalAlloc`/`GlobalFree` and C++ `new`/`delete` usage with macros that record expression, file, and line metadata in debug builds, while compiling to normal allocation operations when instrumentation is disabled.

## Important APIs, Types, and Functions

- `NO_DEBUG_ALLOC` is automatically defined when `DEBUG` is not defined, disabling instrumentation.
- `MEMMGR_CALLCONV` defaults to `_cdecl`; `EXPORTED` defaults to `__declspec(dllexport)`.
- In non-instrumented mode, `Allocate`, `Free`, `New`, `New2`, and `Delete` directly wrap `GlobalAlloc`, `GlobalFree`, `new`, and `delete`.
- In instrumented mode, those macros call `MemMgr_AllocateMemory`, `MemMgr_FreeMemory`, `MemMgr_TrackNew`, and `MemMgr_TrackDelete` with source metadata.
- Debug UI exports are `ShowMemoryManager()`, `WhileMemoryManagerShowing()`, and `IsMemoryManagerMessage(MSG *pMsg)`.

## Control Flow

Including the header selects either the fast path or the instrumentation path at compile time. Non-debug code allocates directly. Debug instrumented code routes every macro call to the backend before or after the actual C++ operation, allowing `tal_alloc.cpp` to track metadata and validate frees. `New2` exists for constructors requiring a parenthesized argument list.

## State and Persistence

The header itself has no state. It controls whether client code contributes state to the backend memory manager. In debug builds, UI/window settings and allocation metadata are handled in `tal_alloc.cpp`.

## Dependencies and Integration Points

Consumers must include Windows types and link against the backend implementation when `DEBUG` and instrumentation are enabled. The comments note that DLL users must export/import the memory-manager functions consistently so all modules share the same manager instance.

## Risks and Edge Cases

- The `Delete` macro is single-object `delete`; it does not use `delete[]`, even though the examples show `New(TCHAR[256])`, which is a mismatch in modern C++ terms.
- Instrumentation is compile-time and macro-based, so mixed modules with inconsistent `DEBUG`, `NO_DEBUG_ALLOC`, or import/export settings can track only part of the process.
- Passing macro arguments with side effects is risky because the macros embed them into allocation expressions and metadata strings.

## Test Signals

Compile-time signal is whether macros expand to direct allocation or `MemMgr_*` calls. Runtime signal comes from the backend memory-manager UI and validation warnings when instrumented allocation/free paths are exercised.
