# Group Research: group_456_gfs2_utils_sources_local_fs_gfs2_utils_Makefile_am_sources_local_fs__93bf8906f460

Scope: `Docs/research_subset_a.md` includes `sources/local-fs/gfs2-utils`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/Makefile.am -->
# File Research: sources/local-fs/gfs2-utils/Makefile.am

## Purpose
Top-level Automake file for `gfs2-utils`. It defines distributed extras, clean targets, subdirectories, gettext/aclocal setup, and an RPM build target.

## Main Elements
- `EXTRA_DIST`: ships `autogen.sh` and `README.md`.
- `MAINTAINERCLEANFILES`: removes generated Autotools/libtool/configure artifacts and generated cluster config headers.
- `SUBDIRS`: builds `po`, `gfs2`, `doc`, and `tests`.
- `RPMSPEC`, `RPMRELEASE`, `RPMBUILDDIR`, `RPMBUILDOPTS`: produce a spec from `tests/gfs2-utils.spec.in` and build an in-place RPM.
- `maintainer-clean-local`: removes the local `m4` macro directory.

## Dependencies And Integration
Depends on Autotools-generated `config.status`, gettext/po integration, and the recursive `gfs2` subdir. RPM packaging expects `rpmbuild` and the generated spec template.

## Risk Notes
The RPM release is derived from `git describe` and falls back to `"0"`, so source tarballs without git metadata may produce generic release values.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/autogen.sh -->
# File Research: sources/local-fs/gfs2-utils/autogen.sh

## Purpose
Bootstrap helper for generating the Autotools build system.

## Main Elements
- Creates `m4`.
- Runs `autoreconf -i -v`.
- Prints a short next-step message to run `./configure` and `make`.

## Dependencies And Integration
Used before configuring from a source checkout. Depends on Autoconf, Automake, libtoolize/autoreconf tooling, and macro availability.

## Risk Notes
No error handling beyond shell `&&`; if `mkdir -p m4` succeeds but `autoreconf` fails, users only see autoreconf diagnostics.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/autogen.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/configure.ac -->
# File Research: sources/local-fs/gfs2-utils/configure.ac

## Purpose
Autoconf configuration for `gfs2-utils`, defining package identity, compiler/tool checks, dependency discovery, feature flags, generated files, and the final configure summary.

## Main Elements
- Package setup: requires Autoconf 2.69, initializes `gfs2-utils` version `3.6.1.1.dev`, Automake, libtool, gettext, config headers, and macro directory.
- Prefix sanitation: defaults prefix/sysconf/localstate/libdir to `/usr`, `/etc`, `/var`, and `/usr/lib` or `/usr/lib64`.
- Tool checks: requires GNU make, C compiler with C99, flex, bison, install/ln/make helpers.
- Helper shell functions: `cc_supports_flag()` and `check_lib_no_libs()`.
- Feature options: `--enable-debug`, `--enable-gcov`, `--enable-gprof`, `--with-udevdir`, `--with-testvol`.
- Dependencies: Check unit test framework, zlib, blkid, uuid, bzip2, ncurses, libintl/gettext.
- Compiler flags: large-file defines, include paths, debug/optimization/fortify, optional coverage/profiling, and probed warning flags.
- Outputs: all Makefiles under `gfs2`, `doc`, `tests`, and `po`, plus `tests/atlocal` and spec file.

## Dependencies And Integration
Feeds generated `make/clusterautoconfig.h` and all recursive Automake files. `AM_CONDITIONAL([HAVE_CHECK])` controls inclusion of unit-test make fragments.

## Risk Notes
The script calls `LT_INIT` twice. Several fallback library checks intentionally mutate and restore `LIBS`; mistakes there would over-link targets. `local` in shell helper functions assumes a shell supporting it during configure execution.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/configure.ac -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/Makefile.am -->
# File Research: sources/local-fs/gfs2-utils/gfs2/Makefile.am

## Purpose
Recursive Automake entry point for the `gfs2` utilities tree.

## Main Elements
- `MAINTAINERCLEANFILES = Makefile.in`.
- `SUBDIRS`: `include`, `libgfs2`, `edit`, `fsck`, `mkfs`, `man`, `tune`, `glocktop`, and `scripts`.

## Dependencies And Integration
Defines build order for shared headers/library before tools such as `gfs2_edit` and `fsck.gfs2`.

## Risk Notes
Subdirectory order matters because utility targets link against `gfs2/libgfs2/libgfs2.la`.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/Makefile.am -->
# File Research: sources/local-fs/gfs2-utils/gfs2/edit/Makefile.am

## Purpose
Builds the `gfs2_edit` administrative/editor utility.

## Main Elements
- Installs `gfs2_edit` under `sbin_PROGRAMS`.
- Headers: `gfs2hex.h`, `hexedit.h`, `extended.h`, `struct_print.h`, `journal.h`.
- Sources: `gfs2hex.c`, `hexedit.c`, `savemeta.c`, `extended.c`, `struct_print.c`, `journal.c`.
- Links against `libgfs2`, ncurses, zlib, bzip2, and uuid.
- Includes `checks.am` when Check is available.

## Dependencies And Integration
Uses global `AM_CPPFLAGS` and configured dependency flags from `configure.ac`. The executable depends on libgfs2 metadata parsing, curses display, and compression libraries for save/restore metadata.

## Risk Notes
The unit test target compiles the whole tool with `-DUNITTESTS`; this avoids the real `main()` but still pulls in broad operational code.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/check_edit.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/edit/check_edit.c

## Purpose
Minimal Check framework test harness for `gfs2_edit`.

## Main Elements
- Defines one stub test, `test_edit_stub`, asserting true.
- Creates suite `hexedit.c` and case `gfs2_edit`.
- Runs tests with `CK_ENV` and returns nonzero on failures.

## Dependencies And Integration
Compiled by `gfs2/edit/checks.am` together with all `gfs2_edit` sources and `-DUNITTESTS`.

## Risk Notes
This is only a smoke/stub test and exercises no real editor, metadata, save/restore, or journal behavior.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/check_edit.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/checks.am -->
# File Research: sources/local-fs/gfs2-utils/gfs2/edit/checks.am

## Purpose
Automake test fragment for `gfs2_edit`.

## Main Elements
- `TESTS = check_edit`.
- Builds `check_edit`.
- Reuses `$(gfs2_edit_SOURCES)` plus `check_edit.c`.
- Adds `-DUNITTESTS`, Check CFLAGS/LIBS, and suppresses unused-function warnings.

## Dependencies And Integration
Included only under `if HAVE_CHECK` from `Makefile.am`.

## Risk Notes
Because the test binary links the editor source set, missing external dependencies still break tests even though the test body is a stub.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/checks.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/extended.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/edit/extended.c

## Purpose
Implements the extended display mode for `gfs2_edit`, showing indirect pointers, directory entries, resource group indexes, journal status, and system-file contents beyond raw hex/structure views.

## Main Elements
- Indirect scanning: `_do_indirect_extended()` and `do_indirect_extended()` parse nonzero 64-bit block pointers and preserve metapath indexes.
- Inode context helpers: `get_height()`, `dinode_valid()`, and `metapath_to_lblock()` infer height and file offsets from navigation history.
- Display routines:
  - `display_indirect()` prints indirect block lists and optional recursive details.
  - `display_leaf()` prints directory leaf metadata and dirents.
  - `print_block_details()` recursively reads indirect/leaf chains in non-curses output.
- System-file views:
  - `print_gfs2_jindex()` lists journals and clean/dirty status.
  - `parse_rindex()` prints rindex or backing rgrp data.
  - `print_inum()`, `print_statfs()`, `print_quota()` decode system inode contents.
- `display_extended()` dispatches based on current block identity and available metadata.

## Dependencies And Integration
Uses global editor state from `hexedit.h`, libgfs2 inode/buffer helpers, `gfs2hex.c` directory decoding, and `struct_print.c` field printers. Called from `display()` when `dmode == EXTENDED_MODE`.

## Risk Notes
Several paths read blocks directly from `sbd.device_fd` and may exit on short reads. Recursive display trusts pointer structures enough to follow them for reporting, so corrupt filesystems can produce noisy or aborting diagnostics.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/extended.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/extended.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/edit/extended.h

## Purpose
Header for extended display functions used by `gfs2_edit`.

## Main Elements
- Declares `do_indirect_extended()`.
- Declares `display_extended()`.

## Dependencies And Integration
Depends on `struct iinfo` from `hexedit.h` being visible before use.

## Risk Notes
No standalone includes for dependent types; include ordering matters.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/extended.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/gfs2hex.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/edit/gfs2hex.c

## Purpose
Provides shared global editor state and core GFS2 block decoding for `gfs2_edit`.

## Main Elements
- Defines global display/edit/navigation state: current block, mode, cursor rows, superblock state, indirect data, terminal state, and formatting buffers.
- `eol()` and `print_gfs2()` abstract curses vs stdout output.
- Directory parsing:
  - `idirent_in()` converts on-disk dirents to host fields.
  - `indirect_dirent()` validates and records directory entries.
- `do_dinode_extended()` extracts dinode indirect pointers, stuffed directory entries, or exhash leaf pointers.
- `do_leaf_extended()` parses a leaf block and returns its continuation block.
- `do_eattr_extended()` prints extended attribute entries.
- `display_gfs2()` dispatches typed structure printing by GFS2 metatype.

## Dependencies And Integration
Uses libgfs2 endian/metadata helpers and `struct_print.c` printers. Supplies globals consumed by `hexedit.c`, `extended.c`, `journal.c`, and `savemeta.c`.

## Risk Notes
`print_gfs2()` uses `vsprintf()` into a fixed `PATH_MAX` buffer. Directory parsing uses block-size assumptions and stops on malformed record lengths.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/gfs2hex.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/gfs2hex.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/edit/gfs2hex.h

## Purpose
Public declarations for GFS2-specific display and decode helpers.

## Main Elements
- Declares `display_gfs2()`, `edit_gfs2()`, `do_dinode_extended()`, `do_leaf_extended()`, `print_gfs2()`, and `eol()`.
- Exposes global `block`.

## Dependencies And Integration
Includes `hexedit.h` for shared editor types and globals.

## Risk Notes
Declares `edit_gfs2()` although no implementation appears in this group, suggesting historical or external dead declaration.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/gfs2hex.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/hexedit.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/edit/hexedit.c

## Purpose
Main implementation and entry point for `gfs2_edit`: an interactive curses hex/structure/extended editor plus command-line metadata inspection, mutation, savemeta/restoremeta, journal dump, and resource-group repair tool.

## Main Elements
- UI framework: title rendering, help screen, color setup, `bobgets()` input editor, curses interaction loop, and mode switching among hex, structure, and extended views.
- Block display:
  - `display_block_type()` identifies metadata type and resource group allocation state.
  - `hexdump()` renders block bytes, ASCII, field labels, pointer hints, and trace references.
  - `display()` reads the active block, decodes superblock/dinode/indirect/leaf context, and calls raw/structured/extended display.
- Navigation: block history stack, goto keywords, pointer jumps, paging, home/back/forward behavior.
- Keyword and lookup helpers: master-directory lookup, rindex/RG lookup, journal keyword handling, metadata-type search, block type/RG/bitmap/allocation reporting.
- Mutators:
  - `hex_edit()` writes modified bytes to the device.
  - `process_field()` reads or assigns named metadata fields.
  - `find_change_block_alloc()` changes bitmap allocation state.
  - `set_rgrp_flags()` changes resource group flags.
  - `rg_repair()` reconstructs damaged rgrp/bitmap metadata conservatively.
- CLI parsing: two-pass parameter handling supports `-p`, `-x`, `-d`, `-s`, `identify`, `savemeta`, `savemetaslow`, `savergs`, `restoremeta`, `printsavedmeta`, journal dumps, and RG commands.
- `main()`: allocates global state, opens device read-write, reads superblock/rindex/master directory, processes commands, runs interactive or print mode, and frees state.

## Dependencies And Integration
Central coordinator for `gfs2_edit`. Integrates libgfs2 buffer/inode/rgrp APIs, curses, `gfs2hex.c`, `extended.c`, `journal.c`, `savemeta.c`, and `struct_print.c`.

## Risk Notes
This tool opens devices read-write by default and includes direct metadata mutation paths. Several command-line operations call `exit()` deep in helpers. Editing, bitmap changes, RG repair, and restore paths require extreme care on live or valuable filesystems.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/hexedit.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/hexedit.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/edit/hexedit.h

## Purpose
Shared declarations, constants, global state, and small inline helpers for the `gfs2_edit` modules.

## Main Elements
- Display modes: `HEX_MODE`, `GFS2_MODE`, `EXTENDED_MODE`, `INIT_MODE`.
- Special pseudo-blocks: `RGLIST_DUMMY_BLOCK`, `JOURNALS_DUMMY_BLOCK`.
- Global externs for editor state, block history, terminal/curses state, current superblock, dinode, indirect info, and options.
- Structures:
  - `idirent`: host-format directory entry view.
  - `indirect_info` and `iinfo`: pointer/dirent/leaf display data.
  - `blkstack_info`: navigation history snapshot.
- Color macros for curses output.
- Public functions for block identity, display, save/restore, keyword parsing, master lookup, and metadata type detection.

## Dependencies And Integration
Included by nearly every `gfs2/edit` C file and anchors shared mutable state across modules.

## Risk Notes
Large global-state surface makes module behavior order-dependent. Some declarations depend on libgfs2 and curses types, so this header is not lightweight.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/hexedit.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/journal.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/edit/journal.c

## Purpose
Implements journal location, dumping, and block-tracing support for `gfs2_edit`.

## Main Elements
- `find_journal_block()`: resolves `journalN` through `jindex` and returns journal dinode block and size.
- Journal read helpers:
  - `fsck_readi()` reads inode data and reports the absolute block backing the read.
  - `find_wrap_pt()` locates sequence wrap.
- Descriptor processing:
  - `ld_is_pertinent()` filters descriptors for traced blocks.
  - `print_ld_blks()` prints descriptor target blocks and bitmap state.
  - `process_ld()` decodes descriptor type, length, data count, and target list.
- Trace helpers: `meta_has_ref()` checks whether metadata references a traced block; `get_ldref()` maps descriptor offsets back to referenced blocks.
- `display_log_header()` prints sequence, tail, flags, statfs counters, and timestamp.
- `dump_journal()` iterates the journal, optionally tracing one block through descriptors, metadata, revoke/bitmap context, and detailed block display.

## Dependencies And Integration
Uses current editor globals, libgfs2 journal/inode helpers, metadata display from `hexedit.c`, and GFS2 block printers. Invoked from CLI handling for `journalN`.

## Risk Notes
Primarily read-only, but it follows journal and metadata pointers and exits on some read/type errors. Trace mode mutates global `dmode` and `block` while restoring only the current block around nested display calls.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/journal.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/journal.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/edit/journal.h

## Purpose
Header for `gfs2_edit` journal inspection helpers.

## Main Elements
- Declares `dump_journal()`.
- Declares `find_journal_block()`.

## Dependencies And Integration
Included by `hexedit.c` for command handling and by journal-aware display code.

## Risk Notes
Minimal header; callers must already have global editor/libgfs2 state initialized.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/journal.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/savemeta.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/edit/savemeta.c

## Purpose
Implements `gfs2_edit` metadata capture, compressed metadata-file format, metadata printing, and dangerous metadata restore.

## Main Elements
- File format:
  - `savemeta_header` with magic, format, timestamp, and filesystem byte size.
  - `saved_metablock` records block number and significant length.
- Compression I/O:
  - `metafd` abstracts raw/gzip/bzip2 reads and gzip writes.
  - Restore buffering uses a 2 MiB window with `restore_buf_next()`.
- Save path:
  - Detects system files, per-node entries, journal dinodes, and significant data length.
  - Saves superblock, rgrps/bitmaps, dinodes, indirect blocks, directory leaves, eattrs, system-file data, and metadata-looking journal contents while avoiding ordinary user data where possible.
  - `savemeta()` writes header, walks the rgtree, saves selected ranges, reports progress, and exits.
- Restore/print path:
  - Detects bzip2/gzip/uncompressed-compatible stream handling.
  - Parses new header or falls back to old format scanning.
  - Restores superblock and saved blocks to a destination device/file, or prints saved block types/details.
  - Truncates restored regular files to saved filesystem size when known.

## Dependencies And Integration
Called from `hexedit.c` CLI modes `savemeta`, `savemetaslow`, `savergs`, `restoremeta`, and `printsavedmeta`. Uses libgfs2 rgrp/inode metadata, editor display routines, zlib, and bzip2.

## Risk Notes
Restore writes raw filesystem blocks and exits on many failures. Save mode deliberately omits most user file data, but system files, directories, symlinks, metadata, and journal metadata are preserved. Format parsing supports old layouts by scanning for the superblock, which is useful but fragile with corrupt input.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/savemeta.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/struct_print.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/edit/struct_print.c

## Purpose
Provides structured, endian-aware printing for common on-disk GFS2 metadata structures.

## Main Elements
- `print_it()` formats label/value output for curses or stdout, handles highlighting, edit field capture, and decimal/hex secondary display.
- Print macros convert big-endian 16/32/64-bit fields and 8-bit fields.
- Structure printers: inum, meta header, superblock, rindex, rgrp, quota, dinode, leaf, eattr header, log header, log descriptor, statfs change, and quota change.
- `ea_header_print()` bounds-checks and prints extended attribute names.

## Dependencies And Integration
Used by `gfs2hex.c`, `extended.c`, and restore print mode to render typed structures. Depends on global cursor/display state from `hexedit.h`.

## Risk Notes
Uses fixed buffers and `vsprintf()`. Highlight/edit metadata is tied to global line and mode state, so changes to display layout can affect editing behavior.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/struct_print.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/struct_print.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/edit/struct_print.h

## Purpose
Declares structured print functions for GFS2 on-disk metadata.

## Main Elements
- Prototypes for superblock, dinode, log, quota, statfs, eattr, leaf, rindex, and rgrp printers.
- Comments note that functions expect on-disk data.

## Dependencies And Integration
Included by editor display modules that decode metadata buffers.

## Risk Notes
No type-specific parameters in prototypes, only `void *`, so callers must pass the correct on-disk structure.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/edit/struct_print.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/Makefile.am -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/Makefile.am

## Purpose
Builds the `fsck.gfs2` filesystem checker.

## Main Elements
- Installs `fsck.gfs2` under `sbin_PROGRAMS`.
- Headers include pass helpers, hash/link/lost+found/metawalk/util/recovery declarations.
- Sources include block list, recovery, initialize, inode/link/lost+found, metawalk, passes 1-5, pass1b, rgrepair, and utilities.
- Links against `libgfs2`, gettext, and uuid.
- Includes `checks.am` when Check is available.

## Dependencies And Integration
Builds the full repair executable around libgfs2 and configured gettext/uuid support.

## Risk Notes
Unit test target reuses production fsck sources with compile-time suppressions, but the local test file is only a stub.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/afterpass1_common.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/afterpass1_common.c

## Purpose
Provides common post-pass1 deletion and cleanup callbacks for invalid, duplicate, or removed inode metadata, data, directory entries, and extended attributes.

## Main Elements
- Duplicate handling:
  - `find_remove_dup()` removes this inode’s duplicate reference and reports whether references remain.
  - `delete_block_if_notdup()` frees a block only when it is valid, allocated, and no other duplicate refs remain.
- Directory cleanup:
  - `remove_dentry()` deletes a matching dirent during metawalk.
  - `remove_dentry_from_dir()` loads a parent directory and walks it with deletion callbacks.
- Metadata/data callbacks: `delete_metadata()`, `delete_leaf()`, `delete_data()`.
- Extended attribute cleanup:
  - `del_eattr_generic()` clears EA block references and decrements inode block accounting.
  - `delete_eattr_indir()`, `delete_eattr_leaf()`, `delete_eattr_entry()`, `delete_eattr_extentry()` validate and remove bad EA structures/pointers.

## Dependencies And Integration
Used by later fsck passes through `metawalk_fxns`. Integrates duplicate trees, bitmap repair, inode loading, directory walking, logging, and interactive `query()` repair decisions.

## Risk Notes
These routines perform destructive repair by freeing blocks, modifying inode EA pointers, and deleting dirents. Duplicate-reference handling intentionally avoids freeing blocks still referenced elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/afterpass1_common.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/afterpass1_common.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/afterpass1_common.h

## Purpose
Declares common cleanup callbacks used after fsck pass 1.

## Main Elements
- Prototypes for deleting metadata, leaf, data, EA indirect/leaf/entry/extentry blocks.
- Declares `remove_dentry_from_dir()`.

## Dependencies And Integration
Includes `util.h` and `metawalk.h`, exposing functions shaped for metawalk callbacks.

## Risk Notes
The declared callbacks mutate filesystem state; callers must provide correct fsck context and metawalk private data.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/afterpass1_common.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/block_list.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/block_list.c

## Purpose
Implements a simple list of special block numbers for fsck bookkeeping.

## Main Elements
- `special_free()`: deletes and frees all entries.
- `blockfind()`: linear search for a block number.
- `special_add()`: allocates and appends a block entry.
- `special_set()`: idempotently adds a block if not already present.

## Dependencies And Integration
Uses `osi_list_t` embedded in `struct special_blocks` from `fsck.h`.

## Risk Notes
Allocation failure in `special_add()` is silent; the block is simply not recorded.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/block_list.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/check_fsck.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/check_fsck.c

## Purpose
Minimal Check framework test harness for `fsck.gfs2`.

## Main Elements
- Defines one stub test, `test_fsck_stub`, asserting true.
- Creates suite `main.c` and case `fsck.gfs2`.
- Runs tests with `CK_ENV` and returns nonzero on failures.

## Dependencies And Integration
Compiled by `gfs2/fsck/checks.am` with the full fsck source set under `-DUNITTESTS`.

## Risk Notes
Only verifies test harness linkage; it does not exercise fsck initialization, passes, replay, or repair logic.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/check_fsck.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/checks.am -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/checks.am

## Purpose
Automake test fragment for `fsck.gfs2`.

## Main Elements
- `TESTS = check_fsck`.
- Builds `check_fsck`.
- Reuses `$(fsck_gfs2_SOURCES)` plus `check_fsck.c`.
- Adds `-DUNITTESTS`, Check flags, and warning suppressions for unused const variables/functions.

## Dependencies And Integration
Included only when `HAVE_CHECK` is true.

## Risk Notes
The test target links all fsck sources even though the test itself is a stub, so broad build dependencies affect test build success.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/checks.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/fs_recovery.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/fs_recovery.c

## Purpose
Implements GFS2 journal validation, replay, clearing, and journal-index discovery/rebuild support for `fsck.gfs2`.

## Main Elements
- Revoke tracking: `revoke_add()`, `revoke_check()`, `revoke_clean()` maintain replay-time revoke state.
- Replay scanners:
  - `revoke_lo_scan_elements()` collects revokes in pass 0.
  - `buf_lo_scan_elements()` replays metadata blocks in pass 1.
  - `databuf_lo_scan_elements()` replays journaled data blocks and unescapes magic.
  - `foreach_descriptor()` walks active log descriptors between head tail and head block.
- Journal repair:
  - `check_journal_seq_no()` detects and optionally renumbers out-of-order log header sequences.
  - `recover_journal()` checks head, handles corrupt/dirty/clean states, gates preen safety, prompts, replays, cleans, or clears journals.
- Safety: `preen_is_safe()` prevents automatic preen on cluster locking unless forced or lock_nolock.
- Journal validation: range-check metawalk callbacks ensure journal inode pointers are in range and point to indirect blocks.
- Public orchestration:
  - `replay_journals()` checks each journal inode, replays or reports, counts clean journals, and fsyncs.
  - `ji_update()` reads `journalN` inodes from `jindex`.
  - `build_jindex()` recreates the journal index and journals.
  - `init_jindex()` validates/rebuilds `jindex`, checks entry names, and populates journal info.

## Dependencies And Integration
Used during fsck initialization/recovery before normal passes. Integrates libgfs2 journal helpers, metawalk validation, logging, user queries, resource group refresh, and fsck options.

## Risk Notes
Journal replay writes metadata and journaled data to the filesystem. Preen safety is conservative for clustered filesystems, but forced/manual modes can still clear or replay journals based on user confirmation.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/fs_recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/fs_recovery.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/fs_recovery.h

## Purpose
Declares journal recovery and journal-index helpers for `fsck.gfs2`.

## Main Elements
- `replay_journals()`.
- `preen_is_safe()`.
- `ji_update()`.
- `build_jindex()`.
- `init_jindex()`.

## Dependencies And Integration
Includes `libgfs2.h` for `fsck_cx`, `lgfs2_sbd`, and option-related types.

## Risk Notes
Functions include both read-only validation and mutating recovery/rebuild operations; callers must honor options and safety checks.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/fs_recovery.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/fsck.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/fsck.h

## Purpose
Central shared header for `fsck.gfs2`, defining exit codes, core bookkeeping structures, global pass state, validation helpers, and pass/function declarations.

## Main Elements
- Constants: fsck-compatible exit codes, hash sizes, max format, bad pointer tolerance.
- Core structs:
  - `bmap` for bitmap storage.
  - `inode_info`, `dir_info`, `dir_status` for inode/directory accounting.
  - `duptree`, `inode_with_dups`, and `enum dup_ref_type` for duplicate block tracking.
  - `enum rgindex_trust_level` for resource group index confidence.
  - `fsck_options` and `fsck_cx` for runtime options and context.
  - `special_blocks` list node.
- Function declarations for initialization/destruction, passes 1-5, rindex repair, query, inode helpers, duplicate/directory tree operations, and filesystem skeleton rebuild helpers.
- Global externs for lost+found, pass control, error counters, duplicate counters, and filesystem block bounds.
- Inline validation helpers: `valid_block()`, `rgrp_contains_block()`, and `valid_block_ip()`.

## Dependencies And Integration
Included across fsck modules. Depends on libgfs2 and `osi_tree.h` data structures.

## Risk Notes
Many globals coordinate pass behavior, so ordering and reset semantics matter. `valid_block()` and `valid_block_ip()` are core safety gates before repair operations.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/fsck/fsck.h -->