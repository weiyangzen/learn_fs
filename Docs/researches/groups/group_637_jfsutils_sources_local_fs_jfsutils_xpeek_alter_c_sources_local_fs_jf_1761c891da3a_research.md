# Group Research: group_637_jfsutils_sources_local_fs_jfsutils_xpeek_alter_c_sources_local_fs_jf_1761c891da3a

Scope verified against `Docs/research_subset_a.md`: `sources/local-fs/jfsutils` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/xpeek/alter.c -->
# File Research: sources/local-fs/jfsutils/xpeek/alter.c

Implements the `alter` command for `jfs_debugfs`, allowing direct byte-level modification of a block device by supplying a JFS aggregate block number, a hex offset within that block, and an even-length hex digit string.

Main entry point:
- `alter(void)`: parses arguments from the current `strtok` command stream or prompts interactively.
- Converts `block` to a byte address with `block << l2bsize`.
- Parses `offset` as hexadecimal.
- Validates that the supplied hex string has an even number of digits.
- Reads a block-aligned region from disk with `ujfs_rw_diskblocks(..., GET)`.
- Converts each pair of hex digits into a byte and writes it into the buffer at the requested offset.
- Writes the modified aligned region back with `ujfs_rw_diskblocks(..., PUT)`.

Integration points:
- Uses globals `fp`, `bsize`, and `l2bsize` from `xpeek.c`/`xpeek.h`.
- Uses libfs device I/O from `devices.h`.
- Exposed through the command dispatcher in `xpeek.c`.

Notable behavior and risks:
- This is a raw destructive editor with no structural validation of JFS metadata.
- Length rounding uses `offset + hex_length` where `hex_length` is digit count, not byte count, so it may read/write a larger aligned range than strictly necessary.
- No explicit bounds check ensures `offset + bytes_to_write` stays within the allocated block-aligned buffer if pathological offsets overflow unsigned arithmetic.
- Uses `strtoull`/`strtoul` errno checks but does not reset `errno` before parsing `offset`.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/xpeek/alter.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/xpeek/directory.c -->
# File Research: sources/local-fs/jfsutils/xpeek/directory.c

Implements directory listing and interactive display/edit traversal for JFS directory B-trees (`dtree`) and extent trees (`xtree`). This is one of the central metadata inspection files for `jfs_debugfs`.

Major commands:
- `directory(void)`: displays directory entries for an inode.
- `dtree(void)`: displays and optionally modifies the root directory tree stored in a directory inode.
- `xtree(void)`: displays and optionally modifies an inode extent tree, using `di_dirtable` for directories and `di_btroot` for non-directories.

Directory listing flow:
- Parses inode number and optional fileset, currently only fileset `0` for `directory`/`dtree`.
- Resolves the inode using `find_inode`.
- Reads the inode with `xRead`.
- Swaps disk endian representation with `ujfs_swap_dinode`.
- Verifies `IFDIR`.
- If the dtree root is a leaf, prints entries from root slots directly.
- If not a leaf, descends through internal dtree nodes to the leftmost leaf, then follows `header.next` across leaf pages.

Directory entry handling:
- `print_direntry(struct dtslot *, uint8_t)`: reconstructs multi-slot Unicode names from a leaf entry plus continuation slots, converts them to UTF-8 with `Unicode_String_to_UTF8_String`, and prints inode number plus name.
- Uses global `UTF8_Buffer[8 * JFS_PATH_MAX]`.

Dtree interactive display/edit:
- `dtree(void)` prints root dtree header fields including DASD limit/used, flags, `nextindex`, free list, `idotdot`, and slot table.
- Allows modification of selected root fields through shared `m_parse`.
- Writes modified inode back after swapping with `ujfs_swap_dinode(..., PUT)`.
- Uses `display_leaf_slots`, `display_internal_slots`, `display_slot`, and `display_extent_page` for traversal.

Xtree interactive display/edit:
- `xtree(void)` resolves an inode from filesystem, primary aggregate, or secondary aggregate inode table.
- Displays root xtree fields through `display_xtpage`.
- Allows modification of xtpage header fields and writes the containing inode back.
- Traverses leaf/internal XAD arrays with `display_leaf_xads` and `display_internal_xads`.
- Descends to non-root xtpage blocks with `display_internal_xtpage`.

Helper APIs:
- `display_xtpage(xtpage_t *)`: prints xtpage flags, `nextindex`, `maxentry`, and self PXD address.
- `display_leaf_slots(...)`: displays leaf directory entries and optional directory index field when `type_jfs & JFS_DIR_INDEX`.
- `display_internal_slots(...)`: displays internal dtree child extents and separator names.
- `display_slot(...)`: recursively prints continuation slots.
- `display_extent_page(int64_t)`: reads, displays, modifies, and writes a non-root dtree page.
- `display_leaf_xads(...)` / `display_internal_xads(...)`: display XAD extents and allow descent for internal pages.
- `display_internal_xtpage(xad_t)`: reads and edits a child xtpage.
- `strToUcs(...)`: simplistic byte-to-`UniChar` copy for modified names.

Integration points:
- Depends on `find_inode`, `xRead`, `xWrite`, `m_parse`, and `prompt`.
- Uses JFS structures/macros from `jfs_dtree.h`, `jfs_xtree.h`, `jfs_filsys.h`, `jfs_unicode.h`, and endian helpers.
- Uses global `type_jfs` to choose endian conversion and directory-index display behavior.

Notable behavior and risks:
- The interactive modification paths can corrupt on-disk directory and extent trees; validation is minimal.
- `strToUcs` is not a full UTF-8 to UCS converter; edits through it only copy byte values into `UniChar`.
- Several reads/writes assume metadata structure sizes and block mappings are valid.
- Some traversal command returns are overloaded as character actions (`u`, `d`, `x`) and can be hard to reason about.
- Duplicate prototype for `display_slot` appears near the top.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/xpeek/directory.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/xpeek/display.c -->
# File Research: sources/local-fs/jfsutils/xpeek/display.c

Implements the generic `display` command for reading arbitrary aggregate blocks and rendering them as raw hex/ascii or selected JFS metadata structures.

Main entry point:
- `display(void)`: parses `block [offset [format [count]]]`, reads an aligned region, and dispatches by format.

Supported formats:
- `a`: byte/ascii hex dump; default length is one aggregate block.
- `x`: 4-byte unit hex-style dump through the same byte display routine; default count is `bsize / 4`.
- `i`: `struct dinode`; swaps with `ujfs_swap_dinode`, then calls `display_inode`.
- `I`: `struct iag`; swaps with `ujfs_swap_iag`, then calls `display_iag`.
- `s`: `struct superblock`; swaps with `ujfs_swap_superblock`, calls `display_super`, and writes back if changed.
- `X`: accepted in size calculation as `xad_t`, but falls through to “specified format not yet supported” in the final switch.

Hex rendering:
- `display_hex(char *addr, unsigned length, unsigned offset)` prints 16 bytes per line with offset, grouped hex text, and printable ASCII.
- Calls `more()` every 16 lines.

Integration points:
- Calls shared structure display functions implemented in `inode.c`, `iag.c`, and `super.c`.
- Uses globals `fp`, `bsize`, `l2bsize`, and `type_jfs`.
- Uses `ujfs_rw_diskblocks` for raw block access.

Notable behavior and risks:
- The `X` format is partially implemented only for sizing, not actual XAD rendering.
- `len` is rounded up to the aggregate block size, but allocation and read size are driven directly by user-controlled count and offset.
- If `display_super` changes a superblock, this command writes the whole read buffer back to the originally requested block address, making correct offset/block selection important.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/xpeek/display.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/xpeek/dmap.c -->
# File Research: sources/local-fs/jfsutils/xpeek/dmap.c

Implements interactive display and modification of the JFS aggregate block allocation map (`dmap`). It navigates from the block map inode to the dbmap control page, control pages at levels 0-2, dmap leaves, summary trees, and allocation bitmaps.

Main command:
- `dmap(void)`: reads aggregate block map inode `BMAP_I`, reads logical block 0 as `struct dbmap`, initializes `dmap_level` and `dmap_l2bpp`, then runs an action loop.

State/actions:
- `DISPLAY_DBMAP`: show top-level `struct dbmap`.
- `DISPLAY_CPAGE`: show a control page (`struct dmapctl`).
- `DISPLAY_LEAF`: show a dmap leaf (`struct dmap`).
- `DMAP_EXIT`: terminate.

Page mapping macros:
- `L1PAGE`, `L0PAGE`, and `DMAPPAGE` encode logical block numbers for the map tree layout.
- `decode_pagenum(...)` reverses logical page numbers into level-1, level-0, and dmap indexes.

Top-level control:
- `display_dbmap(...)` prints and edits map size, free count, AG geometry, preferred AG, AG free counts, and related fields.
- `display_agfree(...)` paginates/modifies the `dn_agfree` array.
- Writes back after endian swapping with `ujfs_swap_dbmap`.

Control pages:
- `display_cpage(...)` reads a mapped logical block through `ujfs_rwdaddr`, displays `nleafs`, `l2nleafs`, `leafidx`, `height`, and `budmin`.
- Supports modifying fields, going up, left/right sibling navigation, or entering the summary tree.

Dmap leaves:
- `display_leaf(...)` displays dmap leaf metadata, summary tree, working map (`wmap`), and persistent map (`pmap`).
- Uses `display_map` from `iag.c` for bitmap array editing.
- Supports sibling navigation and parent navigation.

Summary tree:
- `display_tree(...)` prints a small visual tree rooted at a selected top level/index.
- Supports back, descend to child page/leaf, goto, modify tree value, right/left, up, and exit.
- Marks `changed` when `stree` entries are edited so callers can write back the containing page.

Integration points:
- Depends on `find_inode`, `xRead`, `xWrite`, `ujfs_rwdaddr`, and `display_map`.
- Uses structures from `jfs_dmap.h`, `jfs_filsys.h`, and endian helpers.
- Uses global `type_jfs`, `bsize`, and `l2bsize`.

Notable behavior and risks:
- Modification paths have little semantic validation; incorrect map values can make allocation metadata inconsistent.
- `display_leaf` edits scalar dmap fields but returns to redisplay without immediately writing unless changes occur through subtree/map paths; scalar modifications rely on subsequent flow and may not persist as obviously as other paths.
- `display_tree` has hardcoded `tree_offset[6]` and accepts only heights 1-5.
- Several navigation paths assume fixed `LPERCTL` fanout and may not validate whether the logical target page exists in a smaller aggregate.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/xpeek/dmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/xpeek/fsckcbbl.c -->
# File Research: sources/local-fs/jfsutils/xpeek/fsckcbbl.c

Implements inspection and editing of JFS fsck workspace metadata, ClearBadBlockList/fsck communication records, and journal log superblock data.

Top-level commands:
- `cbblfsck(void)`: reads fsck workspace header, displays/edits the embedded `fsckcbbl_record`, writes back if changed.
- `fsckwsphdr(void)`: reads fsck workspace header, displays/edits `fsck_blk_map_hdr.hdr`, writes back if changed.
- `logsuper(void)`: reads the journal log superblock with `ujfs_get_logsuper`, displays/edits it, writes back with `ujfs_put_logsuper` if changed.

Display/edit helpers:
- `display_cbblfsck(struct fsck_blk_map_hdr *)`: prints fields such as eyecatchers, return code, block sizes, bad-block counts, relocation counts, LVM list count, and saved pointer fields. Allows field-by-field modification.
- `display_fsck_wsphdr(struct fsck_blk_map_hdr *)`: prints workspace header positions, timestamps, return code, fsck log offsets/status, and log write errors. Allows edits.
- `display_logsuper(struct logsuper *)`: prints log magic/version/serial, size, aggregate block size, flags, state name, end, UUID, label, and active filesystem UUIDs. Allows edits to main fields and parses UUID strings.

Workspace I/O:
- `get_fsckwsphdr(...)`: reads one page from global `fsckwsp_offset` using `xRead`, then endian-swaps with `ujfs_swap_fsck_blk_map_hdr`.
- `put_fsckwsphdr(...)`: swaps to disk order, writes one page with `xWrite`, then swaps back for continued in-memory use.

Integration points:
- Uses offsets initialized in `xpeek.c` from the mounted aggregate superblock.
- Uses `fsckcbbl.h`, `fsckwsp.h`, `jfs_logmgr.h`, `jfs_superblock.h`, `super.h`, and endian helpers.
- Shared UI parsing uses `m_parse`.

Notable behavior and risks:
- Several fields displayed/edited are pointer-valued fields from fsck structures; persisted pointer values are only meaningful in their original context and are risky to edit.
- Uses `%p` with manually prefixed `0x` in some output, which may print doubled prefixes on some C libraries.
- `jlog_super_offset` is declared extern but not used directly in this file.
- UUID edits validate format through `uuid_parse`; most other edits do not validate consistency.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/xpeek/fsckcbbl.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/xpeek/help.c -->
# File Research: sources/local-fs/jfsutils/xpeek/help.c

Implements textual help for `jfs_debugfs`.

Main entry point:
- `help(void)`: accepts zero or one command argument.
- With no argument, prints a full command list.
- With a command prefix, prints command-specific syntax and short explanations.

Covered commands:
- `alter`, `btree`, `cbblfsck`, `directory`, `dtree`, `display`, `dmap`, `fsckwsphdr`, `help`, `iag`, `inode`, `logsuper`, `quit`, `set`, `superblock`, `s2perblock`, `unset`, and `xtree`.

Integration points:
- Uses the same prefix-matching convention as `xpeek.c`.
- Documents some commands that are not implemented or only partially implemented in the dispatcher, such as `btree`, `set`, and `unset`.

Notable behavior and risks:
- Help advertises some `display` formats (`b`, `d`) that are not implemented in `display.c`.
- Help text for `s2perblock` prints `su[perblock] [p | s]`, likely a typo.
- Some messages contain spelling errors inherited from original utility text, such as “aggragate”.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/xpeek/help.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/xpeek/iag.c -->
# File Research: sources/local-fs/jfsutils/xpeek/iag.c

Implements display/modification of JFS inode allocation groups (IAGs), shared bitmap display helpers, inode extent display helpers, and the `find_iag` resolver used by inode lookup.

Main command:
- `iag(void)`: parses IAG number and optional table selector:
  - default filesystem inode table,
  - `a` for primary aggregate inode table,
  - `s` for secondary aggregate inode table.
- Resolves the IAG address with `find_iag`.
- Reads the IAG with `xRead`, endian-swaps with `ujfs_swap_iag`, displays it, and writes back if changed.

Display/edit helpers:
- `display_iag(struct iag *)`: prints AG start, IAG number, free-list links, inode/extents maps, free inode/extent counts, and menu labels for working map, persistent map, and inode extents.
- `change_iag(struct iag *)`: handles modification of scalar fields, or delegates to:
  - `display_map(iag->wmap, EXTSPERIAG)`,
  - `display_map(iag->pmap, EXTSPERIAG)`,
  - `display_ext(iag->inoext, cmdline)`.
- `display_map(unsigned *map, int size)`: paginates and edits arrays of 32-bit map words; also used by `dmap.c`.
- `display_ext(pxd_t *ext, char *cmdline)`: displays/modifies one inode extent PXD by index.

Lookup:
- `find_iag(unsigned iagnum, unsigned which_table, int64_t *address)`:
  - Converts IAG number to logical block with `IAGTOLBLK`.
  - Selects the fileset inode address from primary aggregate, secondary aggregate, or filesystem table.
  - Reads the fileset inode.
  - Walks its xtree using binary search over XADs.
  - Descends internal pages until it finds a leaf covering the target logical block.
  - Returns the physical byte address of the IAG.

Integration points:
- Used by `inode.c` for `find_inode`.
- Uses `AIT_2nd_offset` initialized in `xpeek.c`.
- Uses `xRead`, `xWrite`, endian helpers, and JFS xtree/filsys macros.

Notable behavior and risks:
- `find_iag` reads the fileset inode but does not explicitly endian-swap the inode/xtree root before using `__le16_to_cpu` on `nextindex`; XAD accessor macros may handle endian details, but this is a sensitive portability area.
- `display_map` calls `m_parse(cmdline, size - 1, ...)`, while `m_parse` accepts fields starting at 1, making index 0 not directly modifiable through that path.
- Editing IAG maps/extents can easily desynchronize inode allocation metadata.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/xpeek/iag.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/xpeek/inode.c -->
# File Research: sources/local-fs/jfsutils/xpeek/inode.c

Implements display/modification of JFS disk inodes and inode address resolution through IAGs.

Main command:
- `inode(void)`: parses inode number and optional table selector (`a`, `s`, or fileset `0`), resolves the inode address with `find_inode`, reads it, swaps to CPU order, displays it, and writes back if modified.

Display/edit:
- `display_inode(struct dinode *)`: prints core inode fields including inode stamp/fileset/number/generation, inode extent PXD, size, block count, link count, uid/gid, mode, timestamps, ACL descriptor, EA descriptor, next index, and ACL type.
- `change_inode(struct dinode *)`: allows modifying 35 displayed fields except reserved ACL/EA fields.
- `mode_string(mode_t)`: returns a compact 4-character type/permission summary, such as directory/read/write/execute indicators.

Lookup:
- `find_inode(unsigned inum, unsigned which_table, int64_t *address)`:
  - Computes IAG number and inode extent number from inode number.
  - Calls `find_iag`.
  - Reads the IAG through raw `ujfs_rw_diskblocks`.
  - Endian-swaps the IAG.
  - Uses `inoext[extnum]` to compute the physical byte address of the inode.

Integration points:
- Depends on `find_iag` from `iag.c`, `xRead`/`xWrite`, `ujfs_rw_diskblocks`, global `l2bsize`, `bsize`, and `type_jfs`.
- `display_inode` is also used by `display.c`.

Notable behavior and risks:
- Editing inode fields has minimal validation; invalid mode, extent, size, or timestamp values can corrupt filesystem semantics.
- `mode_string` tests `mode & ISUID & ISGID`, which only reports both bits if the bitwise chain remains nonzero; this is a questionable idiom and may not mean “both set” as clearly as `(mode & ISUID) && (mode & ISGID)`.
- `find_inode` returns failure when the target inode extent length is zero but does not explain allocation state to the caller.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/xpeek/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/xpeek/io.c -->
# File Research: sources/local-fs/jfsutils/xpeek/io.c

Provides unaligned byte-range read/write wrappers over libfs block I/O.

APIs:
- `xRead(int64_t address, unsigned count, char *buffer)`.
- `xWrite(int64_t address, unsigned count, char *buffer)`.

Behavior:
- Computes `offset = address & (bsize - 1)`.
- Rounds the affected range up to whole aggregate blocks.
- If the request is already block-aligned and block-sized, directly calls `ujfs_rw_diskblocks`.
- Otherwise reads the containing block-aligned range into a temporary buffer.
- `xRead` copies the requested subrange out.
- `xWrite` copies the caller buffer into the temporary block buffer and writes the whole aligned range back.

Integration points:
- Used throughout `xpeek` for structure reads/writes at byte offsets that may not be block aligned.
- Depends on globals `fp` and `bsize`, plus `devices.h`.

Notable behavior and risks:
- Uses bitwise `&` instead of logical `&&` in `if ((offset == 0) & (length == count))`; works for 0/1 comparison results but is non-idiomatic.
- No overflow checks for `offset + count + bsize - 1`.
- Read-modify-write behavior in `xWrite` can overwrite adjacent bytes if the underlying read buffer is stale due to concurrent device changes.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/xpeek/io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/xpeek/super.c -->
# File Research: sources/local-fs/jfsutils/xpeek/super.c

Implements display and modification of the standard JFS primary or secondary aggregate superblock.

Main command:
- `superblock(void)`: accepts optional `p` or `s`, reads the selected superblock with `ujfs_get_superblk`, calls `display_super`, and writes back with `ujfs_put_superblk` if changed.

Display/edit:
- `display_super(struct superblock *)`: prints superblock fields including:
  - magic/version/size/block sizes,
  - aggregate size,
  - platform and feature flags,
  - state,
  - compression,
  - secondary aggregate inode table PXD (`s_ait2`),
  - log device/serial/log PXD,
  - fsck workspace PXD,
  - timestamp,
  - fpack,
  - UUID, label, and log UUID for current JFS version.
- Converts state and flags into readable labels.
- Supports field-by-field modification through `m_parse`.
- Validates UUID fields using `uuid_parse`.

Integration points:
- Used directly by `superblock` command and indirectly by `display.c` format `s`.
- Uses `jfs_byteorder.h` conversion helpers for 24-bit/32-bit PXD fields.
- Uses PXD address macros from JFS headers.

Notable behavior and risks:
- This editor can alter core superblock identity, geometry, log, and fsck pointers with minimal validation.
- Endian conversion for fields uses byteorder macros inline for some PXD subfields; care is needed when comparing this to other code paths that swap whole superblocks.
- Argument handling has an `else if (strtok(...))` attached to the no-argument branch, so “too many arguments” after a valid first argument is not checked.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/xpeek/super.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/xpeek/super2.c -->
# File Research: sources/local-fs/jfsutils/xpeek/super2.c

Implements an alternate superblock display/edit command, exposed as `s2perblock` in the command dispatcher. It shows a different layout including `s_aim2` and fsck log fields.

Main command:
- `superblock2(void)`: accepts optional `p` or `s`, reads primary/secondary superblock with `ujfs_get_superblk`, calls `display_super2`, and writes back if changed.

Display/edit:
- `display_super2(struct superblock *)`: prints fields similar to `display_super`, but with alternate ordering and additional fields:
  - `s_aim2` PXD,
  - `s_fsckloglen`,
  - `s_fscklog`,
  - shortened flag/state labels,
  - UUID, label, and log UUID for current JFS version.
- Supports modifications for up to 32 fields when `s_version == JFS_VERSION`, otherwise up to 29 fields.
- Parses UUIDs through `uuid_parse`.

Integration points:
- Declared locally and referenced as `extern void superblock2(void)` in `xpeek.c`.
- Help text calls the command `s2perblock`.
- Uses `jfs_byteorder.h`, `jfs_filsys.h`, and `super.h`.

Notable behavior and risks:
- Same raw superblock-editing risks as `super.c`.
- There is an apparent naming mismatch: `xpeek.h` declares `void s2perblock(void);`, but this file implements `superblock2(void)` and `xpeek.c` calls `superblock2`.
- Argument handling shares the same weak “too many arguments” pattern as `super.c`.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/xpeek/super2.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/xpeek/ui.c -->
# File Research: sources/local-fs/jfsutils/xpeek/ui.c

Provides shared UI parsing for interactive metadata modification commands.

Main API:
- `m_parse(char *cmd_line, int n_fields, char **value)`.

Behavior:
- Assumes the caller has already parsed the `m` subcommand with `strtok`.
- Reads a field number from the remaining command line or prompts interactively.
- Validates field number is in `1..n_fields`.
- Extracts exactly one value token.
- Rejects missing or extra arguments.
- Returns the selected field number, or `0` on parse/validation failure.

Integration points:
- Used by most editor commands: inode, iag, dmap, dtree/xtree, fsck workspace, logsuper, and superblock handlers.

Notable behavior and risks:
- Only supports single-token values; labels, strings, or names containing spaces cannot be entered through this parser.
- Uses fixed prompt read length of 80 bytes supplied by callers.
- Does not perform numeric conversion itself, so each caller must validate conversion semantics.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/xpeek/ui.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/xpeek/xpeek.c -->
# File Research: sources/local-fs/jfsutils/xpeek/xpeek.c

Contains the `jfs_debugfs` program entry point, global runtime state, device opening, superblock-derived initialization, and the main command dispatcher.

Global state defined:
- `unsigned type_jfs`: superblock flags used by endian/format logic.
- `int bsize`: aggregate block size.
- `FILE *fp`: opened block device stream used by libfs.
- `short l2bsize`: log2 aggregate block size.
- `int64_t AIT_2nd_offset`: secondary aggregate inode table byte offset.
- `int64_t fsckwsp_offset`: fsck workspace byte offset.
- `int64_t jlog_super_offset`: journal log superblock byte offset.

Startup flow:
- Prints version from `VERSION` and `JFSUTILS_DATE`.
- Emits terminal escape sequence to put console into UTF-8 mode.
- Requires exactly one block device argument.
- Opens the device read/write using `fopen(device, "r+")`.
- Reads primary superblock, falling back to secondary if needed.
- Initializes global block size, log2 block size, superblock flags, secondary AIT offset, fsck workspace offset, and journal log super offset.
- Enters a prompt loop reading commands from stdin.

Command dispatch:
- Prefix-matches commands using the typed command length.
- Dispatches implemented commands: `alter`, `cbblfsck`, `directory`, `dmap`, `dtree`, `xtree`, `display`, `fsckwsphdr`, `help`, `iag`, `inode`, `logsuper`, `superblock`, `s2perblock`, and `quit`.
- Reports unimplemented `btree`, `set`, and `unset`.
- Flushes and closes the device at exit.

Integration points:
- Central user-facing hub for all files in this group.
- Relies on `ujfs_get_superblk`, `ujfs_flush_dev`, PXD address macros, and constants such as `LOGPSIZE`.

Notable behavior and risks:
- Prefix matching allows short abbreviations but can make command ambiguity dependent on ordering and minimum-length guards.
- Opens the device read/write even for display-only use.
- The tool assumes the filesystem is unmounted, but this file does not enforce that.
- If both primary and secondary superblock reads fail, execution jumps to cleanup and returns `0`, not an error status.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/xpeek/xpeek.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/xpeek/xpeek.h -->
# File Research: sources/local-fs/jfsutils/xpeek/xpeek.h

Common header for the `xpeek`/`jfs_debugfs` utility. It declares shared globals, status constants, and cross-file function prototypes.

Definitions:
- `AGGREGATE_2ND_I -1`: selector for the secondary aggregate inode table.
- `XPEEK_OK`, `XPEEK_CHANGED`, `XPEEK_REDISPLAY`, `XPEEK_ERROR`: shared return/status flags for interactive editor flows.

Shared globals:
- `extern int bsize`.
- `extern FILE *fp`.
- `extern short l2bsize`.

Declared APIs:
- Commands: `alter`, `cbblfsck`, `directory`, `display`, `dmap`, `dtree`, `help`, `fsckwsphdr`, `iag`, `inode`, `logsuper`, `superblock`, `s2perblock`, `xtree`.
- Display helpers: `display_iag`, `display_inode`, `display_super`.
- Lookup helpers: `find_iag`, `find_inode`.
- UI helpers: `m_parse`, `more`, `prompt`.
- I/O helpers: `xRead`, `xWrite`.

Included JFS structures:
- `jfs_types.h`, `jfs_dinode.h`, `jfs_imap.h`, and `jfs_superblock.h`.

Notable behavior and risks:
- Defines `#define fputs(string,fd) { fputs(string,fd); fflush(fd); }`, wrapping all subsequent `fputs` calls in including translation units to force flushing. This is unusual, can surprise maintainers, and shadows the C library function name.
- Prototype `void s2perblock(void);` does not match the implementation name `superblock2(void)` used by `xpeek.c`.
- The header centralizes many unrelated command prototypes, reflecting the utility’s tightly coupled design.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/xpeek/xpeek.h -->