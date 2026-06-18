# Group Research: util-linux libmount context, fs model, hooks, and support primitives

Scope checked against `Docs/research_subset_a.md`: `sources/block-storage/util-linux` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/context_umount.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/context_umount.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/fs.c -->
# File Research: sources/block-storage/util-linux/libmount/src/fs.c

This file implements `struct libmnt_fs`, the core representation for one fstab, mtab, mountinfo, swap, or statmount-derived filesystem entry. It owns string fields, mount IDs, propagation, source tags, options split by class, swap metadata, and conversion/matching helpers.

Key entry points:

- Lifecycle: `mnt_new_fs()`, `mnt_free_fs()`, `mnt_reset_fs()`, `mnt_ref_fs()`, `mnt_unref_fs()`.
- Copying: `mnt_copy_fs()` copies unset fields into a destination; `mnt_copy_mtab_fs()` creates an mtab-safe copy with options filtered by `MNT_NOMTAB`.
- Source/target/type: `mnt_fs_get_source()`, `mnt_fs_set_source()`, `mnt_fs_get_srcpath()`, `mnt_fs_get_tag()`, `mnt_fs_get_target()`, `mnt_fs_set_target()`, `mnt_fs_get_fstype()`, `mnt_fs_set_fstype()`.
- Options: `mnt_fs_set_options()`, append/prepend variants, `mnt_fs_get_options()`, `mnt_fs_strdup_options()`, `mnt_fs_get_fs_options()`, `mnt_fs_get_vfs_options()`, `mnt_fs_get_user_options()`, and attribute/comment helpers.
- Identity and metadata: mount ID, unique ID, parent IDs, namespace ID, device number, TID, root, bind source, propagation, swap size/priority.
- Matching: `mnt_fs_match_target()`, `mnt_fs_match_source()`, `mnt_fs_match_fstype()`, `mnt_fs_match_options()`.
- Diagnostics and interop: `mnt_fs_print_debug()`, `mnt_fs_to_mntent()`, `mnt_free_mntent()`.

Important behavior:

- Source parsing uses `blkid_parse_tag_string()` to recognize valid `LABEL=`, `UUID=`, and similar tags. When a source is a tag, `mnt_fs_get_srcpath()` deliberately returns `NULL`.
- Filesystem type setting updates cached flags for pseudo filesystems, network filesystems, and swap entries.
- Option strings can be backed by a `libmnt_optlist`. When `mnt_fs_follow_optlist()` is used, getters synchronize cached strings from the optlist age; reads are therefore not purely const-like operations.
- Option merging preserves read-only semantics: `merge_optstr()` removes duplicate `ro`/`rw` entries and gives `ro` precedence unless both sides explicitly specify `rw`.
- `mnt_fs_get_vfs_options_all()` emits all VFS options, including default inverted options from the option map.
- With `HAVE_STATMOUNT_API`, many getters lazily call `mnt_fs_try_statmount()` to fetch missing kernel data on demand.
- Target matching compares raw paths, then target canonicalization, and finally canonicalizes both sides for non-kernel/non-swap entries.
- Source matching first compares native source paths/tags, then cache-resolved paths, then compares tags read through libblkid/cache. It skips canonical source matching for network and pseudo filesystems.

Dependencies and interactions:

- Depends on optstring parsing, optlist age/versioning, libblkid tag parsing, mount type classifiers, cache/path resolution, and statmount support.
- `context_umount.c`, table lookup code, hooks, and update writers rely on this file's source/target/type and option semantics.
- `fs_statmount.c` fills fields that this file lazily exposes.

Risk notes:

- `mnt_copy_fs()` intentionally does not overwrite already-set destination strings. Callers that expect a complete replacement must clear fields first, as `context_umount.c` does for source and target.
- Returning cached internal string pointers makes lifetime depend on the `libmnt_fs`; callers must not free them.
- Statmount-on-demand can make getters perform syscalls unless fetching is disabled.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/fs_statmount.c -->
# File Research: sources/block-storage/util-linux/libmount/src/fs_statmount.c

This file adapts Linux `listmount/statmount` support into `libmnt_fs`. It provides a shared `libmnt_statmnt` object for buffer reuse, default masks, and on-demand fetching control, then applies kernel `ul_statmount` data into existing filesystem entries.

Key entry points:

- `mnt_new_statmnt()`, `mnt_ref_statmnt()`, `mnt_unref_statmnt()`.
- `mnt_statmnt_set_mask()` configures the default statmount mask.
- `mnt_statmnt_disable_fetching()` temporarily disables lazy statmount fetches to avoid recursion.
- `mnt_fs_refer_statmnt()` attaches shared statmount settings to a filesystem entry.
- `mnt_fs_get_statmnt()` returns the attached statmount settings.
- `mnt_fs_fetch_statmount()` fetches and applies kernel mount-node data.

Important behavior:

- When `HAVE_STATMOUNT_API` is absent, construction fails with `ENOSYS` and fetch returns `-ENOTSUP`.
- `apply_statmount()` fills only missing fields: fstype, target, root, source, propagation, classic/unique IDs, parent IDs, namespace ID, devno, VFS options, and FS options.
- VFS options are synthesized from `MOUNT_ATTR_*` flags (`ro/rw`, `nosuid`, `nodev`, `noexec`, `nodiratime`, `nosymfollow`, and atime mode).
- Superblock options are synthesized from `SB_*` flags (`ro/rw`, `sync`, `dirsync`, `lazytime`), while `STATMOUNT_MNT_OPTS` options are unmangled into `fs_optstr`.
- `mnt_fs_fetch_statmount()` ORs explicit masks with shared default masks, skips already-fetched bits via `fs->stmnt_done`, derives `uniq_id` from the target path if needed, and can reuse the shared `libmnt_statmnt` buffer.

Dependencies and interactions:

- Used by `fs.c` getters under `HAVE_STATMOUNT_API`.
- Depends on low-level `ul_statmount()`, `mnt_id_from_path()`, option-string append helpers, unmangling, and kernel statmount/mount-attr constants.

Risk notes:

- The code computes a namespace ID variable but calls `ul_statmount()` with namespace argument `0`; this appears intentional or incomplete depending on the `ul_statmount` wrapper contract.
- `fs->stmnt_done` is ORed with the requested mask even after errors, which can suppress repeated attempts for the same mask.
- Lazy getter behavior means an apparently simple field access can fail to populate data if the mountpoint path is unavailable.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/fs_statmount.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/fuzz.c -->
# File Research: sources/block-storage/util-linux/libmount/src/fuzz.c

This is a libFuzzer entry point for mount table parsing, focused on mountinfo-like input.

Key behavior:

- `LLVMFuzzerTestOneInput()` rejects empty inputs and inputs larger than 128 KiB.
- It allocates a `libmnt_table`, opens the fuzzer bytes through `fmemopen()` in read mode, enables comments, and calls `mnt_table_parse_stream(tb, f, "mountinfo")`.
- It ignores parser return values, then releases the table and stream.

Dependencies and interactions:

- Exercises table allocation, comment parsing, and stream parsing paths.
- Uses `err_oom()` and `err()` for unrecoverable local harness setup failures.

Risk notes:

- The harness is intentionally narrow: it does not fuzz mount/umount execution or hook behavior, only parser handling of bounded input.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/fuzz.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hook_idmap.c -->
# File Research: sources/block-storage/util-linux/libmount/src/hook_idmap.c

This conditional Linux hook implements `X-mount.idmap=` for idmapped mounts using the mount fd API and `mount_setattr(MOUNT_ATTR_IDMAP)`.

Key components:

- `struct id_map` stores uid/gid/both mappings as namespace ID, host ID, and range triples.
- `struct hook_data` owns the user namespace FD and the parsed mapping list.
- `hook_prepare_options()` parses `X-mount.idmap=` and registers a post-mount hook.
- `hook_mount_post()` clones or reuses a detached mount tree, applies the ID mapping, and attaches it to the target.
- `hookset_deinit()` removes hooks and closes/free parsed state.

Important behavior:

- Values beginning with `/` are treated as paths to an existing user namespace and opened with validation through `NS_GET_OWNER_UID` when available.
- Otherwise the option is parsed as entries of `[b|u|g:]id-mount:id-host:id-range`, separated by spaces. `b:` or no prefix applies to both uid and gid maps.
- For explicit mappings, `get_userns_fd_from_idmap()` forks a child, unshares a user namespace, waits for the parent to write `/proc/<pid>/{u,g}id_map`, then opens `/proc/<pid>/ns/user`.
- Non-root gid mapping writes first write `deny\n` to `/proc/<pid>/setgroups` when available.
- Post-mount handling uses `open_tree(... OPEN_TREE_CLONE ...)`, `mount_setattr(... MOUNT_ATTR_IDMAP ...)`, detaches the old target if using a private clone, then `move_mount()`s the idmapped tree to the final target.
- `cxt->force_clone = 1` forces clone-based mount behavior so the mount can be idmapped before final attachment.

Dependencies and interactions:

- Active only with `HAVE_MOUNTFD_API` and `HAVE_LINUX_MOUNT_H`.
- Coordinates with `hook_mount.c` through `mnt_context_get_sysapi()` and `force_clone`.
- Uses namespace, socketpair, fork/wait, and `/proc` uid/gid map mechanics.

Risk notes:

- The map buffer is fixed at 4096 bytes because kernel uid/gid map writes are limited; overflow is detected through `snprintf()` return handling but very large mapping sets will fail.
- Failure after cloning but before move can leave the original target detached only after `umount2()` is reached; current code detaches after successful `mount_setattr()`.
- This feature depends heavily on kernel/user namespace permissions and will fail in restricted environments.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hook_idmap.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hook_loopdev.c -->
# File Research: sources/block-storage/util-linux/libmount/src/hook_loopdev.c

This hook implements automatic and explicit loop device setup for regular-file mounts and cleanup after mount failure or success. It also exposes the current non-hook umount loop deletion helper.

Key entry points:

- `hook_prepare_loopdev()` runs at `MNT_STAGE_PREP_SOURCE` and decides whether a loop device is needed.
- `setup_loopdev()` parses loop options, reuses or creates a loop device, updates `cxt->fs` source to `/dev/loopN`, and keeps a read-only FD open across mount.
- `hook_cleanup_loopdev()` runs after mount and either detaches the loop device on failure or closes the held FD on success.
- `mnt_context_delete_loopdev()` is called from umount code.

Important behavior:

- Loop setup is skipped for bind, move, propagation-only, non-mount actions, missing sources, and `X-mount.noloop`.
- Explicit userspace flags `loop`, `offset`, or `sizelimit` force loop handling.
- Automatic loop handling is enabled for regular files larger than 1 KiB when the filesystem type is known or can be guessed, except for EROFS and unknown non-blkid filesystems.
- Existing overlapping loop devices are detected. Full matching devices can be reused; partial overlap fails with `MNT_ERR_LOOPOVERLAP`.
- Existing reused loop devices are checked for autoclear races, read-only conflicts, unsupported legacy encryption, and conflict with explicit `loop=<device>`.
- New loop devices get `LO_FLAGS_AUTOCLEAR` on Linux >= 2.6.37, and `LO_FLAGS_READ_ONLY` if the mount is read-only.
- The hook removes unnecessary `loop=` from utab when autoclear or reuse makes persistence unnecessary and appends `MS_RDONLY` if the loop device is read-only.

Dependencies and interactions:

- Uses `loopdev.c`/`loopdev.h`, libblkid filesystem recognition, option lists, mountinfo lookups, path cache resolution, and Linux version checks.
- Updates `cxt->fs->source`, so later mount hooks mount the loop block device rather than the original regular file.

Risk notes:

- The race between finding a loop device and setup is handled by retrying stolen devices and revalidating reused loop state.
- On setup error after partial creation, cleanup calls `delete_loopdev()`, which uses the current filesystem source.
- Automatic loop avoidance for EROFS relies on kernel support for file-backed EROFS; older kernels may still need loop devices.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hook_loopdev.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hook_mkdir.c -->
# File Research: sources/block-storage/util-linux/libmount/src/hook_mkdir.c

This hook implements `X-mount.mkdir` and `x-mount.mkdir`, creating missing target directories before mounting.

Key behavior:

- `is_mkdir_required()` searches userspace options for `X-mount.mkdir` or lowercase `x-mount.mkdir`.
- If the target already exists, no action is taken.
- The option value, when provided, is parsed as an octal mode, allowing optional leading/trailing quotes.
- Default mode is `0755`.
- `hook_prepare_target()` creates the target with `ul_mkdir_p()` only for unrestricted contexts. Restricted contexts get `-EPERM`.
- After successful creation, if a path cache exists and canonicalizes the target differently, the filesystem target is updated.

Dependencies and interactions:

- Runs at `MNT_STAGE_PREP_TARGET`.
- SELinux handling can insert a dependent target hook after this hook for `rootcontext=@target`.

Risk notes:

- Mode parsing accepts octal text only; malformed values produce `MNT_ERR_MOUNTOPT`.
- Directory creation is deliberately unavailable for suid/restricted mount operations.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hook_mkdir.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hook_mount.c -->
# File Research: sources/block-storage/util-linux/libmount/src/hook_mount.c

This conditional hook implements mounting through the newer Linux mount fd API: `fsopen()`, `fsconfig()`, `fsmount()`, `open_tree()`, `mount_setattr()`, and `move_mount()`.

Supported operation model:

- New mount: `fsopen` during prepare or mount stage, `fsconfig(source/options)`, `FSCONFIG_CMD_CREATE`, `fsmount`, optional detached subdir open, VFS attributes, then `move_mount`.
- Remount: `open_tree`, `fspick`, `fsconfig` reconfiguration, and `mount_setattr`.
- Propagation-only: `open_tree` and post-stage `mount_setattr` propagation.
- Move/bind: `open_tree`, optional VFS attributes, and post-stage `move_mount`.

Key components:

- `struct libmnt_sysapi` hookset data stores `fd_fs`, `fd_tree`, `is_new_fs`, and optional `subdir`.
- `configure_superblock()` sends superblock and filesystem-specific options through `fsconfig()`, ignoring VFS/userspace/external options.
- `hook_create_mount()` creates a new detached mount and records mount ID through `statx(STATX_MNT_ID)` when available.
- `hook_reconfigure_mount()` uses `fspick()` then `FSCONFIG_CMD_RECONFIGURE`.
- `hook_set_vfsflags()` translates option-list mount attributes into `mount_setattr()` normal and recursive calls.
- `hook_set_propagation()` applies propagation options through post-attach `mount_setattr()`.
- `hook_attach_target()` moves the detached tree to the target, with optional `MOVE_MOUNT_BENEATH`, and marks attached/moved status.
- `hook_prepare()` decides whether to use the new API or recover to legacy.

Important behavior:

- `LIBMOUNT_FORCE_MOUNT2=always|never` can force or disable the classic mount path.
- The new API is skipped for btrfs mounts with SELinux options because of noted fsconfig limitations.
- Helpers use the new API only for propagation setting; helper execution itself remains external.
- ENOSYS or unsupported new API paths return positive `1` from prepare after clearing syscall status, allowing `hook_mount_legacy.c` to continue.
- Kernel versions before 5.14 are rejected for remount `mount_setattr()` use.
- For Linux >= 6.15, `hook_subdir.c` can set `api->subdir`, and this file opens the subdirectory from a detached tree before final attachment.

Dependencies and interactions:

- Active under `USE_LIBMOUNT_MOUNTFD_SUPPORT`.
- Coordinates with `hook_subdir.c`, `hook_idmap.c`, option-list attribute extraction, syscall-message collection, Linux version checks, and context syscall status.

Risk notes:

- The file intentionally has several recovery paths into legacy mount behavior; callers must not treat positive prepare return as fatal.
- File descriptor ownership is central. `close_sysapi_fds()` is used on failure/deinit; other hooks may reuse `fd_tree`.
- Some classic `MS_*` flags are interpreted as superblock options for backward compatibility, so option map correctness is critical.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hook_mount.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hook_mount_legacy.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hook_mount_legacy.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hook_owner.c -->
# File Research: sources/block-storage/util-linux/libmount/src/hook_owner.c

This hook implements post-mount ownership and mode changes requested by `X-mount.owner=`, `X-mount.group=`, and `X-mount.mode=`.

Key behavior:

- `hook_prepare_options()` parses requested owner, group, and mode from userspace options.
- UID/GID/mode parsing uses libmount parsers, so names and numeric values are handled consistently with other mount options.
- If any setting is present, it registers a `MNT_STAGE_POST` hook.
- `hook_post()` runs after mount finalization work and applies `lchown()` for owner/group and `chmod()` for mode on the target.
- Failures are reported as `MNT_ERR_CHOWN` or `MNT_ERR_CHMOD`.

Dependencies and interactions:

- Runs at `MNT_STAGE_PREP_OPTIONS` for parsing and at `MNT_STAGE_POST` for filesystem mutation.
- Uses target from `cxt->fs`.

Risk notes:

- These operations happen after a successful mount; failure means the filesystem may already be mounted but requested metadata changes failed.
- `lchown()` avoids following a symlink for ownership, while `chmod()` follows normal chmod behavior.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hook_owner.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hook_selinux.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hook_selinux.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hook_subdir.c -->
# File Research: sources/block-storage/util-linux/libmount/src/hook_subdir.c

This hook implements `X-mount.subdir=`, allowing callers to mount only a subdirectory from a filesystem source. It adapts to classic mount, older fd-based mount APIs, and newer detached-tree subdirectory support.

Key behavior:

- `is_subdir_required()` accepts `X-mount.subdir` only for normal mount operations, rejecting bind, move, remount, and propagation-only cases.
- The hook stores the requested subdir and registers `hook_mount_pre()`.
- On Linux >= 6.15 with mount fd support and no helper, `hook_mount_pre()` passes the subdir to `hook_mount.c` via `api->subdir`; `hook_mount.c` opens the detached subdirectory directly.
- On older paths, it creates `/run/mount` temporary target state, unshares the mount namespace, makes the runtime directory or temp target private, changes the context target to `MNT_PATH_TMPTGT`, and registers `hook_mount_post()`.
- `hook_mount_post()` binds or moves the requested subdirectory from the temporary root to the original target, then unmounts the temporary root and switches back to the original namespace.

Dependencies and interactions:

- Requires namespace support for fallback paths.
- Coordinates with `hook_mount.c` through `libmnt_sysapi` when mount fd support is available.
- Uses target mutation on `cxt->fs` and global hookset data to preserve the original target.

Risk notes:

- Fallback paths depend on mount namespace manipulation and can fail if unshare/setns/mount-private operations are not permitted.
- Cleanup is essential: `free_hookset_data()` calls `tmptgt_cleanup()` if the namespace was created.
- A comment typo says "ateched"; behavior is still clear.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hook_subdir.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hook_veritydev.c -->
# File Research: sources/block-storage/util-linux/libmount/src/hook_veritydev.c

This conditional hook implements dm-verity setup for mount options such as `verity.hashdevice=`, `verity.roothash=`, `verity.roothashfile=`, FEC settings, root-hash signatures, and corruption policy. It uses libcryptsetup directly or through `dlopen()`.

Key components:

- `struct hookset_data` stores the created mapper device path and optional dlopen handles/function pointers.
- `new_hookset_data()` loads libcryptsetup symbols when configured for dlopen, enables cryptsetup debug logging for verbose contexts, and installs a log callback.
- `is_veritydev_required()` checks userspace verity option flags for normal mounts.
- `setup_veritydev()` parses options, creates or reuses a dm-verity mapper device, and rewrites `cxt->fs` source to `/dev/mapper/<roothash>-verity`.
- `hook_mount_post()` deletes or defers deletion of the mapper device.

Important behavior:

- Verity mounts are forced read-only by appending `MS_RDONLY`.
- Mandatory inputs are a hash device plus either root hash or root hash file; root hash and root hash file are mutually exclusive.
- Hash/FEC offsets and roots are parsed as sizes; default FEC roots is `2`.
- `verity.roothashsig=` reads a non-empty regular file and activates by signed key when libcryptsetup supports it.
- `verity.oncorruption=` accepts `ignore`, `restart`, and optionally `panic` if the cryptsetup flag exists.
- The mapper device name is derived from the root hash to allow deduplication and reuse.
- If activation returns `-EEXIST`, the hook opens the existing mapper, extracts the current root hash where supported, compares it to the requested hash, and validates signed/unsigned consistency when signatures are supported.
- Successful setup changes mount source to the mapper device. Cleanup uses deferred deactivation when the mount succeeded.

Dependencies and interactions:

- Active only with `HAVE_CRYPTSETUP`.
- Uses libcryptsetup APIs, path reading helpers, userspace option maps, and mount status to decide deferred cleanup.

Risk notes:

- Device reuse is intentionally conservative; inability to verify an existing device's root hash is treated as `-EEXIST`.
- Root hash conversion requires even-length valid hex matching libcryptsetup's volume key size.
- When using `dlopen()`, missing symbols surface as user messages from `dlerror()`.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hook_veritydev.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hooks.c -->
# File Research: sources/block-storage/util-linux/libmount/src/hooks.c

This file implements libmount's hook dispatcher and registers built-in hooksets. Hooksets provide staged callbacks for source preparation, target preparation, option preparation, mount execution, post-mount work, and final post-processing.

Built-in hook order on Linux:

- `__loopdev`
- `__veritydev` when cryptsetup is enabled
- `__mkdir`
- `__selinux` when libselinux is enabled
- `__subdir`
- `__mount` when mount fd support is enabled
- `__legacy-mount`
- `__idmap` when mount fd and Linux mount headers are available
- `__owner`

Key APIs:

- `mnt_context_deinit_hooksets()` calls every hookset deinitializer and resets hook lists.
- `mnt_context_get_hookset()` finds a built-in hookset by name.
- `mnt_context_set_hookset_data()` and `mnt_context_get_hookset_data()` manage per-hookset global data.
- `mnt_context_append_hook()` appends a staged callback.
- `mnt_context_insert_hook()` appends a staged callback that should run after another hookset name.
- `mnt_context_remove_hook()` removes a matching hook and optionally returns its data.
- `mnt_context_has_hook()` checks for existing active hooks.
- `mnt_context_call_hooks()` invokes first callbacks for a stage, then active callbacks for that stage.

Important behavior:

- Hookset data and individual hook callback data are separate lists.
- Each hook records hookset, stage, data pointer, optional `after` dependency name, callback, and an `executed` bit.
- A hook callback can register more hooks dynamically for any stage.
- `call_depend_hooks()` runs hooks whose `after` field matches the just-called hookset name and stage.
- Positive return codes from first hooks are recoverable and do not abort the stage; negative return codes abort.
- Fake contexts skip callback execution but log fake calls.
- After a stage, executed bits for that stage are reset so hooks can be called again in later cycles if needed.

Dependencies and interactions:

- All hook modules depend on this dispatcher for lifecycle and ordering.
- SELinux uses dependency insertion after `__mkdir`; legacy mount checks whether `__mount` registered active hooks.

Risk notes:

- Dependency matching is by hookset name string, so renaming hooksets can silently break ordered hooks.
- `mnt_context_deinit_hooksets()` sums deinit return values rather than preserving first failure.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/hooks.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/init.c -->
# File Research: sources/block-storage/util-linux/libmount/src/init.c

This file defines libmount debug subsystem initialization.

Key behavior:

- `UL_DEBUG_DEFINE_MASK(libmount)` and `UL_DEBUG_DEFINE_MASKNAMES(libmount)` define debug categories including cache, context, diff, fs, hook, locks, loop, options, optlist, table, update, utils, monitor, btrfs, and verity.
- `mnt_init_debug()` initializes the debug mask once, using the supplied mask or `LIBMOUNT_DEBUG` environment variable.
- When debugging is enabled beyond init/help, it logs library version and feature strings.
- Help debug prints supported masks.

Dependencies and interactions:

- All files use `DBG`, `DBG_OBJ`, and subsystem masks defined here.
- The optional test program parses a numeric mask and initializes debugging.

Risk notes:

- Debug initialization is one-shot; later calls cannot alter the mask once initialized.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/init.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/iter.c -->
# File Research: sources/block-storage/util-linux/libmount/src/iter.c

This file implements libmount's small generic iterator object used to traverse internal lists and tables forward or backward.

Key APIs:

- `mnt_new_iter(direction)` allocates an iterator and stores the direction.
- `mnt_free_iter()` frees it.
- `mnt_reset_iter(itr, direction)` clears iterator state and either applies a new direction or preserves the old one when passed `-1`.
- `mnt_iter_get_direction()` returns the current direction.

Dependencies and interactions:

- Used heavily by table and option-list traversal code, including umount iteration, fstab/utab scans, and hook option scans.

Risk notes:

- `mnt_reset_iter()` assumes `itr` is non-null; the public header marks it nonnull.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/iter.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/libmount.h.in -->
# File Research: sources/block-storage/util-linux/libmount/src/libmount.h.in

This header template defines the public libmount API, version macros, opaque types, option maps, error codes, exit codes, flags, and exported functions. Build substitution fills `@LIBMOUNT_VERSION@` and version components.

Major declarations:

- Opaque types: cache, lock, iterator, filesystem, table, update, context, monitor, tabdiff, namespace, and statmount settings.
- `struct libmnt_optmap` and option-map masks (`MNT_INVERT`, `MNT_NOMTAB`, `MNT_PREFIX`, `MNT_NOHLPS`, `MNT_NOFSTAB`, `MNT_SUPERBLOCK`).
- Action constants `MNT_ACT_MOUNT` and `MNT_ACT_UMOUNT`.
- Private libmount error codes `MNT_ERR_*`, including loop, mount option, apply flags, lock, namespace, chown/chmod, idmap, and exec failures.
- Public command-style exit codes `MNT_EX_*`.
- API declarations for initialization, version/features, utilities, cache, optstring parsing, iterators, option maps, locks, filesystem entries, statmount, table parsing/manipulation, listmount, updates, diffs, monitor, context configuration/status, mount/umount flows, and namespace switching.
- Userspace mount option bits such as `MNT_MS_LOOP`, `MNT_MS_OFFSET`, dm-verity bits, helper/uhelper bits, and ownership/user bits.
- Linux `MS_*` fallback constants and derived masks such as `MS_PROPAGATION`, `MS_SECURE`, and `MS_OWNERSECURE`.

Important relationships:

- Declares the implementation surface provided by files in this group: `init.c`, `iter.c`, `lock.c`, `fs.c`, `fs_statmount.c`, and `context_umount.c`.
- The hook files are internal and not directly exposed here, but their errors and option bits are part of the public surface through `MNT_ERR_*` and `MNT_MS_*`.
- The header exposes staged mount/umount APIs: prepare, do, finalize, full operation, and next-entry iteration.

Risk notes:

- Because this is an installed public API template, changes here affect ABI/API consumers.
- Some error and flag values are fixed numeric contracts; renumbering would break callers.
- Fallback `MS_*` definitions are guarded to avoid collisions with libc/kernel headers.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/libmount.h.in -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/lock.c -->
# File Research: sources/block-storage/util-linux/libmount/src/lock.c

This file implements libmount file locking. Since util-linux v2.39, libmount uses `flock()` only rather than classic mtab locking.

Key APIs:

- `mnt_new_lock(datafile, id)` creates a lock object whose lock path is `<datafile>.lock`; `id` is ignored.
- `mnt_ref_lock()`, `mnt_unref_lock()`, and `mnt_free_lock()` implement reference-counted lifecycle.
- `mnt_lock_block_signals()` configures signal blocking while a lock is held.
- `mnt_lock_file()` acquires an exclusive flock.
- `mnt_unlock_file()` releases the lock, closes the FD, clears state, and restores signal masks.

Important behavior:

- Lock files are opened with `O_RDONLY|O_CREAT|O_CLOEXEC` and mode `0600`; mode is corrected with `fchmod()` if needed.
- If signal blocking is enabled, all signals are blocked before opening/flocking and the previous mask is restored on error or unlock.
- `flock(LOCK_EX)` retries on `EAGAIN` and `EINTR`.
- The lock object records whether it currently owns a lock and the lockfile FD.

Dependencies and interactions:

- Used by update-table code for files such as `/run/mount/utab`.
- Debug output uses the lock debug mask from `init.c`.
- The optional test program runs concurrent lock/increment cycles.

Risk notes:

- `mnt_free_lock()` does not unlock; callers should call `mnt_unlock_file()` or use the reference lifecycle carefully.
- If a process exits while holding an FD lock, the kernel releases it, but the lock file remains.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/lock.c -->