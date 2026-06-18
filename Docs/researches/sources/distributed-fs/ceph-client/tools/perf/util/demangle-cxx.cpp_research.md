# sources/distributed-fs/ceph-client/tools/perf/util/demangle-cxx.cpp

## Purpose

`demangle-cxx.cpp` provides perf's C++ symbol demangling wrapper with multiple backend choices.

## Important APIs, Types, and Functions

The single exported function is `cxx_demangle_sym(const char *str, bool params, bool modifiers)`. Depending on build configuration it calls `bfd_demangle()`, `cplus_demangle()`, or `abi::__cxa_demangle()`. `DMGL_PARAMS` and `DMGL_ANSI` are defined when needed to control argument and modifier inclusion.

## Control Flow

The function selects the first available compile-time backend. BFD and cplus-demangle paths honor `params` and `modifiers`; the `__cxa_demangle` path ignores those flags and returns the ABI demangler result. If no backend is compiled in, it returns `NULL`.

## State and Persistence Behavior

No state is stored. Returned demangled strings are heap allocated by the backend and must be freed by the caller according to perf's demangler contract.

## Dependencies and Integration Points

It depends on `demangle-cxx.h`, optional BFD, optional libiberty cplus demangle support, optional C++ ABI demangle support, and C linkage for consumption by C perf code. It integrates with symbol display and reporting paths.

## Risks and Edge Cases

Backend semantics differ: `__cxa_demangle` may include full parameter/modifier information regardless of requested flags, while BFD/libiberty honor flags. Invalid or non-C++ names return `NULL`. Build-system macro order determines which backend is used.

## Test Signals

Tests should cover mangled C++ names with and without parameter/modifier requests, invalid names, all supported backend configurations, no-backend builds, and caller freeing behavior under leak sanitizers.
