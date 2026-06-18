# sources/distributed-fs/ceph-client/tools/perf/util/demangle-ocaml.h

## Purpose

`demangle-ocaml.h` declares perf's OCaml symbol demangling interface.

## Important APIs, Types, and Functions

It declares `char *ocaml_demangle_sym(const char *str);`.

## Control Flow

There is no executable flow. Consumers call the function and use `NULL` as the signal that a symbol was not OCaml-mangled or could not be demangled.

## State and Persistence Behavior

No state is stored. Returned strings are heap allocated and caller-owned.

## Dependencies and Integration Points

The header has no external dependencies and integrates symbol display code with `demangle-ocaml.c`.

## Risks and Edge Cases

Callers must handle `NULL` and free non-null results. The API does not expose flags, so all behavior changes in the implementation affect all consumers.

## Test Signals

Compile tests should cover inclusion from C files. Runtime tests should verify non-OCaml fallback, allocation ownership, and formatted symbol output.
