<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/list.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/list.h

## Purpose
`list.h` provides Linux intrusive doubly linked list and hlist primitives for user-space tools.

## APIs And Flow
It defines list heads, initialization, add, tail add, delete, replace, move, splice, cut, rotate, emptiness tests, entry accessors, forward/reverse/safe iteration macros, and hlist equivalents including add, delete, fake nodes, membership checks, and hlist iteration. Control flow is pointer rewriting around embedded `struct list_head` or `struct hlist_node`; safe iterators prefetch the next cursor before body execution.

## State, Dependencies, Risks, Tests
State is entirely caller-owned intrusive linkage. Dependencies are `linux/types.h`, `linux/poison.h`, `linux/kernel.h`, and `linux/compiler.h`; optional debug-list paths require external implementations. Risks include use-after-delete via poisoned pointers, no inherent locking, unsafe iteration if non-safe macros remove entries, and hlist nodes needing initialization before membership tests. Tests should cover add/delete/move/splice/cut, safe iteration with removal, hlist bucket operations, poison-triggered misuse, and debug-list builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/list.h -->
