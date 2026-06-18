# File Research: sources/block-storage/util-linux/libmount/src/hook_selinux.c

This conditional hook normalizes SELinux mount options when libselinux is available.

Key behavior:

- `hook_prepare_options()` scans `context`, `fscontext`, `defcontext`, `rootcontext`, and `seclabel`.
- If SELinux is disabled, those options are removed.
- For remounts on kernels older than 2.6.39, SELinux options are removed because those kernels did not support remount with SELinux mount options.
- For normal mounts, context values are translated to raw SELinux context strings with `selinux_trans_to_raw_context()`.
- `rootcontext=@target` is deferred: a hook is inserted after `__mkdir` at `MNT_STAGE_PREP_TARGET`, and `hook_selinux_target()` reads the target's raw file context with `getfilecon_raw()` once the target may exist.
- Seeing SELinux options sets `cxt->has_selinux_opt`, which `hook_mount.c` uses to avoid the new fsconfig path for btrfs.

Dependencies and interactions:

- Active only with `HAVE_LIBSELINUX`.
- Coordinates with the mkdir hook by dependency insertion.
- Uses Linux version checks and optlist mutation APIs.

Risk notes:

- Invalid or untranslatable SELinux context values become `MNT_ERR_MOUNTOPT`.
- When SELinux is disabled, user-provided SELinux options are silently removed rather than passed to the kernel.
