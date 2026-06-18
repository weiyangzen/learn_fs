# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_util.c

This file provides broad internal utility support for libzfs: handle lifecycle, error reporting, ioctl nvlist packing, external process execution, property-list printing/parsing, numeric parsing, version reporting, color output, script environment construction, and disk preparation helpers.

Primary responsibilities:
- Maintain and expose libzfs error state.
- Convert system and ZFS kernel errors to libzfs `EZFS_*` errors.
- Allocate memory with libzfs error handling.
- Initialize and finalize `libzfs_handle_t`.
- Run external helper programs and capture stdout.
- Pack/unpack nvlists into `zfs_cmd_t` ioctl structures.
- Print property data in table or JSON form.
- Parse user-facing numeric property values.
- Build/expand property lists for zfs/zpool/vdev commands.
- Report userland/kernel versions.
- Control optional ANSI color output.
- Prepare script environments for vdev helper scripts.
- Run optional disk preparation scripts before labeling.

Error-state API:
- `libzfs_errno()` returns the current libzfs error.
- `libzfs_error_action()` returns the current action string.
- `libzfs_error_description()` returns an explicit auxiliary description or a default string for `EZFS_*`.
- `zfs_error_aux()` stores formatted auxiliary text.
- `zfs_error()` and `zfs_error_fmt()` set libzfs error/action state and return `-1`.
- `zfs_standard_error()` / `zfs_standard_error_fmt()` map errno and ZFS-specific kernel errors to dataset-oriented `EZFS_*`.
- `zpool_standard_error()` / `zpool_standard_error_fmt()` do the same for pool operations.
- `zfs_setprop_error()` specializes property-setting failures such as quota/reservation space semantics, read-only datasets, too-long values, unsupported pool features, boot/root-pool restrictions, and keylocation restrictions.

Handle lifecycle:
- `libzfs_init()` loads the module, allocates the handle, compiles the URI regex, opens `ZFS_DEV`, initializes libzfs_core, property tables, feature tables, mount-table state, and Fletcher-4.
- It reads `ZFS_SENDRECV_MAX_NVLIST` to override the maximum send/receive metadata nvlist size, defaulting to `SPA_MAXBLOCKSIZE * 4`.
- It supports test behavior through `ZFS_PROP_DEBUG` and `ZFS_SYSFS_PROP_SUPPORT_TEST`.
- `libzfs_fini()` closes the fd, frees pool handles and namespace state, finalizes mnttab/libzfs_core/Fletcher, releases regex state, optionally unloads dynamic libfetch, and frees the handle.
- Accessors include `zpool_get_handle()`, `zfs_get_handle()`, and `zfs_get_pool_handle()`.

Memory/process helpers:
- `no_memory()`, `zfs_alloc()`, `zfs_realloc()`, `zfs_strdup()`, and `zfs_asprintf()` provide checked allocation patterns.
- `libzfs_print_on_error()` controls automatic stderr reporting.
- `libzfs_run_process_impl()` forks, sets a new process group, redirects stdout/stderr to `/dev/null` or a pipe depending on flags, supports `execv/execvp/execve/execvpe`, waits, and returns child exit status.
- `libzfs_run_process()`, `libzfs_run_process_get_stdout()`, and `_nopath()` are public wrappers.
- `libzfs_read_stdout_from_fd()` reads child stdout into a heap array of newline-trimmed strings.
- `libzfs_free_str_array()` frees those arrays.
- `libzfs_envvar_is_set()` treats numeric nonzero, `YES`, and `ON` as enabled.

Dataset/path and ioctl nvlist helpers:
- `zfs_path_to_zhandle()` treats non-path input as a dataset name, otherwise resolves a mounted ZFS filesystem through mnttab device matching.
- `zfs_ioctl()` calls `lzc_ioctl_fd()` using the handle fd.
- `zcmd_alloc_dst_nvlist()`, `zcmd_expand_dst_nvlist()`, `zcmd_free_nvlists()`, `zcmd_write_conf_nvlist()`, `zcmd_write_src_nvlist()`, and `zcmd_read_dst_nvlist()` manage packed nvlist buffers in `zfs_cmd_t`.
- `zcmd_print_json()` prints an nvlist as JSON and frees it.

Property display:
- `zprop_print_headers()` computes column widths and prints non-scripted headers.
- `zprop_nvlist_one_property()` adds one property to a JSON nvlist, preserving value and source metadata.
- `zprop_print_one_property()` prints one property row according to selected columns and source filters.
- `zprop_collect_property()` dispatches either JSON collection or table printing.

Numeric and property parsing:
- `str2shift()` validates binary suffixes such as `K`, `M`, `G`, optional `B`/`iB`, and computes base-2 shifts.
- `zfs_nicestrtonum()` parses integer or decimal numeric strings plus suffixes, rejects invalid suffixes and overflow, and returns a `uint64_t`.
- `zprop_parse_value()` converts string/uint64/index property values into DSL-compatible nvlist values. It handles special values such as quota `none`, pool DDT quota `none`/`auto`, filesystem/snapshot limit `none`, vdev checksum/io limit `none`, and volume refreservation `auto`.
- `zprop_get_list()` parses comma-separated property lists, including the synthetic `space` group.
- `addlist()` validates native and user-defined property names by type.
- `zprop_expand_list()` expands `all` into every native property plus leading `name`.
- `zprop_free_list()` frees property-list chains.
- `zprop_iter()` delegates to common property iteration.

Version/color:
- `zfs_version_userland()` returns `ZFS_META_ALIAS`.
- `zfs_version_print()` prints userland and kernel module versions.
- `zfs_version_nvlist()` returns both versions in an nvlist.
- `use_color()` caches whether color output is allowed based on `ZFS_COLOR`, `NO_COLOR`, stdout TTY status, and `TERM`.
- `color_start()`, `color_end()`, and `printf_color()` wrap ANSI-colored output.

Vdev script/disk preparation:
- `zpool_vdev_script_alloc_env()` builds a limited environment for helper scripts with `PATH`, `POOL_NAME`, `VDEV_PATH`, `VDEV_UPATH`, `VDEV_ENC_SYSFS_PATH`, and optional key/value.
- `zpool_vdev_script_free_env()` frees that environment.
- `zpool_prepare_disk()` runs `ZFSEXECDIR/zfs_prepare_disk` if executable, passing vdev environment and capturing stdout.
- `zpool_prepare_and_label_disk()` runs preparation and then labels the disk via `zpool_label_disk()`.

Important behavior:
- Error helpers centralize translation from kernel/userland errno into stable libzfs error categories used throughout the library, including `libzfs_sendrecv.c`.
- `libzfs_init()` must succeed in several stages; failure paths close/free only the resources acquired so far.
- The nvlist write helpers allocate packed buffers owned by `zfs_cmd_t` and released by `zcmd_free_nvlists()`.
- Process execution closes over stdout/stderr behavior with flags; stdout capture uses a nonblocking close-on-exec pipe.
- Numeric parsing uses binary units, not decimal SI units.

Research relevance:
- This file is foundational support code for almost every libzfs module in this group. It explains how libzfs reports failures, communicates nvlists to kernel ioctls, interprets user property values, initializes feature/property state, and invokes external helper scripts.
