# Group Research: group_1415_openzfs_sources_cow_pools_openzfs_cmd_zfs_Makefile_am_sources_cow_p_f5f44687d3cf

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zfs/Makefile.am -->
# File Research: sources/cow-pools/openzfs/cmd/zfs/Makefile.am

This Automake fragment builds the `zfs` userspace CLI under `sbin_PROGRAMS` and adds it to `CPPCHECKTARGETS`.

The program source list is the command implementation set for this directory: `zfs_iter.c`, `zfs_iter.h`, `zfs_main.c`, `zfs_project.c`, `zfs_projectutil.h`, and `zfs_util.h`. The linkage model is direct against OpenZFS userspace libraries: `libzfs.la`, `libzfs_core.la`, `libnvpair.la`, and `$(LTLIBINTL)` for gettext internationalization.

Platform-specific linkage is minimal and explicit. When `BUILD_FREEBSD` is enabled, the CLI also links `-lgeom` and `-ljail`, matching the FreeBSD jail integration compiled in `zfs_main.c`.

Integration notes:
- This file is the build glue for the full `zfs` command, not a standalone module.
- It establishes that `zfs_iter.c` and `zfs_project.c` are part of the same binary as the large `zfs_main.c` command dispatcher.
- The dependency set confirms the command is mostly a thin policy, parsing, traversal, and display layer over `libzfs`, `libzfs_core`, and nvlist APIs.

Risks and maintenance notes:
- Any new command source added under `cmd/zfs` must be included here or in another Automake fragment to enter the binary.
- FreeBSD-only command paths in `zfs_main.c` depend on this conditional link stanza.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zfs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zfs/zfs_iter.c -->
# File Research: sources/cow-pools/openzfs/cmd/zfs/zfs_iter.c

`zfs_iter.c` implements the shared dataset traversal and sorting layer used by many `zfs` subcommands. Its public entry point, `zfs_for_each()`, accepts command-line dataset arguments, traversal flags, target ZFS types, optional sort columns, optional property lists, a depth limit, and a callback. It gathers matching handles into an AVL tree, sorts them, invokes the caller callback in stable order, and then closes all handles.

Core data structures:
- `zfs_node_t` stores a `zfs_handle_t *`, the active callback context, and an AVL node.
- `callback_data_t` stores the AVL tree, iterator flags, target types, sort columns, caller property list pointer, depth state, and a `cb_props_table` used to prune unneeded properties.
- `zfs_sort_column_t` is defined in the header and implemented here as a linked list with a tail pointer in `sc_last`.

Traversal behavior:
- `zfs_include_snapshots()` includes snapshots either when explicitly requested by type or when `ZFS_ITER_PROP_LISTSNAPS` is set and the pool `listsnapshots` property permits it.
- `zfs_callback()` adds matching filesystems, volumes, snapshots, or bookmarks to the AVL tree, expands/prunes requested properties, recurses into child filesystems, snapshots, and bookmarks according to flags and depth, and closes handles that were not retained in the tree.
- `zfs_for_each()` handles both implicit root traversal (`argc == 0`) and explicit arguments. With recursion enabled it broadens acceptable argument types so users can recurse from filesystems and, when appropriate, volumes.

Sorting behavior:
- `zfs_add_sort_column()` validates a built-in or user property name and appends it to the sort list.
- `zfs_free_sort_columns()` releases the linked sort list and any copied user property names.
- `zfs_compare()` is the fallback name comparator. It sorts datasets by base name, puts parent datasets before their snapshots, and orders snapshots by `createtxg` when available.
- `zfs_sort()` applies requested sort columns first. It supports user properties, string properties, and numeric properties; invalid properties for a row sort that row below valid rows. Equal rows fall back to `zfs_compare()`.

Fast-list optimization:
- `zfs_sort_only_by_fast()` and `zfs_list_only_by_fast()` return true only when requested sort/list properties can be populated from fast dataset stats: `name`, `guid`, `createtxg`, `numclones`, `inconsistent`, `redacted`, and `origin`.
- `zfs_main.c` uses these helpers to set `ZFS_ITER_SIMPLE` for `zfs list` when no slow property expansion is required.

Dependencies and integration:
- Depends on `libzfs` handle iteration APIs such as `zfs_iter_root()`, `zfs_iter_filesystems_v2()`, `zfs_iter_snapshots_v2()`, and `zfs_iter_bookmarks_v2()`.
- Uses AVL utilities from the OpenZFS userspace support environment.
- Uses `safe_malloc()` and global `g_zfs` from `zfs_util.h`/`zfs_main.c`.

Risks and maintenance notes:
- The iterator owns retained handles after insertion and closes them during AVL destruction; callers must not close handles passed to their callback unless explicitly documented elsewhere.
- Property pruning is an important performance and correctness contract: callers that pass a proplist must ensure later callbacks access only retained properties plus required implicit properties.
- Sort comparisons temporarily modify names by replacing `@` with NUL and restoring it; this assumes `zfs_get_name()` storage is writable in this context.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zfs/zfs_iter.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zfs/zfs_iter.h -->
# File Research: sources/cow-pools/openzfs/cmd/zfs/zfs_iter.h

`zfs_iter.h` declares the shared iteration and sorting interface for the `zfs` command binary.

Primary exported type:
- `zfs_sort_column_t` is a linked-list node describing one sort key. It stores the built-in property enum, optional user property string, reverse-sort flag, next pointer, and a tail pointer used for append efficiency.

Exported functions:
- `zfs_for_each()` is the generic traversal API used by subcommands that operate over datasets, snapshots, volumes, and bookmarks.
- `zfs_add_sort_column()` parses and appends one sort column.
- `zfs_free_sort_columns()` releases sort column state.
- `zfs_sort_only_by_fast()` and `zfs_list_only_by_fast()` let callers detect whether list/sort operations can use fast dataset stats without full property expansion.

Integration notes:
- This header is included by `zfs_main.c` for list/get/set/inherit/upgrade/userspace/holds/key operations and by `zfs_iter.c` for its own implementation.
- It depends on OpenZFS public types such as `zfs_prop_t`, `zfs_type_t`, `zprop_list_t`, `zfs_iter_f`, and `boolean_t`, supplied through the broader `zfs` command include chain.

Risks and maintenance notes:
- The header exposes only traversal primitives, not the internal AVL/node state, which keeps callers decoupled from sorting internals.
- Adding new fast-list properties requires updating both declarations’ implementation in `zfs_iter.c`, and callers such as `zfs_do_list()` will then automatically benefit.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zfs/zfs_iter.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zfs/zfs_main.c -->
# File Research: sources/cow-pools/openzfs/cmd/zfs/zfs_main.c

`zfs_main.c` is the main implementation of the OpenZFS `zfs` userspace CLI. It owns command dispatch, usage text, option parsing, history logging, libzfs initialization, JSON output schema wrapping, and most subcommand-specific policy before calling into `libzfs`/`libzfs_core`.

Top-level structure:
- Global state includes `g_zfs`, `history_str`, `log_history`, and `current_command`.
- `command_table[]` maps subcommand names to `zfs_do_*` handlers and usage IDs.
- `get_usage()` centralizes localized usage strings for all subcommands.
- `main()` handles aliases (`umount`, `recv`, `snap`), `--help`, `--version`, `help`, libzfs setup, argv duplication, mount-table caching, command dispatch, implicit `property=value` as `zfs set`, history logging, and cleanup.

Utility and parsing support:
- `safe_malloc()`, `safe_realloc()`, and `safe_strdup()` abort through `nomem()` on allocation failure.
- `parseprop()` parses `property=value` into nvlists and rejects duplicate properties.
- `parsepropname()` parses property names for receive exclusions.
- `parse_depth()` validates `-d` recursion depth and sets recursive depth flags.
- Progress helpers manage delayed terminal progress output for long operations.
- `zfs_json_schema()` wraps JSON output with `output_version` metadata; list/get/mount/version/channel-program use JSON support.

Dataset creation and lifecycle commands:
- `zfs_do_clone()` parses `-o`, repeated `-p`, and `-u`; optionally creates ancestors and mounts/shares the clone after `zfs_clone()`.
- `zfs_do_create()` handles filesystems and volumes, dry-run/verbose/parseable modes, parent creation, volume blocksize/reservation calculation, property validation, creation, and mount/share.
- `calculate_volblocksize()` and `default_volblocksize()` derive better default zvol block sizes from pool allocation width, especially for dRAID/RAIDZ.
- `zfs_do_destroy()` supports filesystem/volume destruction, snapshot destruction by snapspec/ranges, bookmark destruction, dry-run/verbose output, recursive and clone-aware modes, deferred snapshot destruction, clone dependency checks, and batched snapshot deletion.
- `zfs_do_snapshot()` builds an nvlist of snapshot names, supports recursive snapshot creation, skips inconsistent datasets on recursive traversal, and calls `zfs_snapshot_nvl()`.
- `zfs_do_rollback()` validates younger snapshots/bookmarks and clone dependents before calling `zfs_rollback()`.
- `zfs_do_rename()`, `zfs_do_promote()`, `zfs_do_redact()`, and `zfs_do_bookmark()` implement rename, clone promotion, redaction bookmark creation, and bookmark creation/copying.

Property and listing commands:
- `zfs_do_get()` parses columns, sources, types, recursion, JSON, and literal output, expands proplists, and uses `zfs_for_each()` with `get_callback()`.
- `get_callback()` collects native, received, user, userquota, and written properties into table rows or JSON.
- `zfs_do_set()` enforces `property=value ... dataset ...` ordering and applies properties through `zfs_prop_set_list_flags()`.
- `zfs_do_inherit()` validates inherited/reverted properties and applies direct or recursive inheritance.
- `zfs_do_list()` parses property columns, sort columns, recursion/depth, dataset types, JSON, and scripted/parseable modes; it uses `zfs_list_only_by_fast()` and `zfs_sort_only_by_fast()` to select simple iteration when possible.
- `collect_dataset()` renders table rows or JSON per dataset, including user properties and special quota/written properties.
- `zfs_do_upgrade()` lists old/new filesystem versions or upgrades selected/all filesystems while tracking success/failure counts.

Quota and identity-space commands:
- `zfs_do_userspace()` implements `userspace`, `groupspace`, and `projectspace`. It queries user/group/project quota properties, optionally translates SMB SIDs, sorts rows through an AVL, and prints configurable fields.
- Helper functions map fields/types, compare quota rows, format human/parseable sizes, and combine used/quota/object-used/object-quota records per identity.

Send/receive and replication:
- `zfs_do_send()` implements incremental, recursive, saved, resumed, raw, compressed, redacted, property-preserving, backup, holds, skip-missing, and exclude-list send modes. It rejects terminal stdout for real streams, validates incompatible flag combinations, normalizes relative snapshot/bookmark source names, and dispatches to `zfs_send_one()`, `zfs_send()`, `zfs_send_resume()`, or `zfs_send_saved()`.
- `zfs_do_send_exclude()` filters recursive send datasets by excluded prefixes.
- `zfs_do_receive()` parses property overrides/exclusions and receive flags, handles aborting resumable receive state, rejects terminal stdin, and calls `zfs_receive()`.

Delegation, holds, and permissions:
- Delegation permission names and notes are declared locally to support `allow`/`unallow` display and updates.
- ACL parser/printer structs build a filesystem permission model from nested nvlists, separating permission sets/create-time permissions from user/group/everyone permissions.
- `zfs_do_allow_unallow_impl()` parses allow/unallow modes, opens the dataset, prints current permissions or constructs update nvlists, and supports recursive unallow.
- `zfs_do_hold()` and `zfs_do_release()` share `zfs_do_hold_rele_impl()` to add/release user holds, with recursive handling.
- `zfs_do_holds()` gathers and prints holds, including recursive matching by snapshot name.

Mount/share and unmount/unshare:
- `share_mount_one()` validates zones, legacy/none mountpoints, share properties, `canmount`, encrypted key availability, resumable receive state, redacted datasets, existing mount/share state, and then mounts or shares.
- `share_mount()` implements `zfs mount` and `zfs share`, including `-a`, recursive dataset sets, mount options, overlay/force flags, crypto-key loading mode, JSON mount listing, and parallel mounting up to a fixed thread count when safe.
- `get_all_datasets()` and related callbacks collect filesystem handles for bulk mount/share.
- `unshare_unmount()` implements `zfs unmount` and `zfs unshare`, including all-mounted traversal from `/proc/self/mounts`, deepest-first ordering via AVL, path-based unmount/unshare, legacy checks, and protocol-specific sharing.
- `unshare_unmount_path()` verifies path mount identity and delegates to libzfs unshare/unmount helpers.

Other operational commands:
- `zfs_do_diff()` validates snapshot arguments, ignores SIGPIPE, and calls `zfs_show_diffs()`.
- `zfs_do_channel_program()` reads a Lua channel program from a file or stdin, builds argv nvlists, runs sync or nosync channel programs with limits, and prints nvlist or JSON output.
- `zfs_do_load_key()`, `zfs_do_unload_key()`, and `zfs_do_change_key()` manage encryption keys, recursive encryption-root filtering, alternate keylocation validation, noop verification, and rewrap/inherit operations.
- `zfs_do_project()` parses project quota file-attribute operations and delegates per target to `zfs_project_handle()` in `zfs_project.c`.
- `zfs_do_rewrite()` recursively rewrites files through `ZFS_IOC_REWRITE`, with flags for BRT/snapshot/physical behavior, offset/length, verbosity, recursion, and cross-device restriction.
- `zfs_do_wait()` loops on selected dataset activity status, currently including `deleteq`.
- `zfs_do_version()` prints text or JSON version data.
- `zfs_do_help()` execs the relevant man page.
- Linux builds include `zfs_do_zone()`/`zfs_do_unzone()` for namespace attachment. FreeBSD builds include `zfs_do_jail()`/`zfs_do_unjail()` for jail attachment.

Dependencies and integration:
- Heavy dependencies include `libzfs`, `libzfs_core`, `libnvpair`, `libzutil`, ZFS property/delegation headers, mount-table APIs, pthreads, passwd/group lookup, ioctl definitions, and platform zone/jail APIs.
- `zfs_iter.c` supplies shared traversal and sorting for list/get/inherit/upgrade/set/holds/key workflows.
- `zfs_project.c` supplies the file-level project quota operation engine.
- Many command paths call into libzfs for actual pool/dataset mutation; this file primarily enforces CLI semantics, validation, output, batching, and user-facing error text.

Risks and maintenance notes:
- This is a very large command multiplexer; option parsing is localized but stateful and many handlers mutate copied argv strings using `strsep`, delimiter replacement, or `getopt`.
- Several operations are safety-sensitive: destroy batching, rollback dependency checks, send/receive stream validation, recursive mount/share, delegation ACL updates, encryption key handling, project quota ioctls, and rewrite ioctls.
- `main()` duplicates argv before dispatch because many handlers intentionally modify argument strings; future command handlers should preserve that convention.
- Bulk mount/share has concurrency and libshare constraints: mounts may run in parallel, but sharing and crypto prompt paths are serialized.
- JSON schemas are versioned per command output wrapper, but individual property payload shape is still command-specific.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zfs/zfs_main.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zfs/zfs_project.c -->
# File Research: sources/cow-pools/openzfs/cmd/zfs/zfs_project.c

`zfs_project.c` implements the file-tree worker used by `zfs project` in `zfs_main.c`. It lists, checks, clears, and sets project quota IDs and project-inherit flags on regular files and directories using ZFS-specific FS xattr ioctls.

Core data structure:
- `zfs_project_item_t` is a list node with a flexible trailing pathname buffer. It is used as a queue for iterative recursive directory traversal.

Main helpers:
- `zfs_project_item_alloc()` allocates and appends a queued directory path.
- `zfs_project_sanity_check()` stats the top-level target, restricts operations to regular files and directories, and rejects directory-only or recursive options on non-directories.
- `zfs_project_load_projid()` opens the top target and reads its current project ID with `ZFS_IOC_FSGETXATTR`; this supplies the expected project ID when the user did not pass `-p`.
- `zfs_project_handle_one()` opens one path, reads `zfsxattr_t`, and performs the selected operation:
  - list: prints project ID, inherit flag marker, and path.
  - check: reports paths whose project ID or inherit flag does not match expectations, optionally NUL-separated.
  - clear: clears `FS_XFLAG_PROJINHERIT` and optionally resets project ID to `ZFS_DEFAULT_PROJID`.
  - set: sets the expected project ID and optionally `FS_XFLAG_PROJINHERIT`.
  - mutations are applied with `ZFS_IOC_FSSETXATTR`.
- `zfs_project_handle_dir()` scans a directory, handles each regular file or directory child, and queues child directories when recursive mode is active.
- `zfs_project_handle()` is the exported entry point. It validates the target, derives the expected project ID when needed, handles the top path, and then breadth/depth iterates queued directories without recursive call stack growth.

Error behavior:
- Top-level missing/open/stat failures are reported.
- During directory traversal, `zpc_ignore_noent` is set so entries removed or renamed during traversal can be ignored.
- `ENOTSUP` during set emits a module/userspace version mismatch hint when the kernel version differs from `ZFS_META_ALIAS`.

Dependencies and integration:
- Uses `zfs_project_control_t` and operation constants from `zfs_projectutil.h`.
- Uses `ZFS_IOC_FSGETXATTR`, `ZFS_IOC_FSSETXATTR`, `zfsxattr_t`, `FS_XFLAG_PROJINHERIT`, and project ID constants from ZFS project quota headers.
- Uses `safe_malloc()` and `zfs_version_kernel()` from the broader `zfs` command support code.
- Called only by `zfs_do_project()` after CLI option validation.

Risks and maintenance notes:
- Recursive descent relies on `dirent.d_type == DT_DIR` for queuing subdirectories; filesystems that return unknown d_type may not recurse into those entries unless upstream behavior guarantees types here.
- Path construction checks against `PATH_MAX` before `asprintf()`, avoiding obvious overflow but still returning errors on very long names.
- Traversal is race-tolerant for disappearing children but not a transactional tree operation; concurrent renames can affect what is checked or updated.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zfs/zfs_project.c -->