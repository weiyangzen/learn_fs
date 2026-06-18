# sources/distributed-fs/ceph-client/tools/perf/util/comm.c

Purpose: represents thread command names with string interning, reference counting, and safe sharing across perf thread histories.

Important APIs/functions: exports `comm__new`, `comm__override`, `comm__free`, and `comm__str`; internal code manages `struct comm_str` lookup, insertion, refcounting, and removal.

Control flow: a process-wide intern table initializes once with an rwsem and sorted pointer array. Lookups use read lock plus `bsearch`; misses take a write lock, grow capacity, allocate a refcounted string, and insert in sorted order. Comm objects hold timestamp and exec state.

State and persistence: static `_comm_strs` stores interned strings for the process. Each `comm` owns a reference; the table holds references until entries are otherwise unused.

Dependencies and integration: uses perf rwsem wrappers, Linux refcounting, rc-check helpers, `reallocarray`, and thread/comm consumers.

Risks: removal is subtle because `comm_str__put` may trigger table deletion while refs change. Sorted-array invariants must stay aligned with `bsearch`. `comm__free` assumes non-NULL.

Test signals: duplicate strings, override paths, concurrent find/new/free, capacity growth, refcount leaks, and exec flag preservation.
