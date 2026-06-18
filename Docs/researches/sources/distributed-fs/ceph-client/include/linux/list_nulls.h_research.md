<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_nulls.h -->
# sources/distributed-fs/ceph-client/include/linux/list_nulls.h

## Purpose
This header defines nulls-terminated hlists, a hash-list variant whose end marker encodes a bucket value. It supports lockless lookup patterns that can detect when traversal ended in the wrong bucket after concurrent movement.

## Important APIs, Types, and Functions
`struct hlist_nulls_head` stores `first`; `struct hlist_nulls_node` stores `next` and `pprev`. `NULLS_MARKER(value)` encodes an odd-valued terminal pointer. APIs include `INIT_HLIST_NULLS_HEAD`, `HLIST_NULLS_HEAD_INIT`, `is_a_nulls`, `get_nulls_value`, `hlist_nulls_unhashed`, `hlist_nulls_unhashed_lockless`, `hlist_nulls_empty`, `hlist_nulls_add_head`, `hlist_nulls_del`, and traversal macros.

## Control Flow
Insertion replaces the head first pointer and links the node ahead of the old first pointer, which may be a nulls marker. Traversal stops when `is_a_nulls()` detects the marker and can verify the marker value. Deletion updates predecessor storage and poisons the node.

## State and Persistence Behavior
State lives in caller-owned nodes and marker values. The marker is not a real object pointer and must be recognized before container conversion. There is no persistent state.

## Dependencies and Integration Points
It depends on `poison.h`, `const.h`, and external synchronization/RCU patterns in callers. Networking and hash-table users rely on the nulls value to detect concurrent hash bucket changes.

## Risks and Test Signals
Risks include treating a marker as a node, using the wrong nulls value, and assuming traversal is safe without the caller's required RCU/locking rules. Test signals are lookup retry coverage, debug poisoning failures, KCSAN/KASAN reports, and hash-table stress under concurrent insert/delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_nulls.h -->
