# sources/distributed-fs/ceph-client/tools/perf/util/unwind.h

## Purpose

`unwind.h` declares the generic DWARF unwind abstraction used by perf callchain code.

## Important APIs, Types, and Functions

`struct unwind_entry` carries a `map_symbol` and IP. `unwind_entry_cb_t` is the callback type. `struct unwind_libunwind_ops` is the backend vtable for prepare, flush, finish, and entry extraction. Depending on build flags, the header declares real `unwind__get_entries()`, libunwind register and access functions, or inline no-op stubs.

## Control Flow and State

The header gates unwind functionality by `HAVE_DWARF_UNWIND_SUPPORT` and `HAVE_LIBUNWIND_SUPPORT`. Unsupported builds compile callers but return no entries.

## Dependencies and Integration Points

It depends on map-symbol state and is used by callchain sampling, thread map insertion, and report/script unwinding.

## Risks and Test Signals

Risks include callers not distinguishing no-op stubs from successful empty unwinds, and build matrix drift. Tests should cover DWARF-enabled and disabled builds.
