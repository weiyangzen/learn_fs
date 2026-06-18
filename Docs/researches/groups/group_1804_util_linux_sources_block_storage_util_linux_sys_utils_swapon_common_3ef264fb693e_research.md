# Group Research: group_1804_util_linux_sources_block_storage_util_linux_sys_utils_swapon_common_3ef264fb693e

Scope: `Docs/research_subset_a.md`, specifically the `sources/block-storage/util-linux` source tree. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/swapon-common.c -->
# File Research: sources/block-storage/util-linux/sys-utils/swapon-common.c

This file provides shared state and helpers for the `swapon`/swap tooling. It owns lazily parsed `libmnt_table` instances for fstab and active swaps, plus the global `struct libmnt_cache *mntcache` used for source/tag resolution.

`get_fstab()` allocates the fstab table once, installs `table_parser_errcb()`, attaches the global cache, and parses the requested fstab path. `get_swaps()` does the same for `/proc/swaps` through `mnt_table_parse_swaps()`. Parse errors are reported as warnings and ignored by returning `1` from the callback. `free_tables()` unreferences both cached tables.

The small query helpers are `match_swap()`, which delegates to `mnt_fs_is_swaparea()`, and `is_active_swap()`, which checks the cached swaps table for a source match in reverse iteration order. `cannot_find()` centralizes the warning and `-1` return used when a requested swap device or tag cannot be resolved.

The file also stores command-line `-L` label and `-U` UUID lists in growable arrays. `add_label()`, `get_label()`, `numof_labels()`, `add_uuid()`, `get_uuid()`, and `numof_uuids()` are intentionally minimal; they retain pointers to option arguments rather than duplicating strings.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/swapon-common.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/swapon-common.h -->
# File Research: sources/block-storage/util-linux/sys-utils/swapon-common.h

This header exposes the shared swap helper API implemented by `swapon-common.c`. It includes `libmount.h`, declares the global `mntcache`, and publishes table accessors for fstab and active swaps.

The exported functions cover three responsibilities: table lifecycle and parsing (`get_fstab()`, `get_swaps()`, `free_tables()`), swap matching/resolution diagnostics (`match_swap()`, `is_active_swap()`, `cannot_find()`), and retained command-line tag lists for labels and UUIDs.

It is a narrow internal header for util-linux swap commands, not a public libmount interface. The declarations make the cache/table/tag-list state available to `swapon.c` while keeping storage private to `swapon-common.c`.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/swapon-common.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/swapon.c -->
# File Research: sources/block-storage/util-linux/sys-utils/swapon.c

This file implements `swapon(8)`: listing active swap, enabling individual swap devices/files, enabling all fstab swap entries, resolving labels/UUIDs, parsing swap options, and validating swap headers before calling the `swapon(2)` syscall.

Output mode is built around `struct swapon_ctl`, the `infos[]` column table, and libsmartcols. `display_summary()` preserves the deprecated `-s` tabular format from `/proc/swaps`; `show_table()` and `add_scols_line()` implement `--show`, optional raw/no-heading/byte output, annotations, and optional UUID/LABEL lookup through `get_swap_prober()`.

Activation preflight is centered on `swapon_checks()`. It opens the target, warns about insecure permissions and non-root-owned regular files, rejects sparse regular swap files, obtains block-device or file size, reads up to `MAX_PAGESIZE`, detects swap or suspend signatures, compares swap-header page size to the system page size, optionally runs `mkswap` through `swap_reinitialize()`, and rewrites obsolete software-suspend signatures through `swap_rewrite_signature()`. `swap_get_size()` handles byte-swapped swap headers, and `swap_get_info()` preserves label/UUID when reinitializing.

`do_swapon()` resolves noncanonical specs through `mnt_resolve_spec()`, runs the checks, constructs kernel flags from priority and discard policy, then calls `swapon(path, flags)`. Discard handling accepts whole-device discard, `once`, `pages`, or both policy bits collapsed to `SWAP_FLAG_DISCARD` for the kernel. Label and UUID activation are wrappers around `mnt_resolve_tag()`.

`parse_options()` understands fstab/`-o` options relevant to swap: `nofail`, `discard[=once|pages]`, and `pri=<n>`. `swapon_all()` iterates swap fstab entries with `match_swap()`, skips `noauto`, merges per-entry options over global defaults, resolves tags to real devices, skips already-active swaps, honors `nofail` for missing/inaccessible devices, and enables each remaining swap.

`main()` initializes locale, libmount debug state, the global cache, parses options, enforces incompatible option groups, and dispatches to summary, show-only default output, `--all`, label/UUID lists, and positional specs. It frees the shared libmount tables and cache before returning the ORed syscall/status result.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/swapon.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/switch_root.c -->
# File Research: sources/block-storage/util-linux/sys-utils/switch_root.c

This file implements `switch_root(8)`, used during early boot to move from an initramfs root to a real root filesystem and exec the new init. It has no libmount dependency; it works directly with `stat`, `mount(MS_MOVE)`, `chroot`, `fork`, and `execv`.

`recursiveRemove()` deletes directory contents below an fd without crossing mount points. It uses `fdopendir()`, compares each entry's `st_dev` to the root directory device, recurses into same-device directories with `openat()`, and removes entries with `unlinkat()`. The input fd is always closed, either by `closedir()` or directly on failure before `fdopendir()`.

`switchroot()` first records old and new root device numbers. It attempts to move `/dev`, `/proc`, `/sys`, and `/run` into corresponding directories under the new root when the old location is a separate mount and the new destination is still part of the new root. If moving fails, it force-unmounts the old mount; if the new destination is already mounted or not usable, it lazily detaches the old one.

After moving auxiliary mounts, `switchroot()` changes to `newroot`, opens the old `/`, moves `newroot` onto `/`, performs `chroot(".")`, and changes to `/`. A child process checks whether the old root fd is `ramfs` or `tmpfs`; only then does it recursively delete the old initramfs contents. The parent closes the fd and returns so `main()` can verify and exec the requested init.

`main()` only supports `--help` and `--version`, requires `<newrootdir> <init> [args...]`, calls `switchroot()`, warns if the init is not executable, and replaces itself with `execv(init, initargs)`.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/switch_root.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/tunelp.c -->
# File Research: sources/block-storage/util-linux/sys-utils/tunelp.c

This deprecated maintenance-mode utility configures Linux line-printer (`lp`) driver parameters. It parses command options into a linked list of ioctl commands, opens the target device nonblocking, verifies it is a character device, applies queued ioctls, optionally prints status, and prints the IRQ/polling mode by default.

Each option appends a `struct command` containing an lp ioctl number and value: `LPSETIRQ`, `LPTIME`, `LPCHAR`, `LPWAIT`, `LPABORT`, `LPABORTOPEN`, `LPCAREFUL`, `LPGETSTATUS`, and `LPRESET`. Numeric arguments use util-linux checked parsers; `on|off` arguments go through `ul_parse_switch()`. `-q` controls whether the final IRQ query is printed.

The device is opened `O_WRONLY | O_NONBLOCK` specifically to avoid blocking when `ABORTOPEN` is already configured and the printer is offline or in error. The program tests for old-kernel ioctl numbering compatibility by probing `LPGETIRQ`; if the new ioctl range returns `EINVAL`, it subtracts `0x0600` from ioctl numbers.

For `LPGETSTATUS`, it handles historical kernels that return status as the ioctl return value rather than through the output pointer, then decodes busy, ready, out-of-paper, online, and error bits. For all other commands it warns on ioctl failure but continues through the command list. The final IRQ query treats zero as polling mode and nonzero as the active IRQ.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/tunelp.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/umount.c -->
# File Research: sources/block-storage/util-linux/sys-utils/umount.c

This file implements `umount(8)` as a command-line driver around libmount's `libmnt_context`. It handles option parsing, restricted-user behavior, namespace switching, recursive/all-target unmounts, libmount exit-code translation, and user-facing diagnostics.

`suid_drop()` drops setuid-root privilege for restricted operations, verifies privilege cannot be regained, forces the libmount context into unrestricted mode, and restores sanitized environment variables. The main parser allows only a small option set for restricted users; security-sensitive options cause the program to drop privileges before continuing. Restricted positional paths are canonicalized with `ul_canonicalize_path_restricted()`, and non-root users may not pass tag specs.

`mk_exit_code()` converts libmount API/syscall state into `MNT_EX_*` exit codes with `mnt_context_get_excode()`, implements `--graceful` success for already-gone targets, and suppresses selected "not mounted" messages under `--quiet`. `success_message()` prints verbose successful unmount messages only when the libmount operation actually succeeded and no helper error is pending.

`umount_all()` iterates mount entries backward through `mnt_context_next_umount()`, respecting libmount's ignore decisions and accumulating exit codes. `umount_one()` sets the target, calls `mnt_context_umount()`, retries after `suid_drop()` for a restricted `-EPERM` path where libmount did not reach the syscall, translates the result, optionally prints success, and resets the context.

`new_mountinfo()` temporarily switches to the target mount namespace configured by `--namespace`, parses `/proc/self/mountinfo` into an independent table with the context cache, and switches back. Recursive unmounting uses that table: `umount_do_recurse()` first handles an overmount, then children in backward order, then the target itself through `umount_one_if_mounted()`. `umount_alltargets()` resolves the source once, then unmounts every mountinfo entry with the same device number, optionally recursively.

`main()` creates the libmount context, installs parser warnings, maps CLI options to libmount context flags (`force`, `lazy`, `fake`, `loopdel`, `rdonly_umount`, no helpers, no mtab, fstype/options patterns), supports PID or path mount namespace selection, enforces incompatible option groups, dispatches `--all`, `--all-targets`, `--recursive`, or positional unmounts, and clamps accumulated exit status to 255.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/umount.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/unshare.c -->
# File Research: sources/block-storage/util-linux/sys-utils/unshare.c

This file implements `unshare(1)`, combining Linux namespace creation with optional persistent namespace bind mounts, user/group ID mapping, mount propagation changes, proc/binfmt setup, time namespace offsets, chroot/chdir, signal-aware forking, capability retention, and environment filtering before executing a command or shell.

Namespace persistence is represented by `namespace_files[]`, mapping `CLONE_NEW*` flags to `/proc/<pid>/ns/...` names and optional user-specified bind targets. `set_ns_target()` records targets, and `bind_ns_files()` bind-mounts namespace files from a chosen process. When persistent namespaces interact with mount or user namespaces, `bind_ns_files_from_child()` uses an `eventfd` handshake so a helper child binds the parent's namespace files after `unshare()` has happened.

User namespace setup is the densest part of the file. It parses single users/groups, explicit ranges, `auto`, `subids`, and `all` modes into linked `struct map_range` chains. `read_subid_range()` reads `/etc/subuid` or `/etc/subgid`; `read_kernel_map()` mirrors existing kernel maps; `add_single_map_range()` adds a current-user/current-group single-ID mapping while splitting existing ranges to avoid overlap. `map_ids_from_child()` synchronizes with the parent and uses direct `/proc/<pid>/{uid,gid}_map` writes when effective root, otherwise execs `newuidmap`/`newgidmap`.

The parent-child synchronization helpers are `fork_and_wait()`, `sync_with_child()`, and `waitchild()`. They ensure external mapping helpers or namespace bind helpers wait until the parent has called `unshare()`. `setgroups_control()` writes `/proc/self/setgroups`, and simple self-mapping paths use `map_id()` after `unshare()`.

Mount-related setup includes `parse_propagation()` and `set_propagation()` for recursive root propagation, optional proc mounting at `--mount-proc`, optional `binfmt_misc` mounting at `--mount-binfmt`, and `load_interp()` for binfmt registrations. Fixed binfmt interpreters combined with `--root` are loaded before `chroot()` against the host `/proc/sys/fs/binfmt_misc`; other registrations are loaded after namespace/chroot setup.

Forking support handles PID namespaces and supervision options. `--fork`, `--kill-child`, and `--forward-signals` alter the flow: the parent blocks or forwards SIGINT/SIGTERM, waits for the child, propagates signal termination to itself, and for `--kill-child` the child sets `PR_SET_PDEATHSIG` and optionally verifies the original parent is still alive through `pidfd_open()`/`poll()`.

`main()` parses all namespace and setup options, validates time offsets require `CLONE_NEWTIME`, prepares helper children where needed, optionally changes owner uid/gid before `unshare()`, calls `unshare(unshare_flags)`, completes id mapping and time offset writes, forks if requested, persists namespace files, applies self maps/setgroups/mount propagation, mounts proc/binfmt, changes root and directory, applies requested uid/gid, raises permitted caps to ambient when requested, clears or whitelists environment, and finally execs the specified command or the user's shell.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/unshare.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/wdctl.c -->
# File Research: sources/block-storage/util-linux/sys-utils/wdctl.c

This file implements `wdctl(8)`, a watchdog status/configuration utility. It reads watchdog identity, options, status, boot status, timeouts, time left, pretimeout governor data, and can set timeout, pretimeout, or pretimeout governor.

Watchdog flags are described by `wdflags[]`, and output columns by `infos[]`. `show_flags()` renders supported watchdog option bits with libsmartcols, including current status and boot-status bit values. `print_device()` chooses between pretty multi-line output, one-line `NAME=value` output, and optional flag tables depending on `struct wd_control`.

Device discovery prefers `/dev/watchdog0` over legacy `/dev/watchdog`. `get_sysfs()` resolves the character device through `/sys/dev/char/<major>:<minor>` and requires an `identity` attribute before treating sysfs as usable. The `struct wd_device` stores sysfs context, watchdog info, timeouts, governor strings, status bitmasks, and booleans describing which fields were successfully read.

The file is careful with watchdog device opens. `set_watchdog()` and `read_watchdog_from_device()` block signals while the watchdog fd is open, avoid `err()`/`exit()` in the critical section, write the magic close character `V` in a retry loop, and then close the fd to avoid unintentionally arming a reboot. Setting timeouts uses `WDIOC_SETTIMEOUT` and `WDIOC_SETPRETIMEOUT`; setting the pretimeout governor writes the sysfs `pretimeout_governor` attribute.

`read_watchdog_from_sysfs()` is preferred and reads identity, firmware version, options, status, bootstatus, nowayout, timeout, pretimeout, and timeleft. `should_read_from_device()` avoids opening the device when sysfs has enough data or `nowayout` is set, falling back to ioctl reads only when needed. `read_governors()` parses `pretimeout_available_governors` and current `pretimeout_governor`.

`main()` parses output filters, column selection, hide/raw/oneline modes, set operations, and target devices. It initializes default flag columns, picks the default device if none is supplied, optionally applies requested settings, reads the watchdog, prints the requested view, releases sysfs path context, and returns failure if any device operation failed.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/wdctl.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/sys-utils/zramctl.c -->
# File Research: sources/block-storage/util-linux/sys-utils/zramctl.c

This file implements `zramctl(8)`, used to list, find, create/configure, and reset compressed RAM block devices. It interacts primarily with zram sysfs attributes, optionally with systemd `sd-device` to wait for udev initialization, and uses libsmartcols for status output.

`struct zram` stores the device path, a flock fd, sysfs path context, cached `mm_stat` fields, optional `sd_device`, and probes for zram-control support. Device naming helpers default to `/dev/zramN`, parse the numeric suffix, resolve sysfs from the block devno, canonicalize nonabsolute names through sysfs, and test existence/used state by reading `disksize`.

Dynamic device management uses `/sys/class/zram-control`. `zram_control_add()` reads `hot_add` to allocate a device and updates the object name; `zram_control_remove()` writes the numeric device id to `hot_remove`. `find_free_zram()` scans from zero, using existing unused devices or hot-adding when possible, and returns the first unused zram object.

Concurrency and udev handling are explicit. `zram_wait_initialized()` waits up to three seconds for a block disk device to become initialized when systemd device APIs are available; otherwise it is a no-op. `zram_lock()` opens the device, optionally via `sd_device_open()`, and uses `flock()` to coordinate with udev or other users. Creation intentionally unlocks before writing `reset` because the kernel refuses reset while the device node is open.

Status output reads modern Linux `mm_stat` first and falls back to older per-attribute files. `get_mm_stat()` returns either bytes or human-readable strings and can also return numeric values for compression-ratio calculation. `fill_table_row()` populates columns for name, disk size, data/compressed/total/limit/peak memory, algorithm selected inside brackets from `comp_algorithm`, streams, zero pages, migrated objects, compression ratio, and mountpoint via `check_mount_point()`. `status()` either reports one specified device or scans `/dev` for used `zramN` devices.

`main()` parses actions and output modifiers, enforces mutually exclusive modes, initializes default columns, and dispatches to status, reset, find-only, or create. Reset validates existence, waits for initialization, takes an exclusive nonblocking lock, writes `reset`, then tries hot-remove. Create chooses a free or specified device, waits for initialization, locks/unlocks, resets it, writes optional streams, compression algorithm, algorithm parameters, then writes `disksize`; `--find --size` prints the allocated device name.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/sys-utils/zramctl.c -->