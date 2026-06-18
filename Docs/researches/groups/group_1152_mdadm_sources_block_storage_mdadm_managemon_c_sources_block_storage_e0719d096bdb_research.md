# Group Research: group_1152_mdadm_sources_block_storage_mdadm_managemon_c_sources_block_storage_e0719d096bdb

Scope: `Docs/research_subset_a.md` (`sources/block-storage/mdadm`).

This group covers mdadm/mdmon command orchestration, external metadata monitoring, runtime array map persistence, shared option/layout mappings, Linux md userspace/kernel ABI headers, and the primary mdadm/mdadm.conf manual sources.

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/managemon.c -->
# File Research: sources/block-storage/mdadm/managemon.c

## Role
`managemon.c` implements the mdmon management thread for containers using external metadata. It handles blocking and allocation-heavy work that the monitor thread avoids: discovering new member arrays, reacting to container disk changes, assigning spares to degraded arrays, replacing active-array snapshots, and receiving metadata update messages from external mdadm processes.

## Major Responsibilities
- Maintains `struct active_array` instances for arrays within an external-metadata container.
- Watches `/proc/mdstat` through `manage()` and compares it with mdmon’s in-memory container/array model.
- Adds newly appeared container disks into metadata with `add_disk_to_container()`.
- Removes missing container disks from metadata with `remove_disk_from_container()`.
- Opens sysfs attributes needed by monitor-side polling through `sysfs_open2()` and `disk_init_and_add()`.
- Handles member-array lifecycle: new discovery, degraded-array spare activation, reshape device discovery, level changes, linear/raid0 removal from monitoring, and member disk removal.
- Queues metadata updates through `update_queue_pending`, `update_queue`, and `update_queue_handled`.
- Accepts mdmon socket messages in `read_sock()` and converts them into metadata updates or ping/control actions.
- Coordinates replacement of active-array structures with the monitor thread using `replace_array()`, `pending_discard`, `discard_this`, and SIGUSR1 wakeups.

## Control Flow
`do_manager()` is the long-running loop. When no metadata update is actively being consumed, it reads mdstat, calls `manage()`, accepts at most one socket client via `read_sock()`, frees mdstat, removes old replaced arrays, promotes pending metadata updates, marks the manager ready, wakes the monitor during shutdown, and waits on mdstat/socket or signal state.

`manage()` iterates mdstat entries. The container entry is sent to `manage_container()`, while container member arrays are matched by metadata version and either passed to `manage_member()` or discovered through `manage_new()`.

`manage_new()` builds an `active_array` from sysfs, opens per-device and per-array sysfs files, parses the external subarray instance, initializes safemode handling, captures reshape checkpoints for already-reshaping arrays, asks the metadata handler to open/manage the new instance, and replaces any victim placeholder in the container array list.

`manage_member()` refreshes runtime sysfs details, honors frozen/sync-active states, updates level changes, lowers safe-mode delay during SIGTERM shutdown, removes requested member disks after monitor descriptors are no longer in use, activates metadata-provided spares for degraded arrays, queues resulting metadata updates, waits for updates to drain, replaces the array snapshot, and starts recovery. It also handles reshape-triggered new device discovery and array-size restoration.

## Important Invariants
- The manager never mutates the monitor’s live active-array object in place for structural changes; it duplicates and replaces it.
- `duplicate_aa()` skips devices with invalid `state_fd`, so disk removal invalidates future clones.
- Monitor wakeups are sent with `tgkill(..., SIGUSR1)` to the monitor thread id.
- Degraded spare assignment is skipped while metadata updates are pending to avoid decisions based on stale metadata.
- Disk removal waits for monitor descriptors to be unused before writing `remove` through a newly opened sysfs descriptor, avoiding a kernel suspend deadlock noted in comments.

## Risks
The file has delicate cross-thread ownership. File descriptors may be shared with clones unless `container` is cleared, and replacement/discard sequencing relies on monitor cooperation. Several paths continue after partial sysfs open failures, so future changes need to preserve the “monitor only ready arrays” behavior enforced by `aa_ready()`.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/managemon.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/mapfile.c -->
# File Research: sources/block-storage/mdadm/mapfile.c

## Role
`mapfile.c` maintains mdadm’s runtime map from md kernel device names to metadata type, array UUID, and user-facing device path. It is primarily used by incremental assembly and udev naming so partially assembled arrays can be tracked consistently.

## File Format
The map file is line-oriented and space-separated: md device name, metadata string, UUID as four colon-separated 32-bit hex words, and path, typically under `/dev/md/`. Default paths are derived from `MAP_DIR` and `MAP_FILE`; companion `.new` and `.lock` files provide atomic writes and locking.

## Major Functions
- `open_map()` opens the requested map, new-map, lock, or directory path and creates the map directory when needed.
- `map_write()` writes non-bad entries to the `.new` file, checks stream errors, and atomically renames it over the live map.
- `map_lock()` opens/flocks the lock file, detects stale unlinked lock files, frees any caller-supplied map, and reloads the map.
- `map_unlock()` unlinks and closes the lock and frees the caller’s map.
- `map_fork()` closes inherited lock state around fork without flushing.
- `map_add()`, `map_read()`, `map_free()`, `map_update()`, `map_delete()`, and `map_remove()` implement list and persistence operations.
- `map_by_uuid()`, `map_by_devnm()`, and `map_by_name()` perform lookups and mark entries `bad` when `mddev_busy()` shows the md device is no longer active.
- `RebuildMap()` reconstructs the map by reading mdstat, probing component superblocks, deriving array identity, selecting a stable `/dev/md/` path, writing the map, and triggering sysfs change uevents for active arrays.

## Important Invariants
Writers use `.new` plus `rename()` for atomic replacement. The lock file is unlinked before close by the lock owner. Bad/stale entries are skipped on write, allowing lookups to lazily prune dead mappings. `map_read()` attempts `RebuildMap()` if the map cannot be opened.

## Risks
The map is runtime state, not authoritative metadata. It can be stale, missing, or rebuilt from incomplete system state. Naming decisions depend on homehost policy and mdadm.conf matching, so changes in config parsing can affect udev-visible array names.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/mapfile.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/maps.c -->
# File Research: sources/block-storage/mdadm/maps.c

## Role
`maps.c` centralizes string-to-number and number-to-string mappings for mdadm concepts: RAID levels, layouts, command modes, faulty personalities, consistency policies, sysfs array states, and supported update options.

## Mappings
- `r5layout[]` maps RAID5 layouts including left/right symmetric/asymmetric, parity-first/last, abbreviations, and DDF-compatible names.
- `r6layout[]` maps RAID6 layouts including RAID5-compatible names, DDF rotating layouts, and intermediate `*-6` layouts used during conversion.
- `r0layout[]` captures RAID0 layout compatibility names for the Linux 3.14 layout bug: original, alternate, numeric aliases, and dangerous.
- `pers[]` maps RAID personality names and synonyms to md level constants.
- `modes[]` maps command mode names to mdadm mode constants.
- `faultylayout[]`, `consistency_policies[]`, `sysfs_array_states[]`, and `update_options[]` map faulty injection modes, consistency policies, sysfs states, and `--update=` names.

## Functions
`map_num()` returns the first mapping name for a numeric value or `NULL`. `map_num_s()` is the assert-backed variant for required values. `map_name()` returns the numeric value for a string, or the terminal entry’s sentinel value.

## Risks
Name ordering matters because `map_num()` uses the first matching numeric value as canonical display text. Adding a new update/layout/policy option requires coordinated parser, implementation, and documentation changes.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/maps.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/md5.h -->
# File Research: sources/block-storage/mdadm/md5.h

## Role
`md5.h` declares the MD5 digest API and context structure imported from GNU libc-style code. It provides mdadm with a local MD5 interface when not using libc-internal names.

## API Surface
The header declares `struct md5_ctx` plus `__md5_init_ctx()`, `__md5_process_block()`, `__md5_process_bytes()`, `__md5_finish_ctx()`, `__md5_read_ctx()`, `__md5_stream()`, and `__md5_buffer()`. Outside `_LIBC`, the `__md5_*` names are macro-aliased to public `md5_*` names.

## Portability Support
It conditionally includes integer headers, defines `__GNUC_PREREQ`, `__THROW`, and `__attribute__` compatibility helpers, and uses `uint32_t` as `md5_uint32`.

## Important Invariants
Digests are written in little-endian byte order. `__md5_process_block()` requires 64-byte-multiple input. Some result buffers must be correctly aligned for 32-bit access.

## Risks
MD5 is cryptographically broken for security use. In mdadm context this header should be treated as a compatibility/checksum facility, not as a secure hash primitive.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/md5.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/md_p.h -->
# File Research: sources/block-storage/mdadm/md_p.h

## Role
`md_p.h` defines the physical on-disk layout for Linux md RAID metadata and related journal/PPL structures. It is a userspace copy of kernel-facing md format definitions used by mdadm when reading, writing, examining, or updating native metadata.

## Native Superblock Layout
The file defines v0.90-style reserved geometry and superblock sizing: `MD_RESERVED_BYTES`, apparent-size macros, 4096-byte superblock dimensions, section offsets, descriptor counts, and `MD_SB_MAGIC`.

`mdp_disk_t` describes one member device. `mdp_super_t` is the full native superblock with constant identity fields, state fields, event/checkpoint/reshape fields, personality layout/chunk fields, disk descriptors, reserved space, and the this-disk descriptor. `md_event()` combines event words into a 64-bit counter.

## Constants
The header defines disk state bits such as faulty, active, sync, removed, clustered add/candidate, write-mostly, failfast, replacement, and journal. It defines role sentinels for spare, faulty, journal, and max regular role. Superblock state bits cover clean, errors, bad-block metadata errors, container reshape blocking, volume blocking, clustered md, and bitmap presence.

## RAID5 Journal and PPL Structures
It defines packed RAID5 log structures for payload headers, data/parity payloads, flush payloads, and `r5l_meta_block`, plus `R5LOG_VERSION` and `R5LOG_MAGIC`. It also defines PPL header entries, capacity macros, and `struct ppl_header`.

## Risks
Structure layout and packing are ABI/format contracts. Any casual refactor can corrupt on-disk compatibility and must be treated as a kernel/userland format change.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/md_p.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/md_u.h -->
# File Research: sources/block-storage/mdadm/md_u.h

## Role
`md_u.h` defines the ioctl interface and userspace structures for communication between mdadm and the Linux md kernel driver. It is the operational ABI counterpart to `md_p.h`’s on-disk format definitions.

## Ioctl Definitions
Status ioctls include `RAID_VERSION`, `GET_ARRAY_INFO`, `GET_DISK_INFO`, `RAID_AUTORUN`, and `GET_BITMAP_FILE`.

Configuration ioctls include `ADD_NEW_DISK`, `HOT_REMOVE_DISK`, `SET_ARRAY_INFO`, `SET_DISK_FAULTY`, and `SET_BITMAP_FILE`.

Lifecycle ioctls include `RUN_ARRAY`, `STOP_ARRAY`, `STOP_ARRAY_RO`, `RESTART_ARRAY_RW`, and `CLUSTERED_DISK_NACK`.

## Structures
`mdu_version_t` reports kernel md version. `mdu_array_info_t` carries array identity, version, creation time, level, size, disk counts, preferred minor, state counters, layout, and chunk size. `mdu_disk_info_t`, `mdu_start_info_t`, `mdu_bitmap_file_t`, and `mdu_param_t` carry disk, bitmap path, and run parameters.

## Risks
These definitions are legacy ABI contracts with the kernel. Changing structure definitions or ioctl constants would break compatibility. New code should prefer sysfs where mdadm already does, but these definitions remain necessary.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/md_u.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/mdadm.8.in -->
# File Research: sources/block-storage/mdadm/mdadm.8.in

## Role
`mdadm.8.in` is the primary manual page source for the `mdadm` command. It documents supported RAID concepts, command modes, options, operational workflows, environment variables, examples, device naming, and related files.

## Major Content Areas
The manual describes supported md personalities, container metadata, modes, global options, create/build/grow geometry and consistency options, assemble identity and recovery options, manage operations, misc operations, incremental and monitor modes, grow-mode workflows, environment variables, examples, file references, portable name rules, device naming, output interpretation, and related links/manpages.

## Integration With Code
This manual corresponds closely to option parsing in `mdadm.c` and mapping definitions in `maps.c`. Placeholder tokens such as `{DEFAULT_METADATA}`, `{CONFFILE}`, `{CONFFILE2}`, and `{MAP_PATH}` are substituted at build/install time. Documented update options match `update_options[]`, documented modes match `modes[]`, and layout/policy names match mapping tables.

## Important Operational Semantics
- Auto-assembly uses config, homehost, metadata type policy, and device discovery to choose names and whether arrays are local or foreign.
- Grow operations can be destructive or non-reversible; the manual emphasizes filesystem resizing, array-size staging, and backup-file requirements.
- Backup files are required for several reshape cases and must be supplied on assemble after crashes.
- Monitor mode can send mail, run alert programs, log to syslog, move spares by spare-group or policy domain, and integrate with systemd mdmonitor service.
- Incremental mode is designed for hotplug/udev, maintains `{MAP_PATH}`, and can start arrays when enough devices arrive or later via `--incremental --run --scan`.

## Risks
This file is the user-facing contract. Parser behavior, accepted option values, and mode constraints in `mdadm.c` should remain synchronized with it. Grow and force sections document high-risk operations where inaccurate wording could lead to data loss.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/mdadm.8.in -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/mdadm.c -->
# File Research: sources/block-storage/mdadm/mdadm.c

## Role
`mdadm.c` is the main command-line entry point for mdadm. It parses global and mode-specific options, validates cross-option constraints, initializes context/shape/identity state, opens target md devices where needed, checks privilege and cluster locks, and dispatches to the mode implementations in other source files.

## Primary State
`main()` builds and mutates `mode`, `struct context c`, `struct shape s`, `struct mddev_ident ident`, and `struct mddev_dev *devlist`. Together these represent the selected command mode, runtime policy, array geometry, identity, and ordered device/disposition list.

## Helper Functions
- `set_bitmap_value()` validates `--bitmap=` values and sets bitmap type, including cluster defaults.
- `shape_set_logical_block_size()` parses and range-checks `--logical-block-size=`.
- `scan_assemble()` assembles arrays from config, repeatedly handling dependency/stacking cases, and optionally auto-assembles homehost arrays.
- `misc_scan()` applies detail or wait-clean to mdstat-listed arrays.
- `stop_scan()` repeatedly stops mdstat-listed arrays until no progress is possible.
- `misc_list()` dispatches per-device misc operations.
- `SetAction()` writes a requested sysfs `sync_action`.

## Option Parsing
The parser first handles mode-independent options, then determines or verifies the command mode, then processes mode-specific options using `O(mode,opt)` pairs. It enforces single-use options, validates numeric ranges, maps textual values through `maps.c`, and rejects invalid combinations early.

Notable validations include mode conflicts, build-level restrictions, layout parsing by level, `--update=` restrictions, `--backup-file` versus `--data-offset`, logical block size only for metadata 1.x, write journal only for RAID4/5/6, PPL only for RAID5, bitmap/consistency-policy compatibility, and superuser checks.

## Mode Dispatch
- `MANAGE`: readonly state, subdevice operations, run/stop.
- `ASSEMBLE`: direct assembly, config-derived assembly, listed scan assembly, or full config/auto scan.
- `BUILD`: validates no bitmap/write-behind misuse and calls `Build()`.
- `CREATE`: validates clustered bitmap/node restrictions, default bitmap prompting, and calls `Create()`.
- `MISC`: dispatches examine, detail-platform, scan stop/detail/wait-clean, udev rules, or per-device misc operations.
- `MONITOR`: validates devices or scan, daemon/pid constraints, default delay from config, and calls `Monitor()`.
- `GROW`: handles apparent array-size changes, add-device grow, bitmap changes, continue, reshape, and consistency-policy changes.
- `INCREMENTAL`: handles map rebuild, scan/run, fail/remove, or normal incremental add.
- `AUTODETECT`: calls kernel autodetect.

## Important Invariants
Mode must be known before interpreting most options. The first device is the md array for manage/build/create/grow and non-scan assemble. Device dispositions are stateful: options such as `--add`, `--fail`, `--remove`, `--replace`, and `--with` affect following device arguments. Clustered arrays require DLM locking before operations that can affect clustered state.

## Risks
This file is a dense compatibility parser. Small changes can alter longstanding CLI behavior, implicit mode selection, or dangerous-operation safeguards. Any new option needs updates across long option tables, short option mode sets, parser validation, dispatch code, mappings if textual, and `mdadm.8.in`.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/mdadm.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/mdadm.conf.5.in -->
# File Research: sources/block-storage/mdadm/mdadm.conf.5.in

## Role
`mdadm.conf.5.in` is the manual page source for mdadm’s configuration file. It defines file syntax, supported directives, auto-assembly policy, alert settings, creation defaults, hotplug policy, sysfs defaults, monitoring delay, encryption verification overrides, probing options, default config file locations, and examples.

## Syntax Rules
The file is parsed as whitespace-separated words. `#` starts a comment from that word to end of line. Single or double quotes protect whitespace. Lines beginning with whitespace continue the previous line. Empty lines are ignored. Keywords are case-insensitive and can generally be abbreviated to three characters, with noted exceptions.

## Directives
- `DEVICE`: devices/patterns to scan, or `containers` and `partitions`; defaults to `DEVICE partitions containers`.
- `ARRAY`: identifies arrays by device name or `<ignore>`, then identity tags such as `uuid=`, `super-minor=`, `devices=`, `level=`, `num-devices=`, `spares=`, `spare-group=`, `bitmap=`, `metadata=`, `container=`, and `member=`.
- `MAILADDR`, `MAILFROM`, and `PROGRAM`: monitor alert configuration.
- `CREATE`: defaults for owner, group, mode, metadata, names, and bad-block-list behavior.
- `HOMEHOST` and `HOMECLUSTER`: host and cluster identity defaults.
- `AUTO`: metadata/homehost auto-assembly allow/deny policy.
- `POLICY` and `PART-POLICY`: hotplug and spare migration policy by domain, metadata, path, type, action, and auto.
- `SYSFS`: sysfs attribute defaults applied after assembly by uuid or name.
- `MONITORDELAY`: default monitor polling delay.
- `ENCRYPTION_NO_VERIFY`: disables selected encryption verification, currently `sata_opal` for IMSM contexts.
- `PROBING`: probe behavior options such as extended DDF header scanning.

## Policy Semantics
`POLICY` and `PART-POLICY` describe what mdadm may do automatically for newly appearing devices. Actions are ordered by permissiveness: include, re-add, spare, spare-same-slot, and force-spare. Domains allow spare migration when destination domains contain the new disk’s domains or arrays share a spare group.

## Integration With Code
The directives documented here are consumed by mdadm config parsing and used by `mdadm.c`, `mapfile.c`, incremental assembly, monitor spare migration, udev rule generation, create defaults, and sysfs post-assembly configuration.

## Risks
Configuration behavior affects unattended boot, hotplug, spare migration, and alerting. Documentation must stay synchronized with parser keyword names and policy implementation, especially for automatic actions that can add bare disks or migrate spares.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/mdadm.conf.5.in -->