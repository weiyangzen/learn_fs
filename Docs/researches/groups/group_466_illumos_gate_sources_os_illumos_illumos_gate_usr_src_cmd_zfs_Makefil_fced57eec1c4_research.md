# Group Research: group_466_illumos_gate_sources_os_illumos_illumos_gate_usr_src_cmd_zfs_Makefil_fced57eec1c4

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/Makefile -->
# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/Makefile

This makefile builds the illumos `zfs` command-line frontend.

Build targets and objects:
- Produces `zfs`.
- Compiles `zfs_main.o`, `zfs_iter.o`, and `zfs_project.o`.
- Builds message catalog fragments from the same source set and concatenates them into `zfs.po`.

Install behavior:
- Installs the real program under the standard command target from `Makefile.cmd`.
- Creates `/usr/sbin/zfs` as a symlink back to `/sbin/zfs`.
- Creates ZFS filesystem helper symlinks for `mount` and `umount` under both `/usr/lib/fs/zfs` and `/etc/fs/zfs`, all pointing back to `/sbin/zfs`. This matches `zfs_main.c`, where `argv[0]` selects normal `zfs` behavior or filesystem-specific mount/unmount behavior.

Dependencies:
- Links against ZFS and illumos support libraries: `libzfs_core`, `libzfs`, `libuutil`, `libumem`, `libnvpair`, `libsec`, `libidmap`, `libzutil`, and `libcmdutils`.
- `libcmdutils` is specifically noted for `list(9F)` functions used by project quota code.
- Includes common ZFS headers, kernel ZFS headers, and libzutil common headers.

Build configuration:
- Includes `Makefile.cmd`, `Makefile.cmd.64`, and `Makefile.ctf`.
- Uses GNU99 C mode.
- Defines `_REENTRANT`.
- Adds `DEBUG` for non-release builds.
- Enables parallel make with `.PARALLEL`.

Risk notes:
- The helper symlink layout is part of the runtime ABI for `/etc/fs/zfs/mount` and `/etc/fs/zfs/umount`; changing it affects legacy mount integration.
- Link library order matters because the frontend calls into libzfs, libzfs_core, libshare/idmap-facing code, nvlist helpers, and project quota support.
- The include paths intentionally mix userland and kernel ZFS headers; moving or narrowing them can break ioctl/property structure visibility.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_iter.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_iter.c

This file implements the private dataset iteration engine used by `zfs list`, `zfs get`, `zfs inherit`, `zfs upgrade`, key management, holds, and other subcommands.

Main API:
- `zfs_for_each(argc, argv, flags, types, sortcol, proplist, limit, callback, data)`: opens requested datasets, recursively gathers matching descendants when requested, stores handles in a sorted AVL tree, invokes the caller callback in sorted order, then closes all retained handles.
- `zfs_add_sort_column(sc, name, reverse)`: appends a native or user-property sort key.
- `zfs_free_sort_columns(sc)`: releases the sort list.
- `zfs_sort_only_by_name(sc)`: detects the simple `name`-only sort case.

Iteration behavior:
- With no dataset arguments, it iterates all roots via `zfs_iter_root()` and forces recursive traversal.
- With explicit arguments, it opens by dataset name or path depending on `ZFS_ITER_ARGS_CAN_BE_PATHS`.
- Recursive mode always permits filesystems as traversal roots; if snapshots or bookmarks are requested, volumes can also be traversal roots.
- Filesystems recurse through child filesystems.
- Snapshots are included when the requested type includes snapshots, or when `ZFS_ITER_PROP_LISTSNAPS` is active and the pool `listsnapshots` property is set.
- Bookmarks are included when the requested type includes bookmarks.
- `ZFS_ITER_DEPTH_LIMIT` bounds recursion by `cb_depth_limit`.
- `ZFS_ITER_SIMPLE` selects the simple snapshot iterator for fast name-only listing.

Sorting behavior:
- Dataset handles are retained in a libuutil AVL tree.
- Explicit sort columns can be native numeric properties, native string properties, `name`, or user properties.
- Invalid-for-row properties sort that row to the bottom.
- Reverse sorting is handled per column.
- If explicit columns tie or no columns are given, `zfs_compare()` sorts by dataset name with snapshots grouped under parents and snapshots ordered by `createtxg` when available.
- `zfs_compare()` temporarily truncates names at `@` while comparing parent names, then restores the delimiters before returning.

Property handling:
- When a property list is supplied, the iterator can prune handles down to only properties needed by the output list and sort columns.
- It always preserves `zoned` and `createtxg` when pruning, because other property paths and snapshot ordering depend on them.
- It expands property lists with received or literal formatting when `ZFS_ITER_RECVD_PROPS` or `ZFS_ITER_LITERAL_PROPS` is set.

State and ownership:
- Nodes own retained `zfs_handle_t *` values only after successful insertion into the AVL tree.
- Duplicate handles are closed immediately.
- The final robust AVL walk removes every node, closes each retained handle, and frees each node.
- `avl_pool` is a file-scope global initialized per `zfs_for_each()` call.

Risk notes:
- Callback callers must not access properties pruned out of the handle unless they supplied them in the property or sort lists.
- The snapshot inclusion rule depends both on command flags and the pool `listsnapshots` property, so list/get behavior can differ when types are omitted.
- The global `avl_pool` makes the helper unsuitable for concurrent independent invocations inside one process.
- The comparator mutates handle name buffers in place around `@`; correctness depends on restoring those bytes on every path.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_iter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_iter.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_iter.h

Small private header for the `zfs` command's dataset iteration helpers.

Exports:
- `zfs_sort_column_t`, a linked list node describing one sort key.
- `zfs_for_each()`, the central sorted dataset iteration wrapper.
- `zfs_add_sort_column()`, `zfs_free_sort_columns()`, and `zfs_sort_only_by_name()`.

Iteration flags:
- `ZFS_ITER_RECURSE`: recurse through descendants.
- `ZFS_ITER_ARGS_CAN_BE_PATHS`: resolve command arguments as paths as well as dataset names.
- `ZFS_ITER_PROP_LISTSNAPS`: include snapshots according to the pool `listsnapshots` property.
- `ZFS_ITER_DEPTH_LIMIT`: enforce the supplied maximum recursion depth.
- `ZFS_ITER_RECVD_PROPS`: retain/expand received property values.
- `ZFS_ITER_SIMPLE`: use simple snapshot iteration where supported.
- `ZFS_ITER_LITERAL_PROPS`: use literal/parsable property values.

Integration role:
- Included by `zfs_main.c` for list/get/set-like command walking.
- Implemented by `zfs_iter.c`.
- Uses libzfs types such as `zfs_prop_t`, `zfs_type_t`, `zprop_list_t`, and `zfs_iter_f`, supplied by included libzfs headers in the including translation unit.

Risk notes:
- Flag semantics are tightly coupled to `zfs_iter.c`; adding a flag requires updating recursion, property expansion, or open behavior there.
- `zfs_sort_column_t.sc_last` is used only on the head node to append efficiently; callers should treat the list as opaque.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_iter.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_main.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_main.c

This is the main implementation of the illumos `zfs` userland command. It owns the command table, command-line parsing, high-level user workflows, output formatting, mount helper behavior, and calls into libzfs/libzfs_core for the actual ZFS operations.

Global state and setup:
- Defines global `libzfs_handle_t *g_zfs`, shared with helper files through `zfs_util.h`.
- Maintains `mnttab_file`, command history text, and `log_history`.
- Initializes locale, text domain, libzfs, mount table access, error printing, and libzfs mount-table caching in `main()`.
- Saves command arguments for pool history logging and logs successful commands unless a subcommand already logged history itself.
- Supports `ZFS_ABORT` to abort on exit for leak/debug workflows.
- In DEBUG builds, configures libumem debug/logging defaults.

Command dispatch:
- `command_table` maps command names to implementations and usage IDs.
- Supported commands include dataset lifecycle (`create`, `destroy`, `snapshot`, `rollback`, `clone`, `promote`, `rename`, `bookmark`, `remap`), reporting/property commands (`list`, `get`, `set`, `inherit`, `upgrade`, `userspace`, `groupspace`, `projectspace`, `project`), data transfer (`send`, `receive`), sharing/mounting, delegation (`allow`, `unallow`), holds, encryption key commands, and channel programs.
- Aliases are handled in `main()`: `umount` maps to `unmount`, `recv` maps to `receive`, and `snap` maps to `snapshot`.
- If the command token contains `=`, `main()` treats the invocation as implicit `zfs set`.
- If invoked as filesystem helper program `mount` or `umount`, it routes to `manual_mount()` or `manual_unmount()` instead of normal subcommand parsing.

Common helpers:
- `usage()` prints full or command-specific usage and property/delegation help hints.
- `parseprop()` parses and de-duplicates `property=value` arguments into nvlists, modifying the input string in place.
- `parsepropname()` parses receive `-x` property exclusions.
- `parse_depth()` validates recursive depth options and enables recursive iteration flags.
- `safe_malloc()`, `safe_realloc()`, and `safe_strdup()` exit through `nomem()` on allocation failure.
- Progress helpers implement delayed terminal progress for long operations such as mount-all.
- `zfs_mount_and_share()` mounts and shares newly created filesystems when `canmount=on`.

Dataset creation and clone commands:
- `zfs_do_create()` creates filesystems or volumes, parses `-o`, `-V`, `-b`, `-s`, `-p`, dry-run, verbose, and parseable modes.
- Volume creation rounds `volsize` up to `volblocksize` and sets `reservation` or `refreservation` unless `-s` disables reservation.
- Dry-run validates properties against the target pool without creating the dataset.
- Parent creation uses `zfs_create_ancestors()` for `-p`.
- `zfs_do_clone()` opens a snapshot, optionally creates missing ancestors, calls `zfs_clone()`, then mounts/shares the clone.

Destroy, rollback, and snapshot commands:
- `zfs_do_destroy()` handles filesystem/volume destruction, snapshot ranges, bookmarks, recursive destruction, dependent clone checks, dry-run output, deferred snapshot destruction, and batched snapshot deletion through nvlists.
- Snapshot destruction supports snap specs and recursive filesystem traversal, calculates reclaimable space for verbose output, and can destroy dependent clones for `-R`.
- Bookmark destruction validates bookmark existence and uses `lzc_destroy_bookmarks()`.
- `zfs_do_rollback()` opens the target snapshot and parent dataset, checks for newer snapshots/bookmarks and clone dependents, and then calls `zfs_rollback()`.
- `zfs_do_snapshot()` builds an nvlist of snapshots, supports recursive snapshots, skips inconsistent descendants during recursive traversal, and creates all requested snapshots with one `zfs_snapshot_nvl()` call.

Property and listing commands:
- `zfs_do_get()` parses columns, sources, types, recursion/depth, scripted output, and literal output. It prints native properties, user properties, user/group/project quota pseudo-properties, written properties, and received values when requested.
- `zfs_do_set()` accepts one or more `property=value` arguments followed by one or more datasets, validates argument ordering, and calls `zfs_prop_set_list()` for each dataset.
- `zfs_do_inherit()` validates readonly/non-inheritable properties, supports `-S` received-value reversion, and optionally recurses while skipping invalid property/type combinations.
- `zfs_do_list()` parses output fields, types, sort keys, recursion/depth, scripted and literal output. It relies on `zfs_for_each()` for ordering and property expansion and prints aligned table output.
- `zfs_do_upgrade()` lists filesystem versions, reports older/newer datasets, or upgrades filesystem `version` properties after checking required pool SPA versions.

Userspace, groupspace, and projectspace reporting:
- `zfs_do_userspace()` implements the shared backend for `userspace`, `groupspace`, and `projectspace`.
- It gathers user/group/project used/quota and object used/quota records with `zfs_userspace()`.
- It can translate SMB SIDs to POSIX IDs, print numeric names, select output fields, filter entity types, and sort by requested fields.
- It stores rows in libuutil AVL/list structures, calculates output widths, and prints either aligned or scripted output.

Send and receive:
- `zfs_do_send()` supports incremental sends, replication, properties, parsable/verbose/dry-run output, large blocks, embedded data, compressed/raw streams, holds, backup mode, and resume-token sends.
- It refuses to write binary streams to a terminal unless dry-run mode is active.
- It has a special path for sending a filesystem or sending from a bookmark through `zfs_send_one()`, and otherwise uses `zfs_send()`.
- Extra verbose mode can dump send debug nvlists to stderr after redirecting stdout back to stderr.
- `zfs_do_receive()` parses property overrides/exclusions, prefix/tail target modes, holds skipping, dry-run, no-mount, resumable receives, force rollback, verbose mode, and abort-resumable mode.
- It refuses to read a stream from a terminal and calls `zfs_receive()` for normal receives.
- Abort-resumable mode destroys either the `%recv` temporary dataset or an inconsistent dataset with a receive resume token.

Delegated permissions:
- Defines the user-visible delegated permission names and maps them to `zfs_deleg_note_t` notes.
- `allow_usage()` prints allowed permissions and writable properties.
- The parser validates combinations of `-l`, `-d`, `-u`, `-g`, `-e`, `-c`, `-s`, and recursive unallow.
- `construct_fsacl_list()` builds encoded fsacl nvlists for users, groups, everyone, create-time permissions, and named permission sets.
- Permission display parses existing fsacl nvlists into filesystem, subject, and permission AVL/list structures, resolves user/group names where possible, and prints local, descendant, and local+descendant permissions.
- `zfs_do_allow()` and `zfs_do_unallow()` share `zfs_do_allow_unallow_impl()`, using `zfs_get_fsacl()` and `zfs_set_fsacl()`; recursive unallow walks child filesystems.

Holds:
- `zfs_do_hold()` and `zfs_do_release()` share hold/release parsing and call `zfs_hold()` or `zfs_release()` for each snapshot.
- Hold tags beginning with `.` are rejected as reserved for libzfs.
- `zfs_do_holds()` collects hold nvlists, supports recursive matching by snapshot short name, and prints name/tag/timestamp rows in aligned or scripted form.

Mount/share and unmount/unshare:
- `share_mount()` implements `zfs mount` and `zfs share`.
- `share_mount_one()` enforces zone restrictions, `mountpoint`, `sharenfs`, `sharesmb`, `canmount`, encryption key availability, and resumable receive consistency before mounting or sharing.
- Mount-all gathers all filesystems, sorts them by mountpoint through libzfs helpers, and can run mount operations in parallel; share-all avoids parallel libshare usage because libshare is not MT-safe.
- `zfs mount` with no arguments lists mounted ZFS filesystems from `/etc/mnttab`.
- `unshare_unmount()` implements `zfs unmount` and `zfs unshare`, including `-a` traversal through `/etc/mnttab`, reverse mountpoint ordering for unmount-all, legacy mount/share handling, and path-based unmount/unshare resolution.
- `manual_mount()` supports `/etc/fs/zfs/mount` only for datasets whose `mountpoint` is `legacy`; otherwise it tells the user to use ZFS properties.
- `manual_unmount()` accepts path-based unmounts and delegates to the shared path resolver.

Other commands:
- `zfs_do_rename()` supports normal renames, recursive snapshot renames, parent creation, and forced unmount during rename.
- `zfs_do_promote()` promotes clone filesystems/volumes.
- `zfs_do_diff()` validates snapshots, opens the dataset, ignores `SIGPIPE`, and calls `zfs_show_diffs()`.
- `zfs_do_remap()` calls `zfs_remap_indirects()` for a filesystem or volume.
- `zfs_do_bookmark()` validates bookmark syntax, supports relative `@snap` source names, and calls `lzc_bookmark()`.
- `zfs_do_channel_program()` reads a Lua channel program from a file or stdin, applies instruction/memory limits, passes remaining CLI arguments as an nvlist string array, executes sync or nosync channel programs, and prints JSON or nvlist-style output.
- `zfs_do_load_key()` and `zfs_do_unload_key()` share recursive/all-dataset key load/unload logic, counting attempted and failed encryption roots.
- `zfs_do_change_key()` optionally loads the current key, parses encryption properties, and calls `zfs_crypto_rewrap()`.
- `zfs_do_project()` parses project quota file-tree operations and delegates file handling to `zfs_project_handle()`.

Risk notes:
- This file is the administrative command surface for destructive operations; option validation, dry-run behavior, and dependent traversal are safety-critical.
- Several parsers intentionally mutate `argv` strings in place by inserting NUL delimiters; later code must not assume original argument text remains intact.
- Destroy and rollback depend on snapshot/bookmark ordering and clone detection to avoid unsafe partial deletion.
- Mount/share behavior depends on live `/etc/mnttab`, zone state, encryption key state, libshare initialization, and receive-resume state.
- Delegation encoding uses compact string keys in nvlists; mistakes in type/locality/name encoding can grant or revoke the wrong permissions.
- Userspace/projectspace output combines identity translation, sorting, and quota properties; changes can affect both human and scripted output.
- Send/receive paths intentionally guard terminal stdin/stdout because the streams are binary.
- History logging is suppressed manually by a few commands after they log per-pool history themselves; adding cross-pool mutations must account for this.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_project.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_project.c

This file implements the file-tree side of `zfs project`, using ZFS project quota ioctls to list, check, clear, or set project IDs and the project-inherit flag on files and directories.

Main API:
- `zfs_project_handle(name, zpc)`: validates the top-level target, fills an expected project ID when needed, handles the target itself, and optionally walks directory children.

Operation behavior:
- `ZFS_PROJECT_OP_LIST`: prints project ID, project inherit flag state, and path.
- `ZFS_PROJECT_OP_CHECK`: reports paths whose project ID or inherit flag does not match the expected state; `-0` mode prints NUL-terminated path names.
- `ZFS_PROJECT_OP_CLEAR`: clears `ZFS_PROJINHERIT_FL` and, unless `keep_projid` is set, resets the project ID to `ZFS_DEFAULT_PROJID`.
- `ZFS_PROJECT_OP_SET`: sets the expected project ID and optionally sets `ZFS_PROJINHERIT_FL`.

Validation:
- Top-level targets must `stat()` successfully and must be regular files or directories.
- `-d` and `-r` are rejected for non-directory targets.
- If set/check mode has no explicit expected project ID, the top-level target's current project ID is loaded through `ZFS_IOC_FSGETXATTR`.

Traversal:
- Uses illumos `list_t` as a queue of directory names for recursive traversal.
- `zfs_project_handle_dir()` opens a directory, handles each child with `zfs_project_handle_one()`, and enqueues subdirectories when recursive mode is active.
- After the top-level item is processed, `zpc_ignore_noent` is enabled so disappearing non-top children are ignored as directory traversal races.
- `zpc_dironly` prevents child traversal after the top directory itself is handled.

Ioctl behavior:
- Opens each file/directory read-only with `O_NOCTTY`.
- Reads `zfsxattr_t` via `ZFS_IOC_FSGETXATTR`.
- Writes modified `zfsxattr_t` via `ZFS_IOC_FSSETXATTR` for set/clear operations.

State and ownership:
- Queue entries are allocated with a flexible `zpi_name` tail and freed as they are removed.
- File descriptors are closed on every operation path after opening.

Risk notes:
- Path construction uses fixed `PATH_MAX` buffers; long names produce `ENAMETOOLONG`.
- Recursive traversal is race-tolerant for removed children but not a snapshot of the tree.
- The code uses `stat64()` after `readdir()` to identify subdirectories, so symlink and rename behavior follows normal `stat` semantics.
- Set/check default expected ID comes from the top-level target, which is important for recursive project-tree normalization.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_project.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_projectutil.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_projectutil.h

Private header shared by `zfs_main.c` and `zfs_project.c` for `zfs project` control flow.

Exports:
- `zfs_project_ops_t` operation enum:
  - `ZFS_PROJECT_OP_DEFAULT`
  - `ZFS_PROJECT_OP_LIST`
  - `ZFS_PROJECT_OP_CHECK`
  - `ZFS_PROJECT_OP_CLEAR`
  - `ZFS_PROJECT_OP_SET`
- `zfs_project_control_t`, carrying parsed command flags and expected project ID.
- `zfs_project_handle(const char *name, zfs_project_control_t *zpc)`.

Control fields:
- `zpc_expected_projid`: explicit or discovered project ID.
- `zpc_op`: selected operation.
- `zpc_dironly`: operate on the directory itself rather than children.
- `zpc_ignore_noent`: suppress races for disappeared child paths.
- `zpc_keep_projid`: clear inherit flag without resetting project ID.
- `zpc_newline`: select newline or NUL output for check mode.
- `zpc_recursive`: recurse into subdirectories.
- `zpc_set_flag`: set the project inherit flag during set mode.

Integration role:
- `zfs_main.c` parses CLI options into this structure.
- `zfs_project.c` consumes it while validating targets, traversing directories, and issuing project xattr ioctls.

Risk notes:
- The meaning of some fields is operation-specific; CLI validation in `zfs_do_project()` prevents unsupported combinations before this structure reaches `zfs_project.c`.
- `zpc_ignore_noent` is mutable traversal state, not just a parsed option.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_projectutil.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_util.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_util.h

Small private utility header for the `zfs` command.

Exports:
- `safe_malloc(size_t size)`: allocation helper that exits on failure.
- `nomem(void)`: fatal out-of-memory handler.
- `g_zfs`: process-global libzfs handle.

Integration role:
- `zfs_main.c` defines all three exported symbols.
- `zfs_iter.c` uses `safe_malloc()`, `nomem()`, and `g_zfs`.
- `zfs_project.c` uses `safe_malloc()`.

Risk notes:
- `g_zfs` makes these helper modules dependent on `zfs_main.c` initialization and unsuitable as independent library code.
- Allocation helpers terminate the process instead of returning errors; callers are written around that fatal behavior.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/Makefile -->
# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/Makefile

This makefile builds the illumos `zpool` command-line frontend.

Build targets and objects:
- Produces `zpool`.
- Compiles `zpool_main.o`, `zpool_vdev.o`, `zpool_iter.o`, and `zpool_util.o`.
- Derives source, catalog fragment, and clean-file lists from the object list.
- Builds `zpool.po` by concatenating per-object `.po` files.

Install behavior:
- Installs the real program under `/sbin` through the standard command makefile.
- Creates `/usr/sbin/zpool` as a symlink back to `/sbin/zpool`.

Dependencies:
- Links against `libzfs`, `libnvpair`, `libdevid`, `libefi`, `libdiskmgt`, `libuutil`, `libumem`, `libzutil`, `libm`, and `libzpool`.
- Includes common ZFS headers, kernel ZFS headers, and libzutil common headers.
- Includes `../stat/Makefile.stat`, indicating shared iostat/stat support with the `stat` command infrastructure.

Build configuration:
- Includes `Makefile.cmd`, `Makefile.cmd.64`, and `Makefile.ctf`.
- Uses GNU99 C mode.
- Defines `DEBUG` for non-release builds.

Risk notes:
- `zpool_iter.c` and pool/vdev command code depend on libuutil AVL/list support and nvlist layout from libzfs/libzpool.
- Link dependencies include disk, EFI, devid, and zpool internals; removing libraries can break subcommands outside this small file group.
- The `/usr/sbin` symlink is part of the expected administrative command path.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_iter.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_iter.c

This file implements private iteration helpers for the `zpool` command, covering sorted pool lists and recursive vdev traversal.

Pool list API:
- `pool_list_get(argc, argv, proplist, err)`: creates a `zpool_list_t`, opens requested pools or all pools, expands requested property lists, and stores handles in an AVL tree sorted by pool name.
- `pool_list_update(zlp)`: adds newly discovered pools only when the list was created without explicit arguments.
- `pool_list_iter(zlp, unavail, func, data)`: invokes a callback for each pool, optionally including unavailable pools.
- `pool_list_remove(zlp, zhp)`: removes and closes a pool handle from the list.
- `pool_list_free(zlp)`: robust-walks the AVL tree, closes all pool handles, frees nodes, and destroys pools.
- `pool_list_count(zlp)`: returns the number of tracked pools.
- `for_each_pool(...)`: high-level wrapper used by ordinary subcommands.

Pool gathering behavior:
- With no arguments, `zpool_iter()` is used to add every pool and `zl_findall` is set so future updates can discover new pools.
- With explicit arguments, each pool is opened by `zpool_open_canfail()`, and the list remains fixed.
- Duplicate pool names are rejected by AVL lookup; duplicate handles are closed.
- Property expansion uses `zpool_expand_proplist()` when the caller supplies a property list pointer.

Vdev traversal:
- `for_each_vdev(zhp, func, data)` obtains the pool config, extracts `ZPOOL_CONFIG_VDEV_TREE`, and recurses through vdev nvlists.
- The recursion descends through `spares`, `l2cache`, and `children` arrays.
- Hole vdevs marked with `ZPOOL_CONFIG_IS_HOLE` are skipped.
- The callback is invoked for every non-root vdev after its children have been processed.

State and ownership:
- `zpool_list_t` owns its AVL tree, AVL pool, and retained `zpool_handle_t *` values.
- `add_pool()` transfers ownership of a successfully inserted handle to the list; on failure it closes the handle.
- `pool_list_iter()` does not remove or close handles; cleanup is explicit through `pool_list_free()` or `pool_list_remove()`.

Risk notes:
- `pool_list_update()` only works for all-pool lists; explicit lists intentionally do not grow.
- `pool_list_iter()` caches `next_node` before invoking callbacks, allowing callbacks to remove the current pool safely.
- Vdev traversal assumes the pool config contains `ZPOOL_CONFIG_VDEV_TREE`; the code verifies lookup success after a non-NULL config.
- The vdev callback order is post-order, not pre-order, which matters for consumers that aggregate or mutate vdev state.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_iter.c -->