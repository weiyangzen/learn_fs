# File Research: sources/cow-pools/bcachefs-tools/fs/debug/async_objs.c

## Role

Implements optional debugfs exposure of live asynchronous bcachefs objects when `CONFIG_BCACHEFS_ASYNC_OBJECT_LISTS` is enabled.

## Object Printers

The file maps async object list types to text printers:

- Promote operations via `bch2_promote_op_to_text()`.
- Read bios via `bch2_read_bio_to_text()`.
- Write ops via `bch2_write_op_to_text()`.
- Btree read bios via `bch2_btree_read_bio_to_text()`.
- Btree write bios via `bch2_bio_to_text()`.

## Debugfs Read Path

`bch2_async_obj_list_open()` allocates a `dump_iter`, finds the owning `bch_fs` from the `async_obj_list`, initializes iteration state, and creates a print buffer.

`bch2_async_obj_list_read()` repeatedly flushes buffered text to userspace, RCU-walks the `fast_list`, prints each object, advances the genradix iterator, and returns copied bytes or `-ENOMEM`/copy errors.

## Lifecycle

`bch2_fs_async_obj_debugfs_init()` creates an `async_objs` directory under the filesystem debug directory and one read-only debugfs file per async object list.

`bch2_fs_async_obj_init()` initializes each fast list, stores its list index, and assigns printer callbacks. `bch2_fs_async_obj_exit()` releases every fast list.
