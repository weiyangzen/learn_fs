# sources/distributed-fs/ceph-client/tools/perf/util/unwind-libdw.h

## Purpose

`unwind-libdw.h` declares libdw-specific unwind state when libdw support is enabled.

## Important APIs, Types, and Functions

Under `HAVE_LIBDW_SUPPORT`, `struct unwind_info` stores DWFL pointer, sample, machine, thread, callback, callback data, max stack, entry index, ELF flags/machine, best-effort flag, and a flexible array of `unwind_entry`. It declares `libdw__invalidate_dwfl()`.

## Control Flow and State

The state object is per-unwind invocation, while the DWFL pointer may come from maps-level cache.

## Dependencies and Integration Points

It includes `unwind.h` and references maps, machine, sample, and thread structures. It is consumed by libdw unwinding and map cleanup code.

## Risks and Test Signals

Risks include conditional compilation drift between libdw-enabled and disabled builds. Build tests should cover both configurations.
