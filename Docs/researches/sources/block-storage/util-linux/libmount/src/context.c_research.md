# File Research: sources/block-storage/util-linux/libmount/src/context.c

Core high-level libmount context implementation shared by mount and umount flows.

Key responsibilities:
- Allocates, resets, clones, and frees `libmnt_context`.
- Manages context flags, options mode, filesystem object, option list, fstab, mountinfo, utab, cache, lock, target prefix, target namespace, and helper mode.
- Applies fstab or mountinfo entries to the current context.
- Resolves source paths/tags and guesses filesystem types.
- Prepares userspace table updates and emits update events.
- Tracks syscall/helper status and buffered kernel/libmount messages.
- Converts operation outcomes to mount-compatible exit codes.
- Supports forked mount-all children and mount namespace switching.
- Includes a `TEST_PROGRAM` command harness.

Important behavior:
- New contexts are restricted unless real root and not privileged/setuid execution.
- `mnt_reset_context()` resets per-operation state but preserves selected policy flags, cached fstab/cache, target namespace, target prefix, and patterns.
- `mnt_context_get_fs()` lazily creates an FS and links it to the context option list.
- `mnt_context_get_fstab()` and `mnt_context_get_mountinfo()` parse under the target namespace and attach context cache/callbacks.
- Restricted contexts force fstab use through `MNT_OMODE_USER`.
- Source preparation resolves tags, canonicalizes paths unless disabled, skips netfs/pseudofs/ZFS special cases, and invokes source hooks.
- Namespace switching also swaps namespace-associated caches.

Dependencies:
- Depends on `mountP.h`, option-list APIs, table/parser APIs, cache APIs, update/lock APIs, namespace support, hook framework, blkid-derived type probing, and Linux mount constants.

Notable risks:
- Namespace switching is global to the process and must always switch back correctly.
- Error paths around namespace switching can return before cleanup in some helper functions.
- Many APIs return borrowed internal pointers; callers must respect context lifetime.
- `mnt_context_read_mesgs()` loops on `read()` until `-1`; behavior depends on fd readiness/EOF.
