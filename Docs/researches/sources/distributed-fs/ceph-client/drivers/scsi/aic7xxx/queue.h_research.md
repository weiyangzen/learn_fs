# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/queue.h

Purpose: local copy of BSD `queue.h` macros used by the aic assembler host tools and imported driver code for intrusive linked-list data structures.

Important APIs/types/functions: defines `SLIST_*`, `STAILQ_*`, `BSD_LIST_*`/`LIST_*`, `TAILQ_*`, and `CIRCLEQ_*` head/entry/access/manipulation macros. Operations include initialization, empty checks, traversal, head/tail/after/before insertion, removal, and forward/reverse iteration where supported.

Control flow: all behavior is macro-expanded at call sites. Singly linked lists and tail queues require traversal for arbitrary removal; doubly linked list/tail/circle queues remove in O(1) using embedded back pointers.

State and persistence: state is embedded in user structs through entry macros and in caller-owned head structs. The macros do not allocate, free, lock, or persist anything.

Dependencies and integration: standalone C preprocessor header. The aicasm scanner/symbol code relies on `SLIST`, `STAILQ`, and `TAILQ` declarations for include stacks, symbol lists, macro args, critical sections, and scopes.

Risks and test signals: macros perform no validation, can evaluate arguments multiple times in some patterns, and corrupt lists if entries are double-inserted or removed from the wrong list. `BSD_LIST_HEAD` is renamed to avoid Linux `LIST_HEAD` conflicts while still defining `LIST_*` operation names. Test signals are host-tool compilation, parser fixtures exercising list insert/remove/merge paths, and sanitizer/debug builds that catch corrupted intrusive links.
