# Group Research: group_1871_xfsprogs_sources_local_fs_xfsprogs_db

Scope checked against `Docs/research_subset_a.md`: all files are under the included `sources/local-fs/xfsprogs` source tree. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/freesp.c -->
# File Research: sources/local-fs/xfsprogs/db/freesp.c

## Purpose
Implements the `xfs_db freesp` command, which scans allocation-group free-space metadata and produces a histogram, optional summary, and optional raw extent dump of filesystem free space.

## Main Interfaces
- `freesp_init()` registers the `freesp` command.
- `freesp_f()` parses command state, iterates AGs, scans free-space structures, prints histograms and summaries.
- `scan_ag()` reads each AGF and walks either bnobt or cntbt depending on `-c`.
- `scan_freelist()` includes AGFL blocks as one-block free-space observations.
- `scanfunc_bno()` and `scanfunc_cnt()` recursively traverse free-space btrees.
- `addtohist()` applies optional filesystem-block alignment filtering, dumps records, and records extent lengths.

## Behavior Notes
The command supports AG filtering (`-a`), alignment filtering (`-A`), raw dumps (`-d`), summary output (`-s`), count-btree traversal (`-c`), and histogram bin selection via equal-sized, multiplicative, or explicit bucket definitions. It uses `libfrog/histogram` for bucket management and output.

## Dependencies
Depends on the global xfs_db state from `init.h` and `io.h`: `mp`, `iocur_top`, `push_cur`, `set_cur`, and `pop_cur`. It uses type-table entries for AGF, AGFL, BNOBT, and CNTBT reads.

## Edge Cases
The AGFL scan validates `agf_flfirst` and `agf_fllast` against `libxfs_agfl_size` before walking. Btree traversal silently returns if the magic does not match the expected bnobt/cntbt magic. `scan_sbtree` prints a read warning if a btree block cannot be read, but one early return path omits a `pop_cur()` after a failed read.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/freesp.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/freesp.h -->
# File Research: sources/local-fs/xfsprogs/db/freesp.h

## Purpose
Tiny command-registration header for the `freesp` xfs_db module.

## Main Interfaces
- Declares `freesp_init()`.

## Dependencies
Included by command initialization code and by `freesp.c`. No include guard is present, matching several older xfs_db command headers in this directory.

## Edge Cases
No logic.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/freesp.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/fsmap.c -->
# File Research: sources/local-fs/xfsprogs/db/fsmap.c

## Purpose
Implements the `fsmap` command, which displays reverse-mapping records from data-device and realtime reverse mapping btrees.

## Main Interfaces
- `fsmap_init()` registers the command.
- `fsmap_f()` parses `[-r] [start_fsb] [end_fsb]`, checks rmap support, and dispatches to data or realtime scanning.
- `fsmap()` scans data-device per-AG rmap btrees using `libxfs_rmap_query_range`.
- `fsmap_rt()` scans realtime group rmap btrees.
- `fsmap_fn()` and `fsmap_rt_fn()` print each rmap record.

## Behavior Notes
Output includes record number, AG or rtgroup, start block, length, owner, offset, and flags for bmbt, attr fork, and unwritten extent state. Data scans clamp `end_fsb` to filesystem size. Realtime scans return immediately if there are no realtime blocks.

## Dependencies
Uses libxfs rmap btree cursors, perag iteration, rtgroup iteration, rt metadir inode loading, and xfs_db output helpers.

## Edge Cases
Requires `xfs_has_rmapbt(mp)`. Realtime scanning allocates an empty transaction to load realtime metadata inodes. Error paths release btree cursors, buffers, rtgroup/perag refs, and transactions carefully.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/fsmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/fsmap.h -->
# File Research: sources/local-fs/xfsprogs/db/fsmap.h

## Purpose
Command-registration header for the `fsmap` xfs_db module.

## Main Interfaces
- Declares `fsmap_init()`.

## Dependencies
Consumed by initialization code and `fsmap.c`.

## Edge Cases
No logic.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/fsmap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/fuzz.c -->
# File Research: sources/local-fs/xfsprogs/db/fuzz.c

## Purpose
Implements expert-mode field fuzzing for xfs_db. It mutates selected fields of the current on-disk structure and writes them back, optionally bypassing verifier/CRC protections to create deliberately damaged metadata.

## Main Interfaces
- `fuzz_init()` registers `fuzz` only in `expert_mode` and seeds `lrand48`.
- `fuzz_f()` validates mode/current type, parses `-c` and `-d`, adjusts write verifiers, and invokes the current type print/fuzz function with `DB_FUZZ`.
- `fuzz_struct()` parses `field fuzzcmd`, locates field offsets and lengths through flist/field metadata, applies a fuzz verb, writes the current buffer, and prints the mutated field.
- Fuzz verbs: `zeroes`, `ones`, `firstbit`, `middlebit`, `lastbit`, `add`, `sub`, `random`.

## Behavior Notes
`-c` allows corrupt data with bad CRCs by installing `xfs_dummy_verify`; `-d` allows invalid data but recalculates CRCs when possible. Without those flags, normal write verifier paths apply.

## Dependencies
Tightly coupled to the xfs_db field system (`field`, `flist`, `fprint`), bit helpers, `write_cur`, and buffer verifier operations from `io.c`.

## Edge Cases
Disabled in readonly mode. Rejects `-c` and `-d` together. Rejects `-d` for object types without a CRC offset on CRC-enabled filesystems. Numeric add/sub only operate on fields up to 64 bits.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/fuzz.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/fuzz.h -->
# File Research: sources/local-fs/xfsprogs/db/fuzz.h

## Purpose
Header for xfs_db fuzz support.

## Main Interfaces
- Declares `fuzz_init()`.
- Declares `fuzz_struct()` for type-specific print/fuzz dispatch.

## Dependencies
Requires `field_t` from xfs_db field definitions.

## Edge Cases
No logic.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/fuzz.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/hash.c -->
# File Research: sources/local-fs/xfsprogs/db/hash.c

## Purpose
Implements two commands:
- `hash`: compute XFS directory, attribute, or parent-pointer hash values.
- `hashcoll`: generate names with the same dahash value for testing collision behavior.

## Main Interfaces
- `hash_init()` registers `hash` and `hashcoll`.
- `hash_f()` supports attr hashes by default, directory hashes with `-d`, and parent-pointer hashes with `-p parent_ino`.
- `hashcoll_f()` parses collision-generation options and dispatches to directory-entry or xattr collision creation.
- `collide_dirents()` generates same-hash directory names, optionally creating hardlinks in a directory.
- `collide_xattrs()` generates same-hash xattr names, optionally creating user xattrs on a file.
- Duplicate tracking uses `dup_table_*` helpers with CRC32C buckets.

## Behavior Notes
`hashcoll` writes generated names to stdout separated by NUL bytes unless `-p` is used to create real entries. It relies on `obfuscate_name` and `find_alternate` to preserve the original hash while avoiding duplicates.

## Dependencies
Uses libxfs hash functions, xattr syscalls, filesystem syscalls (`open`, `openat`, `linkat`), and `obfuscate.c`.

## Edge Cases
`dup_table_alloc` skips allocation for a single requested name. Duplicate avoidance is bounded by `find_alternate`; exhaustion returns `EEXIST`. `-i` reads up to `MAXNAMELEN - 1` bytes from stdin.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/hash.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/hash.h -->
# File Research: sources/local-fs/xfsprogs/db/hash.h

## Purpose
Command-registration header for hash-related xfs_db commands.

## Main Interfaces
- Declares `hash_init()`.

## Dependencies
Used by command initialization and `hash.c`.

## Edge Cases
No logic.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/hash.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/help.c -->
# File Research: sources/local-fs/xfsprogs/db/help.c

## Purpose
Implements the `help`/`?` command for xfs_db.

## Main Interfaces
- `help_init()` registers the command.
- `help_f()` prints all commands or detailed help for one command.
- `help_all()` iterates `cmdtab`.
- `help_onecmd()` prints one-line usage and invokes command-specific help.
- `help_oneline()` formats command name, altname, args, and one-line summary.

## Dependencies
Depends on `cmdtab`, `ncmds`, `find_command`, `cmdinfo_t`, and `dbprintf`.

## Edge Cases
Unknown command names are reported without failing the process.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/help.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/help.h -->
# File Research: sources/local-fs/xfsprogs/db/help.h

## Purpose
Header for help command registration.

## Main Interfaces
- Declares `help_init()`.

## Dependencies
Used by command initialization.

## Edge Cases
No logic.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/help.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/info.c -->
# File Research: sources/local-fs/xfsprogs/db/info.c

## Purpose
Implements filesystem geometry and reservation reporting commands:
- `info`/`i`
- `agresv`
- `rgresv`

## Main Interfaces
- `info_init()` registers all three commands.
- `info_f()` reports filesystem geometry through `libxfs_fs_geometry` and `xfs_report_geom`.
- `agresv_f()` prints per-AG metadata btree reservation, used, free, and length data.
- `rgresv_f()` prints realtime-group metadata reservation information.
- `print_agresv_info()` and `print_rgresv_info()` do the actual per-group accounting.

## Dependencies
Uses libxfs geometry, perag/rtgroup iteration, AGF reading, refcount/finobt/rmap reserve calculators, rt metadata inode loading, and xfs_db output.

## Edge Cases
AG and rtgroup command arguments are parsed with range checks. Reservation calculators report errors via `xfrog_perror` but continue. Realtime reservation reporting requires loading rt metadir and rtgroup metadata inodes through a temporary empty transaction.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/info.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/init.c -->
# File Research: sources/local-fs/xfsprogs/db/init.c

## Purpose
Main program and initialization path for `xfs_db`.

## Main Interfaces
- `main()` initializes xfs_db, executes `-c` command strings or runs the interactive command loop, then unmounts/destroys libxfs state.
- Static `init()` parses process options, initializes libxfs, reads the superblock, mounts in debugger mode, initializes type tables, stack state, command table, and signal handling.
- Global state exported via `init.h`: `mp`, `x`, `blkbb`, `exitcode`, `expert_mode`, `cur_agno`.

## Behavior Notes
The tool reads the primary superblock without normal validation because xfs_db must inspect damaged filesystems. It still rejects non-XFS magic unless `-F` is supplied. It sets `LIBXFS_DIRECT`, cache flags, and `LIBXFS_MOUNT_DEBUGGER`.

## Dependencies
Depends on libxfs/libxlog, command dispatch, input, I/O cursor stack, signal support, type-table configuration, and allocation wrappers.

## Edge Cases
Supports readonly (`-r`), inactive readonly (`-i`), image-file mode (`-f`), external log/realtime devices, custom prompt/program name, expert mode (`-x`), and version output. It records if libxfs had to clamp a broken AG count by setting `exitcode`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/init.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/init.h -->
# File Research: sources/local-fs/xfsprogs/db/init.h

## Purpose
Shared global-state header for xfs_db.

## Main Interfaces
Declares:
- `blkbb`
- `exitcode`
- `expert_mode`
- `mp`
- `x`
- `cur_agno`

## Dependencies
Almost every command module uses this for mount state, process status, or expert-mode gating.

## Edge Cases
No logic.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/init.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/inode.c -->
# File Research: sources/local-fs/xfsprogs/db/inode.c

## Purpose
Defines xfs_db inode field descriptions, inode-format print helpers, dynamic field sizing/count callbacks, inode navigation, and inode CRC update support.

## Main Interfaces
- `inode_init()` registers the `inode` command.
- `inode_f()` sets or reports the current inode.
- `set_cur_inode()` maps an inode number to the proper inode-cluster buffer, offsets the cursor to the selected inode, records mode/dirino, checks inode CRC, and updates the navigation ring.
- `inode_next_type()` chooses the next logical type for inode contents.
- Field arrays: `inode_hfld`, `inode_crc_hfld`, `inode_flds`, `inode_crc_flds`, `inode_core_flds`, `inode_v3_flds`, `timestamp_flds`, `inode_u_flds`, `inode_a_flds`.
- Print helpers: `fp_dinode_fmt()`, `fp_metatype()`.
- Size helpers: `inode_size()`, `inode_u_size()`, `inode_a_size()`.
- `xfs_inode_set_crc()` recalculates inode CRC for writes.

## Behavior Notes
The field tables expose inode core fields, v3 fields, flags, timestamps, data fork formats, attr fork formats, realtime metadata roots, and large extent count variants. Count/offset callbacks hide or show fields based on inode version, CRC support, metadata flags, fork format, and `XFS_DIFLAG2_NREXT64`.

## Dependencies
Uses the xfs_db type/field/fprint systems, bit helpers, `io.c` cursor functions, libxfs inode geometry macros, and superblock feature checks.

## Edge Cases
`set_cur_inode()` validates AG number, AG block, inode offset, and reverse inode mapping before reading. It uses inode-cluster reads to avoid overlapping libxfs buffers. For CRC filesystems it reports inode CRC errors but still positions the cursor.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/inode.h -->
# File Research: sources/local-fs/xfsprogs/db/inode.h

## Purpose
Header exporting inode field tables and inode helper functions.

## Main Interfaces
Declares inode field arrays, timestamp fields, print helpers, size helpers, `inode_init()`, `inode_next_type()`, `xfs_inode_set_crc()`, and `set_cur_inode()`.

## Dependencies
Consumers include type definitions, print/fuzz logic, cursor type switching, and write/CRC paths.

## Edge Cases
No logic.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/input.c -->
# File Research: sources/local-fs/xfsprogs/db/input.c

## Purpose
Implements command-line input handling, command tokenization, interactive/sourced command reading, and the `source` command.

## Main Interfaces
- `input_init()` registers `source`.
- `breakline()` splits one input line into argv-style tokens.
- `doneline()` frees line/vector storage.
- `fetchline()` reads from stdin or source files, optionally through editline.
- `pushfile()` pushes an input stream.
- `source_f()` executes commands from a file immediately.

## Behavior Notes
The tokenizer is a custom strtok-like parser that respects double quotes and backslash escapes. `fetchline_internal()` supports line continuation with trailing backslash, Ctrl-C recovery, prompt printing, command logging, and nested source-file stacks.

## Dependencies
Uses xfs_db command dispatch, output/logging, signal helpers, allocation wrappers, and optional libedit/history.

## Edge Cases
EOF on a sourced file pops that file and returns control to the lower input level. In `source_f`, the error message for failed open prints `argv[0]` instead of the requested filename `argv[1]`, which looks like a minor diagnostic bug.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/input.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/input.h -->
# File Research: sources/local-fs/xfsprogs/db/input.h

## Purpose
Header for xfs_db input-loop helpers.

## Main Interfaces
Declares `breakline`, `doneline`, `fetchline`, `input_init`, and `pushfile`.

## Dependencies
Used by `init.c`, `namei.c`, and command/input modules.

## Edge Cases
No logic.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/input.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/io.c -->
# File Research: sources/local-fs/xfsprogs/db/io.c

## Purpose
Implements the xfs_db current-object I/O cursor stack, navigation ring, buffer reads/writes, type switching, and commands for cursor navigation.

## Main Interfaces
- `io_init()` registers `pop`, `push`, `stack`, `forward`, `back`, and `ring`.
- Global cursor state: `iocur_base`, `iocur_top`, `iocur_sp`, `iocur_len`.
- Cursor manipulation: `push_cur()`, `pop_cur()`, `push_cur_and_set_type()`, `off_cur()`, `set_cur()`, `set_log_cur()`, `set_rt_cur()`, `set_iocur_type()`.
- Write path: `write_cur()`, `xfs_dummy_verify()`, `xfs_verify_recalc_crc()`.
- Navigation: `ring_add()`, `print_iocur()`, device classification helpers.

## Behavior Notes
The stack explicitly saves locations, while the ring automatically tracks recent positions. `__set_cur()` reads buffers through libxfs with salvage mode so damaged metadata can still be inspected. It preserves inode/dirino/mode when changing current buffer.

## Dependencies
Uses libxfs buffers, type table verifier metadata, inode/dquot CRC hooks, command system, and global mount state.

## Edge Cases
`set_log_cur()` rejects absent external logs; `set_rt_cur()` rejects absent realtime devices. `write_cur()` recalculates inode/dquot CRCs only when normal verifier paths are active, and rechecks inode CRC if writing without automatic CRC update.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/io.h -->
# File Research: sources/local-fs/xfsprogs/db/io.h

## Purpose
Header for xfs_db cursor and buffer I/O state.

## Main Interfaces
- Defines `bbmap_t` for discontiguous buffer maps.
- Defines `iocur_t`, including block address, length, data pointer, inode context, type, buffer pointer, CRC flags, and bmap.
- Declares cursor stack, set/read/write helpers, ring helpers, verifier helpers, and device classification helpers.
- Defines `iocur_crc_valid()` inline.

## Dependencies
Used throughout xfs_db modules that navigate or modify on-disk structures.

## Edge Cases
`iocur_crc_valid()` returns `-1` for unchecked/no-buffer, `0` for bad, and `1` for good, incorporating inode CRC state for inode buffers.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/io.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/iunlink.c -->
# File Research: sources/local-fs/xfsprogs/db/iunlink.c

## Purpose
Implements commands for inspecting and, in expert mode, creating unlinked inode-list entries.

## Main Interfaces
- `iunlink_init()` registers `dump_iunlinked`; registers `iunlink` only in expert mode.
- `dump_iunlinked_f()` parses AG/bucket/quiet/verbose options and walks unlinked chains.
- `dump_unlinked()` reads AGI and dumps one or all unlinked buckets.
- `get_next_unlinked()` loads an inode, optionally prints block/realtime-block counts, reads its on-disk `di_next_unlinked`, and returns the next AG inode.
- `iunlink_f()` creates N unlinked inodes via `create_unlinked()`.

## Behavior Notes
The read-only command traverses `agi_unlinked` buckets and follows `di_next_unlinked`. The expert command creates temp-file style unlinkable inodes and calls `libxfs_iunlink`.

## Dependencies
Uses libxfs inode loading, AGI reading, transactions, inode creation, unlink-chain helpers, and realtime extent counting.

## Edge Cases
`dump_iunlinked` validates AG and bucket ranges. Verbose mode distinguishes data blocks from realtime blocks. Error messages are printed per bad inode-chain element.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/iunlink.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/logformat.c -->
# File Research: sources/local-fs/xfsprogs/db/logformat.c

## Purpose
Implements log-oriented diagnostic and expert commands:
- `logformat` to clear/reformat the log, expert-only.
- `logres` to dump transaction log reservations.
- `untorn_write_max` to compute reservation limits for untorn write emulation.

## Main Interfaces
- `logformat_init()` registers `logformat` only in expert mode.
- `logres_init()` registers `logres` and `untorn_write_max`.
- `logformat_f()` validates log cleanliness and calls `libxfs_log_clear`.
- `logres_f()` walks mount transaction reservations and prints min-log-size reservation.
- `untorn_cow_limits()` computes per-intent and step-size limits for reflink-based untorn writes.

## Behavior Notes
`logformat` refuses to clear a dirty log and defaults to the current cycle and superblock log stripe unit if not supplied. Stripe unit validation enforces block alignment and max v2 log buffer size.

## Dependencies
Uses libxlog tail detection, libxfs log clearing, transaction reservation structures, and intent item log-space calculators.

## Edge Cases
`untorn_write_max` prints unsupported if reflink is absent. The command metadata for `untorn_write_max` points to `logres_help`, though it has its own help function, which looks like a small wiring mistake.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/logformat.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/logformat.h -->
# File Research: sources/local-fs/xfsprogs/db/logformat.h

## Purpose
Header for log formatting and log reservation command registration.

## Main Interfaces
- Declares `logformat_init()`.
- Declares `logres_init()`.

## Dependencies
Used by xfs_db command initialization.

## Edge Cases
No logic.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/logformat.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/malloc.c -->
# File Research: sources/local-fs/xfsprogs/db/malloc.c

## Purpose
Provides xfs_db allocation wrappers that terminate the process on allocation failure.

## Main Interfaces
- `xcalloc()`
- `xmalloc()`
- `xrealloc()`
- `xstrdup()`
- `xfree()`

## Behavior Notes
Allocation failures print `"<progname>: out of memory"` through `dbprintf` and exit with status 4. `xmalloc()` uses `valloc`, preserving older alignment expectations in xfs_db.

## Dependencies
Uses global `progname`, `dbprintf`, and libc allocation APIs.

## Edge Cases
`xrealloc(ptr, 0)` returns the libc result without treating NULL as failure.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/malloc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/malloc.h -->
# File Research: sources/local-fs/xfsprogs/db/malloc.h

## Purpose
Header for xfs_db allocation wrappers.

## Main Interfaces
Declares `xcalloc`, `xfree`, `xmalloc`, `xrealloc`, and `xstrdup`.

## Dependencies
Used widely across xfs_db for fail-fast allocation.

## Edge Cases
No logic.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/malloc.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/metadump.c -->
# File Research: sources/local-fs/xfsprogs/db/metadump.c

## Purpose
Implements `xfs_db metadump`, which copies known XFS metadata into a compact diagnostic image, with optional name/xattr obfuscation and stale-data zeroing.

## Main Interfaces
- `metadump_init()` registers the command.
- `metadump_f()` parses options, selects format v1/v2, opens output, scans all AGs, copies the log, optionally copies realtime superblock metadata, finalizes output, and cleans up.
- Output backends:
  - v1: `init_metadump_v1`, `write_metadump_v1`, `finish_dump_metadump_v1`, `release_metadump_v1`.
  - v2: `init_metadump_v2`, `write_metadump_v2`.
- Metadata traversal:
  - `scan_ag()` copies SB/AGF/AGI/AGFL, free-space btrees, rmap/refcount btrees, inode btrees, inode chunks, and inode-associated metadata.
  - `scan_btree()` is the generic btree block reader/writer.
  - Specialized scan callbacks cover bnobt/cntbt, rmapbt, refcountbt, inobt/finobt, bmbt, realtime rmap, and realtime refcount btrees.
- Inode/fork processing:
  - `copy_inode_chunk()`, `process_inode()`, `process_inode_data()`, `process_exinode()`, `process_btinode()`, `process_rtrmap()`, `process_rtrefc()`.
- Directory/attr/symlink handling:
  - Short-form dir/attr/symlink processors.
  - Leaf/node directory data/free/leaf block processors.
  - Local and remote xattr processors.
  - Multi-FSB directory and symlink processors.
- Obfuscation support:
  - Name table for duplicate avoidance.
  - Parent-pointer remap table to keep dirent and parent-pointer names consistent.
  - Special `lost+found` handling to preserve orphan names that match inode numbers.

## Behavior Notes
Default behavior obfuscates names and zeroes stale metadata. `-a` preserves full metadata blocks, `-o` disables obfuscation, `-e` stops on read errors, `-g` shows progress, `-m` limits suspicious extent size, `-v` selects output version, and `-w` enables warnings.

## Dependencies
Uses nearly every core xfs_db layer: cursor I/O, type table, output, signal state, bmap conversion, dir/attr field helpers, log support, and obfuscation. It also relies heavily on libxfs metadata format helpers and feature checks.

## Edge Cases
The file is deliberately corruption-tolerant. It validates btree levels, record counts, block numbers, inode chunk alignment, extent ordering, extent length, directory entry lengths/tags, attr sizes, and fork sizes before descending or modifying data. It preserves corrupt buffers rather than “fixing” CRCs unless metadump itself changed a previously-good buffer. Dirty logs are copied with warnings because they can leak unobfuscated metadata into an otherwise obfuscated image.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/metadump.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/metadump.h -->
# File Research: sources/local-fs/xfsprogs/db/metadump.h

## Purpose
Header for metadump command registration.

## Main Interfaces
- Declares `metadump_init()`.

## Dependencies
Used by xfs_db command initialization.

## Edge Cases
No logic.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/metadump.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/namei.c -->
# File Research: sources/local-fs/xfsprogs/db/namei.c

## Purpose
Implements path navigation, directory listing, parent-pointer listing, and expert-mode directory link/unlink commands.

## Main Interfaces
- `namei_init()` registers `path`, `ls`/`l`, `parent`/`pptr`, and expert-only `link`/`unlink`.
- `path_walk()` resolves absolute or relative paths and sets the current inode.
- `listdir()` lists directory contents through a caller-provided `dir_emit_t`.
- `ls_f()` lists current or path-selected directories, or prints inode numbers with `-i`.
- `parent_f()` lists parent pointers for current or path-selected files.
- Expert operations:
  - `create_child()` creates a directory entry and updates link counts, dotdot, and parent pointers.
  - `remove_child()` removes a directory entry and updates link counts and parent pointers.

## Behavior Notes
Path parsing collapses repeated slashes and stores components in a `dirpath`. Lookup starts from root for absolute paths, current directory for relative paths, or metadata root with `-m`.

Directory listing supports short-form, block, leaf, and node directory formats. Output includes directory cookie, inode, type, hash, name length, name, and basic name-validity status.

## Dependencies
Uses libxfs directory lookup/listing, inode loading, attr/parent-pointer decoding, transactions, xfs_db cursor stack, and inode type helpers.

## Edge Cases
Metadata directory traversal requires `xfs_has_metadir`. Parent-pointer listing returns no output if parent pointers are unsupported. Expert link/unlink commands are transaction-backed and update parent pointers when available.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/namei.h -->
# File Research: sources/local-fs/xfsprogs/db/namei.h

## Purpose
Public header for path walking and directory listing helpers.

## Main Interfaces
- Declares `path_walk()`.
- Defines `dir_emit_t`.
- Declares `listdir()`.

## Dependencies
Used by modules needing directory traversal callbacks or path-based cursor movement.

## Edge Cases
Uses an include guard, unlike several older headers in this directory.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/namei.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/obfuscate.c -->
# File Research: sources/local-fs/xfsprogs/db/obfuscate.c

## Purpose
Provides hash-preserving name obfuscation and alternate-name generation for metadump and hash collision tools.

## Main Interfaces
- `obfuscate_name()` changes a name in place to another same-length name with the same XFS directory/attribute hash.
- `find_alternate()` generates deterministic alternate same-hash names by applying paired bit flips.
- Static `flip_bit()` performs one hash-preserving bit-pair mutation.

## Behavior Notes
The obfuscator requires names of at least five bytes. It randomizes the prefix, computes the final five bytes needed to preserve the hash, and avoids `/` and NUL. On ASCII case-insensitive filesystems it retries to avoid uppercase correction bytes that would alter the folded hash.

## Dependencies
Uses global `mp` for ASCII-CI feature checks and libxfs casefold helpers.

## Edge Cases
ASCII-CI obfuscation gives up after 1000 attempts and restores the original name. Alternate generation is bounded by name length and returns `-1` when no larger sequence can be represented.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/obfuscate.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/obfuscate.h -->
# File Research: sources/local-fs/xfsprogs/db/obfuscate.h

## Purpose
Header for hash-preserving name obfuscation.

## Main Interfaces
- Defines `is_invalid_char(c)` for `/` and NUL.
- Declares `obfuscate_name()`.
- Declares `find_alternate()`.

## Dependencies
Used by `metadump.c` and `hash.c`.

## Edge Cases
Include guard present.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/obfuscate.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/output.c -->
# File Research: sources/local-fs/xfsprogs/db/output.c

## Purpose
Implements xfs_db formatted output and command logging.

## Main Interfaces
- `output_init()` registers the `log` command.
- `dbprintf()` prints to stdout with optional device prefix, blocks signals during output, and mirrors output to the active log file.
- `logprintf()` writes directly to the active log file.
- `log_f()` starts/stops/reports command logging.

## Dependencies
Uses signal helpers, allocation wrappers, global libxfs init state `x`, and command registration.

## Edge Cases
`dbprintf()` suppresses output after interrupt detection. The `log start <filename>` path opens `argv[2]` but stores `xstrdup(argv[1])`, so status later reports `"start"` rather than the filename; this appears to be a small diagnostic bug.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/output.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/output.h -->
# File Research: sources/local-fs/xfsprogs/db/output.h

## Purpose
Header for xfs_db output/logging helpers.

## Main Interfaces
- Declares global `dbprefix`.
- Declares `dbprintf()`, `logprintf()`, and `output_init()`.

## Dependencies
Used by nearly all command modules.

## Edge Cases
No logic.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/output.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/print.c -->
# File Research: sources/local-fs/xfsprogs/db/print.c

## Purpose
Implements the `print`/`p` command and generic structure/string printing support for xfs_db field descriptions.

## Main Interfaces
- `print_init()` registers `print`.
- `print_f()` invokes the current type’s print function in `DB_READ` mode.
- `print_struct()` prints all fields or selected field expressions.
- `print_string()` prints current data as a bounded string.
- `print_flist()` and `print_flist_1()` print parsed field lists with hierarchical prefixes.
- `print_sarray()` prints arrays of sub-structures.

## Behavior Notes
Selected fields are parsed with `flist_scan` and resolved with `flist_parse`. Array printing clamps count if the requested field range would exceed the current buffer length.

## Dependencies
Uses the field/type/fprint/flist systems, string-vector utilities, bit helpers, output, signal handling, and current cursor state.

## Edge Cases
Reports no current type or no print function gracefully. Stops long output if an interrupt is seen.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/print.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/print.h -->
# File Research: sources/local-fs/xfsprogs/db/print.h

## Purpose
Header for generic xfs_db print helpers.

## Main Interfaces
Declares `print_flist`, `print_init`, `print_sarray`, `print_struct`, and `print_string`.

## Dependencies
Used by field/type implementations and fuzzing.

## Edge Cases
Forward-declares `field` and `flist`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/print.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/quit.c -->
# File Research: sources/local-fs/xfsprogs/db/quit.c

## Purpose
Implements the `quit`/`q` command.

## Main Interfaces
- `quit_init()` registers the command.
- `quit_f()` returns `1`, which the command loop treats as “done”.

## Dependencies
Uses command registration and localized one-line text.

## Edge Cases
No arguments are accepted.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/quit.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/quit.h -->
# File Research: sources/local-fs/xfsprogs/db/quit.h

## Purpose
Header for quit command registration.

## Main Interfaces
- Declares `quit_init()`.

## Dependencies
Used by command initialization.

## Edge Cases
No logic.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/quit.h -->