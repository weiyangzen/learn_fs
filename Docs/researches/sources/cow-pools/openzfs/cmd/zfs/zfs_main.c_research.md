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
