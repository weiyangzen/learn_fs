# Group Research: group_1139_lvm2_sources_block_storage_lvm2_libdm_libdm_common_c_sources_block__4347d1d7d104

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/block-storage/lvm2`, which is included in subset A.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/libdm-common.c -->
# File Research: sources/block-storage/lvm2/libdm/libdm-common.c

## Purpose

`libdm-common.c` implements shared libdevmapper runtime support: library initialization, logging hooks, `dm_task` construction and setters, name/UUID mangling, device-node fallback operations, SELinux labeling, mountinfo/sysfs helpers, and udev synchronization cookies. It is the central glue between higher-level device-mapper task building and the local `/dev`, `/sys`, `/proc/self/mountinfo`, and udev environment.

## Main Responsibilities

- Initializes global libdm behavior from environment:
  - `DM_DISABLE_UDEV` disables udev reliance and forces library-managed nodes.
  - `DM_DEFAULT_NAME_MANGLING_MODE` selects `none`, `auto`, or `hex` name mangling.
- Provides default logging and compatibility wrappers between old `dm_log_fn` and newer `dm_log_with_errno_fn`.
- Creates and configures `struct dm_task` objects with default uid/gid/mode/read-ahead/event/cookie fields.
- Converts device names and UUIDs between unmangled strings and udev-safe `\xNN` escaped strings.
- Manages direct fallback `/dev/mapper` node operations:
  - add block node or symlink in alternate dev dirs,
  - remove node,
  - rename node,
  - get/set read-ahead through sysfs or block ioctls.
- Defers node operations in a stack and flushes them through `update_devs()`, allowing udev to complete first when available.
- Reads mountinfo and sysfs to map major/minor to names and detect holders or mounted filesystems.
- Implements udev cookie synchronization with System V semaphores when built with `UDEV_SYNC_SUPPORT`.
- Provides no-op udev-cookie compatibility paths when udev sync support is not compiled in.

## Key State

- `_dm_dir`: device-mapper directory, default `/dev/mapper`.
- `_sysfs_dir`: sysfs root, default `/sys/`.
- `_default_uuid_prefix`: UUID prefix used by libdm/LVM, default `LVM-`.
- `_verbose`: default logger verbosity gate.
- `_suspended_dev_counter`: process-local counter updated on suspend/resume.
- `_name_mangling_mode`: active string mangling policy.
- `_udev_disabled`: set by `DM_DISABLE_UDEV`.
- `_node_ops` and `_count_node_ops`: deferred node-operation queue.
- Under `UDEV_SYNC_SUPPORT`:
  - `_semaphore_supported`,
  - `_udev_running`,
  - `_sync_with_udev`,
  - `_udev_checking`.

## Important Functions

- `dm_lib_init()` reads environment and initializes udev and mangling defaults.
- `dm_log_init()`, `dm_log_with_errno_init()`, `dm_log_init_verbose()`, `dm_log_is_non_default()` manage logging callbacks.
- `dm_task_create()` allocates and initializes a `dm_task`, also checking libdm/kernel compatibility via `dm_check_version()`.
- `mangle_string()` escapes non-whitelisted characters as `\xNN`.
- `unmangle_string()` decodes `\xNN` sequences and optionally enforces strict whitelisted input.
- `check_multiple_mangled_string_allowed()` rejects double-mangled strings in auto mode.
- `_dm_task_set_name()`, `_dm_task_set_name_from_path()`, `dm_task_set_name()` set names, resolving paths back to `/dev/mapper` names for existing devices.
- `dm_task_set_newname()` and `dm_task_set_uuid()` apply validation/mangling before storing task fields.
- `dm_task_add_target()` appends `struct target` entries to a task.
- `dm_prepare_selinux_context()`, `dm_set_selinux_context()`, `selinux_release()` wrap SELinux file context behavior.
- `_add_dev_node()`, `_rm_dev_node()`, `_rename_dev_node()` perform direct node operations.
- `add_dev_node()`, `rm_dev_node()`, `rename_dev_node()`, `set_dev_node_read_ahead()` stack node operations instead of executing immediately.
- `update_devs()` flushes stacked node operations.
- `dm_set_dev_dir()`, `dm_set_sysfs_dir()`, `dm_set_uuid_prefix()` change process-local roots/prefixes.
- `dm_mountinfo_read()` parses `/proc/self/mountinfo` and invokes a callback per mount line.
- `dm_device_get_name()` resolves kernel or DM names from sysfs.
- `dm_device_has_holders()` and `dm_device_has_mounted_fs()` detect active users of a block device.
- `dm_mknodes()` runs the kernel `DM_DEVICE_MKNODES` task.
- `dm_driver_version()` queries the device-mapper driver version.
- `dm_task_set_cookie()`, `dm_udev_create_cookie()`, `dm_udev_complete()`, `dm_udev_wait()`, `dm_udev_wait_immediate()` implement udev synchronization.

## Behavior Details

Name mangling is intentionally conservative for udev integration, not for kernel DM itself. Allowed characters are alphanumeric plus `# + - . : = @ _`; other bytes become `\xNN`. Auto mode preserves already-mangled strings but rejects mixed mangled/unmangled content. Hex mode permits remangling all disallowed characters.

Path-based task names are treated as references to existing devices. `dm_task_set_name()` detects `/` and calls `_dm_task_set_name_from_path()`, which uses `stat()` and `_find_dm_name_of_device()` to translate an arbitrary block-device path back to a mapper name, then stores it without mangling.

Node operations are intentionally queued. The public node helpers push `NODE_ADD`, `NODE_DEL`, `NODE_RENAME`, and `NODE_READ_AHEAD` into `_node_ops`; `_stack_node_op()` coalesces conflicting operations. Deletes remove outstanding add/rename/read-ahead operations for the same device, adds can cancel a pending delete, and renames remove stale operations for the old name. `update_devs()` processes only operations not marked `rely_on_udev`.

Direct device-node creation handles several real-world races:
- Existing correct block node is accepted.
- Existing wrong node is unlinked.
- Dangling symlinks are removed.
- Alternative device directories may use symlinks to real `/dev/dm-N` nodes when cookies are supported.
- SELinux creation context is prepared before `mknod()` or `symlink()`.

Read-ahead prefers sysfs when major/minor are known and falls back to `BLKRAGET`/`BLKRASET`. Sysfs uses KiB while DM read-ahead uses sectors, so conversions multiply or round by two.

Mountinfo parsing unmangles octal escape sequences and contains a btrfs-specific correction path: if mountinfo reports `0:0` but includes `/dev/mapper/...`, it queries DM info for the true major/minor.

Udev synchronization uses a cookie whose high 16 bits must match `DM_COOKIE_MAGIC`. A System V semaphore is created at cookie allocation, incremented when assigned to a task, decremented by completion, waited to zero by `dm_udev_wait()`, then destroyed. If udev sync support is unavailable, cookie APIs degrade to zero-cookie success and `dm_udev_wait()` simply flushes stacked node operations.

## Dependencies and Interactions

- Uses `libdm/misc/dmlib.h` for memory, logging, string, list, and utility helpers.
- Uses `libdm/ioctl/libdm-targets.h` and `libdm/misc/dm-ioctl.h` for task and ioctl structures.
- Uses `libdm-common.h` for shared internal declarations.
- Calls lower-level ioctl/task helpers implemented elsewhere, including `dm_task_run()`, `dm_task_destroy()`, `dm_task_get_info()`, `dm_cookie_supported()`, and `dm_check_version()`.
- Optional SELinux code depends on `HAVE_SELINUX` and `HAVE_SELINUX_LABEL_H`.
- Optional udev sync depends on `UDEV_SYNC_SUPPORT` and `libudev`.

## Notable Edge Cases

- `dm_task_set_newname()` rejects empty names and names containing `/`.
- `mangle_string()` requires caller buffers at least `DM_NAME_LEN`, even when used for UUID-like strings.
- `_find_dm_name_of_device()` scans `_dm_dir`, so alternate dev directories affect path resolution.
- `dm_device_has_mounted_fs()` first checks mountinfo, then sysfs `/sys/fs/<fs>/<kernel_dev_name>`, with a TODO noting namespace implications.
- `_udev_wait()` supports an immediate/nonblocking mode by inspecting semaphore value before waiting.
- The non-udev build path still calls `update_devs()` in wait functions so direct fallback node operations are not lost.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/libdm-common.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/libdm-common.h -->
# File Research: sources/block-storage/lvm2/libdm/libdm-common.h

## Purpose

`libdm-common.h` is the internal shared header for libdevmapper common helpers. It exposes macros and helper declarations used across the libdm implementation, especially by ioctl/task code and dependency-tree code.

## Contents

- Includes public libdevmapper API definitions through `libdm/libdevmapper.h`.
- Defines `DM_DEFAULT_NAME_MANGLING_MODE_ENV_VAR_NAME`.
- Defines convenience macros:
  - `DEV_NAME(dmt)` returns `mangled_dev_name` when present, otherwise `dev_name`.
  - `DEV_UUID(dmt)` returns `mangled_uuid` when present, otherwise `uuid`.

## Declared Functions

- String mangling:
  - `mangle_string()`
  - `unmangle_string()`
  - `check_multiple_mangled_string_allowed()`
- Target construction:
  - `create_target()`
- Device-node queueing and direct-support APIs:
  - `add_dev_node()`
  - `rm_dev_node()`
  - `rename_dev_node()`
  - `get_dev_node_read_ahead()`
  - `set_dev_node_read_ahead()`
  - `update_devs()`
- SELinux cleanup:
  - `selinux_release()`
- Suspend counter helpers:
  - `inc_suspended()`
  - `dec_suspended()`
- Thin-pool and kernel-version helpers implemented outside this file group:
  - `parse_thin_pool_status()`
  - `get_uname_version()`

## Dependencies and Role

This header forms an internal contract between `libdm-common.c`, `libdm-deptree.c`, and other libdm source files. It is not just a public API declaration file; it exposes internal mechanics such as mangled task fields and queued device-node operations.

## Notable Details

`DEV_NAME()` and `DEV_UUID()` centralize the rule that ioctl calls should use the mangled value when one was generated. That keeps public callers working with their original strings while kernel/udev-facing paths receive the escaped variant when necessary.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/libdm-common.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/libdm-config.c -->
# File Research: sources/block-storage/lvm2/libdm/libdm-config.c

## Purpose

`libdm-config.c` implements libdm’s lightweight hierarchical configuration parser, writer, lookup API, cloning helpers, and cascade/flatten support. It parses LVM-style config syntax into `struct dm_config_tree`, `struct dm_config_node`, and `struct dm_config_value` objects allocated from a `dm_pool`.

## Main Responsibilities

- Create and destroy config trees backed by a memory pool.
- Parse text config into a tree:
  - sections delimited by `{` and `}`,
  - key/value assignments,
  - arrays,
  - integers,
  - floats,
  - quoted strings,
  - escaped double-quoted strings,
  - bare strings in value context,
  - comments starting with `#`.
- Write config trees back through line callbacks or output specs.
- Find nodes and typed values by slash-separated paths.
- Support cascaded config trees where earlier trees override later trees.
- Clone nodes and values into a target memory pool.
- Flatten cascaded trees into one merged tree.
- Remove nodes from a parent’s child list.

## Parser Structures

- `struct parser`
  - Tracks buffer bounds, current token, line number, memory pool, duplicate-node behavior, stop-after-section state, and section nesting.
- `struct config_output`
  - Holds output memory pool, line callback, optional node output spec, and baton.

## Token Model

The tokenizer emits:
- `TOK_INT`
- `TOK_FLOAT`
- `TOK_STRING`
- `TOK_STRING_ESCAPED`
- `TOK_STRING_BARE`
- `TOK_EQ`
- `TOK_SECTION_B`
- `TOK_SECTION_E`
- `TOK_ARRAY_B`
- `TOK_ARRAY_E`
- `TOK_IDENTIFIER`
- `TOK_COMMA`
- `TOK_EOF`

Token interpretation depends on context. After `=`, `[`, or `,`, numeric-looking tokens may become integers/floats and non-delimited tokens may become bare strings. Outside value context, similar text is treated as identifiers.

## Important Functions

- `dm_config_create()` allocates the config pool and root tree object.
- `dm_config_destroy()` destroys the backing pool.
- `dm_config_set_custom()` / `dm_config_get_custom()` store caller-owned context.
- `dm_config_insert_cascaded_tree()` and `dm_config_remove_cascaded_tree()` manage the cascade link.
- `dm_config_parse()` parses with duplicate-node checking.
- `dm_config_parse_without_dup_node_check()` disables duplicate checking.
- `dm_config_parse_only_section()` parses one named section and only top-level non-section nodes after it, intended for metadata scanning.
- `dm_config_from_string()` creates and parses a tree from a null-terminated string.
- `dm_config_write_one_node()`, `dm_config_write_node()`, `dm_config_write_one_node_out()`, `dm_config_write_node_out()` serialize nodes.
- `_section()`, `_value()`, `_type()`, `_get_token()`, `_eat_space()` implement the parser.
- `_find_or_make_node()` finds existing path segments or creates them when given a memory pool.
- `dm_config_find_node()`, `dm_config_find_int()`, `dm_config_find_int64()`, `dm_config_find_float()`, `dm_config_find_bool()`, `dm_config_find_str()`, `dm_config_find_str_allow_empty()` are node-rooted lookup helpers.
- `dm_config_tree_find_node()` and corresponding `dm_config_tree_find_*()` helpers search through cascaded trees.
- `dm_config_get_uint32()`, `dm_config_get_uint64()`, `dm_config_get_str()`, `dm_config_get_list()`, `dm_config_get_section()` provide typed success/fail APIs.
- `dm_config_maybe_section()` heuristically checks whether a text buffer may contain a balanced config section.
- `dm_config_clone_node_with_mem()` and `dm_config_clone_node()` deep-copy node/value structures.
- `dm_config_create_node()`, `dm_config_create_value()`, `dm_config_memory()` expose construction helpers.
- `dm_config_flatten()` merges cascaded trees into a new tree by enumerating lower-priority trees first and overriding paths from higher-priority trees.
- `dm_config_remove_node()` unlinks a child node from a parent.

## Serialization Behavior

`_write_config()` emits one line per node:
- Sections emit `key {`, recursively emit children, then `}`.
- Values emit `key=value`.
- Lists emit `[item, item]`.
- Formatting flags influence quoting, octal integer output, array formatting, and extra spaces.
- Keys containing `#`, `"`, or `!` are double-quoted and escaped.
- String values are double-quoted unless `DM_CONFIG_VALUE_FMT_STRING_NO_QUOTES` is set.

Output can go to a simple `dm_putline_fn` or a richer `dm_config_node_out_spec` with prefix, line, and suffix callbacks.

## Lookup and Cascading

Path lookup uses slash-separated segments. `_find_config_node()` searches within one node tree. `_find_first_config_node()` walks `cft->cascade`, returning the first matching node. Typed lookup functions return caller-provided fallback values when absent or mismatched. Unsupported string values are warned in `_find_config_str()` when appropriate.

`dm_config_flatten()` builds a new tree by walking cascade tail-to-head so earlier/high-priority trees override later/lower-priority trees at identical paths.

## Memory Ownership

All parsed nodes and values live in the tree’s `dm_pool`. Destroying the tree frees the entire parse result. String config values are allocated in the same object block as their `dm_config_value`; node keys similarly follow their `dm_config_node` allocation. Cloning into a supplied memory pool preserves this allocation model.

## Notable Edge Cases

- Duplicate config nodes are warned and ignored unless duplicate checking is disabled.
- Duplicate values overwrite `root->v` after warning.
- Empty arrays are represented by a special `DM_CFG_EMPTY_ARRAY` value.
- Invalid 32-bit-era `creation_time` overflow is repaired to `1527120000` with a warning, preserving compatibility with old metadata.
- `dm_config_maybe_section()` is only a heuristic based on balanced `{` and `}` counts.
- `dm_config_remove_node()` only unlinks; memory remains owned by the pool.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/libdm-config.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/libdm-deptree.c -->
# File Research: sources/block-storage/lvm2/libdm/libdm-deptree.c

## Purpose

`libdm-deptree.c` implements libdevmapper’s dependency-tree model and activation engine. It builds an in-memory graph of device-mapper devices and their dependencies, then uses it to create, preload, suspend, resume, rename, message, and remove mapped devices in dependency-safe order. It also builds target table lines for many DM target types.

## Supported Target Types

The file maps internal segment types to kernel target names for:
- `cache`
- `crypt`
- `error`
- `linear`
- `mirror`
- `snapshot`
- `snapshot-origin`
- `snapshot-merge`
- `striped`
- `zero`
- `writecache`
- `integrity`
- `thin-pool`
- `thin`
- `vdo`
- `raid` variants including raid0, raid1, raid10, raid4, raid5, and raid6 layouts.

Replicator targets are explicitly unsupported and return errors.

## Core Data Structures

- `struct seg_area`
  - Represents an underlying area/device plus offset for segment types that consume other block devices.
- `struct dm_thin_message` and `struct thin_message`
  - Represent queued thin-pool target messages and expected errno values.
- `struct load_segment`
  - Per-table-segment state. It stores the target type, size, device areas, and target-specific fields for snapshot, mirror, raid, cache, thin, VDO, writecache, integrity, and crypt targets.
- `struct load_properties`
  - Per-node activation/load state: read-only flag, major/minor, read-ahead, segment list, delayed resume flags, send-message flags, reload comparison flags, sibling reactivation flags, and related activation controls.
- `struct dm_tree_link`
  - Bidirectional edge wrapper for dependency lists.
- `struct dm_tree_node`
  - A graph node representing one device. It holds name, UUID, `dm_info`, dependency edges, udev flags, caller context, load properties, optional presuspend node, callback, and activation bookkeeping.
- `struct dm_tree`
  - Owns the memory pool, hash tables by dev_t and UUID, root pseudo-node, global activation options, cookie, debug buffer, and optional UUID suffix list.

## Tree and Node Management

- `dm_tree_create()` allocates a tree, root node, memory pool, and hash tables.
- `dm_tree_free()` destroys hash tables and pool.
- `dm_tree_set_cookie()` / `dm_tree_get_cookie()` set/read the shared udev cookie.
- `dm_tree_skip_lockfs()`, `dm_tree_use_no_flush_suspend()`, `dm_tree_retry_remove()` set activation flags.
- `_link_nodes()`, `_unlink_nodes()`, `_link_tree_nodes()` maintain bidirectional dependency edges and special root top/bottom-level links.
- `_create_dm_tree_node()` allocates a node and inserts it into dev and UUID hashes.
- `dm_tree_find_node()` and `dm_tree_find_node_by_uuid()` find existing nodes, with root special cases.
- `_find_dm_tree_node_by_uuid()` supports optional suffix matching and transition handling for missing default UUID prefixes.
- `dm_tree_next_child()` iterates either child dependencies or inverse parent edges.
- `dm_tree_node_num_children()` counts dependencies while treating root pseudo-links specially.
- Accessors expose node name, UUID, info, context, udev flags, read-ahead, callback, and size-change state.

## Discovery and Dependency Import

`_add_dev()` imports an existing kernel device into the tree:
- Calls `_deps()` for DM devices to run `DM_DEVICE_DEPS`.
- Creates a node if absent.
- Links it under the supplied parent.
- Recurses over dependency major/minor pairs.
- Marks implicit dependencies and applies restrictive udev flags to them.

`dm_tree_add_dev()` and `dm_tree_add_dev_with_udev_flags()` expose this import behavior.

New devices are added through `dm_tree_add_new_dev_with_udev_flags()` or `dm_tree_add_new_dev()`. These create a placeholder node when the UUID is absent from the tree, attach it to top and bottom root links until a table is supplied, store requested major/minor, read-only state, context, and udev flags, and optionally clear an inactive table.

## Activation and Deactivation

The activation engine is organized around dependency order and current kernel state.

Important helpers:
- `_info_by_dev()` refreshes `DM_DEVICE_INFO`.
- `_check_device_not_in_use()` detects open devices using open count, sysfs holders, and mounted filesystem checks.
- `_node_has_closed_parents()` prevents deactivation when parent nodes remain open.
- `_create_remove_task()` and `_deactivate_node()` build/run remove tasks.
- `_node_clear_table()` clears inactive tables and removes orphaned incomplete dependencies.
- `_rename_node()` runs a rename task.
- `_resume_node()` runs resume, sets read-ahead, handles udev cookie, and decrements the suspended counter if resuming a previously suspended node.
- `_suspend_node()` runs suspend, honors skip-lockfs and no-flush options, increments the suspended counter, and refreshes info.

Public traversal functions:
- `dm_tree_deactivate_children()` recursively removes children matching a UUID prefix.
- `dm_tree_suspend_children()` suspends children once parents are suspended and may send thin-pool messages instead of suspending lower nodes.
- `dm_tree_activate_children()` activates children in dependency order, handles renames, resolves peer rename conflicts, resumes inactive/suspended nodes, sends post-resume messages, and optionally reactivates siblings.
- `dm_tree_preload_children()` recursively creates missing nodes, loads inactive tables, conditionally resumes extended devices, validates messages for newly-created nodes, handles immediate dev-node synchronization, invokes preload callbacks, and reverts created devices on failure.
- `dm_tree_children_use_uuid()` checks whether any child subtree belongs to a UUID prefix.

## Message Handling

Thin-pool and VDO targets require runtime messages:
- `_thin_pool_get_status()` reads and parses thin-pool status.
- `_thin_pool_node_message()` formats `create_snap`, `create_thin`, `delete`, `set_transaction_id`, `reserve_metadata_snap`, and `release_metadata_snap`.
- `_thin_pool_node_send_messages()` validates transaction IDs, checks failed/read-only/needs-check status, sends queued messages, and verifies transaction-id updates.
- `_vdo_get_status()` reads and parses VDO status.
- `_vdo_node_send_messages()` toggles compression and deduplication/index state when runtime status differs from requested target parameters.
- `_node_send_messages()` dispatches by the last load segment’s type.

## Table Emission

Segment emission converts `load_segment` objects into DM table target parameters:
- `_emit_areas_line()` formats underlying devices and offsets, with special handling for raid null areas.
- `_mirror_emit_segment_line()` emits mirror log parameters, region size, sync/error flags, clustered log UUIDs, and areas. It uses kernel version to choose legacy/current `block_on_error` vs `handle_errors` behavior and userspace clustered logs.
- `_raid_emit_segment_line()` emits raid target lines, including sync flags, rebuild/writemostly bitmaps, recovery rates, writebehind, region size, raid10 copies, reshape parameters, and metadata/data pairs. It checks target version because target parameter ordering differed between raid target versions.
- `_cache_emit_segment_line()` emits metadata/data/origin devices, block size, cache feature mode, metadata2 flag, policy name, migration threshold, and integer policy settings.
- `_writecache_emit_segment_line()` emits writecache device mode, origin/cache devices, block size, and optional settings.
- `_integrity_emit_segment_line()` emits integrity target settings and marks task data secure.
- `_vdo_emit_segment_line()` emits VDO V2/V4 table lines, including data device path, data size, IO/cache/era settings, compression/deduplication controls, and thread/discard parameters. It may read an existing VDO table or metadata logical size to correct virtual size upward.
- `_thin_pool_emit_segment_line()` emits metadata/data devices, block size, low-water mark, and feature flags.
- `_thin_emit_segment_line()` emits pool device, device ID, and optional external origin.
- `_emit_segment_line()` dispatches by segment type and calls `dm_task_add_target()`.
- `_emit_segment()` retries with larger parameter buffers up to `MAX_TARGET_PARAMSIZE`.
- `_load_node()` builds and runs a reload task, suppresses identical reloads, detects table size changes, and applies delayed-resume rules.

## Target Construction APIs

The file provides public functions to add target segments to a node:
- Snapshot:
  - `dm_tree_node_add_snapshot_origin_target()`
  - `dm_tree_node_add_snapshot_target()`
  - `dm_tree_node_add_snapshot_merge_target()`
- Simple:
  - `dm_tree_node_add_error_target()`
  - `dm_tree_node_add_zero_target()`
  - `dm_tree_node_add_linear_target()`
  - `dm_tree_node_add_striped_target()`
  - `dm_tree_node_add_crypt_target()`
- Mirror:
  - `dm_tree_node_add_mirror_target()`
  - `dm_tree_node_add_mirror_target_log()`
- Raid:
  - `dm_tree_node_add_raid_target()`
  - `dm_tree_node_add_raid_target_with_params()`
  - `dm_tree_node_add_raid_target_with_params_v2()`
- Cache:
  - `dm_tree_node_add_cache_target()`
  - `dm_tree_node_add_cachevol_target()`
- Writecache:
  - `dm_tree_node_add_writecache_target()`
- Integrity:
  - `dm_tree_node_add_integrity_target()`
- Thin:
  - `dm_tree_node_add_thin_pool_target()`
  - `dm_tree_node_add_thin_pool_target_v1()`
  - `dm_tree_node_add_thin_pool_message()`
  - `dm_tree_node_set_thin_pool_discard()`
  - `dm_tree_node_set_thin_pool_error_if_no_space()`
  - `dm_tree_node_set_thin_pool_read_only()`
  - `dm_tree_node_add_thin_target()`
  - `dm_tree_node_set_thin_external_origin()`
- Areas and callbacks:
  - `dm_tree_node_add_target_area()`
  - `dm_tree_node_add_null_area()`
  - `dm_tree_node_set_callback()`
- VDO:
  - `dm_tree_node_add_vdo_target()`

## Dependency Linking Rules

Most target add functions find dependency nodes by UUID and link them to the new target node. For physical paths, `dm_tree_node_add_target_area()` uses `stat()` and imports the block device by major/minor. Some targets also adjust activation properties:
- Snapshot origins get activation priority and may trigger sibling reactivation.
- Snapshot merge nodes manipulate priorities so snapshot-merge and merging snapshot resume in the right order.
- Mirror logs may require immediate dev-node creation for clustered logs.
- Thin-pool metadata/data nodes clear `delay_resume_if_new`.
- Thin external origins may delay resume if newly-created.
- Integrity nodes set `skip_reload_params_compare`.
- VDO versions below 4 require runtime messages.

## Validation and Edge Cases

- `_uuid_prefix_matches()` handles default UUID-prefix transitions.
- `_children_suspended()` ignores nodes outside the requested UUID prefix and presuspend exceptions.
- Deactivation skips or errors on open devices depending on level, retry settings, holders, and mounted filesystems.
- Concurrent external resume during suspend is treated as an abort condition.
- Rename conflicts can be resolvable if the conflicting sibling is also being renamed.
- `_load_node()` distinguishes grown, shrunk, unchanged, and zero-length tables and has special delayed-resume handling for thin-pool-on-raid resize scenarios.
- Thin-pool messages require sequential transaction IDs.
- Thin device IDs are bounded by `DM_THIN_MAX_DEVICE_ID`.
- Cache feature flags are validated; cleaner policy forces writethrough mode.
- Cache migration threshold is forced to at least `data_block_size * 8`.
- Thin metadata can be cropped to `DM_THIN_MAX_METADATA_SIZE`.
- Raid supports null areas only for raid segment types.
- Backward-compatible symbol versions are provided under `GNU_SYMVER` for `dm_tree_node_size_changed()` and old cache target feature masking.

## Dependencies and Interactions

- Uses `libdm-common.h` for device-node, UUID-prefix, suspended-counter, thin-status, and kernel-version helpers.
- Uses `dm_task_*` ioctl wrappers extensively for info, deps, create, remove, rename, suspend, resume, reload, clear, status, target messages, and target versions.
- Uses config-tree cloning for cache policy settings.
- Uses udev cookies through `dm_task_set_cookie()` and `dm_udev_wait()`.
- Uses sysfs/mount checks indirectly through `dm_device_has_holders()` and `dm_device_has_mounted_fs()` from `libdm-common.c`.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/libdm-deptree.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/libdm-file.c -->
# File Research: sources/block-storage/lvm2/libdm/libdm-file.c

## Purpose

`libdm-file.c` contains small filesystem and lockfile utilities used by libdevmapper and device-mapper userspace tooling. It handles recursive directory creation, empty-directory detection, reliable `fclose()` error reporting, PID lockfile creation, and daemon-running checks through advisory locks.

## Main Functions

- `_is_dir()`
  - Uses `stat()` to verify an existing path is a directory.
  - Logs an error for non-directory paths.
- `_create_dir_recursive()`
  - Creates each missing parent directory in a path using `mkdir(..., 0777)`.
  - Accepts existing directories.
  - Fails on existing non-directories.
  - Suppresses noisy logging for `EROFS`.
- `dm_create_dir()`
  - Public wrapper that treats an empty string as success.
  - Returns success if the directory already exists.
  - Falls back to recursive creation.
- `dm_is_empty_dir()`
  - Opens a directory and returns true only if it contains no entries other than `.` and `..`.
- `dm_fclose()`
  - Combines prior stream error state from `ferror()` with the result of `fclose()`.
  - Clears `errno` when only a prior stream error existed but `fclose()` itself succeeded.
- `dm_create_lockfile()`
  - Opens/creates a lockfile.
  - Acquires a write lock with `fcntl(F_SETLK)`.
  - Retries transient `EACCES`/`EAGAIN` lock conflicts up to 20 times with 1 ms sleeps.
  - Truncates the file, writes the current PID, and sets `FD_CLOEXEC`.
  - Intentionally leaves the file descriptor open to keep the lock held.
  - Unlinks and closes on failure after lock acquisition.
- `dm_daemon_is_running()`
  - Opens an existing lockfile and uses `fcntl(F_GETLK)` to determine whether another process holds a write lock.

## Behavior Details

Recursive directory creation duplicates the input path, temporarily inserts null terminators at `/` boundaries, and attempts to create each component. It skips the empty prefix so absolute paths are handled correctly.

The lockfile API uses POSIX advisory locks rather than just PID-file contents. The PID is written for observability, but process liveness is inferred from the kernel lock state. `dm_create_lockfile()` deliberately leaks the locked fd on success; the lock is released by process exit or explicit descriptor close elsewhere.

## Dependencies

- Includes `libdm/misc/dmlib.h` for logging and memory helpers.
- Uses POSIX filesystem APIs:
  - `stat`
  - `mkdir`
  - `opendir`
  - `readdir`
  - `closedir`
  - `open`
  - `fcntl`
  - `ftruncate`
  - `write`
  - `close`
  - `unlink`
  - `usleep`

## Notable Edge Cases

- `dm_create_dir("")` returns success.
- `dm_is_empty_dir()` returns false when `opendir()` fails.
- `dm_fclose()` preserves the important distinction between buffered stream errors and close errors.
- `dm_create_lockfile()` treats `EINTR` during lock acquisition by retrying immediately.
- `dm_daemon_is_running()` returns false if the lockfile cannot be opened.

<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/libdm-file.c -->