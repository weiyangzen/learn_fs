# File Research: sources/cow-pools/bcachefs-tools/include/linux/rhashtable-types.h

This header defines the type layer for resizable hash tables. It includes `struct rhash_head`, `struct rhlist_head`, `struct rhashtable_compare_arg`, hash/compare callback typedefs, `struct rhashtable_params`, `struct rhashtable`, `struct rhltable`, walker state, and iterator state.

It declares `rhashtable_init()` and `rhltable_init()`. Actual insertion, lookup, walking, resize, and destruction behavior is defined outside this header.
