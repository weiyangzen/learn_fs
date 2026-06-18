# Group Research: group_1870_xfsprogs_sources_local_fs_xfsprogs_db_check_c_sources_local_fs_xfsp_92c17729e27a

Scope checked against `Docs/research_subset_a.md`: all listed files are under `sources/local-fs/xfsprogs`, which is included in subset A. All files listed in the work item were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/check.c -->
# File Research: sources/local-fs/xfsprogs/db/check.c

Purpose: implements several `xfs_db` consistency and diagnostic commands centered on whole-filesystem block ownership, inode/link accounting, quota verification, directory verification, realtime metadata verification, block use reporting, and deliberate metadata fuzzing.

Commands registered by `check_init`:
- `blockget`: builds in-memory block/inode ownership maps and checks filesystem consistency.
- `blockfree`: frees the maps allocated by `blockget`.
- `blockuse`: prints recorded ownership/type for current disk block(s).
- `blocktrash`: expert-mode command to randomly or explicitly flip/set/clear/randomize bits in selected metadata blocks.
- `ncheck`: prints inode-to-path mappings after `blockget -n`.

Core data structures:
- `dbm_t` classifies every filesystem/realtime block as superblock, AGF/AGI/AGFL, free space btrees, inode btrees, data, directory, attr, quota, realtime bitmap/summary/data/free, reflink data, CoW staging data, etc.
- `dbmap` records block type per AG or realtime area.
- `inomap` records inode owner per block.
- `inodata_t` tracks per-inode link counts, directory parent/name data, selected inode filtering, security-sensitive inode marker, directory status, and reflink state.
- `blkmap_t` maps file logical block offsets to physical fsblocks for directory, quota, realtime bitmap, and realtime summary scans.
- `qdata_t` accumulates computed and on-disk quota block/inode/realtime counts by quota id.
- Directory leaf/data cross-checking uses a hash table of `(hashval,address)` entries to detect missing and extra leaf entries.

Key behavior:
- `init` validates the primary superblock and log state, allocates per-AG and optional realtime maps, initializes inode hash tables sized from `sb_icount`, parses `blockget` options, infers expected superblock feature bits, and initializes quota checking state.
- `scan_ag` reads each AG superblock, AGF, and AGI; marks fixed metadata blocks; scans the AGFL; scans bnobt/cntbt/rmapbt/refcountbt/inobt/finobt; compares counted free blocks, btree blocks, inode counts, and unlinked-list state against AG headers.
- Allocation btree scan functions mark and cross-check free-space records from bnobt and cntbt, detect out-of-order records, and update `fdblocks`, `agffreeblks`, and `agflongest`.
- Inode btree scan functions read inode chunks, handle sparse inode records, mark inode allocation blocks, process allocated/free dinodes, and compare free counts.
- `process_inode` validates dinode magic/version/format/fork layout, link state, unlinked state, nblocks/nextents/anextents, dispatches local/extents/btree forks, accounts quota usage, and invokes directory/realtime/quota special-file checkers.
- Bmap scanning handles local, extent, and btree forks, marks owned blocks, detects duplicate ownership, tracks per-file `blkmap_t` data, and supports reflink by allowing shared data/reflink-data transitions.
- Directory checking covers shortform, block, leaf, and node directory formats. It verifies `.`/`..`, parent consistency, data bestfree arrays, free-entry tags, leaf hash entries, stale counts, free index blocks, and v2/v3 magic variants.
- Realtime checking reads realtime bitmap and summary files, marks free realtime extents, computes summary counts from the bitmap, and copies on-disk summary data for comparison support.
- Quota checking reads checked quota files, validates quota record magic/version/type/id, and compares on-disk quota accounting against inode-derived counters.
- `ncheck` reconstructs paths from recorded directory parent/name links and can filter by inode or security-sensitive entries.
- `blocktrash` can choose eligible block classes from the `dbmap`, select random blocks by seed, or alter the current buffer with `-z`; it temporarily disables buffer write verification to write intentionally bad data.

Interactions:
- Relies on `libxfs` geometry, btree, directory, inode, realtime, and quota helpers.
- Uses `set_cur`, `push_cur`, `pop_cur`, `write_cur`, type descriptors, and current IO buffers from the `xfs_db` core.
- Uses `convert_extent`, `bmap`, `make_bbmap`, and type tables to walk and read mapped metadata.
- Shares field/type names with `type.c`, `field.c`, `dir2.c`, and `dquot.c`.
- `blocktrash` is only registered when `expert_mode` is enabled.

Risks/notes:
- This is a diagnostic checker, not a repair engine; several comments explicitly defer deeper refcount validation to `xfs_repair`.
- Many scans continue after nonfatal errors but set global `error`, `serious_error`, and `exitcode`; callers must interpret exit status carefully.
- `blocktrash` intentionally corrupts metadata and bypasses verifier protection for testing.
- The checker is tightly coupled to on-disk XFS format details and feature flags, including reflink, finobt, rmapbt, v5 CRC metadata, realtime devices, and sparse inodes.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/check.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/check.h -->
# File Research: sources/local-fs/xfsprogs/db/check.h

Purpose: minimal public declaration for the check command module.

Key contents:
- Declares `check_init(void)`.

Interactions:
- Included by `command.c`, which calls `check_init` from `init_commands`.
- Implemented by `check.c`.

Risks/notes:
- No include guard; this matches the simple style used by several small `xfs_db` headers in this area.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/check.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/command.c -->
# File Research: sources/local-fs/xfsprogs/db/command.c

Purpose: central command registry and dispatcher for `xfs_db`.

Key behavior:
- Maintains global `cmdtab` and `ncmds`.
- `add_command` appends a `cmdinfo_t` and keeps the table sorted by command name with `qsort`.
- `find_command` searches by primary name or alternate name.
- `command` validates argument counts against `argmin`/`argmax`, resets platform getopt state, and calls the command handler.
- `init_commands` initializes all built-in command modules, including address, AG headers, attr, block, bmap, check, convert, crc, debug, echo, frag, freesp, fsmap, help, hash, inode, IO, log, metadump, output, print, quit, realtime, sb, type, write, dquot, fuzz, timelimit, iunlink, bmapinflate, and rdump modules.

Interactions:
- Every command module provides an init function that calls `add_command`.
- Uses `dbprintf` for user-visible command errors.
- Uses `platform_getoptreset` before dispatch so command-local option parsing starts cleanly.

Risks/notes:
- Duplicate command names are not rejected; sorted linear lookup returns the first matching entry.
- Command metadata controls help, stack-push capability, and argument validation.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/command.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/command.h -->
# File Research: sources/local-fs/xfsprogs/db/command.h

Purpose: defines the public command registration and dispatch interface.

Key contents:
- Defines `cfunc_t` for command handlers and `helpfunc_t` for help callbacks.
- Defines `cmdinfo_t` with name, alternate name, handler, argument limits, stack-push capability, argument string, one-line description, and help callback.
- Declares global `cmdtab` and `ncmds`.
- Declares `add_command`, `command`, `find_command`, and `init_commands`.
- Declares init functions implemented outside module-specific headers, such as `convert_init`, `btdump_init`, `info_init`, `btheight_init`, `timelimit_init`, `namei_init`, `iunlink_init`, `bmapinflate_init`, and `rdump_init`.

Interactions:
- Included by command implementations throughout `db/`.
- Provides the common ABI by which `command.c` discovers and invokes commands.

Risks/notes:
- Header assumes surrounding includes provide command implementation dependencies; it only defines the registry-level types.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/command.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/convert.c -->
# File Research: sources/local-fs/xfsprogs/db/convert.c

Purpose: implements `convert` and `rtconvert`, commands that translate among XFS address forms.

Key behavior:
- Defines conversion types for AG block, AG inode, AG number, byte offset in basic block/fsblock/inode, filesystem byte, disk address, fsblock, inode, inode index, inode offset, realtime block, realtime extent, realtime bitmap block/word, realtime summary block/log/info, realtime group block, and realtime group number.
- Each conversion type has accepted aliases, for example `fsblock/fsb/fsbno`, `daddr/bb`, `ino/inode`, `rtblock/rtb/rtbno`, `rgnumber/rgno`.
- `ctydescs` defines legal combinations for regular filesystem address conversions.
- `ctydescs_rt` defines legal combinations for realtime address conversions.
- `convert_f` parses one or more `type value` inputs plus a final output type, rejects conflicting or identical result types, uses `cur_agno` as an implicit AG number when possible, converts inputs to a byte offset, then derives the requested regular output type.
- `rtconvert_f` performs equivalent realtime-device conversions, including realtime groups, bitmap words/blocks, and realtime summary block/info computations.
- `rsumlog` and `rsuminfo` are special context inputs required for realtime summary reverse mappings.
- `convert_init` registers both commands.

Interactions:
- Uses mount geometry from global `mp`, including block size, inode size, AG size, realtime extent size, realtime bitmap geometry, and realtime group geometry.
- Uses libxfs helpers such as `xfs_daddr_to_rtb`, `xfs_rtb_to_daddr`, `xfs_rtx_to_rbmblock`, `xfs_rtsumoffs`, and realtime group metadata.

Risks/notes:
- The command computes numerically; it does not validate that the resulting address points to live metadata.
- Realtime summary conversions require `rsumlog` and sometimes `rsuminfo` to appear in the input set before converting summary block/info addresses.
- Some realtime group conversions return zero when realtime groups are not enabled.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/convert.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/crc.c -->
# File Research: sources/local-fs/xfsprogs/db/crc.c

Purpose: implements the `crc` command for v5 XFS metadata structures.

Key behavior:
- `crc_init` registers the command only when the mounted filesystem has CRC metadata enabled.
- `crc` defaults to validation and accepts exactly one of:
  - `-v`: validate/show CRC.
  - `-r`: recalculate CRC by writing the current buffer.
  - `-i`: invalidate CRC by incrementing the CRC field and writing the current buffer.
- Requires a current type with field definitions.
- Finds the first `FLDT_CRC` field recursively with `flist_find_ftyp`, parses the path with `flist_parse`, and prints it with the generic field-list printer.
- For invalidation, walks down to the leaf CRC field, changes the bit value directly, and temporarily swaps write verifier ops to `xfs_dummy_verify` so a bad CRC can be written.
- Recalculation and invalidation require writable expert mode; otherwise the command refuses to write.

Interactions:
- Uses `field.c`/`flist.c` field metadata, `bit.c` bit accessors, current type/buffer state, `write_cur`, and buffer verifier callbacks.
- Depends on per-type CRC fields registered in field tables such as directories, dquots, btrees, inodes, symlinks, and AG metadata.

Risks/notes:
- `-i` intentionally corrupts metadata for testing.
- The printed CRC status depends on current buffer verification state via `iocur_crc_valid`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/crc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/crc.h -->
# File Research: sources/local-fs/xfsprogs/db/crc.h

Purpose: public declaration for CRC command initialization.

Key contents:
- Forward-declares `struct field`.
- Declares `crc_init(void)`.

Interactions:
- Included by `command.c`, which invokes `crc_init`.
- Implemented by `crc.c`.

Risks/notes:
- The `struct field` forward declaration is not needed by the visible declaration in this header, but is harmless.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/crc.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/debug.c -->
# File Research: sources/local-fs/xfsprogs/db/debug.c

Purpose: implements the `debug` command and global debug bit state.

Key behavior:
- Defines global `long debug_state`.
- `debug` with no argument prints the current debug state.
- `debug flagbits` parses a numeric value with `strtol`, updates `debug_state`, and prints it.
- `debug_init` registers the command.

Interactions:
- `flist.c` checks `debug_state & DEBUG_FLIST` to decide whether to dump parsed field-list internals.
- Uses `dbprintf` for command output and validation errors.

Risks/notes:
- Debug flags are process-global and affect subsequent commands until changed.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/debug.h -->
# File Research: sources/local-fs/xfsprogs/db/debug.h

Purpose: public debug state definitions.

Key contents:
- Defines `DEBUG_FLIST` as bit `0x1`.
- Declares global `debug_state`.
- Declares `debug_init(void)`.

Interactions:
- Included by `debug.c` and `flist.c`.

Risks/notes:
- Only one debug bit is defined in this header.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/debug.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/dir2.c -->
# File Research: sources/local-fs/xfsprogs/db/dir2.c

Purpose: defines `xfs_db` field metadata and helper callbacks for XFS directory v2/v3 block, data, leaf, free, and node formats.

Key behavior:
- Exposes root field descriptors `dir2_hfld` and `dir3_hfld`.
- Defines field tables for:
  - v2/v3 directory top-level views.
  - block tails.
  - data bestfree entries.
  - data headers and data entry/unused unions.
  - leaf entries, leaf headers, and leaf tails.
  - free block headers and bests arrays.
  - DA block info, node entries, and node headers.
  - v3 CRC block headers and DA3 block info.
- Count/offset callbacks inspect magic numbers to expose only the fields valid for the current directory block format.
- Data-union callbacks distinguish live directory entries from unused regions by checking `XFS_DIR2_DATA_FREE_TAG`, compute variable name lengths, tag positions, and entry sizes.
- Block/data callbacks iterate variable-sized entry streams up to the block leaf area or data block end.
- Leaf/free/node callbacks derive array counts from on-disk headers and handle separate v2 and v3 header layouts.
- `dir2_size` returns the current directory geometry block size.
- `xfs_dir3_set_crc` updates the correct CRC offset for v3 block/data/free/leaf/node directory buffers.
- `xfs_dir3_db_buf_ops` supplies a special read verifier that detects the actual directory buffer type by magic number, swaps to the matching libxfs verifier, and calls it. The write verifier rejects unknown directory buffer writes.

Interactions:
- Registered through `field.c` as `FLDT_DIR2`, `FLDT_DIR3`, and many subfield types.
- Used by print/field traversal, CRC manipulation, directory navigation, and check code.
- Depends on `mp->m_dir_geo` and libxfs directory layout helpers.

Risks/notes:
- Field visibility depends on reading plausible magic values from the current buffer; corrupt buffers may expose few or no fields.
- The generic v3 directory verifier is read-time dispatch only; unknown write types are rejected.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/dir2.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/dir2.h -->
# File Research: sources/local-fs/xfsprogs/db/dir2.h

Purpose: declarations shared by directory v2/v3 field modules.

Key contents:
- Declares common field tables for block tails, data free entries, data unions, leaf tails, leaf entries, and DA node entries.
- Declares v2-specific field tables for directory root, data headers, free headers, leaf headers, DA block info, and DA node headers.
- Declares v3-specific field tables for directory root, block headers, data headers, free headers, leaf headers, data unions, DA3 block info, and DA3 node headers.
- Provides inline `xfs_dir2_sf_inumberp` to locate the shortform entry inumber payload.
- Declares size helpers `dir2_data_union_size` and `dir2_size`.
- Declares `xfs_dir3_set_crc` and `xfs_dir3_db_buf_ops`.

Interactions:
- Used by `dir2.c`, `dir2sf.c`, `field.c`, and code that needs directory CRC/verifier support.

Risks/notes:
- Exposes field-table symbols rather than opaque accessors, matching the `xfs_db` field registry design.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/dir2.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/dir2sf.c -->
# File Research: sources/local-fs/xfsprogs/db/dir2sf.c

Purpose: defines field metadata and size/offset callbacks for shortform XFS directory v2/v3 data stored inside an inode fork.

Key behavior:
- Defines `dir2sf_flds` with header and entry list fields.
- Defines `dir2_inou_flds`, exposing either 4-byte or 8-byte inode fields depending on the shortform header `i8count`.
- Defines `dir2_sf_hdr_flds` for `count`, `i8count`, and `parent`.
- Defines `dir2_sf_entry_flds` for namelen, offset, name, and inumber.
- `dir2_sf_entry_size`, `dir2_sf_hdr_size`, `dir2sf_size`, list count, and list offset callbacks walk variable-length shortform entries with libxfs helpers.
- Defines v3 shortform variants `dir3sf_flds` and `dir3_sf_entry_flds`; v3 entries include filetype and place the inumber after the filetype byte.
- `dir2_inou_size` returns either 32-bit or 64-bit inode-number size based on `i8count`.

Interactions:
- Field types are registered by `field.c`.
- Uses `xfs_dir2_sf_inumberp` from `dir2.h` and libxfs shortform directory helpers.
- Used by inode/directory print paths and by any command that traverses shortform directory fields.

Risks/notes:
- Size and offset calculations assume the shortform entry list is structurally walkable; corrupt counts or lengths can affect field traversal.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/dir2sf.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/dir2sf.h -->
# File Research: sources/local-fs/xfsprogs/db/dir2sf.h

Purpose: public declarations for shortform directory field tables and sizing callbacks.

Key contents:
- Declares v2 field tables: `dir2sf_flds`, `dir2_inou_flds`, `dir2_sf_hdr_flds`, `dir2_sf_entry_flds`.
- Declares v3 field tables: `dir3sf_flds`, `dir3_sf_entry_flds`.
- Declares size helpers for the whole shortform directory, inode union, shortform entry, and shortform header.

Interactions:
- Included by `field.c` and `dir2sf.c`.

Risks/notes:
- Header is field-registry oriented; it does not provide validation helpers.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/dir2sf.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/dquot.c -->
# File Research: sources/local-fs/xfsprogs/db/dquot.c

Purpose: defines quota record field metadata and implements the `dquot` command for navigating to a quota record by id.

Key behavior:
- Registers `dquot [-g|-p|-u] id`, defaulting to user quotas.
- Defines `dqblk_hfld`, `dqblk_flds`, and `disk_dquot_flds`.
- Quota field tables expose disk quota magic, version, type, id, block/inode/realtime hard and soft limits, usage counters, timers, warning counters, CRC, LSN, and UUID.
- `dqtype_to_inode` loads the quota inode for user/group/project quotas, including metadir parent handling when `xfs_has_metadir` is set.
- `dquot_f` validates the requested quota type/id, maps quota id to quota file block and record offset, navigates through the quota inode bmap, sets current type to `TYP_DQBLK`, marks the buffer as a dquot buffer, offsets the current view to the specific record, and adds it to the ring.
- `xfs_dquot_set_crc` updates the CRC for the currently selected dquot record.
- `dquot_init` registers the command.

Interactions:
- Uses libxfs quota inode loading, quota path naming, transactions, inode references, and bmap lookup.
- Field types are registered by `field.c`.
- CRC command and write paths can use the dquot CRC setter.

Risks/notes:
- If the quota id maps to an unmapped quota file block, the command reports no quota data.
- CRC update asserts that the current buffer is marked as a dquot buffer.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/dquot.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/dquot.h -->
# File Research: sources/local-fs/xfsprogs/db/dquot.h

Purpose: public declarations for quota field metadata and command/CRC helpers.

Key contents:
- Declares `disk_dquot_flds`, `dqblk_flds`, and `dqblk_hfld`.
- Declares `xfs_dquot_set_crc`.
- Declares `dquot_init`.

Interactions:
- Included by `field.c`, `dquot.c`, and command initialization.

Risks/notes:
- Uses `struct field` declarations without including the full field definition, relying on consumers to include appropriate headers.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/dquot.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/echo.c -->
# File Research: sources/local-fs/xfsprogs/db/echo.c

Purpose: implements a simple `echo` command for `xfs_db`.

Key behavior:
- Registers `echo [args]...`.
- `echo_f` prints each argument separated by a trailing space, then a newline.
- Accepts any number of arguments.

Interactions:
- Uses the common command registry and `dbprintf`.

Risks/notes:
- Always emits a space after each argument before the newline.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/echo.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/echo.h -->
# File Research: sources/local-fs/xfsprogs/db/echo.h

Purpose: public declaration for echo command initialization.

Key contents:
- Declares `echo_init(void)`.

Interactions:
- Included by `command.c`.

Risks/notes:
- Minimal single-function header.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/echo.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/faddr.c -->
# File Research: sources/local-fs/xfsprogs/db/faddr.c

Purpose: implements field-address navigation callbacks used by printable field definitions to jump from a field value to another filesystem object.

Key behavior:
- `fa_agblock` navigates from an AG-relative block field using `cur_agno`.
- `fa_agino` navigates from an AG inode number to a filesystem inode.
- `fa_attrblock`, `fa_cfileoffa`, and `fa_dfiloffa` map attribute fork logical offsets through `bmap`.
- `fa_cfileoffd` and `fa_dfiloffd` map data fork logical offsets through `bmap`, using directory geometry and `bbmap` when the target type is a directory block.
- `fa_cfsblock` and `fa_dfsbno` navigate directly from encoded filesystem block numbers.
- `fa_dirblock` maps directory logical block numbers to physical blocks, building a multi-extent buffer map when needed.
- `fa_drfsbno` navigates realtime filesystem block numbers on the realtime device.
- `fa_drtbno` navigates realtime block numbers using `set_rt_cur`.
- `fa_ino`, `fa_ino4`, and `fa_ino8` navigate from inode fields to inode buffers.
- All callbacks reject null sentinel values and report unmapped logical blocks.

Interactions:
- Function pointers are stored in `ftattrtab` entries in `field.c`.
- Uses current AG state, current inode bmap state, type table entries, `set_cur`, `set_rt_cur`, and `set_cur_inode`.
- Supports field-driven navigation in print/examine workflows.

Risks/notes:
- Many callbacks require valid contextual state, especially `cur_agno` or current inode bmap context.
- Mapped directory blocks can require composite buffer maps when logical directory blocks span multiple extents.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/faddr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/faddr.h -->
# File Research: sources/local-fs/xfsprogs/db/faddr.h

Purpose: declares field-address navigation callback type and implementations.

Key contents:
- Defines `adfnc_t`, the callback signature for navigating from a field value to a next type.
- Declares address callbacks for AG blocks, AG inodes, attr blocks, compact and direct file offsets, fsblocks, directory blocks, realtime blocks, and inode-number variants.

Interactions:
- `field.h` embeds `adfnc_t` in `ftattr_t`.
- `field.c` assigns these callbacks to field types.

Risks/notes:
- Header only declares navigation helpers; behavior depends on current `xfs_db` cursor state.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/faddr.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/field.c -->
# File Research: sources/local-fs/xfsprogs/db/field.c

Purpose: central field-type registry for `xfs_db` and helper functions for field offsets, counts, lookup, and sizes.

Key behavior:
- Defines `parent_flds` for XFS parent records.
- Defines `ftattrtab`, mapping every `fldt_t` field type to:
  - User-visible type name.
  - Print function.
  - Print format.
  - Fixed or dynamic bit size.
  - Field arguments such as null/zero skipping, signedness, dynamic sizing, and empty-union allowance.
  - Optional address navigation callback.
  - Optional subfield table.
- Registers field types for AG headers, AGFL, AGI, attributes, bmap btrees, bmbt roots, free-space btrees, rmap/refcount btrees, realtime rmap/refcount roots, CRCs, dinodes, directory v2/v3 and shortform layouts, quota blocks, realtime bitmap/summary fields, superblocks, timestamps, UUIDs, parent records, and scalar integer/string forms.
- `bitoffset` resolves a field’s bit offset, handling static offsets, dynamic offset callbacks, and static array indexing with optional one-based indexing.
- `fcount` resolves static or dynamic field counts.
- `findfield` locates a named field with nonzero count.
- `fsize` resolves static or dynamic field bit size.

Interactions:
- Pulls field tables from many modules: AGF/AGFL/AGI, sb, attr, dir2, dir2sf, dquot, inode, btree, symlink, realtime group, and others.
- Used by `print`, `flist`, `crc`, and navigation code to parse and display arbitrary metadata structures.

Risks/notes:
- This file is a central coupling point: adding any new on-disk metadata field type requires updating `fldt_t` and `ftattrtab` consistently.
- Dynamic size/count/offset callbacks must tolerate corrupt on-disk data because field traversal is often used for debugging damaged metadata.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/field.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/field.h -->
# File Research: sources/local-fs/xfsprogs/db/field.h

Purpose: defines the field type enum and field metadata structures used by the `xfs_db` structured print/navigation system.

Key contents:
- `fldt_t` enumerates all registered field types, including AG metadata, attr formats, btrees, CRCs, dinodes, directory v2/v3/shortform fields, quota fields, realtime group fields, superblocks, scalar integers, UUIDs, parent records, and `FLDT_ZZZ` terminator.
- Defines `offset_fnc_t`, `count_fnc_t`, and `size_fnc_t` plus helper macros `OI`, `CI`, `C1`, and `SI`.
- Defines `field_t` with name, field type, offset, count, flags, and next navigation type.
- Field flags:
  - `FLD_ABASE1`
  - `FLD_SKIPALL`
  - `FLD_ARRAY`
  - `FLD_OFFSET`
  - `FLD_COUNT`
- Defines `ftattr_t`, the per-field-type descriptor with print function, format, size, arguments, address callback, and subfields.
- Field attribute flags cover skip-zero, null handling, signedness, dynamic size, skipped names, and empty unions.
- Declares `ftattrtab`, `bitoffset`, `fcount`, `findfield`, and `fsize`.

Interactions:
- Consumed by almost every structured metadata module in `db/`.
- Depends conceptually on `prfnc_t` from `fprint.h` and `adfnc_t` from `faddr.h`.

Risks/notes:
- Enum order must match `ftattrtab` indices; mismatches would break field decoding globally.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/field.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/flist.c -->
# File Research: sources/local-fs/xfsprogs/db/flist.c

Purpose: parses, expands, and manages field-selection trees used to print or locate structured metadata fields.

Key behavior:
- `flist_make` allocates a field-list node for a name.
- `flist_free` recursively frees children and siblings.
- `flist_scan` parses user-style field paths such as `field.child[0-3].leaf` into an `flist_t` tree.
- `flist_split` tokenizes names, decimal/hex-ish numbers, brackets, dashes, dots, and quoted strings.
- `flist_parse` resolves names against a field table, validates array indices/ranges, computes offsets, expands array ranges into sibling nodes when needed, auto-expands structures when no child is specified, and recursively parses subfields.
- `flist_expand_arrays` replicates child selections for each requested array index.
- `flist_expand_structs` creates child nodes for all non-skipped subfields of a structure.
- `flist_find_ftyp` recursively searches field tables for the first field of a requested type, returning a field-list path.
- `flist_print` dumps internal field-list structure only when `DEBUG_FLIST` is set.

Interactions:
- Used by print commands and by `crc.c` to locate CRC fields.
- Depends on `field.c` helpers, field attributes, debug state, and allocator wrappers.

Risks/notes:
- Parser is intentionally small and supports a limited field path grammar.
- Dynamic field counts/offsets are evaluated against the current object, so corrupt metadata can affect parse results.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/flist.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/flist.h -->
# File Research: sources/local-fs/xfsprogs/db/flist.h

Purpose: public types and declarations for field-list parsing.

Key contents:
- Defines `flist_t`, a tree/sibling representation of selected fields with array range, flags, and computed offset.
- Defines `FL_OKLOW` and `FL_OKHIGH` array-index validity flags.
- Defines token enum `tokty_t` and token structure `ftok_t`.
- Declares allocation/free, parse, debug print, scan, and field-type search functions.

Interactions:
- Used by `crc.c`, print code, and field traversal users.

Risks/notes:
- Exposes internal parser data structures directly to callers.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/flist.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/fprint.c -->
# File Research: sources/local-fs/xfsprogs/db/fprint.c

Purpose: implements primitive field print functions used by `ftattrtab`.

Key behavior:
- `fp_charns` prints character arrays as quoted strings with C-style escaping for quotes, backslashes, printable characters, control characters, and octal escapes.
- `fp_num` prints numeric fields with signed/unsigned extraction, null formatting, zero/null skipping, array index prefixes, and 32-bit versus 64-bit format handling.
- `fp_sarray` delegates structured array printing to `print_sarray`.
- `fp_time` prints inode timestamp seconds as human-readable time when representable by `time_t`, otherwise raw seconds.
- `fp_nsec` prints inode timestamp nanoseconds.
- `fp_qtimer` prints quota timers, preserving raw values for root/default or non-expired timers and formatting expiration times otherwise.
- `fp_uuid` prints UUIDs using platform UUID formatting.
- `fp_crc` prints CRC values plus verification state: unchecked, bad, correct, or unknown.

Interactions:
- Print functions are referenced by `field.c` field attributes.
- Uses bit extraction from `bit.c`, print helpers, current IO CRC status, signal interruption checks, and libxfs timestamp conversions.

Risks/notes:
- Formatting honors `seenint()` so long output can be interrupted.
- Human-readable timestamp output is intentionally guarded against `time_t` range loss.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/fprint.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/fprint.h -->
# File Research: sources/local-fs/xfsprogs/db/fprint.h

Purpose: declares the primitive field print callback interface.

Key contents:
- Defines `prfnc_t`, the common field print callback signature.
- Declares print functions for character arrays, numbers, structured arrays, inode time, nanoseconds, quota timers, UUIDs, and CRCs.

Interactions:
- `field.h` stores `prfnc_t` in `ftattr_t`.
- `field.c` assigns these functions to scalar and special field types.

Risks/notes:
- Print callbacks receive raw object pointer, bit offset, count, format, size, flags, array base, and array state, so callers must pass consistent field metadata.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/fprint.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/frag.c -->
# File Research: sources/local-fs/xfsprogs/db/frag.c

Purpose: implements the `frag` command, which estimates filesystem file fragmentation by scanning inode extent maps.

Key behavior:
- Registers `frag [-a] [-d] [-f] [-l] [-q] [-R] [-r] [-v]`.
- If no category flags are supplied, enables all categories: attrs, directories, regular files, symlinks, quota files, realtime metadata files, and realtime files.
- Scans all AGs through AGI inobt roots, reads allocated inode chunks, skips free inodes, and processes selected inodes.
- For each selected data or attr fork, reads extent format or btree format mappings into an `extmap_t`.
- `extmap_ideal` counts how many extents would be needed if logically adjacent extents were merged; this is independent of physical contiguity.
- Accumulates `extcount_actual` and `extcount_ideal`, then reports:
  - Actual extent count.
  - Ideal extent count.
  - Fragmentation factor `(actual - ideal) / actual`.
  - Average extents per file.
- `-v` prints per-inode actual/ideal contribution.

Interactions:
- Uses bmap record conversion, inobt scanning logic, type table cursor reads, sparse inode helpers, and inode fork helpers.
- Shares structural patterns with `check.c` but only computes extent statistics.

Risks/notes:
- The command itself prints that the fragmentation factor is largely meaningless.
- It does not validate btree structure deeply; it scans enough to collect extent records and emits errors for unreadable blocks or invalid bmap record counts.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/frag.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/frag.h -->
# File Research: sources/local-fs/xfsprogs/db/frag.h

Purpose: public declaration for fragmentation command initialization.

Key contents:
- Declares `frag_init(void)`.

Interactions:
- Included by `command.c`, which calls `frag_init`.

Risks/notes:
- Minimal single-function header.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/frag.h -->