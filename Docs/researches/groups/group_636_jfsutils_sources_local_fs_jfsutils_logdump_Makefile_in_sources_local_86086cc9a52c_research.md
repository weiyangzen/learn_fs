# Group Research: group_636_jfsutils_sources_local_fs_jfsutils_logdump_Makefile_in_sources_local_86086cc9a52c

Scope confirmed against `Docs/research_subset_a.md`: all files are under `sources/local-fs/jfsutils`, which is included in subset A. Every listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/logdump/Makefile.in -->
# File Research: sources/local-fs/jfsutils/logdump/Makefile.in

Generated Automake 1.11.1 template for the `logdump` subdirectory. It defines `jfs_logdump$(EXEEXT)` as an `sbin_PROGRAMS` target built from `logdump.c` and `helpers.c`.

Key build details:
- Includes `-I$(top_srcdir)/include -I$(top_srcdir)/libfs`.
- Links against `../libfs/libfs.a -luuid`.
- Installs `jfs_logdump.8` into man section 8.
- Uses Autoconf substitution variables for compiler, flags, install paths, dependency tracking, and maintainer-mode regeneration.
- Provides standard Automake targets for build, install, uninstall, clean, distclean, tags, and distribution packaging.

Filesystem relevance: this is build metadata for the JFS journal dump utility, not runtime filesystem logic.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/logdump/Makefile.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/logdump/helpers.c -->
# File Research: sources/local-fs/jfsutils/logdump/helpers.c

Provides minimal helper substitutes for fsck/logredo routines needed by `jfs_logdump` outside the full fsck environment.

Important functions:
- `alloc_wrksp(...)`: allocates heap workspace, rounding the requested size upward. It initializes the output pointer to `NULL`, calls `malloc`, and currently returns `0` even if allocation fails.
- `v_fsck_send_msg(...)`: formats a message from `msg_defs[msg_num]` using varargs, appends source file and line detail, and prints to stdout.

Dependencies:
- Uses `fsck_message.h`, `jfs_types.h`, and external message globals such as `msg_defs`.
- Exists to satisfy logredo/fsck-linked code paths used by log dumping.

Notable risk: `alloc_wrksp` does not set an error return on `malloc` failure, so callers must not assume nonzero return means allocation failure.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/logdump/helpers.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/logdump/logdump.c -->
# File Research: sources/local-fs/jfsutils/logdump/logdump.c

Command-line front end for dumping a JFS journal log. It prints version information, parses options, opens the target block device read-only, and calls external `jfs_logdump(...)`.

Important behavior:
- Supports `jfs_logdump [-a] <block device>`.
- `-a` or `-A` sets `dump_all = -1`, requesting a full log dump instead of only committed transactions since the last sync point.
- Device arguments must begin with `/`; otherwise parsing rejects them.
- Stores the selected device in global `Vol_Label`.
- Opens the device with `fopen(Vol_Label, "r")`, calls `jfs_logdump(Vol_Label, Dev_IOPort, dump_all)`, then closes it.

Globals:
- `Dev_IOPort`, `Dev_blksize`, `Vol_Label`, `dump_all`.
- Defines dummy `log_device[1]` to avoid a linker error.
- Sets external `prog` to `"jfs_logdump"` for message handling.

Filesystem relevance: entry point for reading and decoding JFS journal/log structures through shared libfs/logredo routines.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/logdump/logdump.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/missing -->
# File Research: sources/local-fs/jfsutils/missing

GNU Automake `missing` helper script, version `2009-04-28.21`. It is a portability shim used when maintainer tools are absent or too old.

Supported tool fallbacks:
- `aclocal`, `autoconf`, `autoheader`, `automake`, `autom4te`
- `bison`/`yacc`, `flex`/`lex`
- `help2man`, `makeinfo`, `tar`

Behavior:
- With `--run`, tries to execute the requested tool first.
- If the tool is unavailable, prints a warning and touches or creates generated outputs where possible.
- For parser/lexer generators, may copy existing generated `.c`/`.h` files or create trivial stubs.
- For `help2man`, creates an `.ab help2man is required...` stub if needed.
- Exits with failure for unknown unsupported tools.

Filesystem relevance: build-system support only. It can affect regenerated build artifacts, but contains no JFS logic.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/missing -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/mkfs/Makefile -->
# File Research: sources/local-fs/jfsutils/mkfs/Makefile

Configured Automake-generated makefile for building `jfs_mkfs` in this checked-out tree.

Key build details:
- Builds `jfs_mkfs$(EXEEXT)` from `initmap.c`, `inodemap.c`, `inodes.c`, `mkfs.c`, and headers.
- Links `../libfs/libfs.a -luuid`.
- Adds `AM_CPPFLAGS = -DONE_FILESET_PER_AGGR`.
- Installs the binary into `/sbin`.
- Installs `jfs_mkfs.8` and creates compatibility hard links:
  - `/sbin/mkfs.jfs` -> `jfs_mkfs`
  - `mkfs.jfs.8` -> `jfs_mkfs.8`
- Includes concrete configure outputs: `CC=gcc`, `CFLAGS=-g -O2`, `AM_CFLAGS=-Wall -Wstrict-prototypes -fno-strict-aliasing`, `host_alias=mipsel-buildroot-linux-uclibc-`, and `/data2/jfsutils-1.1.15` build paths.

Filesystem relevance: configured build metadata for the JFS formatter.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/mkfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/mkfs/Makefile.am -->
# File Research: sources/local-fs/jfsutils/mkfs/Makefile.am

Source Automake definition for `jfs_mkfs`.

Defines:
- Include paths to top-level `include` and `libfs`.
- Link dependency on `../libfs/libfs.a -luuid`.
- `AM_CPPFLAGS = -DONE_FILESET_PER_AGGR`.
- `sbin_PROGRAMS = jfs_mkfs`.
- Man page `jfs_mkfs.8`.
- Sources: `initmap.c`, `inodemap.c`, `inodes.c`, `mkfs.c`, `initmap.h`, `inodemap.h`, `inodes.h`.

Install hooks create the standard `mkfs.jfs` command and man-page aliases. Uninstall hook removes those aliases.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/mkfs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/mkfs/Makefile.in -->
# File Research: sources/local-fs/jfsutils/mkfs/Makefile.in

Generated Automake 1.11.1 template for the `mkfs` directory.

Key build details:
- Builds `jfs_mkfs$(EXEEXT)` from `initmap`, `inodemap`, `inodes`, and `mkfs` objects.
- Uses Autoconf substitutions for compiler/tool paths and dependency tracking.
- Includes `AM_CPPFLAGS = -DONE_FILESET_PER_AGGR`.
- Links `../libfs/libfs.a -luuid`.
- Installs `jfs_mkfs.8`.
- Includes install hooks to create `mkfs.jfs` binary and man-page aliases, plus uninstall cleanup.

Filesystem relevance: portable build template for the formatter source files.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/mkfs/Makefile.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/mkfs/initmap.c -->
# File Research: sources/local-fs/jfsutils/mkfs/initmap.c

Implements JFS aggregate block allocation map construction and bad-block recording for `jfs_mkfs`.

Major responsibilities:
- Builds dmap pages and dmapctl hierarchy for the block allocation map.
- Initializes the global block map control page (`dbmap`).
- Tracks allocated/free blocks through `markit`.
- Writes the completed block map to disk.
- Supports bad-block inode growth using xtree append/split logic.
- Optionally verifies unused tail filesystem blocks and records bad media blocks.

Key functions:
- `initdmap(...)`: initializes and writes one dmap page, using a reusable empty-page template for full free dmaps.
- `initctl(...)`: recursively builds dmapctl levels and child dmaps.
- `initbmap(...)`: initializes the full block map tree and writes the control page.
- `alloc_map(...)`: allocates dmap pointer array and control page.
- `initmap(...)`: initializes `dbmap` sizing, free counts, allocation group layout, and AG free counts.
- `calc_map_size(...)`: computes block-map size, initializes the block-map inode, allocates in-memory map structures, and resets allocation tracking.
- `markit(...)`: marks a block allocated or free in the working/persistent dmap maps and updates free counts.
- `write_block_map(...)`: finalizes map trees and writes the block map.
- `dbAlloc(...)`: finds contiguous free blocks for bad-block xtree page allocation.
- `xtSplitRoot(...)`, `xtSplitPage(...)`, `xtAppend(...)`: append bad-block extents to the bad-block inode xtree, splitting pages as needed.
- `verify_last_blocks(...)`: writes and reads unused blocks from `last_allocated + 1` to end of aggregate; records failed blocks into the bad-block inode.

Notable details:
- Uses endian swap helpers before on-disk writes.
- Uses `O_DIRECT` when available during verification to avoid page cache effects.
- `last_allocated` ignores bad blocks so allocator search state is based on real metadata allocations.
- `markit` checks `if (page > sz_block_map_array)`, which appears off by one; valid indices are less than `sz_block_map_array`.

Filesystem relevance: core formatter logic for on-disk JFS block allocation metadata.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/mkfs/initmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/mkfs/initmap.h -->
# File Research: sources/local-fs/jfsutils/mkfs/initmap.h

Header for mkfs block-map initialization.

Defines flags:
- `ALLOC`
- `FREE`
- `BADBLOCK`

Declares:
- `calc_map_size(...)`
- `markit(...)`
- `record_LVM_BadBlks(...)`
- `verify_last_blocks(...)`
- `write_block_map(...)`

Filesystem relevance: public interface from `mkfs.c`, inode initialization, and bad-block handling into block-map construction.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/mkfs/initmap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/mkfs/inodemap.c -->
# File Research: sources/local-fs/jfsutils/mkfs/inodemap.c

Initializes the first inode allocation map extent for either aggregate or fileset inode maps.

Important functions:
- `init_AG_free_list(...)`: determines which allocation group contains the initial inode extent and initializes that AG’s free-inode/free-extent list entries. Other AG entries are set empty.
- `init_inode_map(...)`: allocates a combined inode-map buffer, initializes the dinomap control page and first IAG, writes it to disk, and marks the inode-map blocks allocated in the block map.

Key metadata initialized:
- `dinomap` fields: free IAG, next IAG, inode counts, free counts, blocks per inode extent.
- First `iag`: IAG number, AG start, free-list pointers, free inode/extent counts, working and persistent maps.
- First inode extent descriptor points at the initialized inode table.
- Summary maps (`extsmap`, `inosmap`) are derived from extent descriptors and inode bitmaps.

Special case:
- Aggregate inode map uses initial bitmap `0xf8008000`.
- Fileset inode map uses `0xf0000000`.

Filesystem relevance: creates the on-disk inode allocation structures required before a fresh JFS filesystem can allocate inodes.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/mkfs/inodemap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/mkfs/inodemap.h -->
# File Research: sources/local-fs/jfsutils/mkfs/inodemap.h

Header for inode-map initialization.

Declares:
- `init_inode_map(int, FILE *, int64_t, int, int64_t, int, unsigned short, int, unsigned)`

Includes `devices.h` for device I/O types.

Filesystem relevance: exposes inode allocation map construction to the mkfs aggregate/fileset creation flow.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/mkfs/inodemap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/mkfs/inodes.c -->
# File Research: sources/local-fs/jfsutils/mkfs/inodes.c

Initializes initial aggregate and fileset inodes for a newly formatted JFS filesystem.

Key functions:
- `init_aggr_inode_table(...)`: writes the first aggregate inode extent, initializes aggregate self inode, inline log inode, and bad-block inode, swaps inode endianness for disk, and marks inode-table blocks allocated.
- `init_fileset_inode_table(...)`: writes first fileset inode extent, including reserved inode, extension/superblock-reserved inode, root directory inode, and ACL inode.
- `init_fileset_inodes(...)`: writes the aggregate fileset inode that points to the fileset inode map.
- `init_inode(...)`: common initializer for dinode fields and inline/extent/no-data data roots.

Root directory initialization:
- Creates a directory B+tree root in the root inode’s DASD area.
- Sets `DXD_INDEX | BT_ROOT | BT_LEAF`.
- Initializes root free slot chain, `idotdot`, link count, and directory free counters.

Extent inode initialization:
- Creates an inline xtree root with an initial XAD when data exists.
- For `no_data`, creates an empty xtree root with `nextindex = XTENTRYSTART`.

Filesystem relevance: lays down the minimal inode set required for a valid JFS aggregate and its initial fileset.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/mkfs/inodes.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/mkfs/inodes.h -->
# File Research: sources/local-fs/jfsutils/mkfs/inodes.h

Header for initial inode construction.

Defines:
- `ino_data_type` enum: `inline_data`, `extent_data`, `max_extent_data`, `no_data`.

Declares:
- `init_aggr_inode_table(...)`
- `init_fileset_inode_table(...)`
- `init_fileset_inodes(...)`
- `init_inode(...)`

Filesystem relevance: shared interface for building aggregate/fileset inode tables during formatting.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/mkfs/inodes.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/mkfs/mkfs.c -->
# File Research: sources/local-fs/jfsutils/mkfs/mkfs.c

Top-level `jfs_mkfs` formatter implementation. It parses command-line options, validates the device, creates or attaches a journal, lays out aggregate/fileset metadata, and writes superblocks last.

Command-line options:
- `-c`: verify blocks before building filesystem.
- `-O`: OS/2 compatibility/case-insensitive mode.
- `-q` or `-f`: quiet/no confirmation.
- `-V`: version only.
- `-j log_device`: external journal device.
- `-J device=...` or `-J journal_dev`: attach existing journal or create journal-only device.
- `-L vol_label`: set label.
- `-s log_size`: inline log size in MB.
- Optional trailing block count limits filesystem size.

Main flow:
- Rejects missing/extra args and invalid devices.
- Refuses to format mounted devices.
- Opens the device exclusively.
- Validates size against `MINJFS`.
- Prompts before destructive operations unless quiet.
- Formats external or internal journal via `jfs_logform`.
- Calls `create_aggregate(...)`.
- Flushes and closes device, then reports success/failure.

`create_aggregate(...)`:
- Reserves fsck workspace at the end of the aggregate.
- Initializes block allocation map.
- Clears reserved blocks and zeroes old primary/secondary superblocks first.
- Initializes primary aggregate inode map/table.
- Initializes secondary aggregate inode map/table after the block map.
- Creates the initial fileset.
- Optionally verifies blocks and records bad blocks.
- Writes the completed block map.
- Constructs the superblock, including AG size, log location/device, fsck workspace, UUID, label, flags, and secondary inode-map descriptors.
- Validates and writes primary and secondary superblocks last.

Notable issues:
- In `parse_journal_opts`, the UUID/LABEL open result handling appears inverted: it calls `fclose(log_fd)` when `log_fd == NULL`, which would be invalid.
- Uses `strcpy` into fixed `logdev[255]` for journal device strings.
- `volume_label` is fixed at 16 bytes and copied with `strncpy`.

Filesystem relevance: primary JFS filesystem creation utility and the central orchestrator for all mkfs metadata writers.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/mkfs/mkfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/tune/Makefile -->
# File Research: sources/local-fs/jfsutils/tune/Makefile

Configured Automake-generated makefile for `jfs_tune`.

Key build details:
- Builds `jfs_tune$(EXEEXT)` from `tune.c` and `super.c`.
- Links `../libfs/libfs.a -luuid`.
- Installs into `/sbin`.
- Installs `jfs_tune.8` into man section 8.
- Contains concrete configured values: `CC=gcc`, `CFLAGS=-g -O2`, `AM_CFLAGS=-Wall -Wstrict-prototypes -fno-strict-aliasing`, `host_alias=mipsel-buildroot-linux-uclibc-`, and `/data2/jfsutils-1.1.15` paths.

Filesystem relevance: configured build metadata for the JFS tuning/superblock-editing utility.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/tune/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/tune/Makefile.am -->
# File Research: sources/local-fs/jfsutils/tune/Makefile.am

Source Automake definition for `jfs_tune`.

Defines:
- Include paths to top-level `include` and `libfs`.
- Link dependency on `../libfs/libfs.a -luuid`.
- `sbin_PROGRAMS = jfs_tune`.
- Man page `jfs_tune.8`.
- Sources: `tune.c` and `super.c`.

Filesystem relevance: minimal source build recipe for the superblock/log-superblock tune utility.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/tune/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/tune/Makefile.in -->
# File Research: sources/local-fs/jfsutils/tune/Makefile.in

Generated Automake 1.11.1 template for the `tune` directory.

Key build details:
- Builds `jfs_tune$(EXEEXT)` from `tune.o` and `super.o`.
- Links `../libfs/libfs.a -luuid`.
- Installs `jfs_tune.8`.
- Provides standard Automake compile, dependency, install, uninstall, clean, tags, and dist targets.

Filesystem relevance: portable build template for `jfs_tune`.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/tune/Makefile.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/tune/super.c -->
# File Research: sources/local-fs/jfsutils/tune/super.c

Display helpers for JFS filesystem superblocks and external log superblocks.

Important functions:
- `build_flag_string(...)`: converts `s_flag`/log `flag` bits into readable flag names such as `JFS_LINUX`, `JFS_OS2`, `JFS_GROUPCOMMIT`, `JFS_INLINELOG`, and sparse/DASD flags.
- `display_super(...)`: prints magic, version, state, flags, block sizes, aggregate size, log device, creation time, UUID, label, and external log UUID.
- `display_logsuper(...)`: prints log magic/version, mount serial, block size, size, flags, state, log UUID, label, and active filesystem UUID slots.

Filesystem relevance: read-only inspection formatting for `jfs_tune -l`.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/tune/super.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/tune/tune.c -->
# File Research: sources/local-fs/jfsutils/tune/tune.c

Implements `jfs_tune`, which lists or updates JFS filesystem/log superblock metadata.

Supported operations:
- `-l`: display filesystem or log superblock.
- `-L vol_label`: update volume/log label.
- `-U uuid`: set UUID to explicit UUID, `null`/`clear`, `time`, or `random`.
- `-J device=...`: attach an external journal to a filesystem.
- `-V`: version only.

Main behavior:
- Parses options and requires exactly one device.
- Opens read-only for listing, read/write for mutation.
- Refuses mutation on mounted filesystems; only `-l` is allowed when mounted.
- Tries primary filesystem superblock, then secondary filesystem superblock, then log superblock.
- Fixes a historical mkfs 1.0.18/1.0.19 external-journal version issue by updating filesystem version when safe.
- Updates both old `s_fpack` and newer `s_label` fields for filesystem labels.
- For UUID updates, bumps old filesystem superblock version to 2 so mount can recognize UUIDs.
- External journal attach validates the log superblock, copies log device number and UUID into the filesystem superblock, clears `JFS_INLINELOG`, and writes the updated superblock.

Notable bug:
- `EXIT(fd, rc)` expands to `fclose(fd); exit(rc);`, so it is only safe with valid open `FILE *`.

Filesystem relevance: controlled superblock/log-superblock metadata mutation and inspection utility.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/tune/tune.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/xpeek/Makefile -->
# File Research: sources/local-fs/jfsutils/xpeek/Makefile

Configured Automake-generated makefile for `jfs_debugfs`, the interactive JFS debug/inspection tool.

Key build details:
- Builds `jfs_debugfs$(EXEEXT)`.
- Sources include `alter.c`, `display.c`, `fsckcbbl.c`, `iag.c`, `io.c`, `super2.c`, `xpeek.c`, `directory.c`, `dmap.c`, `help.c`, `inode.c`, `super.c`, `ui.c`, and `xpeek.h`.
- Links `../libfs/libfs.a -luuid`.
- Installs `jfs_debugfs.8`.
- Contains concrete configured values for the local build, including `/data2/jfsutils-1.1.15` paths and `host_alias=mipsel-buildroot-linux-uclibc-`.

Filesystem relevance: configured build metadata for the JFS low-level debug browser/editor.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/xpeek/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/xpeek/Makefile.am -->
# File Research: sources/local-fs/jfsutils/xpeek/Makefile.am

Source Automake definition for `jfs_debugfs`.

Defines:
- Include paths to top-level `include` and `libfs`.
- Link dependency on `../libfs/libfs.a -luuid`.
- `sbin_PROGRAMS = jfs_debugfs`.
- Man page `jfs_debugfs.8`.
- Source list for the interactive debugger: alter/display/fsck callback/directory/dmap/help/iag/inode/io/super/ui/xpeek modules and `xpeek.h`.

Filesystem relevance: build recipe for the JFS inspection/debugging utility.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/xpeek/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/xpeek/Makefile.in -->
# File Research: sources/local-fs/jfsutils/xpeek/Makefile.in

Generated Automake 1.11.1 template for the `xpeek` directory.

Key build details:
- Builds `jfs_debugfs$(EXEEXT)`.
- Compiles all xpeek/debugfs modules into one binary.
- Links against `../libfs/libfs.a -luuid`.
- Installs `jfs_debugfs.8`.
- Includes Automake dependency tracking for each object file.
- Provides standard build, install, uninstall, clean, distclean, tags, and distribution targets.

Filesystem relevance: portable build template for the low-level JFS debug tool.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/xpeek/Makefile.in -->