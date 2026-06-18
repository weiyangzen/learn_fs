# sources/distributed-fs/ceph-client/tools/perf/util/srccode.h

## Purpose

`srccode.h` declares the lightweight state and lookup API for retrieving source-code line slices.

## Important APIs, Types, and Functions

`struct srccode_state` holds a `srcfile` string and current line number. `srccode_state_init()` clears those fields. `srccode_state_free()` releases the state-owned filename. `find_sourceline()` returns a pointer and length for a given source filename and one-based line number.

## Control Flow and Data Flow

Consumers initialize state, resolve or update source file/line state elsewhere, and call `find_sourceline()` when they need the text. The result is a raw slice, not a C string.

## State and Persistence Behavior

The state struct owns `srcfile` when populated. The source-line data returned by `find_sourceline()` is owned by the cache in `srccode.c` and may be invalidated by cache eviction.

## Dependencies and Integration Points

The header is self-contained and is used by source annotation/display code.

## Risks and Edge Cases

Callers must not `free()` the returned line pointer or assume NUL termination. Line numbers are one-based in the API. Failing to call `srccode_state_free()` leaks `srcfile`.

## Test Signals

Compile coverage, initialization/free idempotence, and source-line display tests are the key signals.
