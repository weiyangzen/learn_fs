# sources/distributed-fs/ceph-client/tools/perf/util/unwind-libunwind.c

## Purpose

`unwind-libunwind.c` selects and dispatches libunwind operations for a thread's maps based on build support, target architecture, and DSO bitness.

## Important APIs, Types, and Functions

It defines weak operation pointers `local_unwind_libunwind_ops`, `x86_32_unwind_libunwind_ops`, and `arm64_unwind_libunwind_ops`. Public functions are `unwind__prepare_access()`, `unwind__flush_access()`, `unwind__finish_access()`, and `unwind__get_entries()`.

## Control Flow and State

Preparation is skipped if no DWARF callchain users exist or an address space is already initialized. Otherwise it inspects machine environment architecture and DSO type to choose local, x86-32, or arm64 ops, stores selected ops on maps, and invokes `prepare_access()`. Flush/finish/get delegate through maps-stored ops when present.

## Dependencies and Integration Points

It depends on DSO type detection, maps state, thread maps, machine env architecture, session callchain globals, and architecture-specific libunwind backends. It is called from map insertion and thread preparation paths.

## State and Persistence Behavior

Selected ops and address space are stored in maps. Preparation can report `initialized` to indicate whether a new address space was created.

## Risks and Test Signals

Risks include unsupported arch warnings, wrong backend for mixed-bit DSOs, live mode with missing env arch, and no-op behavior when ops are unavailable. Tests should cover live mode, x86 32-bit perf.data on 64-bit host, arm/arm64 selection, unsupported arch, repeated prepare, flush, finish, and get without ops.
