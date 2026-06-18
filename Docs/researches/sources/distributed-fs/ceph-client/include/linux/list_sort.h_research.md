<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_sort.h -->
# sources/distributed-fs/ceph-client/include/linux/list_sort.h

## Purpose
This header declares the kernel linked-list sort helper. It lets callers sort an intrusive `struct list_head` list using a caller-provided comparison function.

## Important APIs, Types, and Functions
`list_cmp_func_t` is a nonnull comparator taking private context plus two list entries. `list_sort(void *priv, struct list_head *head, list_cmp_func_t cmp)` sorts the list in place.

## Control Flow
The implementation is external. The declared control contract is that `list_sort` walks and relinks list entries according to the comparator result while preserving the caller's embedded nodes.

## State and Persistence Behavior
The header owns no state. Sorting mutates only caller-owned list links at runtime and does not allocate or persist metadata through this declaration.

## Dependencies and Integration Points
It depends on `linux/types.h` and forward-declares `struct list_head`. Consumers include subsystems that need deterministic ordering without copying list contents into arrays.

## Risks and Test Signals
Risks are invalid comparators, sorting a concurrently modified list, and passing corrupt or uninitialized list heads. Test signals are sorted-order assertions, duplicate-key stability expectations documented by the implementation, debug-list checks, and lockdep coverage of caller serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_sort.h -->
