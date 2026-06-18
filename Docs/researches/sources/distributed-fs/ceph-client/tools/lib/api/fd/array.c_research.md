<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fd/array.c -->
# sources/distributed-fs/ceph-client/tools/lib/api/fd/array.c

## Purpose
`fd/array.c` implements a growable array of `struct pollfd` entries with synchronized per-entry private metadata. It is a convenience layer for tools that manage many fds and want filtering/destruction around `poll()`.

## Important APIs, types, and functions
Core functions are `fdarray__init()`, `fdarray__grow()`, `fdarray__new()`, `fdarray__exit()`, `fdarray__delete()`, `fdarray__add()`, `fdarray__dup_entry_from()`, `fdarray__filter()`, `fdarray__poll()`, and `fdarray__fprintf()`. The implementation maintains `entries` and `priv` arrays with identical allocation and indexing.

## Control flow
Users initialize or allocate an array, add fd/event pairs, call `fdarray__poll()`, then call `fdarray__filter()` to clear entries whose `revents` match a mask. Filtering optionally calls a destructor for matching entries and returns the count of remaining filterable entries. Cleanup frees both arrays and resets the structure.

## State and persistence behavior
All state is caller-owned in `struct fdarray`: current count, allocation count, autogrow amount, poll entries, and private metadata. It is runtime-only and freed by `fdarray__exit()`/`fdarray__delete()`.

## Dependencies and integration points
It depends on libc allocation, `<poll.h>`, and the public `array.h`. It integrates with perf/tool event loops that need to keep an fd and an index/pointer side by side.

## Risks and edge cases
`fdarray__grow()` reallocates `entries` first and then `priv`; if the second allocation fails, it frees the newly returned `entries` pointer. When `realloc()` moved storage, that can drop the original entries while `fda->entries` still points to freed memory. Autogrow of zero makes `fdarray__add()` fail once full. Filtering clears event fields but does not compact arrays or close fds unless a destructor does so.

## Test signals
Tests should add beyond initial allocation, verify private metadata stays aligned, poll/filter with a pipe or eventfd, exercise destructor calls, duplicate entries from one array to another, and force allocation-failure paths under fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fd/array.c -->
