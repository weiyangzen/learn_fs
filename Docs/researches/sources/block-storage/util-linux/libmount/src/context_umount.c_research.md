# File Research: sources/block-storage/util-linux/libmount/src/context_umount.c

This file implements libmount's high-level umount workflow: finding the mounted filesystem, preparing permissions and helpers, invoking `umount(2)`/`umount2(2)` or `/sbin/umount.<type>`, cleaning loop devices, updating mount tables, iterating over mountinfo for `umount -a` style operations, and converting return state into mount(8)/umount(8) exit codes.

Key entry points:

- `mnt_context_find_umount_fs()` resolves a target/source/path-image argument to a `libmnt_fs` entry, using `/proc/self/mountinfo`.
- `mnt_context_prepare_umount()` performs lookup, merges mount flags, checks restricted-user permissions, prepares helpers, and decides whether loop detachment is needed.
- `mnt_context_do_umount()` switches to the target namespace, calls `do_umount()`, and deletes loop devices after successful unmounts.
- `mnt_context_finalize_umount()` prepares and writes userspace table updates.
- `mnt_context_umount()` is the full prepare/update/do/update orchestration.
- `mnt_context_next_umount()` iterates mountinfo with fstype/options filters.
- `mnt_context_get_umount_excode()` maps helper, syscall, lock, namespace, and generic failures to public exit codes and messages.

Important behavior:

- `__mountinfo_find_umount_fs()` searches by target first, then optionally by source when swap matching is enabled and the context is unrestricted. If the user passed a regular backing file, it can resolve a single associated loop device and retry lookup by `/dev/loopN`.
- `lookup_umount_fs_by_statfs()` avoids reading huge mountinfo tables when possible. It uses `open(O_PATH)` plus `fstatfs()` for simple directory targets, but refuses the shortcut for restricted users, helpers, force/lazy/no-canonicalize/detach-loop/read-only-umount paths, non-directories, and targets with utab entries.
- `lookup_umount_fs_by_mountinfo()` copies the matched mountinfo entry into `cxt->fs` and marks `MNT_FL_TAB_APPLIED`.
- Restricted unmounts are guarded by `evaluate_permissions()`: non-root users need a mountinfo match, may use `uhelper=`, may unmount their own FUSE mounts by `user_id=`, or must match an fstab pair with `user`, `users`, `owner`, or `group` semantics and a matching `user=` utab record.
- `exec_helper()` forks, drops permissions in the child, switches to the origin namespace, and passes options such as `-n`, `-l`, `-f`, `-v`, `-r`, `-t`, and `-N` to helpers.
- `do_umount()` adds `UMOUNT_NOFOLLOW` for restricted users when supported, uses `mnt_chdir_to_parent()` to reduce symlink races, maps lazy/force to `MNT_DETACH`/`MNT_FORCE`, retries symlink targets with `UMOUNT_NOFOLLOW` for unrestricted callers on `EINVAL`, and can remount read-only on `EBUSY` when requested.

Dependencies and interactions:

- Relies on table lookup and matching APIs from `fs.c`/table code, option list APIs, namespace switching, update-table logic, loop device helpers, and path canonicalization cache.
- Umount loop cleanup still calls `mnt_context_delete_loopdev()` from `hook_loopdev.c`; the comment there notes umount has not yet been converted fully to hooks.
- Uses status fields (`syscall_status`, `helper_exec_status`, `helper_status`) as part of the public error contract.

Risk notes:

- Namespace switch failures can occur in several mid-function paths; most paths restore the previous namespace, but some early returns inside `mnt_context_prepare_umount()` after `prepare_helper_from_option()` errors happen while already switched to the target namespace.
- The statfs optimization intentionally bypasses mountinfo and disables mtab updates; callers depending on full source data must use options that force mountinfo.
- Permission decisions depend on merged option state and utab/fstab agreement, so stale userspace mount tables can affect restricted-user behavior.
