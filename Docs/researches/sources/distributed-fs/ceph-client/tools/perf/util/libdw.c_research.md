<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libdw.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/libdw.c

## Purpose

`libdw.c` implements perf's optional elfutils/libdwfl-backed address-to-source-line and inline-frame lookup.

## Important APIs, Types, and Functions

It defines `offline_callbacks`, `dso__free_libdw()`, `dso__libdw_dwfl()`, callback args for inline unwinding, `libdw_a2l_cb()`, and public `libdw__addr2line()`.

## Control Flow

`dso__libdw_dwfl()` lazily opens the DSO, starts a Dwfl session, reports the file offline, finalizes the report, and caches the Dwfl pointer in the DSO. `libdw__addr2line()` finds the module for an address, obtains DWARF bias, finds source line info, returns file/line, and optionally walks inline functions at the address. The inline callback rewrites caller srcline on the parent frame and appends inline symbols from parent toward leaf.

## State and Persistence Behavior

The Dwfl session is cached per DSO and released by `dso__free_libdw()`. Returned file strings and inline nodes are caller-owned/perf-owned. No persistent files are written.

## Dependencies and Integration Points

It depends on elfutils libdwfl, DSO accessors, srcline helpers, symbol/inline-node helpers, and dwarf auxiliary functions. It is an alternative addr2line backend to libbfd/LLVM.

## Risks and Edge Cases

File descriptor ownership depends on `dwfl_report_offline()` success. Inline srcline ownership is subtle: the callback may transfer or free `leaf_srcline` and existing list srclines. Missing DWARF, absent module, or invalid source line returns not-found without hard error.

## Test Signals

Tests should cover line lookup, missing debug info, inline chains, DSO cleanup, invalid files, and ownership under repeated lookups with leak checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/libdw.c -->
