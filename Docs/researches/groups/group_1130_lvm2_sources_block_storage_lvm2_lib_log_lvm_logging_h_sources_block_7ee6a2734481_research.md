# Group Research: group_1130_lvm2_sources_block_storage_lvm2_lib_log_lvm_logging_h_sources_block_7ee6a2734481

Scope: `Docs/research_subset_a.md`; source tree `sources/block-storage/lvm2` is included in subset A.

Read coverage: complete read of all listed files, 7,772 total source lines.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/log/lvm-logging.h -->
# File Research: sources/block-storage/lvm2/lib/log/lvm-logging.h

Purpose: declares LVM2's core logging interface, log initialization/finalization hooks, stream/syslog/journal configuration, error-message storage accessors, and reporting-context state used to route logs into structured reports.

Read coverage: complete file read, 139 lines.

Key responsibilities:
- Declares `print_log()` and `print_log_libdm()` with printf-format checking and wraps them through `LOG_LINE*` macros that inject source file and line.
- Exposes initialization for custom file descriptors, standard streams, custom log callback functions, indentation, message prefixes, debug fields, log files, syslog, journald fields, suspended-device logging, and abort-on-internal-error behavior.
- Provides lifecycle calls such as `fin_log()`, `reset_log_duplicated()`, `fin_syslog()`, and `unlink_log_file()`.
- Defines stored errno/message helpers used after command failures: `reset_lvm_errno()`, `stored_errno()`, `stored_errmsg()`, and `stored_errmsg_with_clear()`.
- Defines suppression controls for general logging and syslog.
- Defines `log_report_t` plus report context/object enums for emitting command, PV, VG, LV, label, orphan, and pre-command log records through `dm_report`.

Dependencies:
- Includes `lib/misc/lvm-file.h`, `lib/log/log.h`, and uses `struct dm_report`, `struct id`, `FILE`, and `uint32_t`.
- Implemented by the logging subsystem and consumed broadly by command, metadata, activation, and daemon code.

Risk and edge cases:
- The printf-format attributes protect callers only if function signatures remain aligned with the macros.
- Report state is global process state; callers that temporarily set report context/object fields must restore state to avoid misattributing later log messages.
- `log_suppress()` distinguishes suppression to stdout/stderr from suppression everywhere, so callers need the right level for quiet or machine-readable modes.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/log/lvm-logging.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/lvmpolld/lvmpolld-client.c -->
# File Research: sources/block-storage/lvm2/lib/lvmpolld/lvmpolld-client.c

Purpose: implements the client-side connection to `lvmpolld`, allowing LVM commands to delegate long-running polling operations such as pvmove, mirror conversion, and snapshot/thin merge monitoring to the daemon.

Read coverage: complete file read, 364 lines.

Key responsibilities:
- Maintains process-global lvmpolld enablement, socket path, connected state, and `daemon_handle`.
- Opens the daemon using `LVMPOLLD_SOCKET`, protocol name, and protocol version, warning and falling back to local polling if connection fails.
- Builds and sends poll initialization requests for pvmove, conversion, classic snapshot merge, and thin snapshot merge.
- Builds and sends progress requests by LV UUID, optionally including abort requests, `LVM_SYSTEM_DIR`, and devicesfile/system context.
- Interprets daemon responses for in-progress, finished, not-found, invalid, failed, signal termination, and child command return codes.
- Maps LVM2 and lvmpolld-specific return codes to user-facing errors and points users to daemon logs.

Important entry points:
- `lvmpolld_set_active()`, `lvmpolld_set_socket()`, `lvmpolld_use()`, `lvmpolld_disconnect()`.
- `lvmpolld_poll_init()` starts a daemon-tracked operation.
- `lvmpolld_request_info()` checks completion and success/failure of a daemon-tracked operation.

Dependencies:
- Uses libdaemon client I/O, `lvmpolld-protocol.h`, exported metadata LV type flags, `polldaemon.h`, command context, and LVM command return codes.
- Depends on `daemon_request_extend()`, `daemon_send()`, and `daemon_reply_*()` parsing.

Risk and edge cases:
- `lvmpolld_use()` requires both global enablement and a configured socket path; disabled or missing socket returns local polling.
- Requests are keyed by LV UUID and require VG/LV names for logging and daemon parameters.
- The interval string buffer is intentionally small but checked for truncation.
- Error handling must destroy both requests and replies on every path.
- Finished daemon operations can fail either by signal or by LVM child command return code, and both cases are surfaced differently.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/lvmpolld/lvmpolld-client.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/lvmpolld/lvmpolld-client.h -->
# File Research: sources/block-storage/lvm2/lib/lvmpolld/lvmpolld-client.h

Purpose: declares the lvmpolld client API and provides no-op fallbacks when LVM is built without `LVMPOLLD_SUPPORT`.

Read coverage: complete file read, 52 lines.

Key contents:
- Defines the default daemon socket path as `DEFAULT_RUN_DIR "/lvmpolld.socket"`.
- Forward-declares `cmd_context`, `poll_operation_id`, and `daemon_parms`.
- Declares connection, enablement, socket override, poll initialization, and progress request functions.
- Provides macro stubs returning false/no-op behavior when lvmpolld support is not compiled in.

Dependencies:
- Includes `libdaemon/client/daemon-client.h` only under `LVMPOLLD_SUPPORT`.
- Consumed by polling command paths that can transparently fall back to foreground polling.

Risk and edge cases:
- Callers must not assume lvmpolld is available: the header intentionally compiles all calls to no-ops in unsupported builds.
- `lvmpolld_poll_init()` and `lvmpolld_request_info()` return `0` in unsupported builds, so higher-level polling paths must handle fallback behavior.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/lvmpolld/lvmpolld-client.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/lvmpolld/polldaemon.h -->
# File Research: sources/block-storage/lvm2/lib/lvmpolld/polldaemon.h

Purpose: defines shared polling abstractions for long-running LVM operations, including progress states, operation identity, daemon parameters, and callbacks used by foreground or daemon-backed polling.

Read coverage: complete file read, 77 lines.

Key contents:
- Defines `progress_t` states: failed, unfinished, finished current segment, and finished all.
- Defines `struct poll_functions`, the operation-specific callbacks for copy-name lookup, progress polling, metadata update, and finalization.
- Defines `struct poll_operation_id` with VG name, LV name, display name, and UUID.
- Defines `struct daemon_parms` with polling interval, delay behavior, abort/background flags, outstanding count, progress-display fields, LV type flags, callback table, and devicesfile name.
- Declares `poll_daemon()`, `poll_mirror_progress()`, and `wait_for_single_lv()`.

Dependencies:
- Includes `metadata-exported.h` for `logical_volume`, `volume_group`, LV type flags, and LVM metadata types.
- Used by lvmpolld client code and local polling code.

Risk and edge cases:
- `daemon_parms.devicesfile` has a fixed 128-byte buffer, so callers must preserve truncation/validation guarantees before populating it.
- Callback implementations must follow the progress-state contract so poll loops know whether to continue, update metadata, or finish.
- Operation IDs require stable UUID/name values because daemon requests and local status messages depend on them.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/lvmpolld/polldaemon.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/cache_manip.c -->
# File Research: sources/block-storage/lvm2/lib/metadata/cache_manip.c

Purpose: implements LVM cache and cache-pool/cachevol manipulation: cache mode/policy/metadata-format selection, metadata and chunk-size sizing, cache creation/removal, dirty-cache flushing, and cache metadata wiping.

Read coverage: complete file read, 1,279 lines.

Key responsibilities:
- Converts cache modes between enum and strings, validates user-provided modes, and resolves defaults from config/profiles.
- Computes minimum cache metadata sizes from cache data size and chunk size using dm-cache metadata overhead assumptions.
- Selects and validates cache pool chunk sizes against target limits, configured max chunks, metadata LV size, and data LV size.
- Validates cache pool and origin LV suitability before building a cached LV.
- Implements `lv_cache_create()` by inserting an origin layer, changing the top segment to cache, attaching the pool/cachevol, renaming used cache pools with `_cpool`, and inheriting profiles.
- Implements `lv_cache_wait_for_clean()` by polling cache status, switching to cleaner policy when needed, and waiting for dirty blocks to drain.
- Implements `lv_cache_remove()` with special handling for inactive writethrough/passthrough caches, temporary activation for writeback flush, pending-delete cache layer teardown, pool/cachevol detachment, and reload/deactivation sequencing.
- Detects default cache policy and metadata format from kernel target features, preferring `smq` and metadata format 2 when available.
- Applies cache policy settings from explicit config trees or profile config, including flattening old and new policy settings and removing `"default"` placeholder values.
- Implements newer cachevol parameter setup by carving metadata/data regions from one LV and requiring metadata format 2.
- Wipes unused cache-pool metadata/data volumes before use, skipping volumes whose segment type should not be zeroed.

Important entry points:
- Mode/policy/format: `cache_mode_num_to_str()`, `set_cache_mode()`, `cache_set_cache_mode()`, `cache_set_policy()`, `cache_set_metadata_format()`, `cache_set_params()`.
- Sizing/validation: `update_cache_pool_params()`, `validate_cache_chunk_size()`, `validate_lv_cache_chunk_size()`, `validate_lv_cache_create_pool()`, `validate_lv_cache_create_origin()`.
- Lifecycle: `lv_cache_create()`, `lv_cache_wait_for_clean()`, `lv_cache_remove()`, `cache_vol_set_params()`, `wipe_cache_pool()`.

Dependencies:
- Uses metadata, locking, activation, config/defaults, display, segment types, LV allocation, signal handling, and device-mapper cache target status/features.
- Relies on LV relationship helpers such as `first_seg()`, `seg_lv()`, `attach_pool_lv()`, `detach_pool_lv()`, `insert_layer_for_lv()`, and `remove_layer_from_lv()`.

Risk and edge cases:
- Writeback caches must be flushed before detaching; inactive writeback caches are temporarily activated for cleaning.
- Dirty cache flushing can be interrupted, and the code attempts to restore the normal table if cleaner-policy flushing is aborted.
- Cache metadata format 2 is enforced for cachevol creation, while legacy cache pools maintain compatibility with format 1.
- Cache on RAID in writeback mode logs a redundancy-loss warning.
- Chunk size is constrained by dm-cache target min/max, alignment, data volume size, metadata capacity, and configured max chunk count.
- Failed cache removal can leave a temporary pending-delete/cache structure that later commands must be able to complete.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/cache_manip.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/integrity_manip.c -->
# File Research: sources/block-storage/lvm2/lib/metadata/integrity_manip.c

Purpose: implements dm-integrity layering for LVM RAID images, including metadata LV sizing/creation, integrity block-size selection, adding/removing integrity wrappers, metadata extension, mismatch reporting, and integrity setting serialization.

Read coverage: complete file read, 1,057 lines.

Key responsibilities:
- Finds integrity wrapper LVs from origin LVs and identifies integrity origins.
- Estimates integrity metadata size using data size, journal size, VG extent size, and fixed trial-derived metadata overhead rules.
- Creates temporary `_imeta` metadata LVs for integrity, allocated near each RAID image and zeroed before use.
- Extends existing integrity metadata LVs for RAID images when the protected origin grows.
- Removes integrity from all or selected RAID images by removing `_iorig` layers, detaching `_imeta`, clearing flags/settings, reloading active LVs, deactivating unused layers, and removing metadata/origin helper LVs.
- Parses integrity mode strings, accepting journal and bitmap modes.
- Chooses integrity block size based on device logical/physical block sizes, filesystem block size, command context (`lvcreate` versus `lvconvert`), active state, and user override.
- Adds integrity to RAID by creating per-image `_imeta` LVs, optionally reusing an existing metadata LV, inserting `_iorig` layers under each RAID image, replacing each image's first segment with an integrity segment, and setting default tag size/hash/mode/block size.
- Handles active versus inactive setup by either update/reload or commit plus activate, then clears `integrity_recalculate` after initial activation starts kernel initialization.
- Exposes helpers to clear or detect recalculate metadata flags, detect RAID integrity, retrieve settings, and aggregate mismatch counts across RAID images.
- Serializes selected dm-integrity settings into string lists for reporting/config output.

Important entry points:
- `lv_add_integrity_to_raid()`, `lv_remove_integrity_from_raid()`, `lv_extend_integrity_in_raid()`.
- `lv_integrity_from_origin()`, `lv_is_integrity_origin()`, `lv_raid_has_integrity()`, `lv_get_raid_integrity_settings()`.
- `integrity_mode_set()`, `lv_integrity_mismatches()`, `lv_raid_integrity_total_mismatches()`.
- `lv_clear_integrity_recalculate_metadata()`, `lv_has_integrity_recalculate_metadata()`, `integrity_settings_to_str_list()`.

Dependencies:
- Uses metadata, locking, activation, display, segment types, config defaults, LV creation, PV-list discovery, direct block-size probing, filesystem block-size probing, and dm-integrity status structures.
- Relies on RAID segment layout and image/meta LV conventions from the metadata layer.

Risk and edge cases:
- Integrity is limited to supported RAID levels: raid1, raid4, raid5, raid6, and raid10.
- Block-size selection is conservative for active LVs to avoid surprising applications with changed I/O constraints.
- Metadata LV creation and layer insertion have rollback logic, but some failures after VG writes may require manual cleanup.
- The code assumes per-image `_imeta` LVs can be allocated from the image's current PV list and currently treats metadata as single-PV in extension.
- Recalculate metadata must be cleared after initialization starts; otherwise future activations can restart initialization.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/integrity_manip.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/lv.c -->
# File Research: sources/block-storage/lvm2/lib/metadata/lv.c

Purpose: implements core logical-volume utility functions for type checks, report/display duplication, LV relationship discovery, segment device formatting, kernel-status interpretation, RAID health checks, LV naming/VG association, activation, and lock-holder resolution.

Read coverage: complete file read, 1,936 lines.

Key responsibilities:
- Implements `lv_is_locked()` as a recursive check over sub-LVs, replacing a simple top-level flag check.
- Identifies simple single-segment `error` and `zero` LVs and orphan pvmove error LVs.
- Formats segment PV/LV areas and metadata areas into report lists and strings, including extent ranges and optional hidden-device marking.
- Provides report duplicate helpers for segment type, tags, cache mode, monitor state, discards, kernel discards, LV names, UUIDs, full names, paths, device-mapper paths, timestamps, hosts, profiles, lock args, and active state.
- Computes segment start/size/chunk size and data/metadata/origin sizes.
- Converts device-mapper target status into percentages for integrity recalculation, cache data/metadata/dirty usage, writecache usage, RAID sync, snapshots, thin pools, thin volumes, and VDO pools.
- Checks whether an LV or any sub-LV is placed on a given PV or list of PVs.
- Resolves LV relationships: origin, parent, mirror log, pool LV, data LV, metadata LV, conversion LV, pvmove source PV, and visible layer names.
- Checks mirror and RAID image sync state through mirror percent or RAID health strings.
- Implements `lv_raid_healthy()` and maps RAID health to refresh/repair needs, including special treatment for virtual/error legs after missing-PV removal and reshape count mismatches.
- Builds the standard 10-character `lv_attr` string, combining LV type, permissions, allocation/lock state, activation state, open state, layout class, zeroing, partial/RAID/cache/thin/writecache health, and activation-skip state.
- Maintains creation metadata, LV names in the VG radix tree, and LV movement between VGs.
- Activates/deactivates LVs while coordinating persistent lockd locks for exclusive/shared activation modes.
- Finds the LV that should hold activation locks through COW, thin, external origin, RAID, pvmove, cache, and pending-delete relationships.

Important entry points:
- Type and relation helpers: `lv_is_historical()`, `lv_is_locked()`, `lv_origin_lv()`, `lv_parent()`, `lv_pool_lv()`, `lv_data_lv()`, `lv_metadata_lv()`, `lv_lock_holder()`.
- Reporting helpers: `lv_attr_dup_with_info_and_seg_status()`, `lv_attr_dup()`, `lvseg_percent_with_info_and_seg_status()`, `lvseg_*_str()`, `lv_*_dup()`.
- RAID/sync helpers: `lv_mirror_image_in_sync()`, `lv_raid_image_in_sync()`, `lv_raid_healthy()`.
- Mutation helpers: `lv_set_creation()`, `lv_set_name()`, `lv_set_vg()`, `lv_active_change()`.

Dependencies:
- Uses metadata, activation, display, config/defaults, lvmlockd, device-mapper status structs, dmeventd monitoring when enabled, radix-tree name indexes, and segment-type callbacks.
- Depends on many metadata helpers declared in `metadata-exported.h` and `lv.h`.

Risk and edge cases:
- Report helpers often allocate from caller-provided pools; allocation failures are logged and returned as `NULL`.
- RAID health strings may not match area counts during reshape, so the code falls back to broader unhealthy detection.
- `lv_attr` is dense external-facing behavior; changing character meanings can break scripts and user expectations.
- `lv_set_name()` must keep the VG radix tree consistent and rejects duplicate names.
- Lock-holder resolution must skip pending-delete and unused cache-pool users to avoid locking dead or irrelevant layers.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/lv.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/lv.h -->
# File Research: sources/block-storage/lvm2/lib/metadata/lv.h

Purpose: defines the in-memory logical volume structures and declares LV relationship, property, reporting, kernel-state, mutation, activation, percentage, and RAID-health helper APIs.

Read coverage: complete file read, 224 lines.

Key contents:
- Defines `struct lv_list`, `struct logical_volume`, `struct historical_logical_volume`, and `struct generic_logical_volume`.
- `struct logical_volume` contains LVID/name/VG, profile, status flags, size and LE count, allocation/read-ahead/minor-major state, snapshot counters/links, segment/tag/user lists, historical ancestry links, timestamps, lockd state bits, hostname, and lock args.
- Historical LV support represents removed LVs through dummy live `logical_volume` objects whose `this_glv` points to historical metadata.
- Declares LV dependency discovery helpers for parent, conversion layer, origin, mirror log, data LV, metadata LV, and pool LV.
- Declares LV property helpers for sizes, segment properties, lock holder, committed LV lookup, mirror/RAID sync, segment device/range lists, and RAID health.
- Declares kernel-property helpers for major/minor/read-ahead/discards.
- Declares LV mutation helpers for creation metadata, name/VG assignment, and activation changes.
- Declares many report-string duplication helpers and percent calculation helpers.

Dependencies:
- Includes `lib/metadata/vg.h` and relies on metadata types such as `union lvid`, `lv_segment`, `profile`, `dm_list`, `dm_pool`, `dm_percent_t`, and activation enums.
- Implemented primarily by `lv.c`, with some declarations implemented in other metadata modules.

Risk and edge cases:
- `lvid` must remain the first member of `struct logical_volume` because report code relies on its offset.
- Historical LV representation intentionally blurs live and removed LV handling, so callers must check `lv_is_historical()` when accessing fields that may be blank.
- Function declarations expose many allocation-returning helpers; callers must pass a valid memory pool and handle `NULL`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/lv.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/lv_alloc.h -->
# File Research: sources/block-storage/lvm2/lib/metadata/lv_alloc.h

Purpose: declares LV segment allocation and area manipulation APIs used to allocate extents, build LV segments, connect segment areas to PVs/LVs, release areas, and derive parallel allocation constraints.

Read coverage: complete file read, 88 lines.

Key contents:
- Declares `alloc_lv_segment()` for constructing an `lv_segment` with segment type, LV, LE/length/reshape metadata, status, stripe/cache/mirror sizing, area counts, copies, copied extents, and pvmove source.
- Declares area setters and movers for PV-backed and LV-backed segment areas.
- Declares release helpers, including a discard-aware release path.
- Forward-declares `struct alloc_handle` and declares `allocate_extents()` for central VG/LV extent allocation.
- Declares helpers to add allocated areas as normal segments, mirror areas, segmented mirror images, mirror LVs, log segments, and virtual segments.
- Declares `alloc_destroy()` and `build_parallel_areas_from_lv()`.

Dependencies:
- Includes `metadata-exported.h` for LV, VG, PV, segment type, allocation policy, and list types.
- Implemented by LV allocation/manipulation code and used by cache/integrity/merge/layering code when constructing or splitting segments.

Risk and edge cases:
- Segment area ownership and back references must remain consistent with `segs_using_this_lv` and PV segment lists, or validation in `merge.c` will fail.
- `allocate_extents()` has many geometry and policy parameters; incorrect stripe/mirror/log values can create invalid metadata even if allocation succeeds.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/lv_alloc.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/merge.c -->
# File Research: sources/block-storage/lvm2/lib/metadata/merge.c

Purpose: implements LV segment merging, segment splitting, and deep metadata consistency validation for LV segment graphs across striped, mirrored, RAID, thin, cache, VDO, integrity, snapshot, pvmove, and pool layouts.

Read coverage: complete file read, 1,049 lines.

Key responsibilities:
- Merges adjacent compatible segments through segment-type `merge_segments` callbacks while avoiding pvmove and locked LV structures.
- Defines bounded validation error accumulation to avoid unbounded error storms.
- Performs RAID-specific validation for raid0, raid1, raid4/5/6/10, including area counts, metadata areas, stripe size, region size, recovery-rate ordering, data offsets, reshape flags, image/meta LV flags, size consistency, and visibility rules.
- Validates cache segments: cache LV flags, pool/cachevol references, metadata format, mode, policy name/settings, chunk size, and metadata-format flag consistency.
- Validates mirror logs, mirror image back references, mirror region size, and mirrored image sizing.
- Validates pool segments for one data LV, metadata LV presence, and bidirectional references.
- Validates thin pool and thin volume fields, including chunk size, zero/discard/crop settings, transaction IDs, pool references, device IDs, external origins, and merge LV flags.
- Validates VDO pool and VDO LV fields and target parameters.
- Validates integrity segments and `_iorig` naming/relationship expectations.
- Validates segment fields that must be unset for unrelated segment types, including pool LV, chunk size, transaction ID, VDO params, policy fields, and segtype-private storage.
- Checks complete VG metadata for single-segment type requirements, pool data back references, metadata LV naming suffixes, external-origin counts, and read-only requirements.
- Checks incomplete VG metadata for consecutive/non-overlapping segments, LE count consistency, PV segment back references, LV `segs_using_this_lv` references, reference counts, and historical indirect-origin links.
- Splits a segment at a requested logical extent by cloning the segment, copying tags, adjusting lengths/LEs/area offsets, and reassigning PV or LV areas.

Important entry points:
- `lv_merge_segments()`.
- `check_lv_segments_complete_vg()`.
- `check_lv_segments_incomplete_vg()`.
- `lv_split_segment()`.

Dependencies:
- Uses metadata, defaults, LV allocation, PV allocation, string lists, segment-type helpers, display helpers, VDO validation, thin/cache chunk validators, and many LV flag helpers from `metadata-exported.h`.
- Relies on segment-type operation callbacks for merge and split capability.

Risk and edge cases:
- Validation encodes many metadata invariants; changing LV status flags or segment fields requires updating these checks.
- RAID reshape states intentionally relax or alter some constraints, especially data offsets and health/count matching.
- Segment splitting must update PV segment ownership or LV area LE offsets exactly, or later allocation and validation will see inconsistent graphs.
- `ERROR_MAX` limits diagnostics to 100 errors, so severe corruption may produce truncated validation output.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/merge.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/metadata-exported.h -->
# File Research: sources/block-storage/lvm2/lib/metadata/metadata-exported.h

Purpose: defines LVM2's exported metadata model and large public-internal API surface for PV/VG/LV metadata, flags, segment structures, creation/resize parameters, pool/cache/raid/integrity/vdo operations, activation modes, and validation helpers.

Read coverage: complete file read, 1,507 lines.

Key contents:
- Defines sector, stripe, extent, and historical-LV constants.
- Defines extensive VG/PV/LV status flags, including visible/read/write, snapshot, pvmove, lock, mirror, RAID, thin, cache, writecache, integrity, VDO, pending-delete, reshape, metadata-format, activation-skip, and derived partial state.
- Defines format feature flags, mirror conversion flags, VG read flags, and VG read failure flags.
- Provides LV type macros for thin, mirror, RAID, cache, pool, writecache, integrity, VDO, removed, component, virtual, partial, and snapshot/origin state.
- Defines key enums: area type, force/prompt level, thin zero/discards/crop metadata, cache mode, cache metadata format, lock type, and activation change.
- Defines metadata container structures: `format_type`, `format_instance`, `pv_segment`, `lv_segment_area`, `lv_thin_message`, `lv_segment`, `pe_range`, `pv_list`, `glv_list`, `vg_list`, and `vgnameid_list`.
- `struct lv_segment` is the central per-segment model with generic geometry plus fields for mirror/RAID, snapshot, thin, pool, cache, writecache, integrity, and VDO targets.
- Defines PV creation and pvcreate parameter structures, LV resize parameters, wipe parameters, VDO conversion parameters, LV creation parameters, VG creation parameters, LV removal parameters, and status structs for thin, snapshot, RAID, cache, and VDO.
- Declares VG/PV lifecycle APIs: read, write, commit, revert, create, remove, rename, extend, split metadata areas, move PVs, validate names, validate VGs, orphan handling, PV resize/analyze/write, and system-id/foreign checks.
- Declares LV lifecycle APIs: create, extend, resize, remove, rename, update/reload, wipe, activate/wipe, layer insertion/removal, tag changes, pool metadata handling, and activation skip handling.
- Declares thin-pool, cache, VDO, mirror, RAID, writecache, snapshot, pvmove, integrity, and reporting helper APIs.

Dependencies:
- Includes ID, PV, VG, LV, percent, and lvmlockd headers plus `<stdbool.h>`.
- Used across lib metadata, tools, activation, daemon polling, segment-type handlers, and exported library-facing code.

Risk and edge cases:
- Many status bits are shared between object classes or reused for historical compatibility, so callers must interpret them in the right PV/VG/LV context.
- `struct lv_segment` is a cross-target union-like structure without an explicit union; validation must ensure fields for unrelated target types remain unset.
- Macros such as `lv_is_component()` depend on helper functions and flag combinations, so they can have non-obvious side effects or evaluation costs.
- This header is a broad contract: changing flags, structures, or prototypes can ripple across the whole metadata layer, tools, and reporting code.
- Fixed-size fields such as devicesfile in polling params and names in creation code require callers to preserve upstream validation and length limits.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/metadata-exported.h -->