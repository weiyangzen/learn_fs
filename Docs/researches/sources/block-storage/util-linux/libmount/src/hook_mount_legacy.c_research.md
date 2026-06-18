# File Research: sources/block-storage/util-linux/libmount/src/hook_mount_legacy.c

This hook implements the classic `mount(2)` path and compatibility extra syscalls for propagation and bind-remount semantics.

Key behavior:

- `hook_prepare()` skips work if the new `__mount` hook has already registered active hooks.
- For normal mount operations without helpers and not propagation-only, it registers `hook_mount()` at `MNT_STAGE_MOUNT`.
- `hook_mount()` builds source, target, type, flags, and filesystem-specific data/options from the context and optlist, calls `mount(2)`, records syscall status, and marks the filesystem attached or moved.
- `prepare_propagation()` removes propagation flags from the primary mount options and registers one post-mount `mount("none", target, NULL, flags, NULL)` call per propagation option.
- `prepare_bindremount()` registers a post-mount `mount(2)` call with `MS_REMOUNT|MS_BIND` to apply settable flags after the initial bind mount.

Dependencies and interactions:

- Serves as fallback when `hook_mount.c` is disabled, unsupported, or declined.
- Uses option maps and status tracking from the core context and optlist code.

Risk notes:

- Propagation failures map to `MNT_ERR_APPLYFLAGS`; bind-remount failures return the raw `mount(2)` result rather than normalizing through syscall status in the same way as primary mount.
- The debug message says "bint-remount", a harmless typo.
