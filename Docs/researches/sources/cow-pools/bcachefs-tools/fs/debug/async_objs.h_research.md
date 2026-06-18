# File Research: sources/cow-pools/bcachefs-tools/fs/debug/async_objs.h

## Role

Header for optional async-object debug tracking.

## Enabled Configuration

When `CONFIG_BCACHEFS_ASYNC_OBJECT_LISTS` is enabled:

- `__async_object_list_add()` inserts an object into a `fast_list`, stores a positive index, and returns zero or an error.
- `__async_object_list_del()` removes the stored index and resets it to zero.
- `async_object_list_add()` and `async_object_list_del()` select the appropriate `c->async_objs[]` list using `BCH_ASYNC_OBJ_LIST_*`.
- Filesystem debugfs/init/exit functions are declared.

## Disabled Configuration

When disabled, add/delete macros compile to no-ops, `__async_object_list_add()` returns success, and the init/debugfs/exit helpers are inline stubs.
