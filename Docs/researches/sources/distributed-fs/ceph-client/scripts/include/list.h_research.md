# sources/distributed-fs/ceph-client/scripts/include/list.h

## Purpose
Implements a scripts-side subset of Linux doubly linked list and hlist primitives for host tools.

## APIs, Control Flow, and State
The header provides `container_of()`, list poisons, `LIST_HEAD` initializers, add/delete/replace/move helpers, empty/position tests, entry accessors, forward/reverse/safe typed iteration macros, and hlist initialization, deletion, add-head, entry, and iteration helpers. State is held by caller-owned `struct list_head` or `struct hlist_node` links.

## Dependencies and Integration
It depends on `stddef.h` and `list_types.h`, and uses GCC extensions such as `typeof`, statement expressions, and `_Static_assert`. It supports host utilities such as `genksyms`.

## Risks and Test Signals
Risks are typical intrusive-list hazards: deleting uninitialized nodes, using entries after poison, empty-list misuse with first/last accessors, and compiler incompatibility outside GCC/Clang-like hosts. Test signals are host-tool builds with warnings enabled and focused add/delete/iteration tests if helpers change.
