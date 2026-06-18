# Group Research: group_1151_mdadm_sources_block_storage_mdadm_Manage_c_sources_block_storage_md_2bd7b1e423ef

Scope: `Docs/research_subset_a.md`, source tree `sources/block-storage/mdadm`.

This grouped report covers mdadm array management, query/help/config support, bitmap handling, CRC helpers, linked-list utilities, drive-encryption probing, and clustered md RAID1/RAID10 test scripts.

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/Manage.c -->
# File Research: sources/block-storage/mdadm/Manage.c

## Purpose
`Manage.c` implements mdadm's live md-array management operations: run, stop, read-only/read-write transitions, hot add, spare add, journal add, re-add, fail, remove, replace, preferred replacement, subarray update, spare migration, and kernel autodetect.

## Main Flow
`Manage_subdevs()` is the central dispatcher. It reads array/sysfs metadata, identifies the array supertype, expands special operands such as `failed`, `faulty`, `detached`, `missing`, and `set-X`, resolves target devices to major/minor or sysfs member attributes, freezes sync when needed, then dispatches by disposition character.

`Manage_add()` validates the candidate device, loads or copies metadata, tries optimized re-add for recently removed members, writes new superblocks when needed, and finally adds through `ADD_NEW_DISK` or external-metadata `sysfs_add_disk()`.

`Manage_stop()` obtains exclusive access, coordinates with mdmon-managed arrays and containers, handles reshape pause/retry logic, issues `STOP_ARRAY`, removes mdadm-created device links, and updates the mdadm map.

## Key Behavior
- `Manage_ro()` handles native arrays with ioctls and external subarrays through `metadata_version`, `array_state`, and mdmon signaling.
- Re-add compares member UUIDs and disk state, optionally updates write-mostly/failfast/superblock fields, and sets clustered add/candidate flags.
- External metadata add uses metadata-handler validation, drive policies, metadata sync/mdmon notification, and sysfs disk insertion.
- Journal add requires a read-only array and attempts to return the array to read-write afterward.
- Faulting a device is guarded by `is_remove_safe()`, which checks remaining synced slots against md redundancy rules.
- Clustered md has special handling for candidate confirmation, cluster add flags, and `CLUSTERED_DISK_NACK`.
- `Update_subarray()` validates active-state restrictions, delegates to metadata-specific update hooks, and flushes or syncs metadata.
- `move_spare()` removes a spare from one array, adds it to another, and rolls back if destination add fails.

## Integration Notes
This file depends on mdadm core helpers, sysfs md attributes, md ioctls, metadata supertype methods, mdmon signaling, map-file locking, udev state, policy checks, and kernel md member state names.

## Risks
This file coordinates live kernel state, raw component devices, metadata handlers, and mdmon, so race handling is central. Sensitive areas include exclusive-open retry windows, reshape freeze/unfreeze behavior, cleanup after partial superblock writes, clustered flags, and preserving return codes for test mode and busy devices.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/Manage.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/Query.c -->
# File Research: sources/block-storage/mdadm/Query.c

## Purpose
`Query.c` implements `mdadm --query`, a brief classifier for md arrays and component devices.

## Behavior
`Query()` opens a device, checks whether it is an active md array using sysfs first and md ioctls as fallback, prints array size/level/device/spare summary, then guesses and loads any member superblock to report component membership.

For component devices, it extracts superblock UUID and disk information, looks up active arrays by UUID in the mdadm map, and reports whether the component appears active, inactive, mismatched, or undetected.

## Integration Notes
It uses `sysfs_read()`, `md_get_array_info()`, `guess_super()`, metadata `load_super/getinfo_super/uuid_from_super`, map lookup by UUID, and md disk info ioctls.

## Risks
The output is intentionally heuristic. Stale map entries, missing sysfs data, or inaccessible active md devices can produce `undetected` or `mismatch` even when the component superblock is valid.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/Query.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/ReadMe.c -->
# File Research: sources/block-storage/mdadm/ReadMe.c

## Purpose
`ReadMe.c` centralizes mdadm version text, command-line option tables, short-option strings, and user-facing help text.

## Contents
It defines:
- `Version`, defaulting to mdadm `4.6` and date `2026-03-16`.
- Short option strings for normal, monitor, bitmap, and bitmap-auto parsing.
- `long_options[]`, mapping major modes and flags to getopt tokens.
- General and mode-specific help text for create, build, assemble, manage, misc, monitor, grow, incremental, and config.
- `mode_help[]`, selecting help by mdadm mode.
- `fprint_update_options()`, which prints valid `--update` or `--update-subarray` options from `update_options`.

## Integration Notes
This file is both parser metadata and CLI documentation. Option token values are consumed by mdadm's main parser, while help strings define visible behavior and aliases such as `--monitor`/`--follow`, `--daemonise`/`--daemonize`, and deprecated `--auto`.

## Risks
Option definitions and help text can drift from parser behavior elsewhere. Because this file owns option registration, missing entries can make implemented functionality unreachable from the CLI.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/ReadMe.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/bitmap.c -->
# File Research: sources/block-storage/mdadm/bitmap.c

## Purpose
`bitmap.c` reads, displays, creates, checks, and updates md bitmap files or internal bitmap areas on member devices.

## Main Flow
`bitmap_file_open()` opens a block device with `O_DIRECT`, guesses metadata if needed, and calls metadata `locate_bitmap()` for a selected clustered node slot.

`bitmap_fd_read()` reads the bitmap superblock into aligned memory, converts little-endian fields, and, unless brief mode is requested, counts total and dirty bitmap bits.

`ExamineBitmap()` prints bitmap metadata, UUID, event counters, chunk size, write mode, sync size, dirty-bit percentage, and clustered node details. `IsBitmapDirty()` checks clustered bitmap nodes for dirty bits. `CreateBitmap()` writes a bitmap superblock and initializes all chunks dirty. `bitmap_update_uuid()` rewrites the bitmap UUID in place.

## Key Behavior
- Dirty-bit counting treats truncated bitmap files as warnings and only counts readable bits.
- Clustered bitmaps iterate node slots and reopen/relocate through metadata hooks.
- Default chunk size grows until the number of chunks remains near the intended limit.
- Created bitmap payload is initialized to `0xff`, marking chunks dirty until synced.

## Integration Notes
The file uses `bitmap_super_t` from `bitmap.h`, metadata-specific bitmap location hooks, mdadm UUID formatting/swapping rules, and common size-formatting helpers.

## Risks
`O_DIRECT` requires aligned reads. Clustered-node iteration reuses descriptors and metadata guesses carefully. `CreateBitmap()` writes regular bitmap files, while examination expects block/member devices.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/bitmap.h -->
# File Research: sources/block-storage/mdadm/bitmap.h

## Purpose
`bitmap.h` defines md bitmap superblock constants and the on-disk bitmap superblock layout.

## Contents
It declares bitmap major versions, including clustered and lockless versions, `BITMAP_MAGIC`, bitmap state bit values, and `bitmap_super_t`.

The superblock stores magic, version, UUID, event counters, sync size, state, chunk size, daemon sleep interval, write-behind count, reserved sectors, clustered node count, cluster name, and padding to 256 bytes.

## Integration Notes
Fields are little-endian on disk and converted by `bitmap.c`. The layout matches kernel md bitmap expectations.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/00r10_Create -->
# File Research: sources/block-storage/mdadm/clustermd_tests/00r10_Create

## Purpose
Tests clustered RAID10 creation and assembly across two nodes.

## Behavior
The script creates clustered RAID10 arrays with normal sync, assume-clean, spare-device, and named-array variants. It assembles on `NODE2`, verifies resync/PENDING behavior when appropriate, checks RAID10 type, clustered bitmap presence, clean state, member state, spare count, name propagation, and dmesg cleanliness, then stops the array on all nodes.

## Integration Notes
It relies on `func.sh`, shared variables such as `$md0`, `$dev0`-`$dev2`, `$NODE1`, `$NODE2`, and remote `ssh` execution.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/00r10_Create -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/00r1_Create -->
# File Research: sources/block-storage/mdadm/clustermd_tests/00r1_Create

## Purpose
Tests clustered RAID1 creation and assembly across two nodes.

## Behavior
The script creates clustered RAID1 arrays in normal, assume-clean, spare-device, and named-array forms. It assembles on `NODE2`, verifies resync/PENDING behavior, RAID1 identity, clustered bitmap, no active sync after wait, member state, spare count, name visibility, and clean dmesg output.

## Integration Notes
It mirrors the RAID10 creation test but targets RAID1 mirror behavior.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/00r1_Create -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/01r10_Grow_bitmap-switch -->
# File Research: sources/block-storage/mdadm/clustermd_tests/01r10_Grow_bitmap-switch

## Purpose
Tests bitmap policy transitions for clustered RAID10.

## Behavior
The script creates an assume-clean clustered RAID10 array, stops it on `NODE2`, switches bitmap mode from clustered to none, verifies member bitmaps disappear, switches none to internal, verifies internal bitmap creation, switches internal to none, then switches none back to clustered and reassembles on `NODE2`.

It verifies clustered bitmap metadata by checking `mdadm -X` output for `Cluster name` on all nodes.

## Integration Notes
This exercises `mdadm --grow --bitmap=` transitions and clustered bitmap visibility across nodes.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/01r10_Grow_bitmap-switch -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/01r10_Grow_resize -->
# File Research: sources/block-storage/mdadm/clustermd_tests/01r10_Grow_resize

## Purpose
Tests clustered RAID10 grow operations for size and chunk changes.

## Behavior
The first scenario creates RAID10 with a small explicit size, grows to max, waits for resync, shrinks back to the original size, and verifies state. The second scenario creates RAID10 with 64 KiB chunks, grows chunk size to 128 KiB, waits for reshape, then verifies chunk size, member state, and dmesg cleanliness.

## Integration Notes
The script validates grow behavior on `NODE1` while the clustered array is assembled on both nodes.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/01r10_Grow_resize -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/01r1_Grow_add -->
# File Research: sources/block-storage/mdadm/clustermd_tests/01r1_Grow_add

## Purpose
Tests adding clustered RAID1 mirror members through grow operations.

## Behavior
The script covers three RAID1 grow cases:
- Grow from two to three raid devices while adding a new disk.
- Grow from two active plus one spare to three active while adding another disk.
- Grow from two active plus one spare to three active without an explicit add disk, consuming the spare.

Each case waits for recovery on whichever node reports it, verifies final `UUU` state, checks dmesg, and stops the array.

## Integration Notes
Recovery may appear on either local or remote node, so the script probes `/proc/mdstat` and checks the appropriate node.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/01r1_Grow_add -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/01r1_Grow_bitmap-switch -->
# File Research: sources/block-storage/mdadm/clustermd_tests/01r1_Grow_bitmap-switch

## Purpose
Tests bitmap policy transitions for clustered RAID1.

## Behavior
The script creates an assume-clean clustered RAID1 array, switches clustered bitmap to none, none to internal, internal to none, and none back to clustered. It verifies bitmap disappearance/creation with `mdadm -X`, checks `/proc/mdstat` bitmap state, reassembles on `NODE2`, confirms `Cluster name` in bitmap output on all nodes, and verifies final state.

## Integration Notes
This is the RAID1 counterpart of the RAID10 bitmap-switch test.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/01r1_Grow_bitmap-switch -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/01r1_Grow_resize -->
# File Research: sources/block-storage/mdadm/clustermd_tests/01r1_Grow_resize

## Purpose
Tests clustered RAID1 size grow and shrink.

## Behavior
The script creates a clustered RAID1 array with an explicit small size, grows it to max, waits for resync, shrinks it back to the original size, verifies no sync is active, checks final state and dmesg, and stops the array.

## Integration Notes
This focuses on size changes only; RAID1 has no chunk reshape path here.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/01r1_Grow_resize -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/02r10_Manage_add -->
# File Research: sources/block-storage/mdadm/clustermd_tests/02r10_Manage_add

## Purpose
Tests clustered RAID10 `--manage --add` behavior.

## Behavior
The first scenario fails and removes one RAID10 member, zeros a replacement disk, adds it, waits for recovery, and verifies restored `UU` state. The second scenario adds an extra disk to a healthy array and verifies it becomes a spare.

## Integration Notes
This validates both replacement-add and spare-add behavior through the generic `--add` path.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/02r10_Manage_add -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/02r10_Manage_add-spare -->
# File Research: sources/block-storage/mdadm/clustermd_tests/02r10_Manage_add-spare

## Purpose
Tests clustered RAID10 `--manage --add-spare`.

## Behavior
The script creates a healthy clustered RAID10 array, adds one spare, verifies spare count, then repeats with an initial spare and adds a second spare. Each scenario checks RAID10 identity, bitmap state, member state, spare count, and dmesg.

## Integration Notes
This isolates explicit spare addition from replacement recovery.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/02r10_Manage_add-spare -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/02r10_Manage_re-add -->
# File Research: sources/block-storage/mdadm/clustermd_tests/02r10_Manage_re-add

## Purpose
Tests clustered RAID10 re-add of a recently failed and removed member.

## Behavior
The script creates a clustered RAID10 array, fails and removes one device, re-adds the same device, waits, verifies final `UU` state, checks dmesg, and stops the array. A comment notes that even non-clustered arrays may avoid a visible sync job for this re-add path.

## Integration Notes
This targets mdadm's re-add optimization and clustered metadata handling.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/02r10_Manage_re-add -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/02r1_Manage_add -->
# File Research: sources/block-storage/mdadm/clustermd_tests/02r1_Manage_add

## Purpose
Tests clustered RAID1 `--manage --add` behavior.

## Behavior
The first scenario fails/removes a member, zeros a replacement, adds it, waits for recovery, and verifies restored state. The second scenario adds an extra disk to a healthy RAID1 and verifies it becomes a spare.

## Integration Notes
This is the RAID1 counterpart of the RAID10 manage-add test.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/02r1_Manage_add -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/02r1_Manage_add-spare -->
# File Research: sources/block-storage/mdadm/clustermd_tests/02r1_Manage_add-spare

## Purpose
Tests clustered RAID1 `--manage --add-spare`.

## Behavior
The script adds one spare to a healthy RAID1 array, then repeats with an array already containing one spare and adds a second. It verifies spare counts, RAID1 identity, clustered bitmap, `UU` member state, and dmesg cleanliness.

## Integration Notes
This validates explicit spare growth without failing members.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/02r1_Manage_add-spare -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/02r1_Manage_re-add -->
# File Research: sources/block-storage/mdadm/clustermd_tests/02r1_Manage_re-add

## Purpose
Tests clustered RAID1 re-add of a failed and removed member.

## Behavior
The script creates a clustered RAID1 array, fails and removes one member, re-adds the same device, waits for completion, verifies `UU` state, checks dmesg, and stops the array.

## Integration Notes
This exercises the optimized same-device re-add path for clustered mirrors.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/02r1_Manage_re-add -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/03r10_switch-recovery -->
# File Research: sources/block-storage/mdadm/clustermd_tests/03r10_switch-recovery

## Purpose
Tests clustered RAID10 recovery ownership transfer between nodes.

## Behavior
The script creates RAID10 with a spare, fails one active device to start remote recovery, stops the array on `NODE1`, verifies recovery continues on `NODE2`, waits for completion, checks `UU` state, checks dmesg, and stops the remaining node.

## Integration Notes
This targets clustered md failover during recovery.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/03r10_switch-recovery -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/03r10_switch-resync -->
# File Research: sources/block-storage/mdadm/clustermd_tests/03r10_switch-resync

## Purpose
Tests clustered RAID10 resync ownership transfer between nodes.

## Behavior
The script creates a non-assume-clean clustered RAID10 array, confirms resync on `NODE1` and PENDING on `NODE2`, stops `NODE1`, verifies resync continues on `NODE2`, waits, reassembles on `NODE1`, and verifies clean RAID10 bitmap state.

## Integration Notes
This covers initial resync failover rather than replacement recovery.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/03r10_switch-resync -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/03r1_switch-recovery -->
# File Research: sources/block-storage/mdadm/clustermd_tests/03r1_switch-recovery

## Purpose
Tests clustered RAID1 recovery ownership transfer between nodes.

## Behavior
The script creates RAID1 with a spare, fails one active device, waits for remote recovery visibility, stops `NODE1`, verifies recovery continues on `NODE2`, waits for completion, verifies `UU` state, checks dmesg, and stops `NODE2`.

## Integration Notes
This is the RAID1 counterpart of the RAID10 recovery-switch test.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/03r1_switch-recovery -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/03r1_switch-resync -->
# File Research: sources/block-storage/mdadm/clustermd_tests/03r1_switch-resync

## Purpose
Tests clustered RAID1 initial resync ownership transfer.

## Behavior
The script creates a non-assume-clean clustered RAID1 array, checks resync on `NODE1` and PENDING on `NODE2`, stops `NODE1`, verifies `NODE2` takes over resync, waits, reassembles on `NODE1`, and verifies RAID1 bitmap, no sync, `UU` state, and clean dmesg.

## Integration Notes
This validates clustered md resync failover for mirrors.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/03r1_switch-resync -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/func.sh -->
# File Research: sources/block-storage/mdadm/clustermd_tests/func.sh

## Purpose
`func.sh` is the shared harness for clustered mdadm tests.

## Main Flow
It validates the two-node environment, discovers test devices, ensures cluster/DLM services are available, manages cleanup, saves logs, stops arrays locally or remotely, controls RAID sync speed limits, and provides common assertions over `/proc/mdstat`, `mdadm`, and `dmesg`.

## Key Behavior
- `check_ssh()` reads `NODE1`/`NODE2` from `$CLUSTER_CONF` and requires passwordless root SSH.
- `fetch_devlist()` supports either configured device lists or iSCSI target discovery, removes SBD devices, exports `dev0`, `dev1`, etc., and requires at least six disks.
- `check_dlm()` creates Pacemaker DLM resources if absent and verifies `dlm_controld`.
- `check_env()` requires root, built mdadm, required commands, required kernel modules, and no pre-existing RAID arrays.
- `stop_md()` stops all arrays or a specific md device on one or both nodes.
- `save_log()` copies logs, clears/saves dmesg, captures `/proc/mdstat`, `mdadm -D`, bitmap examination, and superblock examination.
- `check()` implements assertions for spares, RAID level strings, recovery/resync/reshape/PENDING, wait completion, bitmap/nobitmap, chunk size, member state, no sync, readonly state, and dmesg errors.

## Integration Notes
The test scripts source this file and rely on global variables for nodes, devices, mdadm path, log paths, and speed-limit settings. The harness assumes Pacemaker/crm, DLM, md-cluster, ssh, and shared block devices.

## Risks
The harness is environment-sensitive and destructive: it stops md arrays and zeroes devices. Some checks parse human-readable `/proc/mdstat` and may be brittle across kernel output changes.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/clustermd_tests/func.sh -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/config.c -->
# File Research: sources/block-storage/mdadm/config.c

## Purpose
`config.c` parses mdadm configuration files and exposes configuration-derived device lists, array identities, monitor settings, create defaults, homehost/homecluster, auto-assembly policy, probing flags, and encryption verification settings.

## Main Flow
`load_conffile()` loads the selected config file, fallback Debian config, and `.d` directory entries. `conf_file_or_dir()` handles a regular file or sorted `.conf` directory entries. `conf_file()` reads logical lines through `conf_line()` and dispatches by keyword.

Line handlers parse:
- `DEVICE` into scan patterns, `partitions`, or `containers`.
- `ARRAY` into `mddev_ident` entries with UUID, device name, metadata, bitmap, device patterns, spare group, container/member, and compatibility fields.
- `CREATE` into ownership, group, mode, metadata, names, and bad-block defaults.
- `AUTO` into metadata auto-assembly policy rules.
- monitor mail/program/from/delay settings.
- `HOMEHOST`, `HOMECLUSTER`, `POLICY`, `PART-POLICY`, `SYSFS`, `ENCRYPTION_NO_VERIFY`, and `PROBING`.

## Key Behavior
- Device-name validation accepts md numbered devices, `/dev/md/<name>`, `md_<name>`, bare names, and config-only `<ignore>`.
- `conf_get_devs()` defaults to `/proc/partitions` plus external containers when no DEVICE lines exist, otherwise expands configured globs.
- `AUTO` supports `yes`, `no`, `homehost`, `+metadata`, `-metadata`, `+all`, `-all`, and prepends `MDADM_CONF_AUTO` environment tokens.
- `conf_test_metadata()` evaluates auto-assembly policy with `yes`, `homehost`, and `no` precedence.
- `conf_match()` matches loaded superblock info against ARRAY lines by UUID, device patterns, super-minor, and identity presence, rejecting ambiguous matches.
- `conf_verify_devnames()` detects duplicate configured md names.

## Integration Notes
The file uses the local `dlink` word-list abstraction from `lib.c` tokenization, global policy helpers, metadata supertype matchers, mdstat/map helpers, glob/fnmatch, `/proc/partitions`, and external container discovery.

## Risks
Configuration state is stored globally and loaded once. Parser leniency preserves compatibility but can hide bad lines. `AUTO` policy ordering is significant, and config/device glob expansion affects assembly behavior system-wide.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/config.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/coverity-gcc-hack.h -->
# File Research: sources/block-storage/mdadm/coverity-gcc-hack.h

## Purpose
`coverity-gcc-hack.h` supplies fake `_Float*` typedefs for Coverity's GCC model on x86_64.

## Behavior
When outside the kernel, on x86_64, and Coverity reports GCC version at least 7.0, it typedefs `_Float128`, `_Float64`, `_Float32`, and extended variants as vector-sized `float` types.

## Integration Notes
This is a static-analysis compatibility shim, not runtime mdadm logic.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/coverity-gcc-hack.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/crc32.c -->
# File Research: sources/block-storage/mdadm/crc32.c

## Purpose
`crc32.c` provides a zlib-derived CRC-32 implementation used by mdadm metadata code.

## Main Flow
The file can either generate CRC tables dynamically or include the generated `crc32.h` table. `get_crc_table()` returns the table. `crc32()` updates a supplied CRC seed over a byte buffer, with optional word-at-a-time big/little-endian paths when `BYFOUR` is enabled.

In this source, `NOBYFOUR` is defined, so the byte-wise table path is used unless compile configuration changes.

## Integration Notes
The code is adapted from zlib, carries zlib license text, and defines local zlib compatibility macros/types. It intentionally does not apply initial/final XOR in `crc32()`, leaving callers to choose seed/finalization conventions.

## Risks
If `DYNAMIC_CRC_TABLE` is enabled, table generation is only weakly protected against concurrency as noted in the source. Caller seed/final-XOR expectations must match the metadata format being checked.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/crc32.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/crc32.h -->
# File Research: sources/block-storage/mdadm/crc32.h

## Purpose
`crc32.h` is a generated lookup-table header for fast CRC-32 calculation.

## Contents
It defines `crc_table[TBLS][256]` as `local const unsigned long FAR`, with the base 256-entry CRC table and conditional additional tables for `BYFOUR`.

## Integration Notes
The header is included directly by `crc32.c` when dynamic CRC table generation is disabled. It depends on `local`, `FAR`, and `TBLS` being defined by the including source.

## Risks
This is generated data; hand edits risk corrupting CRC results. The conditional `BYFOUR` sections must stay in sync with `crc32.c` table-generation logic.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/crc32.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/crc32c.c -->
# File Research: sources/block-storage/mdadm/crc32c.c

## Purpose
`crc32c.c` implements bitwise CRC32, CRC32C, and big-endian CRC32 helpers.

## Behavior
`crc32_le_generic()` computes little-endian CRC with a supplied polynomial. `crc32_le()` uses the Ethernet AUTODIN II polynomial, and `crc32c_le()` uses the Castagnoli CRC32C polynomial. `crc32_be_generic()` and `crc32_be()` implement big-endian Ethernet CRC32.

## Integration Notes
The file is kernel-derived GPLv2 code adapted for mdadm. It uses Linux integer types and takes caller-supplied seed values without imposing final XOR semantics.

## Risks
The implementation is simple and portable but bitwise, so it is slower than table-driven CRC. Callers must choose the correct polynomial and seed/finalization convention.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/crc32c.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/dlink.c -->
# File Research: sources/block-storage/mdadm/dlink.c

## Purpose
`dlink.c` implements a small hidden-header doubly linked list allocation helper used by mdadm parsers.

## Behavior
`dl_alloc()` allocates hidden prev/next header space before the returned payload. `dl_head()` creates a circular sentinel. `dl_init()` initializes a payload as a circular list node. `dl_insert()` inserts after the head; `dl_add()` appends before the head; `dl_del()` unlinks a node and nulls its links. `dl_free()` frees the hidden allocation, and `dl_free_all()` frees a whole list. `dl_strdup()` and `dl_strndup()` allocate string payload nodes.

## Integration Notes
The config parser uses these lists to represent logical lines and words. Allocation uses mdadm's `xcalloc()`.

## Risks
The API relies on callers passing pointers returned by `dl_alloc`/`dl_strdup`, because metadata lives immediately before the payload pointer. Passing ordinary memory corrupts memory or frees invalid pointers.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/dlink.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/dlink.h -->
# File Research: sources/block-storage/mdadm/dlink.h

## Purpose
`dlink.h` declares and macro-defines mdadm's hidden-header doubly linked list API.

## Contents
It defines `struct __dl_head`, allocation macros `dl_alloc`, `dl_new`, `dl_newv`, accessor macros `dl_next` and `dl_prev`, and function prototypes for list creation, insertion, deletion, freeing, initialization, and string duplication.

## Integration Notes
The macros require `xcalloc()` to be visible in the including compilation unit.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/dlink.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/drive_encryption.c -->
# File Research: sources/block-storage/mdadm/drive_encryption.c

## Purpose
`drive_encryption.c` probes NVMe and ATA/SATA drives for encryption ability and lock status, including Opal self-encrypting drives and ATA standard security.

## Main Flow
For NVMe, `get_nvme_opal_encryption_information()` checks optional admin command support, checks supported security protocols, reads Opal Level 0 discovery with `NVME_IOCTL_ADMIN_CMD`, and extracts the Opal locking feature.

For ATA/SATA, `get_ata_encryption_information()` reads ATA identify data through SG_IO ATA PASS-THROUGH(12), optionally verifies Opal support through trusted-computing/security-protocol checks, requires `libata.allow_tpm=1` unless disabled by config, then either parses Opal Level 0 discovery or falls back to ATA security status.

## Key Behavior
- Encryption ability maps to `None`, `Other`, or `SED`.
- Encryption status maps to `Unencrypted`, `Locked`, or `Unlocked`.
- Opal locking feature parsing follows variable-length discovery feature records and uses big-endian feature codes/lengths.
- NVMe support is gated by OACS bit 0 and security protocol `0x01`.
- ATA standard security reports `Other` ability when ATA security is supported but Opal is not confirmed.
- SATA Opal verification can be skipped by `ENCRYPTION_NO_VERIFY sata_opal` config.
- ATA pass-through validates SG status, driver/host status, and both descriptor and fixed-format sense data.

## Integration Notes
The file uses Linux NVMe ioctls, SCSI generic `SG_IO`, ATA PASS-THROUGH sense validation, mdadm verbose logging, fd-to-kernel-name helpers, sysfs libata TPM checks, and config accessors.

## Risks
The probing path depends on device/driver support and can fail on permission, kernel config, libata TPM policy, or transport translation quirks. The code uses packed bitfields over endian-converted words, so compiler/layout assumptions matter.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/drive_encryption.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/drive_encryption.h -->
# File Research: sources/block-storage/mdadm/drive_encryption.h

## Purpose
`drive_encryption.h` declares mdadm's drive encryption status model and probe API.

## Contents
It defines `encryption_status_t`, `encryption_ability_t`, `encryption_information_t`, and declarations for NVMe Opal probing, ATA probing, and string mapping helpers.

## Integration Notes
Metadata display code can call these helpers to report member drive encryption state without depending on the ioctl details in `drive_encryption.c`.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/drive_encryption.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/mdadm/lib.c -->
# File Research: sources/block-storage/mdadm/lib.c

## Purpose
`lib.c` contains shared mdadm utility functions for device-name mapping, config tokenization, quoted output, string/name validation, environment checks, numeric parsing, and small math/hostname helpers.

## Key Behavior
- `is_string_lq()` validates non-empty strings shorter than a limit including NUL space.
- Device helpers map `dev_t`, `stat`, or fd values to kernel names and md dev names through `/sys/dev/block`, with md major fallbacks.
- `/dev` scanning via `nftw()` builds a major/minor map; `map_dev_preferred()` chooses preferred, shortest, `/dev/md/`, or caller-preferred paths, and can fall back to `major:minor`.
- `conf_word()` tokenizes config/mdstat-style words with comments, quotes, indentation rules, and compatibility fixes for old `(auto-read-only)` mdstat output.
- `conf_line()` builds a dlink word list for one logical config line; `free_line()` releases it.
- `print_quoted()` emits strings with quotes only when needed.
- `is_name_posix_compatible()` enforces POSIX portable filename characters and forbids leading `-`.
- `parse_num()` safely parses non-negative `int` values.
- `s_gethostname()` wraps `gethostname()` and forces NUL termination.

## Integration Notes
This file is foundational for config parsing, mdstat parsing, metadata display, and device discovery. It uses `dlink`, `xmalloc`, sysfs paths, `/proc/devices`, and POSIX file tree walking.

## Risks
`map_dev_preferred()` caches `/dev` scans globally and refreshes only on miss. Several helpers return static buffers, so callers must copy results if they need stable storage across calls.
<!-- END FILE RESEARCH: sources/block-storage/mdadm/lib.c -->