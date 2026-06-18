# sources/distributed-fs/ceph-client/lib/plist.c

## Purpose
Implements non-inline operations for priority-sorted doubly linked lists, where `node_list` preserves all nodes in priority order and `prio_list` links one representative per priority.

## APIs, Control Flow, and State
Exports `plist_add()`, `plist_del()`, and `plist_requeue()` through normal linkage from the list library. Add validates node emptiness, searches from both ends of the priority representatives, inserts into the representative list if this priority is new, then inserts into the full node list before the first lower-priority node. Delete repairs the priority representative list by promoting the next same-priority node when needed, then removes the node from both lists. Requeue moves a node to the end of its same-priority group with optimized lookup. Under `CONFIG_DEBUG_PLIST`, consistency check helpers validate prev/next links and an init-time randomized/worst-case test exercises add/delete/requeue.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/plist.h`, list primitives, BUG/WARN infrastructure, and optional scheduler clock/module init for debug tests. Risks include corrupting both list dimensions if callers reuse non-empty nodes, priority representative repair bugs, missing caller locking, and debug-only test code not running in production builds. Test signals include `CONFIG_DEBUG_PLIST`, randomized add/delete/requeue validation, lockdep coverage in users, and list corruption warnings.
