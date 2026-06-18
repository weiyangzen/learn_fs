# sources/distributed-fs/ceph-client/tools/perf/util/unwind-libdw.c

## Purpose

`unwind-libdw.c` implements DWARF callchain unwinding using elfutils libdwfl. It unwinds post-mortem samples from captured user registers and user stack dumps.

## Important APIs, Types, and Functions

Public functions are `unwind__get_entries()` for libdw builds and `libdw__invalidate_dwfl()`. Internal types include `struct dwfl_ui_thread_info`, which stores a cached `Dwfl` and current `unwind_info`. Key helpers report modules to DWFL, read memory from sample stack or DSOs, map perf registers to DWARF registers, process frames, and store `unwind_entry` records.

## Control Flow and State

`unwind__get_entries()` validates user regs, allocates an `unwind_info` with entry storage, obtains or creates a per-maps DWFL, sets it as busy, reads the initial IP, reports the module, attaches thread state callbacks, and calls `dwfl_getthread_frames()`. Frame callbacks adjust non-activation PCs, report modules, store entries, and stop at max depth. After unwind, entries are emitted in caller or callee order according to `callchain_param.order`, map symbols are released, and the cached DWFL is marked idle.

## Dependencies and Integration Points

It depends on libdw/libdwfl, DSOs, maps, symbols, threads, machine/env, perf regs, callchain ordering, sample user stack/regs, and build-id or symfs paths. It integrates with DWARF callchain sampling and map invalidation.

## State and Persistence Behavior

The DWFL object is cached on `struct maps` and invalidated by `libdw__invalidate_dwfl()`. During one unwind, `dwfl_ui_thread_info->ui` points to current state and asserts only one unwind per DWFL. Entries are transient and passed to the caller callback.

## Risks and Test Signals

Risks include stale cached DWFL after map changes, missing user regs/stack, unsafe unaligned stack reads, DSO module base mismatches, JIT mapping base handling, and silent best-effort failures. Tests should capture DWARF callchains, unwind through shared libraries and JIT-like maps, invalidate maps, test caller/callee ordering, handle truncated stacks, and run with and without debuginfo/build-id paths.
