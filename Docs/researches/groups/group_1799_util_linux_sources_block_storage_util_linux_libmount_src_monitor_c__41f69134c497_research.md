# Group Research: group_1799_util_linux_sources_block_storage_util_linux_libmount_src_monitor_c__41f69134c497

Scope: `Docs/research_subset_a.md`, specifically the `sources/block-storage/util-linux` source tree. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/monitor.c -->
# File Research: sources/block-storage/util-linux/libmount/src/monitor.c

This file implements the public `libmnt_monitor` object: allocation, reference counting, epoll fd creation, backend entry registration, event waiting, event draining, and retrieval of optional per-event filesystem details. The monitor is an epoll multiplexer over a list of `struct monitor_entry` objects defined in `monitor.h`; each entry delegates backend-specific work through `struct monitor_opers`.

Core lifecycle functions are `mnt_new_monitor()`, `mnt_ref_monitor()`, `mnt_unref_monitor()`, `monitor_new_entry()`, and `free_monitor_entry()`. `mnt_unref_monitor()` closes the top-level monitor fd, disables and closes all backend fds, then frees every entry. `monitor_modify_epoll()` toggles an entry in the monitor epoll set, asks the backend for its fd via `op_get_fd`, sets `ev.data.ptr` to the entry, and drains the initial EPOLLIN/EPOLLET event used by the mountinfo backend.

The main event path is `mnt_monitor_get_fd()`, `read_epoll_events()`, `mnt_monitor_wait()`, and `mnt_monitor_next_change()`. `mnt_monitor_get_fd()` lazily creates an `EPOLL_CLOEXEC` epoll instance and adds all enabled entries. `read_epoll_events()` waits for one event, calls the backend `op_process_event()`, and marks the entry active only if the backend accepts the event. `mnt_monitor_wait()` converts internal return codes to public `1` changed, `0` timeout, or negative error. `mnt_monitor_next_change()` returns pending active entries first, otherwise polls without timeout, stores the last returned entry in `mn->last`, and exposes the entry path and type.

`mnt_monitor_event_cleanup()` drains pending changes when callers do not need details. `mnt_monitor_event_next_fs()` delegates to the last event backend's `op_next_fs`; this is currently meaningful for fanotify mount events, and returns `-ENOTSUP` for monitor types without filesystem-detail support.

Important behavior: the top-level monitor fd is stable until `mnt_monitor_close_fd()`; enabling or disabling entries after epoll creation updates the active epoll set. A backend may return `1` from `op_process_event()` to indicate a false-positive or veiled event, causing the monitor loop to keep waiting. The test program exercises direct waiting and nesting the libmount monitor fd inside another epoll.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/monitor.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/monitor.h -->
# File Research: sources/block-storage/util-linux/libmount/src/monitor.h

This private header defines the internal monitor data model shared by `monitor.c` and the backend implementations. It is not the public libmount API; it exposes only implementation structs and helper prototypes used inside `libmount/src`.

`struct monitor_entry` represents one monitored source. It stores a private backend fd, an external identifier (`id`, normally `-1` unless the backend supports multiple instances such as fanotify namespace fds), a display path returned to callers, a public `MNT_MONITOR_TYPE_*`, desired epoll events, backend operations, backend-private data, enabled/active booleans, and a list link. `active` means an accepted event is ready for `mnt_monitor_next_change()`.

`struct libmnt_monitor` owns a refcount, the top-level public epoll fd, the list of entries, a pointer to the last entry returned by `mnt_monitor_next_change()`, and `kernel_veiled`, which tells kernel-monitor backends to suppress events when a libmount userspace utab operation is active.

`struct monitor_opers` is the backend vtable. `op_get_fd` lazily opens or returns the backend fd, `op_close_fd` closes backend resources, `op_free_data` releases backend-private data, `op_process_event` validates and drains backend events, and `op_next_fs` optionally returns filesystem details for the last event. The helper prototypes (`monitor_modify_epoll`, `monitor_get_entry`, `monitor_new_entry`, `free_monitor_entry`) are the common entry-management API used by backend files.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/monitor.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/monitor_fanotify.c -->
# File Research: sources/block-storage/util-linux/libmount/src/monitor_fanotify.c

This file implements the fanotify-based kernel mount table monitor. It is compiled only when `HAVE_STRUCT_FANOTIFY_EVENT_INFO_HEADER` is available; otherwise `mnt_monitor_enable_fanotify()` returns `-ENOTSUP`. The backend targets modern Linux fanotify mount-namespace notifications and can report affected mount IDs, unlike the classic `/proc/self/mountinfo` epoll monitor.

The compatibility block defines missing `FAN_MNT_ATTACH`, `FAN_MNT_DETACH`, `FAN_REPORT_MNT`, `FAN_MARK_MNTNS`, and `struct fanotify_event_info_mnt` for build environments older than the target kernel API. Backend-private data stores the watched namespace fd plus a buffer, current pointer, and remaining byte count for parsed fanotify records.

`fanotify_get_fd()` creates a nonblocking close-on-exec fanotify fd with `FAN_REPORT_MNT`, then marks the mount namespace fd with `FAN_MARK_ADD | FAN_MARK_MNTNS` for attach and detach events. `fanotify_process_event()` reads into the private buffer and initializes iteration state. If `mn->kernel_veiled` is set and `MNT_PATH_UTAB ".act"` exists, it drains all pending fanotify data and reports no accepted event, allowing libmount userspace updates to hide duplicate kernel notifications.

`fanotify_next_fs()` parses one buffered fanotify record at a time. It validates `FAN_EVENT_OK()` and metadata version, extracts the mount event info, resets the supplied `libmnt_fs` while preserving its statmount reference, sets `uniq_id` from `mnt_id`, and marks the fs as attached or detached based on `meta->mask`. The buffer pointer advances with `FAN_EVENT_NEXT()`, returning `1` when no more event data remains.

`mnt_monitor_enable_fanotify()` supports multiple fanotify monitors on one `libmnt_monitor`, keyed by namespace fd. Passing `ns < 0` opens `/proc/self/ns/mnt` privately and uses that path as the event name; passing an fd uses `/proc/self/fd/<fd>` as the path and treats the fd as application-owned. Disable paths remove the entry from epoll and close only the fanotify fd.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/monitor_fanotify.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/monitor_mountinfo.c -->
# File Research: sources/block-storage/util-linux/libmount/src/monitor_mountinfo.c

This file implements the classic kernel mount table monitor based on epolling `/proc/self/mountinfo`. It is the portable fallback for detecting that the kernel mount table changed, but it does not identify which mount changed or how.

The backend operations are intentionally small. `mountinfo_get_fd()` opens the configured path read-only with `O_CLOEXEC` and reuses the fd after the first open. `mountinfo_close_fd()` closes it. `mountinfo_process_event()` accepts the event unless `mn->kernel_veiled` is enabled and `MNT_PATH_UTAB ".act"` exists, in which case it returns `1` so the top-level monitor treats the wakeup as not useful.

`mnt_monitor_enable_mountinfo()` creates a single entry of type `MNT_MONITOR_TYPE_MOUNTINFO` with path `_PATH_PROC_MOUNTINFO`. It uses `EPOLLIN | EPOLLET` rather than only `EPOLLPRI` or a passive fd because the top-level libmount monitor may itself be nested inside another epoll instance and callers need to identify which low-level fd fired. Since mountinfo would otherwise appear constantly readable, edge-triggered polling is paired with the initial drain in `monitor_modify_epoll()`.

`mnt_monitor_enable_kernel()` is a deprecated alias to `mnt_monitor_enable_mountinfo()`. `mnt_monitor_veil_kernel()` toggles duplicate suppression for kernel monitor backends during libmount-managed userspace table updates.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/monitor_mountinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/monitor_utab.c -->
# File Research: sources/block-storage/util-linux/libmount/src/monitor_utab.c

This file implements the userspace mount table monitor based on inotify. It watches libmount's private utab event file machinery rather than the kernel mount table directly. The default watched logical file is `mnt_get_utab_path()` (`/run/mount/utab` in normal builds), and the actual event file is `<utab>.event`.

Backend-private data stores the currently watched path, which may be the final event file or an ancestor directory. `userspace_add_watch()` first attempts to watch `<utab>.event` for `IN_CLOSE_WRITE | IN_DELETE_SELF`. If it does not exist, it walks up parent directories and watches the nearest existing directory for `IN_CREATE | IN_ISDIR | IN_DELETE_SELF`, remembering the chosen path to avoid redundant watches. This allows the monitor to survive missing `/run/mount` components and later event-file creation.

`userspace_monitor_get_fd()` opens a nonblocking close-on-exec inotify fd and installs the initial watch. `userspace_process_event()` drains the inotify buffer. `IN_CLOSE_WRITE` on the final event file is the meaningful change signal and returns success. Directory creation or self-delete events trigger watch re-evaluation; if a new watch replaces an old watch descriptor, the old watch is removed. `IN_DELETE_SELF` also frees saved backend data so the watch path can be rebuilt.

`mnt_monitor_enable_userspace()` creates or toggles the single userspace entry of type `MNT_MONITOR_TYPE_USERSPACE`. The filename parameter is honored only on first enable; subsequent toggles reuse the existing entry. Disabling removes the entry from epoll and closes the inotify fd, but keeps the entry available for re-enable.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/monitor_utab.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/mountP.h -->
# File Research: sources/block-storage/util-linux/libmount/src/mountP.h

This is libmount's private umbrella header. It defines internal structs, flags, paths, debug masks, iterator helpers, and cross-module prototypes used throughout `libmount/src`. It includes public `libmount.h`, util-linux support headers, and private utility headers, then layers libmount-specific internal state on top.

The header defines debug categories (`MNT_DEBUG_*`) and the `DBG`/`DBG_OBJ` wrappers, library paths such as `MNT_PATH_UTAB`, `MNT_PATH_TMPTGT`, and `MNT_MNTTABDIR_EXT`, test harness types under `TEST_PROGRAM`, and prototypes for utility functions, table parsing, listmount/statmount support, btrfs support, context helpers, option string/list functions, filesystem helpers, and update/event functions.

The central internal data structures are `struct libmnt_fs`, `struct libmnt_table`, and `struct libmnt_context`. `libmnt_fs` represents one fstab/mountinfo/utab/swaps row and stores identifiers, parent IDs, unique statmount IDs, namespace IDs, device numbers, source/tag/root/target/fstype strings, VFS/FS/user option strings, mount attributes, swap metadata, status flags, optional statmount state, comments, and user data. It defines internal flags for pseudo, network, swap, kernel, merged, attached, and detached status, plus inline helpers to mark attach, detach, or move.

`libmnt_table` owns a list of filesystems plus parse format, refcount, comment state, path/tag cache, parser error/filter callbacks, optional listmount and statmount references, noautofs behavior, and userdata. The generic `libmnt_iter` macros provide forward/backward traversal over libmount list heads and are used heavily by table, option-list, monitor, and diff code.

`libmnt_context` is the high-level mount/umount operation state: action, privilege mode, patterns, current filesystem, fstab/mountinfo/utab tables, parser callbacks, password callbacks, option mode, mount data, cache/lock/update objects, option lists and maps, target prefixes, flags, helper process status, syscall status, messages, namespace state, hook data, and feature booleans. The header also defines internal context flags and hook stages.

With `USE_LIBMOUNT_MOUNTFD_SUPPORT`, the header defines `struct libmnt_sysapi` for fsopen/fsmount/open_tree-style mount APIs and an accessor for hookset data. Overall, this header is the dependency hub that connects the monitor, option, parser, table, context, and update subsystems.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/mountP.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/optlist.c -->
# File Research: sources/block-storage/util-linux/libmount/src/optlist.c

This file implements `struct libmnt_optlist`, the parsed mount option container. It preserves option order while deriving cached flags and rendered option strings for specific maps and filtering modes. Options may originate from strings or bit flags, may be mapped or unknown, may be marked external-only, and may carry values, quoted values, empty `name=` separators, recursive state, and VFS/Linux-map state.

The list object tracks refcount, age, registered option maps, the built-in Linux map, per-map and all-filter caches, propagation flags, and shortcuts for remount, bind/rbind, readonly, move, silent, and recursive propagation. Allocation initializes the Linux map; map registration deduplicates maps up to `MNT_OL_MAXMAPS`.

Mutation paths are `mnt_optlist_set_optstr()`, `append_optstr()`, `prepend_optstr()`, `append_flags()`, `set_flags()`, `remove_flags()`, `insert_flags()`, `remove_opt()`, and `remove_named()`. String parsing uses `ul_optstr_next()` and `mnt_optmap_get_entry()` to attach map entries. Flag insertion walks map entries and adds only non-inverted flags that do not require mandatory values. Every mutation increments `age` and invalidates cached flag/string results.

`mnt_optlist_merge_opts()` deduplicates by walking backward and keeping the last option, removing earlier exact duplicates and opposite inverted options with the same map id. `mnt_optlist_get_flags()` computes map ids after applying inversion semantics and respects filters: default, all, unknown, helpers, or mtab. `mnt_optlist_strdup_optstr()` renders options back to a comma-separated string, places `rw`/`ro` first for generic Linux-facing strings, filters by target audience, and preserves empty values and quoting.

When `USE_LIBMOUNT_MOUNTFD_SUPPORT` is enabled, `mnt_optlist_get_attrs()` converts selected classic `MS_*` flags to `MOUNT_ATTR_*` set/clear masks for `mount_setattr()`. It handles remount reset semantics, recursive vs nonrecursive options, atime mutual exclusion, and `ro=fs` versus VFS-only readonly handling.

Accessor helpers expose option names, values, maps, map entries, external state, `sepnodata`, and substring matching within comma-separated option values. The test program exercises string/flag insertion, setting, rendering, splitting, flag extraction, and value containment.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/optlist.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/optmap.c -->
# File Research: sources/block-storage/util-linux/libmount/src/optmap.c

This file defines libmount's built-in option maps and the map lookup routine. Option maps describe how textual mount options correspond to mount flags or userspace-only libmount flags, plus masks such as `MNT_INVERT`, `MNT_NOMTAB`, `MNT_NOHLPS`, `MNT_PREFIX`, `MNT_SUPERBLOCK`, and `MNT_NOFSTAB`.

`linux_flags_map` covers filesystem-independent kernel mount flags: `ro`/`rw`, exec/suid/dev inversions, sync/async, dirsync, remount, bind/rbind, optional platform flags such as nosub, silent/loud, mandatory locking, atime variants, lazytime, propagation options, nosymfollow, and move. Entries are conditionally compiled according to available `MS_*` macros.

`userspace_opts_map` covers libmount/mount(8)-specific behavior: defaults, auto/noauto, user/nouser/users/nousers, owner/group, `_netdev`, comments, `x-`/`X-` prefixes, loop-related options, nofail, helper/uhelper, and verity-related userspace options. Many of these are marked not for helpers or not for mtab as appropriate.

`mnt_get_builtin_optmap()` returns one of the two static maps for `MNT_LINUX_MAP` or `MNT_USERSPACE_MAP`. `mnt_optmap_get_entry()` searches one or more maps for a parsed option name. It supports prefix entries (`MNT_PREFIX`) by `ul_startswith()`, otherwise compares the parsed name length and accepts exact names, mandatory-value entries (`name=`), and optional-value entries (`name[=]`). It can return both the containing map and the matched map entry.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/optmap.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/optstr.c -->
# File Research: sources/block-storage/util-linux/libmount/src/optstr.c

This file implements the low-level mutable string API for comma-separated mount option strings. It predates and complements `optlist.c`; callers can append, prepend, locate, set, remove, deduplicate, split, map to flags, apply flags, and match option patterns without building a `libmnt_optlist`.

The internal `libmnt_optloc` records the beginning, end, value pointer/length, and name length of a located option. `mnt_optstr_locate_option()` iterates with `ul_optstr_next()` and matches exact parsed names. `mnt_buffer_append_option()` is the central renderer: it inserts commas as needed, writes `name`, optionally writes `=`, preserves empty value syntax (`name=`), and optionally quotes values.

Mutation helpers include `mnt_optstr_append_option()`, `mnt_optstr_prepend_option()`, `mnt_optstr_set_option()`, `mnt_optstr_remove_option()`, `mnt_optstr_remove_option_at()`, and `mnt_optstr_deduplicate_option()`. `insert_value()` handles in-place reallocation and insertion of `=value` at a recorded offset. Removal ensures results do not start/end with commas or contain doubled commas.

Classification helpers include `mnt_split_optstr()` and `mnt_optstr_get_options()`. They parse each option, look it up in the built-in Linux and userspace maps or a supplied map, ignore map entries with no id, ignore value-bearing instances for no-value map entries, and append selected options into newly allocated user/VFS/FS/subset strings while respecting ignore masks.

`mnt_optstr_get_missing()` compares a wanted option string against an existing string and optionally returns a newly allocated list of missing options. `mnt_optstr_get_flags()` sets and clears bits in a caller-supplied flag word according to a map, with special translation of userspace `user`/`users`/`owner`/`group` into secure kernel flags when extracting Linux flags.

`mnt_optstr_apply_flags()` is deprecated but still implements string rewriting from a flag mask. It normalizes leading `ro`/`rw`, removes mapped options not present in the mask, preserves multi-use prefix options, and appends missing non-inverted no-value map entries. `mnt_match_options()` implements mount-style pattern matching, including `no` negation and `+` literal-prefix handling.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/optstr.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/tab.c -->
# File Research: sources/block-storage/util-linux/libmount/src/tab.c

This file implements the core `libmnt_table` container and high-level search logic over parsed filesystem entries. It covers allocation, reference management, comment storage, cache/statmount references, adding/removing/moving entries, iteration, mount tree queries, de-duplication, source/target lookup, mount-root derivation, and fstab-entry mounted checks.

Table lifecycle functions are `mnt_new_table()`, `mnt_reset_table()`, `mnt_ref_table()`, `mnt_unref_table()`, and `mnt_free_table()`. Entries are `libmnt_fs` objects owned by a table through refcounts and list membership. `mnt_table_add_fs()`, `mnt_table_insert_fs()`, `mnt_table_move_fs()`, and `mnt_table_remove_fs()` maintain `fs->tab`, list links, `nents`, and inherited statmount references. Comment APIs store intro/trailing comments and enable parser comment handling.

Iteration is provided by `mnt_table_next_fs()`, `first_fs()`, `last_fs()`, `find_next_fs()`, and `set_iter()`. With statmount/listmount support enabled, `mnt_table_next_fs()` can lazily fetch more mount IDs via `mnt_table_next_lsmnt()`. Mount-tree helpers include `is_mountinfo()`, `mnt_table_get_root_fs()`, `mnt_table_next_child_fs()`, and `mnt_table_over_fs()`, all relying on mountinfo ids and parent ids.

Search functions intentionally mimic mount(8) behavior. `mnt_table_find_target()` tries literal target, relative-to-absolute target, canonical requested target, and canonicalized table targets when a cache is present. `mnt_table_find_srcpath()` tries literal source, canonical source, tag evaluation, and canonicalized table sources, with btrfs default-subvolume filtering. `mnt_table_find_source()` parses tags such as UUID/LABEL and dispatches to tag or source-path lookup. Additional lookups include mountpoint ancestry, target plus option, source/target pair, device number, classic mount id, and unique mount id.

`mnt_table_uniq_fs()` removes duplicates according to a caller comparator while optionally preserving mount-tree parent relationships. `mnt_table_get_fs_root()` predicts the root path that mountinfo will report for a new fs, with special handling for bind mounts, nested btrfs subvolumes/default subvolumes, NFS roots, and CIFS/SMB UNC subdirectories. `__mnt_table_is_fs_mounted()` compares an fstab-style entry against a mount table by resolved source, optional device number, loop backing file, root, and target; it is designed mainly for `mount -a`.

The test program parses tables, finds entries, copies fs entries, checks mounted state, finds mountpoints, and de-duplicates targets.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/tab.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/tab_diff.c -->
# File Research: sources/block-storage/util-linux/libmount/src/tab_diff.c

This file implements `libmnt_tabdiff`, a small diff engine for comparing two mount tables and reporting mount, unmount, remount, and move operations. A diff entry holds an operation code plus referenced old and new `libmnt_fs` pointers.

`mnt_new_tabdiff()` initializes active and unused lists. `mnt_free_tabdiff()` frees all active entries and unrefs held filesystems. `tabdiff_reset()` recycles active entries into an unused list, clears operation state, unrefs old/new fs pointers, and resets the change count. Reusing unused entries reduces allocation churn when a diff object is reused repeatedly.

`tabdiff_add_entry()` obtains an unused or newly allocated entry, references the supplied old/new filesystems, stores the operation, and appends to the active change list. `mnt_tabdiff_next_change()` iterates over recorded changes with a libmount iterator and optionally returns old fs, new fs, and operation.

`mnt_diff_tables()` is the main algorithm. Empty-to-nonempty produces all mounts; nonempty-to-empty produces all unmounts. Otherwise, it scans the new table and uses `mnt_table_find_pair(old_tab, source, target)` to detect new mounts. Existing pairs with changed VFS or FS option strings become remounts. It then scans the old table for pairs missing in the new table. If a missing old entry has a corresponding new mount change with the same source and mount id, the change is converted to `MNT_TABDIFF_MOVE`; otherwise it records an unmount.

Limitations are intentional: matching is source/target-pair oriented and option changes are string comparisons of VFS and FS option strings when both sides exist. The test program prints a human-readable diff between two table files.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/tab_diff.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/tab_listmount.c -->
# File Research: sources/block-storage/util-linux/libmount/src/tab_listmount.c

This file integrates the Linux `listmount()`/`statmount()`-era APIs into `libmnt_table`. When `HAVE_STATMOUNT_API` is not available, all exported functions return `-ENOSYS`. When available, `struct libmnt_listmnt` tracks root mount id, namespace id, last id from the previous syscall, step size, an id buffer, enabled/done status, and traversal direction.

`table_init_listmount()` checks kernel support with `has_listmount()`, allocates `struct libmnt_listmnt` and its id buffer in one block, defaults the root id to `LSMT_ROOT`, preserves old settings when reallocating for a different step size, and reports `-ENOSYS` for unsupported kernels. Public setters configure root id, namespace id, and batch size.

`mnt_table_enable_listmount()` toggles on-demand fetching for `mnt_table_next_fs()` and returns the old status. `mnt_table_want_listmount()` is the private predicate used by `tab.c`. `mnt_table_reset_listmount()` clears fetch state after the table is reset and requires an empty table.

`lsmnt_to_table()` converts returned mount ids into placeholder kernel `libmnt_fs` entries, setting `MNT_FS_KERNEL`, unique mount id, and optional namespace id, then inserting them before or after a saved position depending on traversal direction. The detailed mount data is expected to be filled later via statmount fetching.

`mnt_table_next_lsmnt()` backs lazy iteration. It disables on-demand fetching during the syscall, avoids mixing forward and reverse ordering by fetching all remaining data when direction changes, calls `ul_listmount()`, marks done when fewer than a full batch is returned, inserts new ids, and restores the enabled state. `mnt_table_fetch_listmount()` eagerly resets the table and reads all mount ids, temporarily disabling on-demand statmount and listmount, then marks the listmount state done.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/tab_listmount.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/tab_parse.c -->
# File Research: sources/block-storage/util-linux/libmount/src/tab_parse.c

This file implements parsing for fstab/mtab-style files, `/proc/self/mountinfo`, libmount `utab`, and `/proc/swaps`, plus directory parsing for `*.fstab` fragments and merging utab userspace data into kernel mountinfo rows.

`struct libmnt_parser` stores the file stream, filename, line buffer, current line, and cached `/dev/root` resolution state. Numeric helpers parse signed 32-bit and unsigned 64-bit fields with separator validation. Parsing helpers skip separators, guess table format, detect comments, and attach parsed comments as intro, per-filesystem, or trailing comments when comment parsing is enabled.

Format parsers are field-specific. `mnt_parse_table_line()` parses fstab/mtab source, target, type, optional options, freq, and passno with `unmangle()`. `mnt_parse_mountinfo_line()` parses id, parent, major:minor devno, root, target, VFS options, optional fields up to `" - "`, fstype, possibly empty source, FS options, and then merges VFS plus FS options into `fs->optstr`; it marks entries as kernel and attached. `mnt_parse_utab_line()` accepts key/value variables such as `UNIQID`, `ID`, `SRC`, `TARGET`, `ROOT`, `BINDSRC`, `OPTS`, and `ATTRS`. `mnt_parse_swaps_line()` parses source, type, size, used size, priority, strips deleted suffixes from source, and sets fstype to `swap`.

`mnt_table_parse_next()` reads complete lines, handles missing final newlines, skips blanks/comments, guesses format on first data line, dispatches to the appropriate parser, and turns syntax errors into recoverable or fatal results through `tb->errcb`. `mnt_table_parse_stream()` loops over entries, applies parser filters and noautofs filtering, adds successful filesystems to the table, marks `/proc/mounts` or swaps flags, and runs mountinfo postprocessing. `kernel_fs_postparse()` records the source process TID from `/proc/<tid>/mountinfo` paths and replaces `/dev/root` with a guessed real root device when possible.

File and directory APIs include `mnt_table_parse_file()`, `mnt_table_parse_dir()`, `mnt_new_table_from_file()`, and `mnt_new_table_from_dir()`. Directory parsing uses `scandirat()` when available, otherwise `scandir()`, filters regular or symlink entries ending in `.fstab`, sorts with `versionsort`, and opens files with `*at()` helpers.

Specialized parsers set formats and defaults: `mnt_table_parse_swaps()`, `mnt_table_parse_fstab()`, and `mnt_table_parse_mtab()`. `__mnt_table_parse_mountinfo()` reads mountinfo first, falls back to `/proc/mounts` for default paths on older systems, then reads utab if available and merges userspace options/attributes/bind sources into matching kernel rows. Matching prefers unique id, then classic id, then root/target/source. Parser callback APIs allow custom error handling and entry filtering; `mnt_table_enable_noautofs()` skips ignored autofs entries during parsing.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/tab_parse.c -->