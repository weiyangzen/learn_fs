# File Research: sources/cow-pools/bcachefs/fs/bcachefs/debug/async_objs.h

Header for optional async object list debugging.

Key contents:
- Under `CONFIG_BCACHEFS_ASYNC_OBJECT_LISTS`, defines helpers/macros to add and remove objects from per-filesystem `fast_list` instances.
- Declares debugfs init, exit, and init functions.
- Without the config option, all public helpers compile to no-ops and init returns success.

Important invariants:
- `async_object_list_add()` stores the returned fast-list index in the caller-provided `idx`.
- `async_object_list_del()` clears the stored index after removal.
- The no-config stubs preserve call-site simplicity with zero runtime behavior.
