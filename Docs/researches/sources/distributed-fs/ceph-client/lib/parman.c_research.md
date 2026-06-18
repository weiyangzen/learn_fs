# sources/distributed-fs/ceph-client/lib/parman.c

## Purpose
Implements a priority-based array manager that keeps items grouped by priority in a linear backing array while delegating actual movement and resizing to caller callbacks.

## APIs, Control Flow, and State
Exports `parman_create()`, `parman_destroy()`, `parman_prio_init()`, `parman_prio_fini()`, `parman_item_add()`, and `parman_item_remove()`. `struct parman` tracks callbacks, private data, selected algorithm, item count, capacity limit, and an ordered priority list. The implemented `lsort` algorithm enlarges when full, finds the insertion index after the previous used priority group, shifts later priority groups down by moving their first item to the group tail, appends the new item, and increments count. Removal replaces non-tail removed items with their group tail, shifts later groups upward, decrements count, and shrinks when spare capacity reaches `resize_step`. All locking is caller-owned.

## Dependencies, Integration, Risks, and Tests
Depends on list handling, module exports, and `linux/parman.h`. Risks include callback move/resize failures leaving external arrays inconsistent, caller locking mistakes, priority initialization order misuse, shrink failure being ignored in remove, and unsupported algorithms if `ops->algo` indexes beyond the local array. Test signals include add/remove across multiple priorities, resize failure injection, array order validation after shifts, and destroy/fini warnings for non-empty state.
