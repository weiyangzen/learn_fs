# File Research: sources/cow-pools/openzfs/module/zfs/zfs_onexit.c

## Role

`zfs_onexit.c` manages per-`/dev/zfs` file descriptor cleanup callbacks. It lets kernel ZFS operations accumulate state across multiple ioctls and guarantees cleanup when the associated process closes the cleanup fd or exits.

## Main Components

- `zfs_onexit_init()`: allocates a `zfs_onexit_t`, initializes its mutex, and creates the action list.
- `zfs_onexit_destroy()`: drains the action list, invoking every registered callback with its stored data, then destroys list/mutex state and frees the container.
- `zfs_onexit_fd_hold()`: validates a user-provided fd, gets the corresponding `/dev/zfs` minor through `zfsdev_getminor()`, verifies it has on-exit state, and returns a held `zfs_file_t`.
- `zfs_onexit_fd_rele()`: releases the held file reference.
- `zfs_onexit_minor_to_state()`: maps a minor to `ZST_ONEXIT` state.
- `zfs_onexit_add_cb()`: registers a callback/data pair and optionally returns the action handle, implemented as the address of the action node.

## Important Behavior

- The cleanup model is tied to `/dev/zfs` open-file private state and minor numbers owned in `zfs_ioctl.c`.
- Consumers are expected to call `zfs_onexit_fd_hold()` before doing work that will later add a callback, preventing the fd from disappearing between validation and registration.
- Destroy invokes callbacks outside the lock, then reacquires the lock before removing the next action. This avoids running arbitrary cleanup while holding the list mutex.
- Callback nodes are appended to the tail and executed in head-removal order during destroy.

## Dependencies

- `zfs_file_get()` / `zfs_file_put()` for fd lifetime.
- `zfsdev_getminor()` and `zfsdev_get_state()` from the ioctl/device layer.
- Kernel list/mutex/kmem primitives.
- Consumers include temporary snapshots and user holds in `zfs_ioctl.c`; comments also describe receive-side accumulated state.

## Invariants And Safety Notes

- `zfs_onexit_fd_hold()` returns `NULL` for invalid fd, invalid minor, or missing on-exit state.
- `zfs_onexit_add_cb()` requires a valid minor that maps to live on-exit state.
- The returned `action_handle` is a kernel pointer cast to `uintptr_t`; it is only meaningful to cooperating kernel paths that validate it against the minor-owned state.
- Callbacks must tolerate being invoked during fd close/process cleanup rather than during the original ioctl.

## When Modifying

- Preserve the hold/release protocol around fd-derived minor numbers.
- Do not run callbacks while holding `zo_lock`.
- Any new consumer should define clear ownership of callback data and ensure its callback fully frees or invalidates that state.
