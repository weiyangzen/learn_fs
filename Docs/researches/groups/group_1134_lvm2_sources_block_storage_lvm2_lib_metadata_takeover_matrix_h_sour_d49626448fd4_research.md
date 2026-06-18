# Group Research: group_1134_lvm2_sources_block_storage_lvm2_lib_metadata_takeover_matrix_h_sour_d49626448fd4

Scope: `Docs/research_subset_a.md`, source tree `sources/block-storage/lvm2`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/takeover_matrix.h -->
# File Research: sources/block-storage/lvm2/lib/metadata/takeover_matrix.h

This header defines the RAID takeover dispatch matrix used by LVM metadata code to choose a conversion function between segment layouts.

Core content:
- Maps short macro names such as `lin_r0`, `r0__r1`, `r45_r6`, and `str_r10` to `_takeover_from_*` functions.
- Defines `_segtype_index[]`, translating segment flags into matrix columns for linear, striped, mirror, raid0, raid0_meta, raid1, raid4/5, raid6, raid10, raid01, and other.
- Defines `_takeover_fns[][11]`, where rows are current segment type and columns are requested segment type.
- Uses `N` for `_takeover_noop` and `X` for `_takeover_unsupported`.

Dependencies:
- Expects `takeover_fn_t` and all `_takeover_from_*` functions to be declared in the including translation unit.
- Uses segment flag constants such as `SEG_MIRROR`, `SEG_RAID0`, `SEG_RAID5_LS`, `SEG_RAID6_NC`.

Notable behavior:
- `raid01` handling is effectively disabled/commented out in the table, so raid01 conversions fall through to unsupported “other” behavior.
- Linear-to-striped is unsupported while linear-to-raid0 is supported, reflecting LVM’s explicit raid takeover model.

Risks:
- This file is macro-heavy and intentionally included into another source. Adding or reordering segment categories requires synchronized changes to `_segtype_index[]`, `_takeover_fns`, and the takeover function set.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/takeover_matrix.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/thin_manip.c -->
# File Research: sources/block-storage/lvm2/lib/metadata/thin_manip.c

This file implements thin-pool metadata helpers, queued thin target messages, pool activation/update logic, sizing policy, and external-origin validation.

Main entry points:
- Thin pool access and checks: `data_lv_from_thin_pool()`, `find_pool_lv()`, `thin_pool_is_active()`, `thin_pool_feature_supported()`.
- Message lifecycle: `attach_thin_pool_message()`, `thin_pool_has_message()`, `update_thin_pool_lv()`.
- External origin handling: `attach_thin_external_origin()`, `detach_thin_external_origin()`, `validate_thin_external_origin()`, `thin_pool_supports_external_origin()`.
- Capacity checks: `thin_pool_metadata_min_threshold()`, `thin_pool_below_threshold()`, `thin_pool_check_overprovisioning()`.
- Metadata sizing and configuration: `get_default_allocation_thin_pool_chunk_size()`, `get_thin_pool_max_metadata_size()`, `get_thin_pool_crop_metadata()`, `thin_pool_set_params()`, `update_thin_pool_params()`.
- Thin identity helpers: `get_free_thin_pool_device_id()`, `lv_is_thin_origin()`, `lv_is_thin_snapshot()`, `lv_is_merging_thin_snapshot()`.
- Metadata initialization: `thin_pool_prepare_metadata()` uses configured `thin_restore` to seed a metadata LV.
- Safety validation: `check_new_thin_pool()`, `validate_thin_pool_chunk_size()`, `estimate_thin_pool_metadata_size()`.

Control flow:
- `attach_thin_pool_message()` queues create/delete messages on a thin pool segment and increments `transaction_id` when adding the first updating message.
- `update_thin_pool_lv()` activates the pool if needed, optionally suppresses dmeventd monitoring, validates create messages against pool thresholds, suspends/resumes the origin to deliver messages, clears the message list, then writes and commits VG metadata.
- `update_thin_pool_params()` derives chunk size, metadata size, discard mode, zeroing mode, crop policy, and max addressable data size from config, target features, and user input.
- `thin_pool_prepare_metadata()` temporarily activates the metadata LV, writes XML metadata into a temporary file, invokes `thin_restore`, and deactivates the LV.

Dependencies:
- Activation/status APIs: `lv_info`, `activate_lv_temporary`, `activate_lv`, `deactivate_lv`, `suspend_lv_origin`, `resume_lv_origin`, `lv_thin_pool_status`.
- VG persistence: `vg_write()`, `vg_commit()`.
- Config keys under allocation, activation, and global thin restore settings.
- Device-mapper thin constants and status structures.

Correctness notes:
- Thin transaction IDs are a core guard against applying stale messages or externally modified pools.
- Clustered VGs check related thin volumes, not just the pool LV itself.
- External origins are forced read-only and rejected if internal, writable, pool-like, active non-external-origin, or incompatible with chunk-size constraints.
- Device ID allocation is a naive max-plus-one search and does not fill holes.

Risks:
- Message delivery depends on activation/suspend/resume ordering while VG locks may be held.
- `thin_pool_prepare_metadata()` shells out through `exec_cmd` with configured tool/options and a proc-fd temporary input; failures must preserve deactivation.
- Metadata/chunk calculations mix sectors, extents, and target block limits, so unit mistakes would directly affect pool addressability.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/thin_manip.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/vdo_manip.c -->
# File Research: sources/block-storage/lvm2/lib/metadata/vdo_manip.c

This file implements VDO pool status parsing, VDO LV conversion, target parameter filling, and memory constraint checks.

Main entry points:
- State name helpers: `get_vdo_compression_state_name()`, `get_vdo_index_state_name()`, `get_vdo_operating_mode_name()`, `get_vdo_write_policy_name()`.
- Size helpers: `get_vdo_pool_virtual_size()`, `update_vdo_pool_virtual_size()`, `get_vdo_pool_max_extents()`.
- Status parsing: `parse_vdo_pool_status()`.
- Conversion: `convert_vdo_pool_lv()`, `convert_vdo_lv()`.
- Config parsing: `set_vdo_write_policy()`, `fill_vdo_target_params()`.
- Resource validation: `check_vdo_constraints()`.

Control flow:
- `parse_vdo_pool_status()` parses device-mapper VDO target status, builds the DM name, optionally reads kvdo sysfs counters, then computes usage, saving, and data usage percentages.
- `_format_vdo_pool_data_lv()` builds `vdoformat` arguments, pipes its output, parses the default logical block count if virtual size was not specified, and reports tool output line by line.
- `convert_vdo_pool_lv()` validates VDO parameters, optionally formats the active data LV, deactivates it, inserts a `_vdata` layer, sets the segment type to `vdo-pool`, and records virtual extents/header size.
- `convert_vdo_lv()` handles full user-facing conversion: optional rename to generated pool name, temporary activation, wipe, pool conversion, virtual VDO LV creation, and segment/name swapping when preserving the original LV name.
- `check_vdo_constraints()` estimates RAM requirements from physical size, virtual size, block map cache, index memory, base overhead, and available RAM/swap.

Dependencies:
- Device-mapper VDO status/validation APIs.
- External `vdoformat` configured by `global_vdo_format_executable` and options.
- LVM layer manipulation: `insert_layer_for_lv()`, `move_lv_segments()`, `set_lv_segment_area_lv()`, `lv_create_single()`, `lv_rename_update()`.
- `/proc/meminfo` or `sysinfo()` for memory estimates.
- kvdo sysfs paths in both current `block/dm-N/vdo/...` and older `kvdo/name/...` layouts.

Correctness notes:
- VDO virtual size includes front/back headers to avoid blkid collisions, then subtracts headers before computing virtual extents.
- VDO logical size is rounded to a 4 KiB target boundary.
- Only one VDO LV per VDO pool is assumed in `update_vdo_pool_virtual_size()`.
- Non-auto write policies are accepted but logged as deprecated.

Risks:
- Conversion has many irreversible-looking metadata transformations and relies on correct deactivation after formatting.
- Output parsing from `vdoformat` is locale-sensitive by the file’s own TODO.
- Memory checks are estimates and intentionally conservative, not kernel enforcement.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/vdo_manip.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/vg.c -->
# File Research: sources/block-storage/lvm2/lib/metadata/vg.c

This file implements allocation, lifetime, accessors, attribute rendering, extent-size mutation, limits, persistence flags, and PV removal for `struct volume_group`.

Main entry points:
- Lifetime: `alloc_vg()`, `release_vg()`, `free_orphan_vg()`.
- LV membership: `link_lv_to_vg()`, `unlink_lv_from_vg()`, `vg_max_lv_reached()`.
- Accessors/dup helpers: `vg_fmt_dup()`, `vg_name_dup()`, `vg_system_id_dup()`, `vg_lock_type_dup()`, `vg_lock_args_dup()`, `vg_uuid_dup()`, `vg_tags_dup()`, `vg_seqno()`, `vg_status()`, `vg_size()`, `vg_free()`, and count getters.
- Metadata areas: `vg_mda_count()`, `vg_mda_used_count()`, `vg_mda_copies()`, `vg_mda_size()`, `vg_mda_free()`, `vg_set_mda_copies()`.
- Mutators: `vg_check_new_extent_size()`, `vg_set_extent_size()`, `vg_set_max_lv()`, `vg_set_max_pv()`, `vg_set_alloc_policy()`, `vg_set_system_id()`, `vg_set_lock_type()`, `vg_set_persist()`.
- Reporting/operations: `vg_attr_dup()`, `vgreduce_single()`, `vg_backup_if_needed()`.

Control flow:
- `alloc_vg()` creates a VG memory pool, initializes all list heads, sets defaults, and stores the VG name.
- `release_vg()` recursively releases committed/precommitted VG copies, then destroys config trees, radix trees, and the VG pool.
- `vg_set_extent_size()` validates the new PE size, updates format setup, and recalculates VG, PV, PV segment, LV, LV segment, VDO virtual extent, and area offsets.
- `vgreduce_single()` validates the PV is unused and not the last PV, moves it to orphan state, updates VG counts, splits metadata areas, writes/commits if requested, and clears PV metadata.

Dependencies:
- Format instance operations, metadata area callbacks, radix tree name indexes, archiver backup, PV helpers, and activation persistence helpers.

Correctness notes:
- Extent-size changes require exact divisibility across every affected count and offset.
- `vg_set_max_lv()` counts only visible LVs.
- `vg_attr_dup()` encodes write/resize/export/missing/allocation/shared/persistent reservation state in report format.
- `vg_backup_if_needed()` backs up the committed VG copy, not necessarily the currently mutable in-memory copy.

Risks:
- `vg_set_extent_size()` mutates `vg->extent_size` early; failures after partial recalculation rely on caller-level error handling and VG lifetime discipline.
- `vgreduce_single()` touches both VG and orphan metadata and must clean up PV fids correctly on error or commit.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/vg.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/vg.h -->
# File Research: sources/block-storage/lvm2/lib/metadata/vg.h

This header defines the `struct volume_group` data model and public VG helper prototypes.

Key definitions:
- `alloc_policy_t` enum for allocation policy: invalid, contiguous, cling, internal cling-by-tags, normal, anywhere, inherit.
- Persistent reservation flags: `VG_PR_REQUIRE`, `VG_PR_AUTOSTART`, `VG_PR_PTPL`.
- `MAX_EXTENT_COUNT` as `UINT32_MAX`.

`struct volume_group` contains:
- Command/context pointers, memory pool, format instance, cache info, sequence number, status flags, write/backup state.
- Committed and precommitted metadata copies.
- Allocation policy, profile, status bits, radix trees for LV/PV name and UUID lookup.
- Identity fields: VG id, name, old name, system id, lock type/args.
- Extent accounting, max LV/PV, PV/LV/historical LV/tag lists.
- Removed LV/PV tracking lists, metadata area copy target, persistent reservation state.
- Special LVs: pool metadata spare and sanlock LV.
- Message and lockd-free LV lists.

Public API:
- VG allocation/free, string duplication, accessors, setters, sizing, metadata area metrics, attribute/tag/UUID formatting, visible LV and snapshot counts, and backup trigger.

Dependencies:
- `lib/id/id.h`, `libdevmapper`, `cmd_context`, `format_instance`, and `logical_volume`.

Risks:
- Many list/radix members are maintained by separate metadata subsystems; callers must preserve invariants when adding/removing LVs or PVs.
- Comments make clear that `vg_committed == NULL` implies committed copy, but non-NULL equality is not guaranteed.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/vg.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/writecache_manip.c -->
# File Research: sources/block-storage/lvm2/lib/metadata/writecache_manip.c

This file implements writecache identity checks, kernel status reads, clean checks, detach workflows, cleaner setting, and settings serialization.

Main entry points:
- Identification: `lv_is_writecache_origin()`, `lv_is_writecache_cachevol()`.
- Clean/status: `lv_writecache_is_clean()`.
- Detach: `lv_detach_writecache_cachevol()`.
- Cleaner: `lv_writecache_set_cleaner()`.
- Serialization: `writecache_settings_to_str_list()`.

Control flow:
- `_get_writecache_kernel_status()` creates a temporary pool, calls `lv_info_with_seg_status()`, validates `SEG_STATUS_WRITECACHE`, and copies error/total/free/writeback block fields.
- Inactive detach path:
  - Validates writecache segment, finds fast cachevol and origin.
  - Temporarily activates the LV unless `noflush`, sends `flush`, reads kernel error, deactivates, disconnects cachevol/origin layers, removes hidden origin LV, makes cachevol visible, renames it, then writes/commits the VG.
- Active detach path:
  - Optionally sends `flush_on_suspend`.
  - Removes writecache links in metadata, writes precommit metadata, obtains old committed LV, suspends using old mapping, checks old kernel error, commits, resumes new mapping, deactivates old cachevol and old origin layer, removes hidden origin, makes cachevol visible, and writes/commits again.
- `_rename_detached_cvol()` tries to drop `_cvol` suffix or generates `lvol%d`.

Dependencies:
- Activation/suspend/resume, VG write/commit/revert, LV layer removal, LV remove/deactivate, writecache target messaging, and DM status parsing.

Correctness notes:
- `WRITECACHE_ORIGIN` is used as a fallback identity marker after links have already been destroyed.
- Active detach deliberately consults `lv_committed(lv)` because the kernel still contains the old mapping after metadata mutation and before commit/resume.
- Kernel error status after flushing is treated as detach failure.

Risks:
- Active detach has tight ordering requirements across metadata write, suspend, kernel error read, commit, resume, and cleanup.
- `noflush` skips safety flushing, so callers must understand possible dirty cache data implications.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/writecache_manip.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/mirror/mirrored.c -->
# File Research: sources/block-storage/lvm2/lib/mirror/mirrored.c

This file defines the classic device-mapper mirror segment type plugin/handler.

Main entry points:
- Segment operations through `_mirrored_ops`: display, text import/export, target line generation, target percent, target presence, transient status, modules needed, dmeventd monitor hooks, destroy.
- Initialization: `init_mirrored_segtype()` or shared `init_segtype()`.

Behavior:
- Text import reads `mirror_count`, optional `extents_moved`, `region_size`, `mirror_log`, and `mirrors`.
- Text export writes mirror count, pvmove progress, mirror log, region size, and areas.
- `_mirrored_add_target_line()` handles normal mirrors and pvmove mirrors. Pvmove segments before current copy use the second area, after current copy use a linear first area, and only one segment runs as mirror at once.
- `_add_log()` chooses disk log or core log, sets `DM_CORELOG`, `DM_NOSYNC`, and optionally block-on-error/handle-errors behavior when monitoring is present.
- `_mirrored_target_percent()` parses mirror status and updates `extents_copied`.
- `_mirrored_transient_status()` compares kernel mirror devices/logs with metadata, marks failed legs/logs as `PARTIAL_LV`, and updates VG partial state.

Dependencies:
- Device-mapper mirror target, target version probing, dmeventd monitor library, text import/export helpers, activation info, and segment module lists.

Correctness notes:
- Disk log metadata must match the active kernel log device.
- Region size is required for logged mirrors.
- Block-on-error support is version-gated and warnings are suppressed after first print.
- `mirror_in_sync()` can set `DM_NOSYNC` for non-pvmove mirrors.

Risks:
- Classic mirror code must reconcile metadata and live kernel state; mismatches are treated as errors.
- Pvmove behavior depends on `extents_copied` and `pvmove_mirror_count` sequencing across segments.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/mirror/mirrored.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/crc.c -->
# File Research: sources/block-storage/lvm2/lib/misc/crc.c

This file implements LVM’s endian-independent CRC-32 calculation.

Core behavior:
- Contains a generated 256-entry CRC table for polynomial `0xedb88320`.
- On `__x86_64__`, lazily builds a 16-slice lookup table and processes 16 bytes per loop.
- On other architectures, processes 32-bit little-endian words plus trailing bytes.
- Uses `htole32()` from `xlate.h` so the result is independent of host byte order.
- With `DEBUG_CRC32`, compares the optimized implementation with an older nibble-table algorithm and logs mismatch.

Public API:
- `calc_crc(uint32_t initial, const uint8_t *buf, size_t size)`.

Dependencies:
- `crc.h`, `xlate.h`, logging via `lib.h`.

Correctness notes:
- The file explicitly states the CRC is for error detection, not cryptographic integrity.
- The x86 path assumes unaligned 32-bit loads are acceptable on the tested architecture.

Risks:
- `_crc32_lookup` lazy initialization is guarded only by a simple int, so it assumes benign initialization races or single-threaded early use.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/crc.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/crc.h -->
# File Research: sources/block-storage/lvm2/lib/misc/crc.h

This header declares the CRC helper.

Content:
- Defines `INITIAL_CRC` as `0xf597a6cf`.
- Declares `uint32_t calc_crc(uint32_t initial, const uint8_t *buf, size_t size)`.

Dependencies:
- Includes `<inttypes.h>`.

Role:
- Shared metadata/checksum users include this header for LVM’s CRC-32 implementation.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/crc.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/crc_gen.c -->
# File Research: sources/block-storage/lvm2/lib/misc/crc_gen.c

This is a helper program that generates the CRC lookup table embedded in `crc.c`.

Behavior:
- Iterates byte values `0..255`.
- Applies the CRC-32 polynomial `0xedb88320` for 8 bit steps.
- Prints a C `uint32_t` array initializer formatted eight entries per line.

Dependencies:
- Includes `lib/misc/lib.h` for project-standard types/includes.

Role:
- Build/developer utility, not runtime library code.

Risk:
- Output symbol name is `crctab[]`, while `crc.c` uses `_crctab[]`; generated output may require manual naming adjustment or historical context.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/crc_gen.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/intl.h -->
# File Research: sources/block-storage/lvm2/lib/misc/intl.h

This header defines LVM’s translation macro.

Behavior:
- If `INTL_PACKAGE` is defined, includes `<libintl.h>` and maps `_()` to `dgettext(INTL_PACKAGE, String)`.
- Otherwise `_()` returns the original string.

Role:
- Central conditional gettext support used through `lib.h`.

Risk:
- `_` is a global macro name; including order matters for files that may define their own `_`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/intl.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/last-path-component.h -->
# File Research: sources/block-storage/lvm2/lib/misc/last-path-component.h

This header provides one inline path helper.

API:
- `last_path_component(const char *name)` returns the substring after the last `/`.
- If there is no slash, it returns `name`.
- If the path ends with `/`, it returns the empty string after the slash.

Dependencies:
- `<string.h>` for `strrchr`.

Role:
- Lightweight basename-like helper without allocation and without libc `basename()` mutation/portability issues.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/last-path-component.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lib.h -->
# File Research: sources/block-storage/lvm2/lib/misc/lib.h

This is the required first include for library source files.

Content:
- Includes libdevmapper, zalloc, internationalization, and utility macros.
- Under `DM`, includes `dm-logging.h`.
- Otherwise includes LVM logging, globals, wrappers, and maths helpers.
- Includes `<unistd.h>`.

Role:
- Establishes common project types, logging, utility macros, and build-mode-dependent support for library code.

Risk:
- The comment says this file must be included first by every library source file; violating that can affect macro definitions and conditional logging behavior.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lib.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-exec.c -->
# File Research: sources/block-storage/lvm2/lib/misc/lvm-exec.c

This file implements no-shell external command execution and pipe capture helpers.

Main entry points:
- `exec_cmd()` forks, optionally syncs local device names, logs arguments, resets child logging/locking, calls `execvp()`, waits, and returns exit status.
- `pipe_open()` forks a child whose stdout is connected to a pipe and returns a `FILE *` reader.
- `pipe_close()` closes the stream and waits for the child.
- `prepare_exec_args()` appends configured option strings to an argv array.

Implementation details:
- `_verbose_args()` renders argv for logging.
- `_reopen_fd_to_null()` safely redirects a controlled fd to `/dev/null`.
- Child process uses `execvp()` directly, not a shell.
- `sync_needed` calls `sync_local_dev_names()` before execution where allowed.

Dependencies:
- Locking reset, device sync, command context config, signals/wait, and standard fork/exec APIs.

Correctness notes:
- `exec_cmd()` distinguishes abnormal exit, nonzero exit, and wait failure.
- `pipe_open()` closes unused pipe ends and kills/waits child if `fdopen()` fails.
- `prepare_exec_args()` enforces `DEFAULT_MAX_EXEC_ARGS` and string-only config values.

Risks:
- Child exits with `errno` after failed exec; only low 8 bits are preserved by process exit.
- `execvp()` searches `PATH`, so configured executable resolution matters.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-exec.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-exec.h -->
# File Research: sources/block-storage/lvm2/lib/misc/lvm-exec.h

This header declares external command helpers.

APIs:
- `exec_cmd(struct cmd_context *, const char *const argv[], int *rstatus, int sync_needed)`.
- `struct pipe_data { FILE *fp; pid_t pid; }`.
- `pipe_open()`, `pipe_close()`.
- `prepare_exec_args()`.

Notes:
- Comments warn that device synchronization cannot be done inside activation context.
- Pipe helper is explicitly popen-like but does not run a shell.

Dependencies:
- Includes `lib/misc/lib.h` and forward-declares `cmd_context`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-exec.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-file.c -->
# File Research: sources/block-storage/lvm2/lib/misc/lvm-file.c

This file implements filesystem utility helpers for temporary files, NFS-safe rename, path checks, recursive directory creation, directory sync, fcntl locks, fclose diagnostics, and stat timestamp extraction.

Main entry points:
- `create_temp_name()`: creates `.lvm_hostname_pid_num` temp file with `O_EXCL` and grabs an fcntl write lock.
- `lvm_rename()`: creates a hard link to destination and checks link count before unlinking source.
- `path_exists()`, `dir_exists()`, `dir_create_recursive()`.
- `sync_dir()`: fsyncs containing directory.
- `fcntl_lock_file()`, `fcntl_unlock_file()`.
- `lvm_fclose()`: reports write errors after stream close.
- `lvm_stat_ctim()`.

Dependencies:
- POSIX file APIs, `dm_prepare_selinux_context()`, `dm_create_dir()`, project logging.

Correctness notes:
- Temp file generation sanitizes `/` in hostname.
- `lvm_rename()` is designed not to overwrite an existing destination and to work safely on NFS.
- Recursive directory creation walks slash-separated prefixes.
- `sync_dir()` tolerates `EROFS` and `EINVAL`.
- `fcntl_lock_file()` creates parent directory before opening/locking.

Risks:
- Temp file generation tries only 20 candidates.
- `fcntl_lock_file()` opens lock files mode `0777`, relying on umask and context.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-file.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-file.h -->
# File Research: sources/block-storage/lvm2/lib/misc/lvm-file.h

This header declares file utility APIs and small macros.

Content:
- `struct custom_fds` for output/error/report descriptors.
- Temp file, rename, existence, directory creation, directory sync, fcntl lock, fclose, and ctime helpers.
- `is_same_inode(buf1, buf2)` compares inode and device.
- `is_valid_fd(fd)` checks `F_GETFD`.
- Defines `timespeccmp` fallback for BSD-like compatibility.

Dependencies:
- `<stddef.h>`, `<stdio.h>`, `<time.h>`, `<sys/stat.h>` and fcntl usage via macro.

Role:
- Common file/lock helper interface for metadata and command code.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-file.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-flock.c -->
# File Research: sources/block-storage/lvm2/lib/misc/lvm-flock.c

This file implements flock-based lock-file management with optional write-lock prioritization.

Main entry points:
- `init_flock()`: initializes lock list and reads `global_prioritise_write_locks`.
- `lock_file()`: acquire, convert, or release read/write locks.
- `release_flocks()`: releases all tracked locks.

Implementation details:
- Tracks locks in `_lock_list` as resource path plus fd.
- `_do_flock()` opens/creates lock file, takes flock, and validates fd inode against path inode to avoid races.
- Blocking locks temporarily allow SIGINT via `sigint_allow()`/`sigint_restore()`.
- `_do_write_priority_flock()` uses an auxiliary `:aux` lock file so write locks can serialize ahead of readers.
- `_undo_flock()` takes exclusive lock, verifies inode, unlinks lock file, and closes fd.

Dependencies:
- LVM lock flag constants, signal helpers, config, `is_same_inode`.

Correctness notes:
- `LCK_CONVERT` uses existing lock entry and calls `flock()` on the same fd.
- Releasing with `unlock=0` only closes shared fd without unlink/unlock cleanup.

Risks:
- Lock files are unlinked when no longer used; behavior assumes all participants follow the same protocol.
- Signal interruption during blocking flock causes “Giving up waiting for lock.”
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-flock.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-flock.h -->
# File Research: sources/block-storage/lvm2/lib/misc/lvm-flock.h

This header declares the flock helper interface.

APIs:
- `init_flock(struct cmd_context *cmd)`.
- `lock_file(const char *file, uint32_t flags)`.
- `release_flocks(int unlock)`.

Dependencies:
- `<stdint.h>` and forward-declared `cmd_context`.

Role:
- Used by higher-level locking code to manage local file locks.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-flock.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-globals.c -->
# File Research: sources/block-storage/lvm2/lib/misc/lvm-globals.c

This file stores and exposes process-wide LVM runtime settings.

Main state:
- Verbose/silent/test/debug settings.
- Filtering settings for MD, internal devices, fwraid, udev device list, external device info source.
- Command logging prefix/file strings and command name.
- Mirror sync, dmeventd monitoring, background polling, suspended-device handling.
- Static build, udev checking, retry deactivation, activation checks, PV minimum size, unknown device name, IO memory size.

Main APIs:
- `init_*()` setters for all global options.
- Getter functions such as `test_mode()`, `use_aio()`, `dmeventd_monitor_mode()`, `mirror_in_sync()`, `verbose_level()`, `debug_level()`, `pv_min_size()`, etc.
- `set_cmd_name()`, `get_cmd_name()`, `log_command_info()`, `log_command_file()`.
- `debug_class_is_logged()`.

Correctness notes:
- `init_test()` prints a warning the first time test mode is enabled.
- `init_dmeventd_monitor()` and `init_ignore_suspended_devices()` are frozen when dmeventd monitoring is disabled.
- `init_log_command()` always fills `_log_command_file` with command name and pid, while `_log_command_info` depends on configured flags.

Risks:
- All state is global process state, so callers must reset/reinitialize carefully across command contexts, callbacks, and forks.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-globals.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-globals.h -->
# File Research: sources/block-storage/lvm2/lib/misc/lvm-globals.h

This header declares global runtime setting APIs.

Content:
- Defaults: `VERBOSE_BASE_LEVEL`, `SECURITY_LEVEL`, `PV_MIN_SIZE_KB`.
- Setter/getter prototypes for logging, filtering, test mode, dmeventd, udev, activation, memory, command name, and misc behavior.
- Defines `DMEVENTD_MONITOR_IGNORE` as `-1`.

Dependencies:
- `<stdint.h>` and forward-declared `enum dev_ext_e`.

Role:
- Shared interface for process-global LVM state.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-globals.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-maths.c -->
# File Research: sources/block-storage/lvm2/lib/misc/lvm-maths.c

This file provides simple integer math helpers.

APIs:
- `gcd(unsigned long n1, unsigned long n2)` using Euclidean algorithm.
- `lcm(unsigned long n1, unsigned long n2)` as `(n1 / gcd(n1, n2)) * n2`, returning 0 if either input is 0.

Risk:
- `lcm()` can overflow `unsigned long`; callers must ensure range safety.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-maths.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-maths.h -->
# File Research: sources/block-storage/lvm2/lib/misc/lvm-maths.h

This header declares:
- `gcd(unsigned long n1, unsigned long n2)`.
- `lcm(unsigned long n1, unsigned long n2)`.

Role:
- Small common math utility interface included through `lib.h` in non-`DM` builds.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-maths.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-percent.c -->
# File Research: sources/block-storage/lvm2/lib/misc/lvm-percent.c

This file implements extent percentage conversion.

API:
- `percent_of_extents(uint32_t percents, uint32_t count, int roundup)` returns `percents * count / 100`, optionally rounding up by adding 99 before division.

Correctness note:
- Uses 64-bit intermediate arithmetic to avoid overflow for `uint32_t` inputs.

Role:
- Converts user percentage requests into extent counts.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-percent.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-percent.h -->
# File Research: sources/block-storage/lvm2/lib/misc/lvm-percent.h

This header defines percentage-related enums and helper declaration.

Content:
- `sign_t`: none, plus, minus.
- `percent_type_t`: none, VG, free, LV, PVs, origin.
- `LVM_PERCENT_MERGE_FAILED` aliases `DM_PERCENT_FAILED`.
- Declares `percent_of_extents()`.

Role:
- Shared parsing/reporting vocabulary for percentage-sized LVM operations.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-percent.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-signal.c -->
# File Research: sources/block-storage/lvm2/lib/misc/lvm-signal.c

This file manages SIGINT/SIGTERM handling and full signal blocking around critical sections.

Main APIs:
- `sigint_allow()`: installs temporary handlers for SIGINT/SIGTERM, clears `SA_RESTART`, and unmasks those signals.
- `sigint_restore()`: restores saved masks/handlers.
- `sigint_caught()`, `sigint_clear()`.
- `sigint_usleep()`: interruptible sleep with temporary signal handling.
- `block_signals()`, `unblock_signals()`.

Implementation details:
- Supports up to three nested allow/restore levels.
- `_catch_sigint()` only sets a `volatile sig_atomic_t` flag.
- Signal changes are skipped when `memlock_count_daemon()` is active.

Dependencies:
- `memlock.h`, POSIX signal APIs.

Correctness notes:
- Interrupt flags are not cleared automatically; command runner is expected to call `sigint_clear()`.
- Blocking uses `sigfillset()` and saves old mask.

Risks:
- Nesting beyond `MAX_SIGINTS` silently stops saving new handler state.
- `sigint_caught()` logs “Interrupted...” every time the flag is observed.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-signal.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-signal.h -->
# File Research: sources/block-storage/lvm2/lib/misc/lvm-signal.h

This header declares signal helper APIs:
- `sigint_allow()`, `sigint_restore()`, `sigint_caught()`, `sigint_clear()`, `sigint_usleep()`.
- `block_signals()`, `unblock_signals()`.

Dependencies:
- `<stdint.h>`, `<unistd.h>` for `useconds_t`.

Role:
- Shared interrupt/signal control interface for locking and activation paths.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-signal.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-string.c -->
# File Research: sources/block-storage/lvm2/lib/misc/lvm-string.c

This file implements string formatting, name validation, reserved LV name detection, DM UUID construction, suffix removal, and line splitting.

Main APIs:
- `emit_to_buffer()`: safe append-style `vsnprintf()` wrapper.
- `validate_tag()`, `validate_name()`, `validate_name_detailed()`.
- `copy_systemid_chars()`.
- `apply_lvname_restrictions()`, `is_reserved_lvname()`, `is_component_lvname()`.
- `build_dm_uuid()`.
- `first_substring()`, `drop_lvname_suffix()`, `split_line()`.

Behavior:
- Valid LVM names allow alnum plus `.`, `_`, `-`, `+`, reject empty, leading hyphen, `.`/`..`, invalid chars, and length over `NAME_LEN`.
- Tags allow a broader set including `/`, `=`, `!`, `:`, `&`, `#`.
- Reserved LV prefixes include `pvmove` and `snapshot`.
- Reserved component strings include `_cdata`, `_cmeta`, `_corig`, `_cpool`, `_cvol`, `_wcorig`, `_mimage`, `_mlog`, `_rimage`, `_rmeta`, `_tdata`, `_tmeta`, `_vdata`, `_imeta`, `_iorig`; additional reserved strings include `_pmspare`, `_vorigin`.
- `build_dm_uuid()` chooses implicit layer suffixes for internal LVs such as `real`, `pool`, `tdata`, `tmeta`, `vdata`, `cvol`.

Dependencies:
- Metadata LV classification helpers, display/logging, libdevmapper UUID builder.

Correctness notes:
- DM UUID layer suffix choices must match activation/dev-manager code comments.
- `copy_systemid_chars()` skips invalid characters and truncates to `NAME_LEN`.

Risks:
- Reserved substring detection starts at first `_`, so naming behavior depends on underscore placement.
- `split_line()` mutates the input buffer.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-string.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-string.h -->
# File Research: sources/block-storage/lvm2/lib/misc/lvm-string.h

This header defines the string utility interface.

Content:
- `NAME_LEN` as 128 and `UUID_PREFIX` as `LVM-`.
- `name_error_t` enum with detailed validation failures.
- Prototypes for buffer emission, DM UUID building, name/tag validation, systemid copying, reserved/component checks, substring search, suffix drop, and line splitting.

Dependencies:
- `<sys/types.h>`, forward declarations for `dm_pool` and `logical_volume`.

Role:
- Common string/name contract for metadata, activation, and reporting.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-string.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-wrappers.c -->
# File Research: sources/block-storage/lvm2/lib/misc/lvm-wrappers.c

This file provides wrappers around udev, page size, entropy, and unbiased random selection.

Main APIs:
- `udev_init_library_context()`, `udev_fin_library_context()`, `udev_is_running()`, `udev_get_library_context()`.
- `lvm_getpagesize()`.
- `read_urandom()`.
- `lvm_even_rand()`.

Behavior:
- With `UDEV_SYNC_SUPPORT`, creates a `udev` context unless `DM_DISABLE_UDEV` is set, checks active udev queue, and exposes the context.
- Without `UDEV_SYNC_SUPPORT`, udev functions become safe stubs.
- `read_urandom()` opens `/dev/urandom`, verifies it is a character device, reads exactly requested bytes, and closes.
- `lvm_even_rand()` rejects modulo-biased values from the incomplete top slice of `RAND_MAX`.

Risks:
- `read_urandom()` performs a single `read()` and treats short reads as failure.
- `lvm_even_rand()` uses `rand_r`, suitable for utility randomness, not cryptographic use.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-wrappers.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-wrappers.h -->
# File Research: sources/block-storage/lvm2/lib/misc/lvm-wrappers.h

This header declares wrapper APIs for:
- udev library context lifecycle and running check.
- `lvm_getpagesize()`.
- `/dev/urandom` reads.
- unbiased bounded `rand_r` helper.

Dependencies:
- `<stddef.h>`.

Role:
- Portability and optional-feature abstraction for LVM utility code.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/lvm-wrappers.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/sharedlib.c -->
# File Research: sources/block-storage/lvm2/lib/misc/sharedlib.c

This file resolves configured shared library/plugin paths.

API:
- `get_shared_library_path(struct cmd_context *cmd, const char *libname, char *path, size_t path_len)`.

Behavior:
- Empty or NULL `libname` yields empty path.
- Absolute `libname` is used as-is.
- Relative `libname` is first tried under `cmd->lib_dir`, initialized from `global_library_dir`.
- If the constructed path cannot be statted, falls back to copying `libname`.

Dependencies:
- Config lookup, command context, `stat()`.

Role:
- Used for monitor/plugin DSO path resolution.

Risk:
- A missing file under `global_library_dir` silently falls back to the original string, leaving final resolution to later loader code.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/sharedlib.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/sharedlib.h -->
# File Research: sources/block-storage/lvm2/lib/misc/sharedlib.h

This header declares:
- `get_shared_library_path()`.

Dependencies:
- `<stddef.h>` and forward-declared `cmd_context`.

Role:
- Shared interface for resolving DSO/plugin library paths.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/sharedlib.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/misc/util.h -->
# File Research: sources/block-storage/lvm2/lib/misc/util.h

This header defines common compiler, math, bit, version, and printf-format utilities.

Content:
- GCC analyzer suppression pragmas for fd, leak, and buffer warnings.
- Type-checking `min()` and `max()` macros.
- `is_power_of_2()`.
- Checked `_dm_strncpy()` wrapper marked `warn_unused_result`.
- `clz()` and `clzll()` using builtins or portable fallbacks.
- `ffs()` fallback requirement.
- `KERNEL_VERSION()`.
- Portable printf format macro aliases such as `FMTu64`, `FMTsize_t`, `FMTVGID`.

Dependencies:
- `libdm/libdevmapper.h`.

Correctness notes:
- `min`/`max` use GNU statement expressions and type comparison tricks.
- Fallback `clz()` returns 32 for zero; `clzll()` returns 64 for zero via fallback path.

Role:
- Widely included low-level helper header.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/misc/util.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/mm/memlock.c -->
# File Research: sources/block-storage/lvm2/lib/mm/memlock.c

This file manages memory locking and process priority around device suspension and daemon critical paths.

Build modes:
- Without `DEVMAPPER_SUPPORT`, all APIs are inert stubs.
- With `DEVMAPPER_SUPPORT`, full memory locking, map filtering, priority management, and debug mmap trapping are enabled.

Main APIs:
- Critical sections: `critical_section_inc()`, `critical_section_dec()`, `critical_section()`, `prioritized_section()`.
- Daemon locking: `memlock_inc_daemon()`, `memlock_dec_daemon()`, `memlock_count_daemon()`.
- Lifecycle: `memlock_init()`, `memlock_reset()`, `memlock_unlock()`.

Implementation details:
- Preallocates/touches stack and heap reserves to reduce allocation during suspended-device windows.
- Locks memory either with `mlockall(MCL_CURRENT|MCL_FUTURE)` or by parsing `/proc/self/maps` and calling `mlock()` on selected readable mappings.
- Filters mappings with built-in blacklist or configured `activation_mlock_filter`.
- Skips expected uncommitted anonymous `ENOMEM` regions.
- Can temporarily patch `mmap`/`mmap64` to `hlt` in debug x86 builds to catch mmap during locked sections.
- Raises process priority on prioritized/critical entry and restores when possible.

Dependencies:
- Command context/config, `/proc/self/maps`, `mlock`, `munlock`, `mlockall`, resource limits, glibc `mallinfo`/`mallinfo2`, activation suspended counter, profile loading.

Correctness notes:
- Only reason `"suspending"` enters true critical section and locks memory; other reasons raise priority only.
- Memory remains locked after leaving critical section until `memlock_unlock()` if no daemon lock remains.
- Daemon memlock forces `mlockall()` so future thread memory remains resident.
- `memlock_reset()` is required after fork-like daemon contexts.

Risks:
- Map parsing and blacklist coverage are platform-sensitive.
- Preallocation behavior is glibc-specific and disabled for valgrind.
- Incorrect counter balance can leave memory locked or priority raised.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/mm/memlock.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/mm/memlock.h -->
# File Research: sources/block-storage/lvm2/lib/mm/memlock.h

This header declares memory-lock/critical-section APIs.

Key contract:
- Inside a critical section, memory is locked.
- After leaving, memory remains locked until `memlock_unlock()`.
- `memlock_reset()` clears state after forking/polldaemon use.

APIs:
- `critical_section_inc/dec()`, `critical_section()`, `prioritized_section()`.
- `memlock_inc_daemon()`, `memlock_dec_daemon()`, `memlock_count_daemon()`.
- `memlock_init()`, `memlock_reset()`, `memlock_unlock()`.

Role:
- Used by activation and daemon paths to avoid swap-related deadlocks while devices are suspended.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/mm/memlock.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/mm/xlate.h -->
# File Research: sources/block-storage/lvm2/lib/mm/xlate.h

This header provides endian conversion compatibility macros.

Behavior:
- On Linux, includes `<endian.h>` and `<byteswap.h>`.
- On non-Linux, includes `<machine/endian.h>` and defines `bswap_16/32/64`.
- For Coverity, undefines endian macros so fallback definitions look used.
- Defines `htobe16`, `htole16`, `be16toh`, `le16toh`, and 32/64-bit variants if missing, depending on `BYTE_ORDER`.

Role:
- Backward compatibility for older glibc and non-glibc systems.

Risks:
- Relies on `BYTE_ORDER`, `LITTLE_ENDIAN`, and integer types being available through included platform headers/project includes.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/mm/xlate.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/notify/lvmnotify.c -->
# File Research: sources/block-storage/lvm2/lib/notify/lvmnotify.c

This file implements optional D-Bus notifications to `lvmdbusd`.

Build modes:
- With `NOTIFYDBUS_SUPPORT`, uses systemd `sd-bus`.
- Without it, notification APIs are stubs and `lvmnotify_is_supported()` returns 0.

Main APIs:
- `lvmnotify_is_supported()`.
- `lvmnotify_send(struct cmd_context *cmd)`.
- `set_vg_notify()`, `set_lv_notify()`, `set_pv_notify()`.

Behavior:
- Notification flags on `cmd` are coalesced; if none are set, no action is taken.
- Before sending, flags are cleared.
- `lvmdbusd_running()` checks the daemon lock file, using `LVM_DBUSD_LOCKFILE` env override or `/var/lock/lvm/lvmdbusd`, and determines running state by lock availability.
- `lvmnotify_send()` avoids starting the daemon implicitly, opens system bus, calls `ExternalEvent` with the command name, parses integer result, and logs warnings only for unexpected failures.

Dependencies:
- `cmd_context`, `get_cmd_name()`, sd-bus, lock file protocol used by lvmdbusd.

Correctness notes:
- Unexpected lock-file errors are treated as “daemon running” to avoid missing notifications.
- Known service-not-present errors are debug-level only.

Risks:
- Notifications are best-effort; failures do not fail the LVM command path.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/notify/lvmnotify.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/notify/lvmnotify.h -->
# File Research: sources/block-storage/lvm2/lib/notify/lvmnotify.h

This header declares D-Bus notification helpers:
- `lvmnotify_is_supported()`.
- `lvmnotify_send()`.
- `set_vg_notify()`, `set_lv_notify()`, `set_pv_notify()`.

Dependencies:
- Forward-declared `cmd_context`.

Role:
- Command code uses this to mark VG/LV/PV changes and send a coalesced external event.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/notify/lvmnotify.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/properties/prop_common.c -->
# File Research: sources/block-storage/lvm2/lib/properties/prop_common.c

This file implements generic property get/set dispatch.

Main APIs:
- `prop_not_implemented_get()`, `prop_not_implemented_set()` log `ENOSYS`.
- `prop_get_property()`.
- `prop_set_property()`.

Behavior:
- Both dispatchers linearly scan a sentinel-terminated `struct lvm_property_type` array by `id`.
- `prop_get_property()` validates requested type mask, copies the descriptor to the caller’s `prop`, then invokes the property getter.
- `prop_set_property()` validates existence, settable flag, and type mask, copies string or integer value from caller prop into descriptor, then invokes setter.

Dependencies:
- `prop_common.h`, logging with errno.

Risks:
- Property arrays must be sentinel-terminated with `id[0] == 0`.
- Setter copies only string/integer union members; signed integer fields depend on compatible representation/usage.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/properties/prop_common.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/properties/prop_common.h -->
# File Research: sources/block-storage/lvm2/lib/properties/prop_common.h

This header defines common property infrastructure and report-field-to-property macros.

Content:
- `struct lvm_property_type` with type mask, id, flags for settable/string/integer/signed, value union, getter, setter.
- Prototypes for generic get/set and not-implemented handlers.
- Macros to generate numeric, signed numeric, and string property getter/setter functions.
- Field type constants: `STR`, `NUM`, `BIN`, `SIZ`, `PCT`, `TIM`, `SNUM`, `STR_LIST`.
- `FIELD_MODIFIABLE`.
- `FIELD(...)` macro that maps report field definitions into property descriptors.

Role:
- Bridges report column definitions and property API machinery.

Risks:
- Heavy macro use means field definitions must match expected naming conventions for `_id_get` and `_id_set`.
- `FIELD` encodes string/integer/signed flags from field type; adding a new field type requires updating this mapping.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/properties/prop_common.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/raid/raid.c -->
# File Research: sources/block-storage/lvm2/lib/raid/raid.c

This file defines device-mapper RAID segment types and their handler operations.

Main entry points:
- `_raid_ops`: display, text import/export, target status compatibility, target line generation, percent, target present, transient status, modules needed, dmeventd hooks, destroy.
- `raid_is_available()`.
- Initialization: `init_raid_segtypes()` or shared `init_multiple_segtypes()`.

Behavior:
- Text import accepts either `device_count` or `stripe_count`, reads RAID attributes (`region_size`, `stripe_size`, `data_copies`, recovery rates, writebehind, data_offset), and imports metadata/data LV pairs.
- Text export distinguishes raid0-style `stripe_count`/`raid0_lvs` from parity/mirror `device_count`/`raids`.
- `_raid_add_target_line()` builds `dm_tree_node_raid_params_v2`, including raid type, mirrors/stripes/data copies, region size, stripe size, rebuild bitmap, writemostly bitmap, recovery rates, reshape delta disks, data offset, and `DM_NOSYNC`.
- `_raid_target_percent()` parses device-mapper raid status and updates progress.
- `_raid_transient_status()` validates active kernel dev count, checks meta/data LV existence, marks dead devices as `PARTIAL_LV`, and updates VG partial state.
- `_raid_target_present()` probes raid target version and exposes feature flags for raid10, raid0, shrinking, rebuild+emptymeta, reshape, and raid4 support.
- `raid_is_available()` implements degraded-availability policy for raid0, raid1, raid4/5, raid6, and raid10.

Segment types:
- Registers raid0, raid0_meta, raid1, raid10, raid10_near, raid4, raid5 variants, and raid6 variants.
- raid0/raid0_meta are never monitored; other raid types may get dmeventd DSO monitoring.

Dependencies:
- Device-mapper raid target, text import/export, activation/status, dmeventd, segment allocation and registration, metadata LV classification.

Correctness notes:
- Kernel MD/dm-raid limits area count to `DEFAULT_RAID_MAX_IMAGES`.
- Raid4 support is excluded for target version 1.8 and 1.9.0.
- Raid10 availability checks one live leg per mirror group using current two-copy assumption.
- Import treats `_rmeta_` LVs as optional metadata devices preceding data devices.

Risks:
- Reshape delta plus/minus flags are mutually exclusive and checked at target-line generation.
- Area pair import depends on naming convention `_rmeta_`.
- Feature gating is cached statically, so target version changes during process lifetime are not re-evaluated.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/raid/raid.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/report/columns-cmdlog.h -->
# File Research: sources/block-storage/lvm2/lib/report/columns-cmdlog.h

This header defines report columns for command log reporting through repeated `FIELD(...)` macro invocations.

Columns:
- `log_seq_num`: numeric sequence.
- `log_type`: log type.
- `log_context`: current context.
- `log_object_type`: current object type.
- `log_object_name`: current object name.
- `log_object_id`: current object ID.
- `log_object_group`: current object group.
- `log_object_group_id`: current object group ID.
- `log_message`: log message.
- `log_errno`: signed errno.
- `log_ret_code`: signed return code.

Role:
- Included by report/property generation code with `FIELD` defined by the includer.

Risks:
- This is not standalone C; include context must define `FIELD`, type identifiers such as `CMDLOG`, and display helpers.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/report/columns-cmdlog.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/report/columns-devtypes.h -->
# File Research: sources/block-storage/lvm2/lib/report/columns-devtypes.h

This header defines report columns for the `devtypes` reporting command via `FIELD(...)` macros.

Columns:
- `devtype_name`: device type name as it appears in `/proc/devices`.
- `devtype_max_partitions`: maximum partitions/minors reserved for each device.
- `devtype_description`: device type description.

Role:
- Include-time column definition consumed by LVM report infrastructure.

Risks:
- Like other column headers, it depends on an includer-provided `FIELD` macro and matching display functions/types.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/report/columns-devtypes.h -->