# sources/distributed-fs/ceph-client/lib/list_sort.c

Purpose: stable in-place merge sort for Linux circular doubly linked lists.

Important APIs/types/functions: public `list_sort()`, internal `merge()`, and `merge_final()`.

Control flow: `list_sort()` returns for zero/one element lists, breaks the circular list into a null-terminated singly linked list, then processes elements into a pending stack of sorted power-of-two sublists. It merges eagerly based on bit transitions in `count`, keeping merges at least 2:1 balanced. Final merging rebuilds `prev` links and restores the circular list head.

State/persistence: temporarily repurposes `prev` links in pending sublists as list-of-lists pointers and null-terminates `next` chains. On success the original list head owns a sorted circular doubly linked list.

Dependencies/integration: exported for kernel users needing stable list sorting. Comparator receives caller `priv` and list nodes and must provide antisymmetric/transitive ordering; boolean comparison style is supported.

Risks: invalid comparator ordering can produce incorrect sort results. The algorithm mutates links throughout; callers must not inspect or concurrently modify the list. Stability depends on taking `a` first when compare returns `<= 0`.

Test signals: not tested in this subset; expected signals are sorted order, stable equal-key order, and intact `next`/`prev` circular links.
