# sources/distributed-fs/ceph-client/tools/perf/util/demangle-java.h

## Purpose

`demangle-java.h` declares perf's Java symbol demangling function and option flag.

## Important APIs, Types, and Functions

It defines `JAVA_DEMANGLE_NORET` and declares `char *java_demangle_sym(const char *str, int flags);`.

## Control Flow

There is no control flow. Consumers include the header and request Java descriptor demangling with or without return types.

## State and Persistence Behavior

No state is stored. Returned strings are heap allocated by `demangle-java.c` and owned by the caller.

## Dependencies and Integration Points

The header has no external dependencies beyond C compilation. It integrates perf's symbol formatting logic with the Java parser.

## Risks and Edge Cases

Callers must accept `NULL` for non-Java or malformed names. The flag space currently contains only `JAVA_DEMANGLE_NORET`, so future flags should avoid changing existing behavior.

## Test Signals

Tests should compile consumers, verify flag handling, and ensure display paths fall back gracefully when demangling returns `NULL`.
