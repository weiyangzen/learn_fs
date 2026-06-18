# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/async_objs.c

Optional debugfs support for live asynchronous bcachefs objects when `CONFIG_BCACHEFS_ASYNC_OBJECT_LISTS` is enabled.

Key entry points:
- Object renderers adapt promote ops, read bios, write ops, btree read bios, and btree write bios to a common `obj_to_text` callback.
- `bch2_async_obj_list_open()` initializes a `dump_iter` for a selected async object list.
- `bch2_async_obj_list_read()` iterates the `fast_list` from the saved cursor, renders each object, and flushes the print buffer to userspace.
- `bch2_fs_async_obj_debugfs_init()` creates the `async_objs` debugfs directory and one read-only file per async object list.
- `bch2_fs_async_obj_init()` initializes all fast lists and callback pointers.
- `bch2_fs_async_obj_exit()` destroys the fast lists.

Important invariants:
- The file is compiled only under `CONFIG_BCACHEFS_ASYNC_OBJECT_LISTS`.
- `dump_iter.iter` is used as the persistent fast-list cursor across reads.
- All list files share `bch2_dump_release()` and `bch2_debugfs_flush_buf()` from the general debugfs implementation.
