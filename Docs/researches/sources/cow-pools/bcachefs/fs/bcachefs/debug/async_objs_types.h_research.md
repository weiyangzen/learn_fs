# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/async_objs_types.h

Type definitions for async object debug lists.

Key contents:
- Defines `BCH_ASYNC_OBJ_LISTS()` for promote, rbio, write_op, btree_read_bio, and btree_write_bio.
- Defines `enum bch_async_obj_lists` ending with `BCH_ASYNC_OBJ_NR`.
- Defines `struct async_obj_list`, containing a `fast_list`, object-to-text callback, and list index.

Important invariants:
- The enum order must match callback assignment and debugfs file creation in `async_objs.c`.
- `idx` lets a list recover its containing `bch_fs` from `c->async_objs[idx]`.
