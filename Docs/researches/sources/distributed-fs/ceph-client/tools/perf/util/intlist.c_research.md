<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intlist.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/intlist.c

## Purpose

`intlist.c` implements a sorted set/list of unsigned long integers on top of perf's generic red-black-tree `rblist` helper.

## Important APIs, Types, and Functions

The file implements `intlist__new()`, `intlist__delete()`, `intlist__add()`, `intlist__remove()`, `intlist__find()`, `intlist__findnew()`, and `intlist__entry()`. Internal callbacks `intlist__node_new()`, `intlist__node_delete()`, and `intlist__node_cmp()` adapt `struct int_node` to `rblist`.

## Control Flow

Construction initializes `rblist` callbacks and optionally parses a comma-separated decimal list. Adding and lookup pass the integer value cast through `void *` into rblist. Parsing loops over `strtol()`, requiring each token to end in comma or NUL, and aborts by deleting the list on malformed input or allocation failure.

## State and Persistence Behavior

State is entirely heap-resident in `struct intlist`; each `struct int_node` stores the key and a caller-owned `priv` pointer. There is no serialization.

## Dependencies and Integration Points

It depends on `rblist`, Linux rb-tree helpers, `container_of`, and errno values. Users include filters and KVM/stat helpers needing ordered integer sets.

## Risks and Edge Cases

The integer is cast through `void *`, which is conventional in this codebase but depends on pointer width being able to carry `unsigned long`. `strtol()` permits leading whitespace and signs but the destination is unsigned long; negative inputs can wrap. Duplicate behavior is inherited from `rblist__add_node()`. Empty or trailing-comma strings should be validated by callers/tests.

## Test Signals

Unit tests should cover sorted insertion, duplicate insertion behavior, lookup without creation, findnew creation, removal during safe iteration, parsing valid comma lists, invalid separators, empty input, and negative or overflow-like values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intlist.c -->
