# sources/distributed-fs/ceph-client/tools/perf/util/demangle-cxx.h

## Purpose

`demangle-cxx.h` declares the C-compatible interface for C++ symbol demangling.

## Important APIs, Types, and Functions

It declares `char *cxx_demangle_sym(const char *str, bool params, bool modifiers);` and wraps the declaration in `extern "C"` when included from C++.

## Control Flow

There is no runtime flow. The C++ guard ensures that the implementation can be compiled as C++ while perf's C code can link to an unmangled symbol.

## State and Persistence Behavior

No state is stored. The returned pointer ownership belongs to the caller.

## Dependencies and Integration Points

It depends on `<stdbool.h>` and integrates symbol formatting code with `demangle-cxx.cpp`.

## Risks and Edge Cases

Callers must handle `NULL` when no backend exists or demangling fails. Because output allocation is backend-owned, callers should use the expected free routine rather than stack storage assumptions.

## Test Signals

Build tests should include C and C++ translation units including this header. Runtime tests should verify flags are forwarded and `NULL` is accepted by display paths.
