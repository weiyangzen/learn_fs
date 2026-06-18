<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/list_sort.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/list_sort.h

## Purpose
This header declares the generic list sorting routine for intrusive kernel-style lists.

## APIs And Flow
It includes `linux/list.h` and declares `list_sort(void *priv, struct list_head *head, int (*cmp)(void *priv, const struct list_head *a, const struct list_head *b))`. The actual control flow lives in the linked implementation; callers provide private comparison context and a comparator over list nodes.

## State, Dependencies, Risks, Tests
State is the caller's list, reordered in place by the implementation. Dependencies are `list.h` and whatever object file supplies `list_sort`. Risks are comparator instability, corrupt lists, and missing linkage if the implementation is not included in a tool build. Tests should sort empty, one-element, already sorted, reverse, duplicate-key, and large lists while validating list integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/list_sort.h -->
