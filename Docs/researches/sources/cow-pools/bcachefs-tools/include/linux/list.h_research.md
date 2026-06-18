# File Research: sources/cow-pools/bcachefs-tools/include/linux/list.h

This header maps Linux list APIs onto Userspace RCU `cds_list_*` and `cds_hlist_*` primitives. It defines aliases for list heads, initialization, add/delete/replace/move/splice, entry, and iteration helpers.

It adds kernel-compatible helpers not directly provided by URCU, including `list_empty_careful()`, `list_move_tail()`, splice-tail variants, first/last entry helpers, reverse safe iteration, hlist safe entry helpers, `list_count_nodes()`, and `list_is_last()`.

This is a key compatibility header for intrusive lists throughout bcachefs-tools.
