# Group Research: group_1318_ntfs_3g_sources_local_fs_ntfs_3g_ntfsprogs_ntfsusermap_8_in_sources_3e6266a57aef

Scope checked against `Docs/research_subset_a.md`: all researched files are under `sources/local-fs/ntfs-3g`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsusermap.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsusermap.8.in

## Purpose

Manual page for `ntfsusermap`, an interactive tool that builds an NTFS-3G `UserMapping` file mapping Windows SIDs/accounts to Linux user and group IDs.

## Behavior Described

`ntfsusermap` is invoked with a Windows system NTFS device first, followed by optional other NTFS devices shared between that Windows installation and Linux. The man page states that the command must run as root and that target devices must not be mounted.

The tool scans existing NTFS files, looks for significant owners/groups, prompts the operator for Linux uid/gid mappings, and writes `UserMapping` in the current directory. That file must then be moved to `.NTFS-3G/UserMapping` at the root of every shared NTFS volume, and the volume must be remounted for the mapping to apply.

## Interface Contract

No options are defined. Exit status is documented as `0` for no detected error and `1` for detected error.

## Dependencies And Related Files

This man page corresponds to `sources/local-fs/ntfs-3g/ntfsprogs/ntfsusermap.c`. It also points users to `ntfsprogs(8)`, `attr(5)`, and `getfattr(1)`.

## Notes

The page warns not to map users to Linux root because standard Windows users such as Administrator are mapped implicitly. The AUTHORS section appears to say `ntfs-3g.secaudit` rather than `ntfsusermap`, likely a copy/paste documentation mistake.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsusermap.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsusermap.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsusermap.c

## Purpose

Interactive Windows-SID to Linux uid/gid mapper for NTFS-3G. It scans NTFS volumes through libntfs-3g security APIs, asks the operator to identify unmapped Windows owners/groups, and emits a `UserMapping` file for `.NTFS-3G`.

## Main Flow

`main()` detects whether stdout is a tty, prints a welcome message in interactive mode, validates arguments, and on Unix calls `process()`. On Windows it can also emit a minimal mapping proposal when stdout is redirected.

`process()` initializes the global linked list of mappings, opens each supplied volume read-only with `ntfs_initialize_file_security()`, scans from `/`, closes the volume, sanitizes incomplete mappings, then writes the mapping file with `outputmap()`.

`getusers()` scans for `Documents and Settings` and `Users`, then scans other root directories. Recursive traversal uses `ntfs_read_directory()` and `callback()` to skip special files (`.`, `..`, `$*`, and DOS-name type), descend a bounded number of levels, and call `account()` for candidate files.

`account()` queries `OWNER_SECURITY_INFORMATION`, `GROUP_SECURITY_INFORMATION`, and optionally `DACL_SECURITY_INFORMATION` through `ntfs_get_file_security()`. Owner/group SIDs and ACL SIDs are passed to `domapping()`.

## Core Data Structures

`struct USERMAPPING` is a global linked list node containing uid string, gid string, SID string, raw SID bytes, optional Windows login, and whether the mapping was decided.

`struct CALLBACK` carries traversal context: account name, directory, recursion depth, and directory scan state (`STATE_USERS`, `STATE_HOMES`, `STATE_BASE`).

## SID And Mapping Logic

The file contains local little-endian helpers (`get2l()`, `get4l()`, `get6h()`), a simple `decodesid()` formatter, and a `makegroupsid()` helper that rewrites the last RID to `513` for a generic domain users group.

`domapping()` only considers domain SIDs under `S-1-5-21-*`. If a SID has no final decision, or if a previous undecided mapping came from a different account name, it calls `askmapping()`.

`askmapping()` prompts for Linux uid/gid, rejects `0` and `root`, creates or updates a `USERMAPPING`, and records raw SID bytes plus decoded SID string. For a user mapping, uid and gid are set to the same input; for a group mapping, uid is empty and gid is set.

`sanitize()` requires at least one user mapping. If no group mapping exists, it asks whether to define a standard group and uses either an already discovered generic group SID or a generated group SID derived from the first owner.

## Output

`outputmap()` writes a banner and mapping records as `uid:gid:sid`. It first emits owner-only or group-only records, then records that define both owner and group. On Unix it writes `UserMapping` in the current directory and tells the user to move it to `.NTFS-3G`; on Windows it tries to create the target directory and write directly under the chosen volume.

## Dependencies

The file is tightly coupled to libntfs-3g headers and APIs: `security.h`, `volume.h`, `device.h`, `attrib.h`, `index.h`, `mft.h`, `ntfs_get_file_security()`, `ntfs_read_directory()`, `ntfs_initialize_file_security()`, and `ntfs_leave_file_security()`. It also has conditional Windows declarations for `LookupAccountNameA()` and `GetUserNameA()` because including `windows.h` conflicts with NTFS layout definitions.

## Risks And Quirks

The code uses fixed-size buffers for security descriptors (`MAXATTRSZ` 2048) and SID strings (`MAXSIDSZ` 80), with manual formatting and allocation. It assumes terminal UTF-8 and implements a limited UTF-16LE to UTF-8 conversion that does not handle surrogate pairs.

There are memory leaks in long-running terms, but this is a short-lived CLI. More importantly, `outputmap()` treats `write()` returning `0` as an error signal, but does not check partial writes correctly. The scanner also relies on heuristics and bounded recursion, so it may miss owners on unusual layouts.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsusermap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfswipe.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfswipe.8.in

## Purpose

Manual page for `ntfswipe`, a utility that overwrites unused or recoverable data areas on an NTFS volume with zeroes or selected/random bytes.

## Options Documented

The page documents wiping modes for all unused areas (`--all`), directory indexes, `$LogFile`, MFT slack/unused MFT records, pagefile, undelete data, file tails, unused clusters, and fast unused-cluster wiping.

It also documents operational controls: `--bytes` for replacement byte list, `--count` for repeat count, `--force`, `--info`, `--no-action`, `--quiet`, `--verbose`, `--version`, and `--help`.

## Behavioral Contract

The tool can run in report/no-write modes and can wipe sensitive remnants from several NTFS metadata surfaces: deleted names in directory indexes, MFT slack, deleted-file remnants, Windows swap space, unused clusters, and journal data.

`--undel` is documented as incompatible with `--bytes`; undelete data is overwritten by random values or a standard list.

## Related Source

This page corresponds to `sources/local-fs/ntfs-3g/ntfsprogs/ntfswipe.c` and `ntfswipe.h`.

## Notes

The man page claims there are no known problems. The implementation has several cautionary behaviors: force is required for dirty volumes, real wiping waits five seconds unless forced, and some internal recovery/wipe paths are complex and metadata-sensitive.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfswipe.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfswipe.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfswipe.c

## Purpose

CLI implementation of `ntfswipe`, which overwrites NTFS unused space, metadata slack, pagefile, journal, file tails, and deleted-file remnants.

## Main Flow

`main()` installs the NTFS logging handler, parses options, mounts the volume read-only for info/no-action or read-write for wiping, rejects dirty volumes unless `--force` is used, chooses `act_info`, `act_test`, or `act_wipe`, waits five seconds before real wiping unless forced, then iterates `count * bytes` and invokes selected wipe routines.

If no wipe target is specified, `parse_options()` defaults to info mode. `--all` enables directory, logfile, MFT, pagefile, tails, unused clusters, and undelete wiping. `--unused-fast` is separate and can supersede normal unused wiping in the main loop. `--bytes` parses comma-separated octal/decimal/hex byte values in range 0-255. `--undel` is explicitly incompatible with `--bytes`.

## Data Structures

`struct options` is defined in `ntfswipe.h` and stores all CLI flags plus the device and byte list.

Local `struct filename`, `struct data`, and `struct ufile` are mostly borrowed from undelete-style logic. In this file they are used by deleted-record wiping and cleanup, though much of the metadata collection shape is not fully populated here.

`patterns[NPAT]` defines 22 shred-style bit patterns. `fill_buffer()` chooses random/fixed patterns across passes for undelete-data wiping.

## Wipe Targets

`wipe_unused()` walks every cluster and writes one cluster at a time when `$Bitmap` says the cluster is free.

`wipe_unused_fast()` processes 64 clusters at a time, skips fully allocated blocks, reads partially free blocks, skips unused clusters already filled with the target byte, and writes the whole block back after replacing free clusters.

`wipe_tails()` iterates base MFT records, opens each `$DATA` attribute, and calls `wipe_attr_tail()`. Non-resident uncompressed tails use `wipe_attribute()`, while compressed data uses `wipe_compressed_attribute()` to find unused compressed-unit slack and rewrite it via runlist I/O.

`wipe_mft()` overwrites slack at the end of in-use MFT records and constructs sanitized empty records for unused MFT records. It writes both `$MFT` and, when covered, `$MFTMirr`.

`wipe_directory()` scans MFT records for directories with `$INDEX_ALLOCATION`, `$BITMAP`, and `$INDEX_ROOT`, derives INDX record size, then `wipe_index_allocation()` overwrites unused index record tails and whole unused index blocks.

`wipe_logfile()` opens `$LogFile/$DATA`, verifies it can read the entire attribute, then writes `0xff` blocks over the journal regardless of the requested byte.

`wipe_pagefile()` opens `pagefile.sys/$DATA` and overwrites its non-resident data stream.

`wipe_unrm()` reads the MFT bitmap to find deleted MFT records and calls `destroy_record()` on each. `destroy_record()` wipes resident file names, resident data, non-resident deleted data clusters that are no longer allocated, and metadata length fields over multiple passes.

## Dependencies

The implementation depends heavily on libntfs-3g internals: volume mounting (`utils_mount_volume()`), `$Bitmap` helpers (`utils_cluster_in_use()`, `utils_mftrec_in_use()`), raw cluster and attribute I/O (`ntfs_pread()`, `ntfs_pwrite()`, `ntfs_attr_pread()`, `ntfs_attr_pwrite()`, `ntfs_cluster_write()`), MFT record I/O/fixups (`ntfs_attr_mst_pread()`, `ntfs_attr_mst_pwrite()`, `ntfs_mft_records_write()`), runlist handling, inode/attribute open/close, and NTFS constants/layout structures.

## Safety Properties

The program supports `--info` and `--no-action`. Real wipe mode writes to raw device/attributes and has a five-second abort delay unless `--force` is set. Dirty volumes are rejected unless forced. Several routines avoid warnings on uninitialized MFT records with `NVolSetNoFixupWarn()` while scanning.

## Risks And Quirks

The code performs metadata writes across many NTFS structures, so correctness depends on layout invariants, endianness helpers, and fixup handling. Some paths have partial error cleanup: for example, early `return 0` in `wipe_logfile()` and `wipe_pagefile()` for zero-length attributes bypasses closing already opened objects.

`wipe_index_allocation()` accepts an `act` parameter but marks it unused and writes regardless of info/test mode when called; the caller's `act` is therefore not fully honored for directory index wiping. In contrast, many other routines distinguish `act_info`, `act_test`, and `act_wipe`.

The undelete wipe logic mutates deleted MFT records and length fields using repeated random/fixed patterns. This is intentionally destructive to recoverability, but it is also the most invasive part of the file.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfswipe.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfswipe.h -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfswipe.h

## Purpose

Header for `ntfswipe.c`, defining the action mode and parsed option structure used by the NTFS wiping utility.

## Public Types

`enum action` has three modes:

`act_info`: report what would be wiped.

`act_test`: execute traversal/calculation without writing to disk.

`act_wipe`: perform writes.

`struct options` stores the device path, log/verbosity flags, no-action flag, iteration count, replacement byte list, and per-target wipe flags: directory, logfile, MFT, pagefile, tails, unused, unused-fast, and undelete.

## Dependencies

Includes `types.h` for project integer types. It is consumed directly by `ntfswipe.c`.

## Notes

This header exposes only CLI/runtime configuration, not the wipe helpers themselves. The action enum is central to safety semantics, although individual implementation functions do not all honor it equally.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfswipe.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/playlog.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/playlog.c

## Purpose

Recovery helper for `ntfsrecover`: replays or reverses parsed NTFS `$LogFile` action records against an NTFS volume. It applies redo actions from earliest to latest and undo actions from latest to earliest, touching MFT records, INDX records, raw clusters, bitmap data, resident/non-resident values, mapping pairs, and file/index creation/deletion metadata.

## External Interface

The exported functions are:

`play_redos(ntfs_volume *vol, const struct ACTION_RECORD *firstaction)`

`play_undos(ntfs_volume *vol, const struct ACTION_RECORD *lastaction)`

`show_redos(void)`

`freeclusterentry(struct STORE *entry)`

These are declared through `ntfsrecover.h` and used by `ntfsrecover.c`.

## Global Context And Dependencies

The file depends on NTFS-3G layout and recovery internals: `logfile.h`, `ntfsrecover.h`, MFT/inode/attribute/index/runlist helpers, MST fixups, bitmap helpers, logging/debug helpers, and global recovery state such as `clustersz`, `clusterbits`, `mftrecsz`, `mftrecbits`, `latest_lsn`, `restart_lsn`, `optc`, `optn`, `opts`, `optv`, `redos_met`, `redocount`, and `undocount`.

It also uses helper functions from `ntfsrecover` infrastructure, including action naming, offset extraction, LCN-range filters, exception handling, attribute-table lookup/copy, Unicode name display, and endian accessors.

## Raw And Protected I/O

`read_raw()` and `write_raw()` read/write all clusters referenced by a log record. In no-write mode (`optn`), `write_raw()` stores modified clusters in an in-memory binary tree of `struct STORE`, and `read_raw()` consults that store before the device so later simulated actions see prior simulated writes.

`read_protected()` reads raw clusters, extracts a record-sized slice when needed, and applies MST post-read fixup validation for FILE/INDX records.

`write_protected()` validates and updates FILE or INDX records, sets their LSN to the action LSN when syncing, performs MST pre-write fixup, writes the raw clusters, and mirrors MFT records to `$MFTMirr` when appropriate.

## Sanity Checking

`sanity_mft()` checks attribute ordering, valid attribute types, duplicate/sane instances, embedded index-root lists, and MFT record used/allocated lengths.

`sanity_indx()` and `sanity_indx_list()` validate index entry lengths, end markers, allocation lengths, and can print detailed index contents when verbose.

These checks are rough defensive guards before writing replayed metadata.

## Generic Mutation Helpers

The file has reusable helpers for resident attribute changes, index value changes, attribute insertion/removal, resident value expansion/shrinkage, mapping-pair updates, bitmap bit forcing, root/allocation index entry updates, and record-size adjustments.

Examples include `change_resident()`, `change_resident_expect()`, `change_index_value()`, `insert_resident()`, `remove_resident()`, `expand_resident()`, `shrink_resident()`, `resize_attribute()`, `adjust_instance()`, and `adjust_high_vcn()`.

## Redo Handling

`play_one_redo()` classifies each action as operating on MFT, INDX, raw data, or none. It reads the relevant record, checks whether the action appears already executed based on LSN and exceptions, and dispatches through `distribute_redos()`.

Redo handlers cover adding/deleting index entries, root index changes, bitmap bit set/clear, compensation records, creating/deleting attributes and file records, opening non-resident attributes, updating sizes/mapping pairs/resident values/non-resident values, Win10 action 37, and write-end operations.

`play_redos()` walks forward from the first action and replays only actions flagged `ACTION_TO_REDO`, with optional LCN filtering.

## Undo Handling

`play_one_undo()` similarly classifies actions, reads the target record, checks whether the action had been executed using record LSN ordering, and dispatches through `distribute_undos()`.

Undo handlers reverse the redo transformations where supported: remove inserted index entries, reinsert deleted entries, reverse bitmap bits, uncreate/restore attributes and file records, reverse size/mapping/value changes, and ignore or special-case unsupported/no-data cases.

`play_undos()` walks backward from the last action.

## Partial And Unsupported Behavior

Several paths are explicitly incomplete or risky:

`delete_non_resident()` is not implemented and returns failure.

`add_non_resident()` prints not implemented but returns success, which can hide unsupported work.

`insert_index_allocation()` and `create_indx()` are marked unsupported when `opts` indicates real sync; comments say they are only useful for turning the clock backward and cannot work generally.

`shrink_resident()` contains comments stating its test is wrong and that old-data checks are missing in known cases.

`undo_update_value()` may ignore actions when no undo data exists.

Win10 action 37 undo is explicitly ignored.

Some comments state certain logic is controversial, especially recreating deleted files and deleting names in `undo_delete_file()`.

## Safety And Maintenance Notes

This file is a dense recovery engine over on-disk metadata. It is designed to be idempotent where possible by comparing existing data to redo/undo payloads before writing. It also distinguishes stale/current records by LSN, but comments note complications from ntfs-3g resetting logs and from Windows version differences.

Maintenance risk is high: it relies on precise NTFS structure offsets, action opcode pairings, global state, and partial knowledge of Windows log semantics. Unsupported branches should be treated as correctness boundaries, not minor TODOs.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/playlog.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/sd.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/sd.c

## Purpose

Constructs default NTFS security descriptors used by `mkntfs` when formatting NTFS 3.1 volumes. It initializes descriptors for system files, the root directory, and initial `$Secure:$SDS` entries.

## Public Functions

`init_system_file_sd(int sys_file_no, u8 **sd_val, int *sd_val_len)` returns a static relative security descriptor for NTFS system files other than the root directory. It sets owner to Local System, group to Builtin Administrators, and builds a DACL with Local System and Builtin Administrators ACEs. `$AttrDef` and `$Boot` get read-oriented masks; other system files get broader read/write-style masks.

`init_root_sd(u8 **sd_val, int *sd_val_len)` returns a static Vista-style root directory descriptor. It creates an 8-ACE DACL granting/inheriting rights for Builtin Administrators, Local System, Authenticated Users, and Builtin Users, then sets owner/group to Local System.

`init_secure_sds(char *sd_val)` writes two security descriptor entries into a caller-provided `$SDS` buffer, with fixed hashes, security IDs `0x0100` and `0x0101`, offsets `0x00` and `0x80`, and DACLs for Local System and Builtin Administrators.

## Dependencies

Includes `types.h`, `layout.h`, and `sd.h`. It uses NTFS layout structures such as `SECURITY_DESCRIPTOR_RELATIVE`, `ACL`, `ACCESS_ALLOWED_ACE`, `SID`, and `SECURITY_DESCRIPTOR_HEADER`, plus endian conversion macros and NTFS/Windows security constants.

`mkntfs.c` calls these functions when creating `$Volume`, root directory, `$AttrDef`, `$Boot`, `$Secure`, and other system-file security descriptors.

## Memory Contract

`init_system_file_sd()` and `init_root_sd()` return pointers to static buffers. The caller must not free them and cannot rely on prior returned content after another call that reuses the static buffer.

`init_secure_sds()` writes directly into caller-owned memory and does not validate the destination size.

## Risks And Notes

The descriptors are built manually with many fixed offsets and sizes. This makes the code compact but brittle: structure layout assumptions, alignment, and constant correctness are critical. Comments mention Windows Vista and Windows 2003 formatting behavior, so these defaults are version-model approximations rather than dynamically discovered descriptors.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/sd.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/sd.h -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/sd.h

## Purpose

Header declaring the security descriptor construction helpers implemented in `sd.c`.

## API

`init_system_file_sd(int sys_file_no, u8 **sd_val, int *sd_val_len)`

`init_root_sd(u8 **sd_val, int *sd_val_len)`

`init_secure_sds(char *sd_val)`

## Dependencies And Consumers

Includes `types.h` for `u8`. The primary consumer in this tree is `mkntfs.c`, which uses these functions while creating default NTFS metadata.

## Notes

The header does not document ownership, but `sd.c` makes clear that the first two functions return static memory and that `init_secure_sds()` writes into caller-provided storage.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/sd.h -->