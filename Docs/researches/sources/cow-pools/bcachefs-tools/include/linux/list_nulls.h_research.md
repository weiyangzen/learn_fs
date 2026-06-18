# File Research: sources/cow-pools/bcachefs-tools/include/linux/list_nulls.h

This header implements nulls-terminated hlist variants. A nulls marker is encoded by setting the low pointer bit and storing a marker value in the upper bits, allowing special end-of-chain values.

It defines `struct hlist_nulls_head`, `struct hlist_nulls_node`, marker/init macros, `is_a_nulls()`, `get_nulls_value()`, unhashed/empty checks, add-head, delete, and iteration macros. Deletion poisons `pprev` with `LIST_POISON2`.

The API is useful for lockless hash/list patterns that need to detect list restarts or table movement.
