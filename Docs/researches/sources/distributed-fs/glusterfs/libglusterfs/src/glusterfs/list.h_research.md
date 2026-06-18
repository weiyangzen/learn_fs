# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/list.h

## Purpose
Provides GlusterFS's intrusive circular doubly linked list primitives, closely resembling Linux kernel `list_head`.

## APIs, Types, and Functions
`struct list_head` stores next/prev pointers. APIs/macros initialize, add head/tail, ordered add by comparator, delete, delete-and-init, move head/tail, test empty/last/singular, splice/append with optional source reinit, replace with optional old reinit, rotate left, convert node to containing entry, access first/last/next/previous entries, iterate forward/reverse, safe iterate while deleting, and return nullable next/prev entries relative to a head. `LIST_POISON1` and `LIST_POISON2` mark deleted links.

## Control Flow, State, and Persistence
Lists are embedded into owning structures; the head is a sentinel and empty list points to itself. Operations directly mutate links and do not perform locking. Persistence is whatever lifetime the embedding structure provides.

## Dependencies and Integration
No external dependencies beyond compiler `typeof` support. Used throughout libglusterfs for inode/fd/dentry lists, event slots, iobuf arenas, graphs, volfiles, lock lists, and thread pools.

## Risks and Test Signals
Risks include using uninitialized nodes, deleting twice, iterating without safe macros while deleting, missing locks around shared lists, and type errors hidden by intrusive casting. Test signals include list primitive unit tests, ASAN/UBSAN for poisoned pointers, stress tests on inode/event/iobuf lists, and code review for safe iteration in deletion paths.
