# sources/distributed-fs/ceph-client/tools/perf/util/unwind-libunwind-local.c

## Purpose

`unwind-libunwind-local.c` implements local post-mortem DWARF unwinding using libunwind over perf's captured register and stack dumps.

## Important APIs, Types, and Functions

The file defines libunwind accessors for procedure info, memory, registers, unsupported fpregs/resume/name lookups, and cache cleanup. It includes ELF helpers for `.eh_frame_hdr`, `.debug_frame`, executable detection, and base address calculation. Publicly, it publishes `local_unwind_libunwind_ops` with `prepare_access`, `flush_access`, `finish_access`, and `get_entries`.

## Control Flow and State

`_unwind__prepare_access()` creates a libunwind address space with custom accessors and stores it on maps. `find_proc_info()` locates the map/DSO for an IP, tries `.eh_frame_hdr` first using libunwind's remote table search, then `.debug_frame` when enabled. `access_mem()` reads from the captured stack if an address falls in the sampled stack range, otherwise reads from mapped DSO data. `access_reg()` maps libunwind registers to perf regs and reads from sample user regs. `_unwind__get_entries()` builds initial state and `get_entries()` records the sampled IP, initializes a remote cursor, steps frames up to max depth, adjusts non-signal-frame return IPs, and emits entries in configured order.

## Dependencies and Integration Points

It depends on libunwind, libelf/gelf, maps, DSOs, symbols, machine/session, perf regs, callchain configuration, and sample user stack/regs. `unwind-libunwind.c` selects these ops for supported target architectures.

## State and Persistence Behavior

The libunwind address space is stored in maps and uses global caching policy. DSO data caches `.eh_frame_hdr`, `.debug_frame`, and ELF base offsets. Unwind entries are transient callback outputs.

## Risks and Test Signals

Risks include unsupported pointer encodings, stale address-space caches, missing CFI sections, debuglink path failures, stack range boundary mistakes, register mapping gaps, and architecture mismatch for 32-bit or arm targets. Tests should cover unwinding through binaries with `.eh_frame_hdr`, `.debug_frame`, debuglink debuginfo, missing stack/register data, cache flush/finish, caller/callee ordering, and mixed-architecture perf.data.
