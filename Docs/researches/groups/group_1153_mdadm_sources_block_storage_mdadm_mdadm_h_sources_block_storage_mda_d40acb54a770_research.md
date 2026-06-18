# Group Research: group_1153_mdadm_sources_block_storage_mdadm_mdadm_h_sources_block_storage_mda_d40acb54a770

Scope: `Docs/research_subset_a.md` (`sources/block-storage/mdadm`).

This group covers mdadm shared declarations, mdmon external-metadata monitoring, mdmonitor alerting/spare migration, `/proc/mdstat` parsing, md device creation/opening, mdmon messaging, Intel IMSM platform capability discovery, and device policy handling.

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/mdadm.h -->
# File Research: sources/block-storage/mdadm/mdadm.h

## Role

`mdadm.h` is the central internal header for mdadm. It establishes compile feature macros, platform defaults, common data structures, metadata-handler contracts, sysfs/ioctl helpers, command entry points, policy APIs, mdmon hooks, cluster hooks, RAID constants, and small utility inlines.

## Major Contents

- Defines runtime paths and service names such as `DEV_DIR`, `DEV_NUM_PREF`, `DEV_MD_DIR`, `MAP_DIR`, `MDMON_DIR`, `FAILED_SLOTS_DIR`, `MDMON_SERVICE`, and `GROW_SERVICE`.
- Includes Linux md headers, common mdadm headers, libc/system headers, and optional Corosync/DLM compatibility shims.
- Defines portable helpers for unaligned access, type-checked `min`/`max`, timer comparisons, byte/sector conversion, fd validation, level checks, safe fd close, `signal_s()`, debug logging, and `xasprintf()`.
- Defines the core `struct mdinfo`, carrying generic array, disk, UUID, name, size, reshape, bitmap/PPL, consistency, sysfs, bad-block, mdmon state, and linked-list device information.
- Defines command/config structures: `createinfo`, `spare_criteria`, `mddev_ident`, `context`, `shape`, `mddev_dev`, `mdstat_ent`, `map_ent`, `dev_policy`, `pol_rule`, `domainlist`, `metadata_update`, `supertype`, and `superswitch`.
- Centralizes command mode enums, special getopt values, update modes, bitmap modes, sysfs read flags, member state mapping, policy actions, RAID level/layout constants, resync sentinel values, and maximum disk limits.

## Metadata Contract

The `struct superswitch` table is the central plugin interface for metadata formats. It covers metadata examination, export, bad-block inspection, copy/detail/platform reporting, UUID extraction, generic info extraction, homehost matching, metadata updates, superblock initialization, add/remove/store/write/load/compare/free operations, geometry validation, bitmap/PPL handling, drive policy validation, container enumeration, subarray update/delete, reshape handling, mdmon lifecycle hooks, spare activation, backup recovery, and bad-block record/clear/list operations.

This contract is used by native metadata, IMSM, DDF, MBR, and GPT handlers and is also the bridge between normal mdadm commands and mdmon.

## Public Surfaces Declared

- `/proc/mdstat`: `mdstat_read()`, wait helpers, lookup helpers, and external/subarray predicates.
- Map file handling: add/update/remove/read/write/lock/unlock and UUID/devnm/name lookup.
- Sysfs: read/write attribute helpers, member state setters, `sysfs_read()`, device add, freeze, wait, fd/string/integer accessors, bad-block/device helpers, and reshape backup helpers.
- Command entry points: `Manage_*`, `Grow_*`, `Assemble`, `Build`, `Create`, `Detail`, `Monitor`, `Kill`, `Wait`, `WaitClean`, `Incremental`, bitmap operations, metadata dump/restore.
- Device helpers: md array ioctl wrappers, parsing, size/sector helpers, md device open/create helpers, path/name translation, mdmon process/socket helpers, systemd continuation, random UUID generation, initrd detection.
- Policy helpers: config policy parsing, disk/path policy, domain matching, udev rule generation, failed-slot persistence, and metadata-specific drive policy checks.
- Cluster hooks for Corosync cmap and DLM.

## Invariants and Risks

- Metadata strings are normalized through `superlist`/`superswitch` names; policy and metadata code depend on pointer-stable names for fast comparisons.
- `struct mdinfo` is reused for array-level, disk-level, sysfs, and mdmon state; callers must know which fields are valid for the read flags or metadata handler used.
- `MAX_DISKS` bounds broad monitor/policy loops and is intentionally larger than current metadata format limits.
- `is_subarray()` encodes mdadm’s convention that external subarrays have metadata versions beginning with `/` or `-`.
- Many declarations assume Linux md sysfs and ioctl semantics; this header is a portability layer only within mdadm’s supported Unix/Linux build variants.

<!-- END FILE RESEARCH: sources/block-storage/mdadm/mdadm.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/mdadm_status.h -->
# File Research: sources/block-storage/mdadm/mdadm_status.h

## Role

`mdadm_status.h` defines the small common status enum used by newer mdadm helper functions.

## API

`mdadm_status_t` has five values:

- `MDADM_STATUS_SUCCESS`
- `MDADM_STATUS_ERROR`
- `MDADM_STATUS_UNDEF`
- `MDADM_STATUS_MEM_FAIL`
- `MDADM_STATUS_FORKED`

## Dependency Notes

The header is guarded and standalone. It is included by `mdadm.h`, which makes the status type available to sysfs, policy, platform, systemd, and metadata helper declarations.

<!-- END FILE RESEARCH: sources/block-storage/mdadm/mdadm_status.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/mdmon.c -->
# File Research: sources/block-storage/mdadm/mdmon.c

## Role

`mdmon.c` is the entry point for the mdmon daemon, which manages arrays with user-space external metadata. It validates the target container, loads its metadata handler, creates pid/socket control files, starts the high-priority monitor worker, and runs the manager loop.

## Main Flow

- Parses `--all`, `--takeover`, `--foreground`, `--offroot`, and `--help`.
- In `--all` mode, scans `/proc/mdstat` and starts mdmon for each external metadata container that is not a subarray.
- Resolves user-supplied container names to md kernel names and validates them through `open_mddev()`.
- `mdmon()` opens the container, optionally forks and reports startup status to the parent, reads sysfs metadata/version/device information, verifies the array is an external-metadata container, and maps the metadata string to a `superswitch`.
- Copies container component device info into `container->devs`, blocks `SIGUSR1`/`SIGTERM`, configures signal handlers, and checks for an existing mdmon.
- On takeover, removes old pid/socket files, creates a new pid file and nonblocking Unix-domain control socket, locks memory with `mlockall()`, starts the monitor worker with pthreads or `clone()`, then runs `do_manager()`.

## Process and IPC Behavior

- `make_pidfile()` writes `${MDMON_DIR}/${devnm}.pid`.
- `make_control_sock()` creates `${MDMON_DIR}/${devnm}.sock` with restrictive umask and nonblocking mode.
- `try_kill_monitor()` verifies an old process looks like mdmon, sends `SIGTERM`, waits for socket closure, and pokes it with `SIGUSR1` while it exits.
- The monitor side is launched either as a detached pthread or a shared address-space `clone()` thread, with shared files, filesystem context, VM, and signal handlers in clone mode.

## Special Handling

- `imsm_set_no_platform(1)` suppresses IMSM platform complaints from mdmon; mdadm proper owns user-facing platform diagnostics.
- If running from initrd, the first character of `argv[0]` is set to `@` so systemd can preserve the task during shutdown.
- Provides stub implementations for reshape/stripe helpers and native `super0`/`super1` symbols so metadata code can link in the mdmon binary.

## Invariants and Risks

- mdmon only accepts containers with external metadata: sysfs level `UnSet`, major version `-1`, minor version `-2`.
- Control paths are fixed-size buffers around `MDMON_DIR`; md device names are constrained by `MD_NAME_MAX`.
- Startup uses a parent/child pipe so foreground command execution knows whether daemon setup succeeded.
- Existing mdmon takeover is race-sensitive and relies on pidfile/socket validation plus metadata loading before replacing the old monitor.

<!-- END FILE RESEARCH: sources/block-storage/mdadm/mdmon.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/mdmon.h -->
# File Research: sources/block-storage/mdadm/mdmon.h

## Role

`mdmon.h` is the shared internal header for the mdmon manager and monitor implementation.

## Key Types

- `enum array_state` maps md sysfs `array_state` words used by mdmon.
- `enum sync_action` maps md sysfs `sync_action` words.
- `struct active_array` tracks one active subarray/member array in a container: generic `mdinfo`, owning container, replacement/discard links, sysfs fds, checkpoint state, previous/current/next array and sync states, and manager notification flags.
- Declares global metadata update queues: `update_queue` and `update_queue_handled`.

## Declared Interfaces

The header declares `do_monitor()`, `do_manager()`, `remove_pidfile()`, `read_dev_state()`, mdstat helpers, process/thread globals, termination flags, and monitor loop counters.

## Important Inline

`is_resync_complete()` computes completion for RAID1/4/5/6 and RAID10 by comparing `resync_start` with the relevant component/sync size. It handles RAID10 copy geometry from layout bits.

## Invariants

- Monitor and manager share address space and coordinate through globals and `SIGUSR1`.
- `struct active_array` stores open sysfs descriptors because mdmon reacts to sysfs poll/select events rather than repeatedly reopening attributes.
- Completion math only handles levels known to mdmon; unsupported levels leave `sync_size` zero.

<!-- END FILE RESEARCH: sources/block-storage/mdadm/mdmon.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/mdmonitor.c -->
# File Research: sources/block-storage/mdadm/mdmonitor.c

## Role

`mdmonitor.c` implements the user-facing mdadm monitor mode. It watches md arrays for state changes, emits alerts through stderr, syslog, mail, or an external program, discovers new arrays in scan mode, supports spare migration across spare groups/domains, and implements `Wait`/`WaitClean`.

## Monitor State

`struct state` records one monitored md device: full `/dev/md/...` name, kernel devnm, parent container devnm, subarray/container links, spare group, active/working/failed/spare/raid counts, per-slot device state and `dev_t`, rebuild percent, expected spares, metadata supertype, and error counters.

`struct alert_info` holds hostname, mail settings, alert command, syslog flag, and test flag.

## Events

Events are mapped by `events_map` and include `SpareActive`, `NewArray`, `MoveSpare`, `TestMessage`, `RebuildStarted`, progress `RebuildNN`, `RebuildFinished`, `SparesMissing`, `DeviceDisappeared`, `Fail`, `FailSpare`, and `DegradedArray`.

Priority markers split events into info, warning, and critical syslog severities.

## Main Monitor Flow

`Monitor()`:

- Rejects incompatible explicit device list plus `--scan`.
- Loads mail/program defaults from config when not supplied.
- Requires at least mail, alert command, or syslog in scan mode.
- Creates `MDMON_DIR`, optionally daemonizes, optionally enforces single autorebuild process, and builds an initial `statelist` from mdadm.conf or explicit devices.
- Loops over `/proc/mdstat`, calls `check_array()` for each known array, auto-adds new arrays in scan mode, attempts spare migration when enabled and arrays are degraded, waits for udev events or mdstat events, and prunes repeatedly failing auto-added arrays.

## Alerting

- `alert()` builds a standardized message, writes it with `pr_err()`, optionally executes the configured alert command, sends email for selected events, and logs to syslog.
- Email includes current `/proc/mdstat` content.
- Alert command is invoked as `alert_cmd event dev disc`.

## Array Checking

`check_array()`:

- Opens the md device, maps it to a devnm, matches it with mdstat, detects containers, validates active arrays, and reads ioctl/sysfs state.
- Detects new arrays, degraded startup, missing expected spares, rebuild start/progress/finish, mismatch count after checks, device failure, failed spare, spare activation, and disappearance.
- Tracks per-disk state with `md_get_disk_info()` and preferred device paths.
- Stores container/subarray parent relationships from external metadata strings.
- Loads metadata with `super_by_fd()` for top-level arrays/containers when needed for spare migration.

## Spare Migration

- `try_spare_migration()` links containers to subarrays, finds degraded arrays without spares, builds policy domains, obtains spare criteria, and searches donor arrays/containers.
- Native arrays choose spares from per-slot md state.
- External containers reload metadata and use `container_choose_spares()`.
- Moves a spare with `move_spare()` and emits `MoveSpare`.

## Wait Helpers

- `Wait()` waits until mdstat no longer reports a resync/recovery/check/reshape for a device, pings mdmon for external arrays, and handles brief frozen states.
- `WaitClean()` waits for external subarrays to become clean, temporarily lowers safemode delay, polls `array_state`, pings mdmon so metadata is marked clean, and restores safemode delay.

## Invariants and Risks

- Scan mode depends on `/proc/mdstat` plus optional udev wait; fallback wait shortens delay after mdstat events.
- External metadata spare migration must coordinate container/subarray relationships and domain policy to avoid stealing unsuitable spares.
- `free_statelist()` frees the list and spare-group strings but not every metadata allocation; metadata lifetimes mostly follow monitor loop usage and process lifetime.
- Only redundant arrays are kept under monitoring; if no redundant array remains, monitor exits.

<!-- END FILE RESEARCH: sources/block-storage/mdadm/mdmonitor.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/mdopen.c -->
# File Research: sources/block-storage/mdadm/mdopen.c

## Role

`mdopen.c` creates, names, opens, and validates md devices for assemble/build/create workflows.

## Key Functions

- `create_named_array()` writes an md kernel devnm to `/sys/module/md_mod/parameters/new_array`.
- `find_free_devnm()` searches for an unused `mdN`, preferring high minor numbers and avoiding mdstat, config name conflicts, and existing `/dev` nodes when udev is unavailable.
- `create_mddev()` is the main allocator/creator for a new md device.
- `open_mddev()` opens a path and verifies it is an md array with `md_array_valid()`.
- `is_mddev()` wraps `open_mddev()` as a boolean path check.

## create_mddev Behavior

`create_mddev()`:

- Initializes md module parameters and optionally blocks udev for the chosen devnm.
- Accepts user names from `/dev/md/<name>`, `/dev/mdN`, `/dev/md_dN`, bare names, metadata-provided names, or no name.
- Sanitizes metadata names by replacing `/` with `-` and whitespace with `_`.
- Resolves conflicts through map lookup and numeric suffixes.
- Creates named arrays via sysfs when supported.
- Falls back to choosing a free number when explicit creation fails or no number/name is supplied.
- When udev is unavailable, creates block nodes and `/dev/md/<name>` symlinks directly using configured uid/gid/mode.
- Returns an exclusive md device fd via `open_dev_excl()`.

## Invariants and Risks

- User-supplied `/dev/...` names must be standard md names unless represented through `/dev/md/<name>`.
- `chosen` is updated to the preferred user-visible path, falling back to `/dev/mdN` when a requested symlink cannot be used.
- Direct node creation path must verify existing nodes match the expected block device to avoid using stale/wrong nodes.
- Udev blocking is only attempted when udev is available; otherwise mdadm owns node/symlink creation.

<!-- END FILE RESEARCH: sources/block-storage/mdadm/mdopen.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/mdstat.c -->
# File Research: sources/block-storage/mdadm/mdstat.c

## Role

`mdstat.c` parses `/proc/mdstat` into mdadm’s `struct mdstat_ent` linked list and provides wait/lookup helpers.

## Parser Behavior

`mdstat_read()`:

- Opens `/proc/mdstat`, or reuses a held fd when requested.
- Reads logical lines through `conf_line()` so continuation lines are folded.
- Skips `Personalities`, `read_ahead`, and `unused` lines.
- Accepts md lines whose devnm begins with `md` and is short enough for mdadm buffers.
- Extracts active/inactive state, RAID level, component member names, metadata version, raid disk count, `[UU_]` pattern, rebuild/resync/check/reshape progress, and delayed/pending/remote states.
- Reorders mdstat entries when md devices are components of other md devices, so components can appear before composites.
- Optionally reverses order for startup operations.

## Data Management

- `free_mdstat()` releases levels, patterns, metadata strings, member lists, and entries.
- `mdstat_close()` closes the held mdstat fd.
- `free_member_devnames()` and `add_member_devname()` manage component name lists.

## Lookups and Predicates

- `is_mdstat_ent_external()` detects `external:` metadata.
- `is_mdstat_ent_subarray()` detects external subarrays by checking the metadata suffix with `is_subarray()`.
- `is_container_member()` tests whether an mdstat entry belongs to a given external container.
- `mddev_busy()` checks whether a devnm appears in mdstat.
- `mdstat_find_by_member_name()`, `mdstat_by_component()`, and `mdstat_by_subdev()` find arrays by component or external subarray metadata and detach the returned entry from the temporary list.

## Waiting

- `mdstat_wait()` uses `select()` exceptional conditions on the held `/proc/mdstat` fd.
- `mdstat_wait_fd()` waits on mdstat plus another fd, using exceptional events for regular proc/sysfs-style fds and read events for non-regular fds.

## Invariants

- Returned detached entries from `mdstat_by_component()` and `mdstat_by_subdev()` must be freed by the caller with `free_mdstat()`.
- The parser is intentionally tolerant of historical mdstat formats and token order.
- `metadata_version` and member parsing are key dependencies for mdmon and mdmonitor external-array behavior.

<!-- END FILE RESEARCH: sources/block-storage/mdadm/mdstat.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/misc/mdcheck -->
# File Research: sources/block-storage/mdadm/misc/mdcheck

## Role

`misc/mdcheck` is a Bash helper intended for periodic systemd/cron execution to run md array consistency checks with optional time budgeting and checkpointing.

## Modes

- `--continue`: only continue checks that have saved `MD_UUID_*` state.
- `--start`: continue saved checks and start arrays not marked as checked.
- `--restart`: remove `Checked_*` files and exit, allowing previously finished arrays to be checked again.
- No mode: start fresh from zero on all arrays, deleting old checked and checkpoint files.

## Options

- `--duration <time-offset>` computes an end time with `date --date` and stops checks after that budget.

## Main Flow

- Logs to journald stderr when run under systemd (`INVOCATION_ID` set), otherwise uses `logger`.
- Finds md devices through `/sys/block/*/md/sync_action`.
- Skips arrays whose `sync_action` is not `idle`.
- Resolves `/dev/...` names from sysfs `uevent`.
- Uses `BINDIR/mdadm --detail --export` to obtain `MD_UUID`.
- Stores checkpoints in `/var/lib/mdcheck/MD_UUID_$UUID`; finished markers use `/var/lib/mdcheck/Checked_$UUID`.
- Writes `sync_min` and then `check` to start or resume checks.
- While under a duration budget, polls `sync_action` and `sync_completed`, updating checkpoints until all finish or time expires.
- On exit cleanup, stops still-running checks by writing `idle`, stores current `sync_min`, removes temp file, and logs pause positions.

## Invariants and Risks

- State is keyed by md UUID, not device name, so renamed arrays can continue checks.
- The script assumes md sysfs paths and mdadm export output are trustworthy local interfaces.
- `BINDIR` is expected to be substituted by the build/install environment.
- Cleanup trap is central to time-budget behavior; premature termination records restart position.

<!-- END FILE RESEARCH: sources/block-storage/mdadm/misc/mdcheck -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/misc/syslog-events -->
# File Research: sources/block-storage/mdadm/misc/syslog-events

## Role

`misc/syslog-events` is a sample shell event handler for `mdadm --follow --program=...`.

## Behavior

- Receives event, md device, and optional component disk as `$1`, `$2`, and `$3`.
- Uses syslog facility `kern` and tag `mdmonitor`.
- Maps `Fail*` events to `error`, `Test*` events to `debug`, and all others to `info`.
- Builds a short message including related disk when present.
- Executes `logger` with the selected facility/priority.

## Invariants

The script is intentionally minimal and stateless. It demonstrates the argument contract expected by mdadm monitor alert programs.

<!-- END FILE RESEARCH: sources/block-storage/mdadm/misc/syslog-events -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/monitor.c -->
# File Research: sources/block-storage/mdadm/monitor.c

## Role

`monitor.c` is the mdmon monitor-thread implementation. It watches sysfs state files for external metadata arrays, updates metadata through the active `superswitch`, handles dirty/clean transitions, records device failures and bad blocks, checkpoints reshape/sync progress, and signals the manager thread when higher-level actions are needed.

## Core Helpers

- `add_fd()` validates sysfs fds and adds them to a select fd set.
- `read_attr()`, `read_resync_start()`, `read_sync_completed()`, `read_state()`, and `read_action()` read sysfs fields.
- `read_dev_state()` maps member state words into mdadm `DS_*` flags.
- `signal_manager()` sends `SIGUSR1` to the manager thread.

## Bad-Block Handling

- `process_ubb()` records an unacknowledged bad block in external metadata, then acknowledges it to the kernel by writing back to the sysfs bad-block descriptor.
- `compare_bb()` compares kernel bad-block entries to metadata entries, recording missing entries or clearing stale metadata entries.
- `read_bb_file()` parses kernel bad-block lines of `sector length\n`.
- `process_dev_ubb()` handles unacknowledged bad blocks.
- `check_for_cleared_bb()` clears metadata bad blocks no longer present in the kernel acknowledged list.

## read_and_act()

`read_and_act()` is the monitor state machine for one active array:

- Reads current array state/action, resync start, sync completion, and per-device state/recovery.
- Marks metadata dirty on `write-pending`, `active`, or `suspended`.
- Handles `active-idle` by moving array to clean before marking metadata clean.
- Moves `readonly` arrays to `read-auto` or `active` unless metadata version begins with `external:-`.
- Detects array stop/deactivation and marks metadata clean.
- Detects resync/recovery completion and updates metadata/device state.
- Detects reshape start and requests manager reshape checks.
- Records failed devices, unblocks blocked faulty devices, requests removal when writable, and propagates degraded checks.
- Updates reshape/sync checkpoints based on `sync_completed` and `reshape_position`.
- Calls `sync_metadata()` and writes pending sysfs state/action/member changes.
- Signals the manager when degraded checks, reshape checks, or member removals are pending.

## Main Monitor Loop

`wait_and_act()`:

- Builds select sets from array state/action/sync fds and each member’s state/bad-block fds.
- Removes deactivated arrays by handing them to `discard_this` for the manager.
- Exits when no arrays remain or `SIGTERM` arrives and arrays are clean, after checking exclusive access to the container.
- Waits with `pselect()` while unblocking `SIGUSR1`.
- Processes queued metadata updates from the manager with `process_update()`.
- Calls `read_and_act()` for each active array.
- Propagates a failed physical device across other container members with `reconcile_failed()`.

`do_monitor()` repeatedly calls `wait_and_act()`, forcing an initial immediate pass.

## Invariants and Risks

- Metadata is synchronized at most once per wakeup after relevant state changes.
- Monitor must not close member descriptors while the manager is removing a disk; it marks `mon_descriptors_not_used`.
- Failure propagation is across arrays sharing the same external container and physical major/minor.
- SIGTERM exits only after dirty arrays are clean, preserving external metadata consistency.

<!-- END FILE RESEARCH: sources/block-storage/mdadm/monitor.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/msg.c -->
# File Research: sources/block-storage/mdadm/msg.c

## Role

`msg.c` implements mdmon Unix-domain socket message framing and client helpers for pinging, blocking/unblocking subarrays, freezing containers, and flushing mdmon state.

## Message Protocol

Messages are framed as:

1. 32-bit start magic `0x5a5aa5a5`
2. signed 32-bit payload length
3. optional payload bytes
4. 32-bit end magic `0xa5a55a5a`

`MSG_MAX_LEN` limits payloads to 4 MiB.

## Transport Helpers

- `send_buf()` and `recv_buf()` use `select()` with optional timeout to complete partial writes/reads.
- `send_message()` and `receive_message()` implement framing.
- `ack()` sends a zero-length message.
- `wait_reply()` receives and discards any payload.
- `connect_monitor()` connects to `${MDMON_DIR}/${container}.sock`, including parsing subarray names to find the parent container socket, and switches the socket to nonblocking mode.
- `fping_monitor()`, `ping_monitor()`, and `ping_monitor_version()` implement request/reply checks.

## Blocking and Freezing

- `block_subarray()` changes sysfs `metadata_version` from `external:/...` to `external:-...`.
- `unblock_subarray()` reverses the marker and optionally sets `sync_action` to `idle`.
- `check_mdmon_version()` ensures a running mdmon is new enough to understand blocking semantics.
- `block_monitor()` walks all subarrays in a container, optionally freezes sync action, marks them blocked, pings mdmon, verifies frozen state, and rolls back on failure.
- `unblock_monitor()` clears blocked metadata markers and pings mdmon when needed.

## Manager Coordination

- `ping_manager()` sends a metadata update message with `len = -1`, prompting the mdmon manager to observe updated container state.
- `flush_mdmon()` pings both manager and monitor, used around takeover/grow paths to drain updates.

## Invariants and Risks

- Blocking uses a single-character semantic marker in `metadata_version`; old mdmon versions can mishandle it, so version checks are mandatory.
- `block_monitor()` is rollback-oriented: any failure while freezing subarrays triggers unblocking of those already modified.
- Message framing rejects bad magic and oversized payloads but otherwise treats payloads as opaque metadata updates.

<!-- END FILE RESEARCH: sources/block-storage/mdadm/msg.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/msg.h -->
# File Research: sources/block-storage/mdadm/msg.h

## Role

`msg.h` declares the mdmon socket/message API shared by mdadm command code and mdmon implementation.

## API Surface

It declares message send/receive, acknowledgements, monitor connection/ping helpers, subarray block/unblock helpers, container block/unblock helpers, manager ping, mdmon flush, and `MSG_MAX_LEN`.

## Invariants

The header forward-declares `struct mdinfo` and `struct metadata_update`, keeping it lightweight. The implementation owns framing details in `msg.c`.

<!-- END FILE RESEARCH: sources/block-storage/mdadm/msg.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/part.h -->
# File Research: sources/block-storage/mdadm/part.h

## Role

`part.h` defines packed MBR and GPT partition table structures used by mdadm partition-detection code.

## Definitions

- MBR constants: `MBR_SIGNATURE_MAGIC`, `MBR_PARTITIONS`, and `MBR_GPT_PARTITION_TYPE`.
- `struct MBR_part_record` for a 16-byte MBR partition entry.
- `struct MBR` for the 446-byte boot area, four partition records, and signature.
- GPT constants: `GPT_SIGNATURE_MAGIC`.
- `struct GPT_part_entry` for GPT partition entry fields.
- `struct GPT` for GPT header fields and padding.

## Invariants

All structures are packed and use explicit Linux integer types/endian conversion macros. They model on-disk layouts, so padding or host-endian assumptions would be incorrect.

<!-- END FILE RESEARCH: sources/block-storage/mdadm/part.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/platform-intel.c -->
# File Research: sources/block-storage/mdadm/platform-intel.c

## Role

`platform-intel.c` discovers Intel storage controllers and IMSM/VROC/RST capabilities from sysfs, PCI option ROMs, EFI variables, ACPI UEFI tables, NVMe/VMD compatibility data, and controller registers. Metadata handlers use this to validate IMSM arrays against hardware/firmware support.

## Controller Discovery

- `find_driver_devices()` scans `/sys/bus/<bus>/drivers/<driver>` for Intel devices, supports `isci`, `ahci`, `nvme`, and `vmd`, and classifies devices as SAS, SATA, NVMe, VMD, or SATA-behind-VMD.
- VMD domains are resolved with `vmd_find_pci_bus()` and `vmd_domain_to_controller()`.
- NVMe devices behind VMD are skipped in plain NVMe discovery, while VMD controllers are included separately.
- `find_intel_devices()` caches the discovered list for 10 seconds.
- `device_by_id()` and `device_by_id_and_path()` search the cached controller list.

## OROM and Capability Discovery

- `scan()` inspects option ROM memory for Intel PCI expansion data and IMSM `$VER` capability blocks.
- `find_imsm_hba_orom()` scans legacy option ROMs unless EFI boot is detected or test modes are active.
- `imsm_platform_test()` synthesizes capabilities for test environments.
- OROM entries are stored in the global `orom_entries` list with associated device IDs.
- `find_imsm_capability()` first checks cached OROMs, then NVMe synthetic caps, EFI caps, VMD caps, and legacy OROM caps.

## EFI and ACPI Discovery

- EFI variable access supports both efivarfs and old sysfs EFI variable layouts.
- ACPI UEFI table scanning reads `/sys/firmware/acpi/tables/UEFI*`, matches controller identifiers by name and GUID, verifies table length, and extracts embedded `struct imsm_orom`.
- SATA, sSATA, tSATA, VROC VMD, and RST VMD identifiers are represented by `imsm_orom_id_t`.

## NVMe and VMD Support

- `find_imsm_nvme()` provides synthetic IMSM-compatible NVMe capabilities.
- `read_vmd_register()` reads VMD PCI config space, and `add_vmd_orom()` builds VMD capabilities from SKU/version bits.
- `find_imsm_vmd()` provides VMD compatibility capabilities.
- `get_nvme_multipath_dev_hw_path()` resolves virtual NVMe subsystem paths to hardware controller paths.
- `devt_to_devpath()` and `diskfd_to_devpath()` map block devices to sysfs device paths at requested `/device` depth.
- `imsm_is_nvme_namespace_supported()` accepts only the lowest NVMe namespace for IMSM.
- `is_multipath_nvme()` detects namespace exposure through `/sys/devices/virtual/nvme-subsystem/`.

## Attachment Helpers

- `devpath_to_vendor()`, `devpath_to_char()`, and internal `devpath_to_ll()` read sysfs controller attributes.
- `is_path_attached_to_hba()`, `devt_attached_to_hba()`, and `disk_attached_to_hba()` test whether disks are under a controller path.

## Invariants and Risks

- Intel vendor ID `0x8086` gates controller discovery.
- EFI/ACPI/OROM capability discovery is intentionally best-effort and supports environment-variable test overrides.
- VMD and NVMe paths need realpath normalization because sysfs may expose virtual layers or still-enumerating devices.
- OROM data is cached globally by device ID; callers should treat returned pointers as process-lifetime capability records.

<!-- END FILE RESEARCH: sources/block-storage/mdadm/platform-intel.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/platform-intel.h -->
# File Research: sources/block-storage/mdadm/platform-intel.h

## Role

`platform-intel.h` declares Intel IMSM platform capability structures, constants, inline capability tests, controller/device list types, and discovery helper prototypes.

## Key Structures

- `struct imsm_orom` models IMSM AHCI/SCU/NVMe/VMD capability data, including signature, version, RAID level capability, supported strip sizes, disk/volume limits, attributes, capabilities, and driver features.
- `struct imsm_level_ops` maps RAID levels to capability and disk-count validators.
- `enum sys_dev_type` classifies discovered controllers as unknown, SAS, SATA, NVMe, VMD, SATA VMD, or max.
- `struct sys_dev` records controller type, sysfs path, PCI ID, device ID, class, and list link.
- `struct efi_guid`, `struct devid_list`, and `struct orom_entry` support EFI/OROM matching and cached capability records.

## Inline Helpers

- `imsm_rlc_has_bit()` tests RAID-level capability bits.
- `imsm_orom_has_chunk()` validates power-of-two chunk sizes against OROM strip-size bits.
- `fls()` provides a local most-significant-bit helper.
- `imsm_orom_is_enterprise()`, `imsm_orom_is_nvme()`, `imsm_orom_is_vmd_without_efi()`, and `imsm_orom_has_tpv_support()` test capability signatures/features.
- `guid_str()` formats EFI GUIDs.

## Exported Interfaces

The header declares controller discovery, capability lookup, sysfs path conversion, HBA attachment tests, OROM lookup by device ID, NVMe multipath/namespace checks, and VMD domain mapping.

## Invariants

The OROM structures are packed firmware-layout definitions. Constants encode Intel IMSM/RST/VROC capability semantics and must match firmware metadata formats expected by IMSM handlers.

<!-- END FILE RESEARCH: sources/block-storage/mdadm/platform-intel.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/policy.c -->
# File Research: sources/block-storage/mdadm/policy.c

## Role

`policy.c` implements mdadm’s device policy engine. It parses config policy rules, derives policies from `/dev/disk/by-path`, metadata handlers, and failed-slot records, evaluates hotplug/spare actions and domains, and can generate udev rules for incremental assembly.

## Policy Model

A `dev_policy` is a sorted name/value/metadata tuple list. Important names are `action`, `domain`, `metadata`, and `auto`.

Rule types are `policy` and `part-policy`. Match predicates are `path` and `type`. Device types are `disk` and `part`.

## Policy Construction

- `policyline()` parses config token lists into `struct pol_rule`.
- `policy_add()` programmatically adds rules.
- `policy_free()` releases config rules and duplicate domain strings.
- `path_policy()` applies all matching rules to a path/type pair.
- `disk_policy()` derives `/dev/disk/by-path` names for a `struct mdinfo` disk and applies `path_policy()`.
- `devid_policy()` wraps `disk_policy()` for a `dev_t`.
- `pol_new()`, `pol_sort()`, and `pol_dedup()` normalize, sort, and deduplicate policy tuples.
- `pol_merge_part()` appends partition suffixes to domains for partition policy matches.

## Metadata-Specific Policy Hooks

- `drive_test_and_add_policies()` calls a metadata handler’s `test_and_add_drive_policies()` hook for one disk.
- `sysfs_test_and_add_drive_policies()` applies that hook to all member disks described by sysfs.
- `mddev_test_and_add_drive_policies()` reads member disks from an md device fd and applies the sysfs helper.

These are used by IMSM and similar metadata formats to enforce controller/hardware-specific drive policies.

## Action Evaluation

- `map_act()` maps `include`, `re-add`, `spare`, `spare-same-slot`, and `force-spare`.
- `policy_action_allows()` tests whether the strongest applicable action permits a requested action.
- `disk_action_allows()` derives disk policy and evaluates it.

Actions are ordered so stronger permissions satisfy weaker requested actions.

## Domain Evaluation

- Domains are sorted linked lists.
- `domain_merge()` adds applicable policy domains.
- `domain_test()` verifies a device’s domains are all present in a target domain list, returning `-1` when the device has no domains.
- `domainlist_add_dev()` and `domain_from_array()` build domain lists from devices or arrays.
- `domain_add()` and `domain_free()` manage explicit domain entries.

Domains drive spare migration and hotplug policy decisions.

## Failed-Slot Tracking

- `policy_save_path()` records metadata type and array UUID under `FAILED_SLOTS_DIR/<ID_PATH>` when a disk is removed.
- `policy_check_path()` looks up by-path entries for a disk and restores the associated array map entry if present.

This supports re-adding replacement disks in the same physical slot.

## Udev Rule Generation

- `Write_rules()` emits an autogenerated udev rule file or stdout.
- `generate_entries()` emits one rule per qualifying policy/part-policy path whose action is at least `spare-same-slot`.
- Rules run `BINDIR/mdadm --incremental $env{DEVNAME}` for matching block add events.

## Invariants and Risks

- Policy name constants are compared by pointer, so rules must use the canonical global strings.
- Metadata names are normalized to known `superswitch` names; unknown metadata is logged and treated as `"unknown"`.
- `/dev/disk/by-path` matching uses `fnmatch()` and optional `-partNN` suffix handling.
- `generate_entries()` is intended for bare hotplug handling, not all policies.

<!-- END FILE RESEARCH: sources/block-storage/mdadm/policy.c -->