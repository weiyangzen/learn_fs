<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fd/array.h -->
# sources/distributed-fs/ceph-client/tools/lib/api/fd/array.h

## Purpose
`fd/array.h` declares the libapi poll fd array abstraction. It exposes the data structure so callers can inspect `struct pollfd` entries directly while relying on helper functions for allocation and filtering.

## Important APIs, types, and functions
`struct fdarray` contains `nr`, `nr_alloc`, `nr_autogrow`, `struct pollfd *entries`, and a parallel `priv` array whose entries can hold either `idx` or `ptr` plus flags. `enum fdarray_flags` defines `fdarray_flag__default`, `fdarray_flag__nonfilterable`, and `fdarray_flag__non_perf_event`. Public helpers cover initialization, allocation, deletion, adding, duplicating, polling, filtering, growing, printing, and `fdarray__available_entries()`.

## Control flow
Callers generally create or initialize an array, add entries, pass the array to `fdarray__poll()`, then inspect `entries[i].revents` or use `fdarray__filter()` to clear matching entries. Direct access to `priv[N].idx` or `priv[N].ptr` is allowed, but replacing the `priv` pointer is explicitly forbidden.

## State and persistence behavior
The structure owns heap allocations for `entries` and `priv` when grown. State persists only for the lifetime of the object and is not thread-safe by itself.

## Dependencies and integration points
The header forward-declares `struct pollfd` and includes `<stdio.h>` for `FILE`. It is installed by the libapi Makefile under `include/api/fd/array.h`.

## Risks and edge cases
Because the structure layout is public, external code can mutate invariants such as `nr`, `nr_alloc`, or `entries`. Users must not store pointers into `entries` or `priv` across growth. The `revents` parameter name in `fdarray__add()` actually fills `events`, which can confuse callers.

## Test signals
Compile users against the installed header, verify direct private metadata use survives `fdarray__grow()`, and run behavioral tests from `array.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fd/array.h -->
