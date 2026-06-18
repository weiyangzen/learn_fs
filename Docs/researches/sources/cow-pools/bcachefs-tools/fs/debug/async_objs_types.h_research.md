# File Research: sources/cow-pools/bcachefs-tools/fs/debug/async_objs_types.h

## Role

Defines the async-object list identifiers and list metadata structure used by the optional debug object registry.

## List Types

`BCH_ASYNC_OBJ_LISTS()` enumerates:

- `promote`
- `rbio`
- `write_op`
- `btree_read_bio`
- `btree_write_bio`

The enum adds `BCH_ASYNC_OBJ_NR` as the array size.

## `struct async_obj_list`

Stores the backing `fast_list`, a polymorphic `obj_to_text()` printer callback, and the list index used to recover the containing `bch_fs` in debugfs open.
