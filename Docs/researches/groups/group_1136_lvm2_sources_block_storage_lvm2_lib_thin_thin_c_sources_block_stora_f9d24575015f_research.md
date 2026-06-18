# Group Research: group_1136_lvm2_sources_block_storage_lvm2_lib_thin_thin_c_sources_block_stora_f9d24575015f

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/block-storage/lvm2`, which is included in subset A. Each listed source was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/thin/thin.c -->
# File Research: sources/block-storage/lvm2/lib/thin/thin.c

## Purpose
Implements LVM2 segment-type support for device-mapper thin provisioning. It registers both `thin-pool` and `thin` segment types, imports/exports their text metadata, builds activation-time device-mapper table lines, probes kernel target feature support, and wires optional dmeventd monitoring for thin pools.

## Main Responsibilities
- `thin-pool` segment:
  - Stores pool metadata LV, pool data LV, transaction id, chunk size, discard behavior, zero-new-blocks behavior, crop-metadata state, and queued thin-pool messages.
  - Imports metadata keys such as `metadata`, `pool`, `transaction_id`, `chunk_size`, `discards`, `zero_new_blocks`, `crop_metadata`, and message blocks.
  - Exports the same state back to LVM text metadata.
  - Builds a `thin-pool` target line with low-water-mark, discard settings, no-space behavior, metadata cropping, and queued create/delete/set-transaction messages.
- `thin` segment:
  - Stores its pool LV, transaction id, device id, optional origin, optional external origin, and optional merge LV.
  - Exports/imports `thin_pool`, `transaction_id`, `device_id`, `external_origin`, `origin`, and `merge`.
  - Builds a `thin` target line pointing to the pool and device id, with special handling for merging thin snapshots and external origins.

## Key Functions
- `_thin_pool_text_import()` validates pool metadata/data LV references, chunk size bounds, discard mode, zeroing, crop metadata, and message blocks.
- `_thin_pool_text_export()` serializes pool configuration and validates message consistency before writing message blocks.
- `_thin_pool_add_target_line()` converts pool metadata into a dm tree node using `dm_tree_node_add_thin_pool_target_v1()`, applies discard/no-space options, and sends queued pool messages when requested by activation options.
- `_thin_text_import()` resolves pool/origin/external-origin/merge LVs and attaches the thin LV to its pool.
- `_thin_add_target_line()` emits the thin target and external-origin dependency when present.
- `_thin_target_present()` probes the `thin-pool` kernel target version, derives feature bits, and applies `global/thin_disabled_features`.
- `init_multiple_segtypes()` / `init_thin_segtypes()` register `thin-pool` and `thin`.

## Important Data Flow
Text metadata import attaches related LVs into `lv_segment`, then activation asks the segtype handler to produce dm-table nodes. Thin-pool activation also converts pending LVM metadata messages into dm-thin messages and finally sends a transaction-id update after all messages.

## Feature Gates
Kernel target feature detection controls:
- discard support
- external origin support
- non-power-of-two chunk sizes
- metadata resize
- error-if-no-space
- smaller external origin extension

Runtime configuration can mask detected features through `global/thin_disabled_features`.

## Edge Cases and Invariants
- Thin pool chunk size must be within `DM_THIN_MIN_DATA_BLOCK_SIZE` and `DM_THIN_MAX_DATA_BLOCK_SIZE`.
- Non-power-of-two chunk sizes require target support.
- Device ids above `DM_THIN_MAX_DEVICE_ID` are rejected.
- Thin-pool messages are only added when activation options allow message sending.
- External-origin LVs smaller than the thin LV require `THIN_FEATURE_EXTERNAL_ORIGIN_EXTEND`.
- Thin snapshot merge is represented by swapping device ids rather than emitting a distinct merge target.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/thin/thin.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/unknown/unknown.c -->
# File Research: sources/block-storage/lvm2/lib/unknown/unknown.c

## Purpose
Provides a fallback LVM2 segment type for metadata segment types unknown to the running binary. It preserves unrecognized segment metadata so it can be round-tripped instead of discarded.

## Main Responsibilities
- Import all config nodes except generic segment keys: `type`, `start_extent`, `tags`, and `extent_count`.
- Clone unknown config nodes into VG memory and store them in `seg->segtype_private`.
- Export the preserved config subtree unchanged with `out_config_node()`.
- Register a named segment type marked as unknown, virtual, and not zeroable.

## Key Functions
- `_unknown_text_import()` walks sibling config nodes, clones unknown fields, and chains them into a private list.
- `_unknown_text_export()` writes the saved config nodes back out.
- `init_unknown_segtype()` allocates a segment type with caller-provided name and flags `SEG_UNKNOWN | SEG_VIRTUAL | SEG_CANNOT_BE_ZEROED`.

## Edge Cases and Invariants
- Allocation failure during config-node cloning aborts import.
- The segment type name is duplicated and freed by `_unknown_destroy()`.
- This handler has no device-mapper activation behavior; it is metadata-preservation support.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/unknown/unknown.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/vdo/vdo.c -->
# File Research: sources/block-storage/lvm2/lib/vdo/vdo.c

## Purpose
Implements LVM2 segment-type support for VDO. It registers `vdo` logical volumes layered on VDO pools and `vdo-pool` segments backed by data LVs, handles VDO metadata import/export, device-mapper target construction, kernel feature probing, and optional dmeventd monitoring.

## Main Responsibilities
- `vdo` segment:
  - Represents a linear mapping onto a VDO pool after the pool header.
  - Imports/exports `vdo_pool` and `vdo_offset`.
  - Emits a linear/striped target area pointing at the backing VDO pool device.
- `vdo-pool` segment:
  - Stores data LV, header size, virtual extents, and full `dm_vdo_target_params`.
  - Imports/exports compression, deduplication, metadata hints, IO size, block-map/cache/index/slab sizing, thread counts, discard size, sparse index, and write policy.
  - Emits the actual dm-vdo target and uses the VDO virtual size rather than physical LV size.

## Key Functions
- `_vdo_text_import()` attaches the VDO LV to its VDO pool LV and marks the LV as `LV_VDO`.
- `_vdo_add_target_line()` builds a linear mapping onto the VDO pool, offset by header size plus logical extent offset.
- `_vdo_pool_text_import()` reads the data LV and VDO parameters, attaches the data LV as `LV_VDO_POOL_DATA`, marks the pool, and hides the data LV.
- `_vdo_pool_text_export()` serializes all VDO pool parameters.
- `_vdo_check()` computes incremental pool-size constraint deltas and calls `check_vdo_constraints()`.
- `_vdo_pool_add_target_line()` builds the dm-vdo target with target format version 2 or 4 depending on feature support.
- `_vdo_target_present()` requires a sufficiently new VDO target, checks linear/striped target availability, derives feature bits, and applies `global/vdo_disabled_features`.
- `init_vdo_segtypes()` registers both `vdo` and `vdo-pool`.

## Feature Gates
- Minimum VDO target version is effectively 6.2.x.
- `VDO_FEATURE_ONLINE_RENAME` requires target version 6.2.3.
- `VDO_FEATURE_VERSION4` requires target version 8.2.0.
- Feature bits can be disabled by `global/vdo_disabled_features`.

## Edge Cases and Invariants
- `minimum_io_size` is stored in target params as sectors but serialized as bytes.
- VDO pool target construction skips constraint checking during critical sections.
- VDO requires the VDO target and linear/striped mapping support.
- The pool handler may gain `SEG_MONITORED` if a dmeventd VDO DSO is configured.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/vdo/vdo.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/writecache/writecache.c -->
# File Research: sources/block-storage/lvm2/lib/writecache/writecache.c

## Purpose
Implements LVM2 segment-type support for dm-writecache. It imports/exports writecache metadata, probes target support, records optional writecache settings, and emits writecache target lines during activation.

## Main Responsibilities
- Import an origin LV, fast writecache LV, writecache block size, and optional writecache tuning settings.
- Export only configured optional settings.
- Track kernel support for `cleaner` and `max_age`.
- Add `writecache` dm target using origin and cache-device UUIDs.
- Register the `writecache` segment type.

## Key Functions
- `_writecache_text_import()` reads `origin`, `writecache`, `writecache_block_size`, and settings such as watermarks, writeback jobs, autocommit values, FUA/nofua, cleaner, max age, metadata-only, pause-writeback, and one arbitrary key/value setting.
- `_writecache_text_export()` serializes the base relationship and all settings whose `_set` flags are present.
- `_target_present()` probes `dm-writecache` target version and records whether kernel minor version supports cleaner/max-age.
- `writecache_cleaner_supported()` exposes cleaner support to the rest of LVM.
- `_writecache_add_target_line()` validates the segment, suppresses unsupported settings on older kernels, checks whether the cache LV is on persistent memory, and calls `dm_tree_node_add_writecache_target()`.
- `init_writecache_segtypes()` registers `SEG_TYPE_NAME_WRITECACHE`.

## Edge Cases and Invariants
- Both origin and cache LVs must resolve during metadata import.
- The writecache LV is added to `segs_using_this_lv`.
- Unsupported `cleaner` and `max_age` settings are cleared with warnings rather than failing activation.
- Device UUID layers are fixed as `"real"` for origin and `"cvol"` for cache volume.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/writecache/writecache.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/zero/zero.c -->
# File Research: sources/block-storage/lvm2/lib/zero/zero.c

## Purpose
Implements the LVM2 `zero` virtual segment type, backed by the device-mapper `zero` target.

## Main Responsibilities
- Merge adjacent zero segments by increasing length and area length.
- Emit a dm-zero target line during activation.
- Probe for zero target availability.
- Report the needed kernel module name.
- Register a virtual, splittable, non-zeroable segment type.

## Key Functions
- `_zero_merge_segments()` combines two zero segments.
- `_zero_add_target_line()` calls `dm_tree_node_add_zero_target()`.
- `_zero_target_present()` caches `target_present(cmd, TARGET_NAME_ZERO, 1)`.
- `_zero_modules_needed()` adds `MODULE_NAME_ZERO`.
- `init_zero_segtype()` registers `SEG_TYPE_NAME_ZERO` with `SEG_CAN_SPLIT | SEG_VIRTUAL | SEG_CANNOT_BE_ZEROED`.

## Edge Cases and Invariants
- Target presence returns false when activation support is disabled.
- The cached target probe is process-local and avoids repeated target checks.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/zero/zero.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/Makefile.in -->
# File Research: sources/block-storage/lvm2/libdm/Makefile.in

## Purpose
Builds and installs the `libdevmapper` library and its exported header/pkg-config metadata.

## Main Responsibilities
- Defines libdm source files, including datastruct, config, deptree, stats, regex, vdo parser/status/stats, pool allocator, and interface-specific ioctl code.
- Builds static and/or shared `libdevmapper` based on configure substitutions.
- Creates compatibility symlinks for shared library names.
- Runs a symbol-version sanity check for `dm_stats_create_region`.
- Installs headers, shared library, static library, and `devmapper.pc`.

## Key Build Variables
- `SUBDIRS=dm-tools`
- `SOURCES` lists all libdm compilation units.
- `LIB_STATIC`, `LIB_SHARED`, `LIB_VERSION`, and `TARGETS` are gated by `@STATIC_LINK@` and `@SHARED_LINK@`.
- `EXPORTED_HEADER=libdevmapper.h`
- `EXPORTED_FN_PREFIX=dm`

## Install Behavior
- `install` expands to dynamic/static/pkg-config install targets as configured, plus header install.
- `install_ioctl` installs the shared library when shared builds are enabled and static library when static builds are enabled.
- `DISTCLEAN_TARGETS` includes generated `libdevmapper.pc` and `make.tmpl`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/Makefile.in -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/datastruct/bitset.c -->
# File Research: sources/block-storage/lvm2/libdm/datastruct/bitset.c

## Purpose
Implements libdm bitset allocation, boolean operations, bit iteration, and parsing of textual CPU/list-style ranges into bitsets.

## Main Responsibilities
- Allocate bitsets either from a dm memory pool or heap.
- Store bit count in `bs[0]`; following words store bit values.
- Compare, intersect, and union bitsets.
- Iterate set bits forward or backward.
- Parse comma/range list syntax into a bitset.

## Key Functions
- `dm_bitset_create()` allocates enough integer words for `num_bits` plus metadata.
- `dm_bitset_destroy()` frees heap-allocated bitsets.
- `dm_bitset_equal()`, `dm_bit_and()`, and `dm_bit_union()` operate wordwise.
- `dm_bit_get_next()` and `dm_bit_get_prev()` scan set bits using `ffs()` and `clz()`.
- `dm_bitset_parse_list()` parses strings like `1,3-5`, determines required bit count on a first pass, then allocates and fills the mask on a second pass.
- `dm_bitset_parse_list_v1_02_129()` preserves ABI compatibility for older callers without `min_num_bits`.

## Edge Cases and Invariants
- Whitespace is allowed around values but not between digits.
- Empty fields are skipped.
- Descending ranges and dangling `-` are rejected.
- On parse failure, allocated masks are freed from the correct allocator.
- `min_num_bits` can force a larger empty tail even when parsed values are smaller.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/datastruct/bitset.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/datastruct/hash.c -->
# File Research: sources/block-storage/lvm2/libdm/datastruct/hash.c

## Purpose
Implements libdm’s general-purpose hash table with binary-key and string-key APIs, optional duplicate-key entries, iteration, wipe, and lookup-by-key/value helpers.

## Main Responsibilities
- Allocate a power-of-two slot array sized from a hint.
- Hash keys using an adapted Jenkins-style hash.
- Store keys inline in `dm_hash_node`.
- Resolve collisions with singly linked chains.
- Support replacement insert for unique keys and prepend insert for duplicate-key mode.

## Key Functions
- `dm_hash_create()` rounds the size hint up to a power of two, allocates table metadata and slots.
- `_hash()` hashes input bytes two at a time where supported.
- `_findh()` searches a chain by hash, key length, and key bytes while updating debug counters.
- `dm_hash_lookup_binary()`, `dm_hash_insert_binary()`, and `dm_hash_remove_binary()` provide raw binary-key operations.
- `dm_hash_lookup()`, `dm_hash_insert()`, and `dm_hash_remove()` wrap string keys including the terminating NUL.
- `dm_hash_insert_allow_multiple()` allows repeated keys with potentially distinct values.
- `dm_hash_lookup_with_val()` and `dm_hash_remove_with_val()` find duplicate-key entries by matching value bytes.
- `dm_hash_lookup_with_count()` returns the first matching value and counts all entries with the same key.
- `dm_hash_iter()`, `dm_hash_get_first()`, and `dm_hash_get_next()` provide table iteration.
- `dm_hash_wipe()` frees nodes and resets slots/counters without destroying the table itself.

## Edge Cases and Invariants
- Normal insert replaces data for an existing key; duplicate insert never searches first.
- Duplicate-key value matching requires stored `data_len` and non-null data.
- Table size is fixed after creation; there is no resize path.
- `dm_hash_destroy()` frees nodes, slots, and table but not user data.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/datastruct/hash.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/datastruct/list.c -->
# File Research: sources/block-storage/lvm2/libdm/datastruct/list.c

## Purpose
Implements libdm’s intrusive circular doubly linked list primitive.

## Main Responsibilities
- Initialize list heads as self-referential sentinels.
- Add elements at tail or head.
- Delete and move elements.
- Query list boundaries and emptiness.
- Return first/last/previous/next elements.
- Count list size by walking.
- Splice one list into another.

## Key Functions
- `dm_list_init()` sets `head->n` and `head->p` to `head`.
- `dm_list_add()` inserts before the head, effectively appending.
- `dm_list_add_h()` inserts after the head, effectively prepending.
- `dm_list_del()` unlinks an element without clearing its own pointers.
- `dm_list_move()` deletes then appends an element elsewhere.
- `dm_list_splice()` appends all elements from `head1` to `head` and reinitializes `head1`.

## Edge Cases and Invariants
- Operations assert initialized list heads where needed.
- Empty lists are represented by `head->n == head`.
- `dm_list_first()` and `dm_list_last()` return `NULL` for empty lists.
- `dm_list_splice()` is a no-op for an empty source list.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/datastruct/list.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/dm-tools/Makefile.in -->
# File Research: sources/block-storage/lvm2/libdm/dm-tools/Makefile.in

## Purpose
Builds and installs device-mapper command-line tools, primarily `dmsetup`, `dmvdostats` via symlink, and optionally `dmfilemapd`.

## Main Responsibilities
- Always builds under the `device-mapper` aggregate target.
- Builds `dmsetup` from `dmsetup.o` and `dmvdostats.o`.
- Optionally includes `dmfilemapd.c` and builds `dmfilemapd` when `@BUILD_DMFILEMAPD@` is enabled.
- Supports shared and static tool variants depending on configure substitutions.
- Installs tool binaries and compatibility symlinks.

## Key Build Behavior
- Shared builds produce `dmsetup` and optionally `dmfilemapd`.
- Static builds produce `dmsetup.static` and optionally `dmfilemapd.static`.
- `dmsetup` install creates `dmstats` and `dmvdostats` symlinks.
- Static install creates `dmstats.static` and `dmvdostats.static` symlinks.
- Tool linking uses `-L$(interfacebuilddir) -ldevmapper`.

## Edge Cases and Invariants
- `install` depends on `install_device-mapper` and `install_dmfilemapd`; `install_dmfilemapd` only has concrete prerequisites when dmfilemapd support is enabled.
- `CLEAN_TARGETS` includes all possible dynamic/static tool outputs.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/dm-tools/Makefile.in -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/libdm/dm-tools/dmfilemapd.c -->
# File Research: sources/block-storage/lvm2/libdm/dm-tools/dmfilemapd.c

## Purpose
Implements `dmfilemapd`, a small daemon that keeps dm-stats filemap regions synchronized with a changing file. It monitors a file by path or inode, reacts to inotify changes, updates dm-stats regions from the file descriptor, and exits when the monitored group disappears or the file no longer has relevant regions.

## Main Responsibilities
- Parse daemon arguments: file descriptor, stats group id, absolute path, follow mode, optional foreground flag, and optional log verbosity.
- Set libdm logging behavior for foreground/background operation.
- Monitor file modifications/deletions through inotify.
- Track allocated block count with `fstat()` and use it as a heuristic for deciding when file extents may have changed.
- Recompute stats regions with `dm_stats_update_regions_from_fd()`.
- In inode-follow mode, detect unlink-and-final-close shutdown conditions.
- Daemonize safely while preserving the monitored file descriptor.

## Key Functions
- `_parse_args()` validates and stores runtime configuration in `struct filemap_monitor`.
- `_setup_logging()` installs dmfilemapd-specific logging callbacks.
- `_is_open()` and `_is_open_in_pid()` scan `/proc/*/fd` for deleted open-file references, used only as a heuristic for inode-follow shutdown.
- `_filemap_monitor_set_notify()` creates a nonblocking inotify instance and watches the path for `IN_MODIFY` and `IN_DELETE_SELF`.
- `_filemap_monitor_get_events()` drains inotify events, marks deletion, requests extent checks on modification, and reopens/re-watches path-followed files.
- `_filemap_monitor_check_file_unlinked()` determines whether the original file descriptor still matches the path or has become deleted/anonymous.
- `_daemonize()` calls `setsid()`, forks, optionally redirects stdio to `/dev/null`, and closes stray fds while preserving the monitored fd.
- `_update_regions()` calls `dm_stats_update_regions_from_fd()`, counts returned regions, updates group id if the leader changed, and records region count.
- `_dmfilemapd()` is the main loop: bind stats handle, set notify, list stats, process events, update regions, check termination conditions, and sleep between iterations.
- `main()` parses args, configures logging, optionally daemonizes, and runs the daemon.

## Modes
- `inode`: follows the opened inode. If the file is unlinked, the daemon continues while another process still holds it open and exits once it appears closed.
- `path`: follows the pathname. On events, the daemon closes and reopens the path so replacement files can be tracked.

## Edge Cases and Invariants
- The path argument must be absolute.
- The daemon assumes at least one region exists at startup and obtains the exact count after the first update.
- Inotify is nonblocking; `EAGAIN` and `EINTR` are nonfatal.
- Deleted-file open detection via `/proc` is explicitly heuristic and can miss short-lived opens or produce false positives for reused paths.
- `dm_stats_group_present()` disappearing is a normal exit condition.
- Zero updated regions is treated as “file contains no extents” and exits the loop.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/libdm/dm-tools/dmfilemapd.c -->