# Group Research: group_1732_reiserfsprogs_sources_local_fs_reiserfsprogs_reiserfscore_reiserfsl_dde1b33dc5a9

Scope: `Docs/research_subset_a.md`, `sources/local-fs/reiserfsprogs` files listed in the work item. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/reiserfslib.c -->
# File Research: sources/local-fs/reiserfsprogs/reiserfscore/reiserfslib.c

Core library implementation for opening, creating, searching, mutating, and iterating ReiserFS filesystems from userspace tools. It owns global canonical keys for root, parent root, lost+found, and bad-block pseudo-files, and initializes root key constants through `make_const_keys()`.

Major responsibilities:
- Filesystem lifecycle: `reiserfs_open()`, `reiserfs_create()`, `reiserfs_reopen()`, `reiserfs_flush()`, `reiserfs_free()`, and `reiserfs_close()`.
- Superblock validation/creation: probes ReiserFS superblock at the old/new 4 KiB locations, validates block size, derives format/hash function, creates format 3.5/3.6 superblocks, and initializes mount/check metadata.
- Tree searching: `reiserfs_search_by_key_3()`, `reiserfs_search_by_key_4()`, `reiserfs_search_by_position()`, `reiserfs_search_by_entry_key()`, `uget_lkey()`, `uget_rkey()`, and `reiserfs_next_key()`.
- Tree mutation wrappers: `init_tb_struct()`, `reiserfs_remove_entry()`, `reiserfs_paste_into_item()`, and `reiserfs_insert_item()` delegate balancing to `fix_nodes()`/`do_balance()`.
- Directory operations: hash generation, entry lookup, insertion, root directory/stat-data creation, and maintenance of `"."`/`".."`.
- Bad-block support: builds bad-block bitmaps from files, iterates bad-block indirect items, removes/replaces bad-block items, and writes bad-block block pointers back into the tree.
- File and directory iterators: `reiserfs_iterate_file_data()` walks direct/indirect items for one file; `reiserfs_iterate_dir()` walks directory entries excluding dot entries.

Important implementation details:
- `is_block_count_correct()` ensures reserved area, superblock, root, and journal fit within first bitmap coverage and filesystem size.
- `reiserfs_search_by_key_x()` descends from the root block using `reiserfs_bin_search()`, with 3-field or 4-field key comparison.
- Directory lookup handles hash collisions by scanning generation counters embedded in directory offsets.
- `make_entry()` constructs one `reiserfs_de_head` plus rounded name payload and marks entries visible.
- `create_dir_sd()` creates old/new stat-data according to filesystem format and uses caller uid/gid for non-root invocations.
- `can_we_format_it()` checks mounted state, block-device type, and whole-disk device patterns before journal/filesystem formatting operations.

Dependencies and interactions:
- Relies heavily on `includes.h`/`reiserfs_lib.h` macros for endian-safe superblock, item-head, directory-entry, key, bitmap, and journal access.
- Depends on buffer cache helpers (`bread`, `getblk`, `bwrite`, `brelse`, dirty/uptodate flags), tree balancing (`fix_nodes`, `do_balance`), journal helpers, bitmap helpers, and misc device checks.
- Used by resize, tune, fsck, mkfs, and debug tools as shared core filesystem manipulation code.

Risks and notes:
- Many failures abort through `die()`/`reiserfs_panic()`, which is normal for these low-level tools but makes partial recovery caller-hostile.
- `reiserfs_close()` calls `reiserfs_free(fs)` before `fsync(fs->fs_dev)`, which reads through `fs` after it has been freed.
- Several functions assume path state remains valid across low-level tree operations and panic on structural inconsistency.
- Directory and file iteration are format-aware but mostly trust item bodies after key/type checks; corrupt images can drive warning/error paths.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/reiserfslib.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/stree.c -->
# File Research: sources/local-fs/reiserfsprogs/reiserfscore/stree.c

Internal tree search helper implementation for ReiserFS userspace code. This file provides key comparison, binary search, path release, delimiting-key lookup, and root-to-leaf traversal.

Major responsibilities:
- Determines whether a buffer is in the tree with `B_IS_IN_TREE()`.
- Compares ReiserFS keys via `comp_short_keys()`, `comp_keys_3()`, and `comp_keys()`.
- Implements generic node-array binary search in `bin_search()`.
- Defines sentinel `MIN_KEY` and `MAX_KEY`.
- Computes left/right delimiting keys with `get_lkey()` and `get_rkey()`.
- Verifies whether a searched key belongs under a path buffer using `key_in_buffer()`.
- Releases all buffers in a search path with `pathrelse()`.
- Descends the formatted tree from root in `search_by_key()` until the requested stop level.

Important implementation details:
- Key comparison reads little-endian fields through `d32_get()` and compares short key, offset, then type.
- `bin_search()` returns both found/not-found status and the insertion/search position.
- Delimiting-key lookup walks parent path elements upward and validates parent child pointers against the child buffer block number.
- `search_by_key()` releases any existing path first, reads blocks with `bread()`, validates tree membership and expected level, then chooses the next child pointer based on binary-search result.

Dependencies and interactions:
- Uses core ReiserFS structures/macros from `includes.h`: block headers, internal keys, child pointers, item heads, path elements, root block, and tree height.
- Complements higher-level search wrappers in `reiserfslib.c`; both provide similar tree traversal services for different call sites.

Risks and notes:
- Structural anomalies panic rather than returning recoverable errors in several places.
- `key_in_buffer()` depends on path consistency; stale or corrupt parent paths become fatal.
- The file comment lists additional mutation helpers that are not present in this excerpt, so this file appears to be a trimmed or refactored subset of older `stree.c` functionality.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/stree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/xattr.c -->
# File Research: sources/local-fs/reiserfsprogs/reiserfscore/xattr.c

Extended attribute and ACL helper code for ReiserFS userspace. It implements checksum calculation compatible with kernel-style partial checksums, validates xattr headers, and counts ACL entries.

Major responsibilities:
- `from32to16()` folds a 32-bit checksum into 16 bits.
- `do_csum()` computes an alignment-aware checksum over an arbitrary buffer.
- `csum_partial()` adds a prior partial checksum to a newly computed buffer checksum.
- `reiserfs_xattr_hash()` returns the xattr data hash.
- `reiserfs_check_xattr()` verifies xattr body length, magic, and hash compatibility.
- `reiserfs_acl_count()` derives the number of ACL entries from serialized ACL size.

Important implementation details:
- `do_csum()` handles odd byte alignment and endian-dependent byte placement.
- `reiserfs_check_xattr()` accepts either exact stored hash or folded stored hash, preserving compatibility with older encodings.
- ACL counting supports the first four short entries and then full ACL entries, returning `-1` for malformed sizes.

Dependencies and interactions:
- Includes system ACL definitions and `reiserfs_lib.h` for xattr/ACL structures and endian helpers.
- Intended for tools that inspect or validate ReiserFS xattr bodies and POSIX ACL item payloads.

Risks and notes:
- The checksum implementation uses unaligned casts to `unsigned short *` and `unsigned int *`; this matches legacy low-level style but can be architecture-sensitive.
- `reiserfs_check_xattr()` treats any nonzero magic/hash result as validity, returning boolean-style success rather than a negative errno except for too-short input.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/reiserfscore/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/resize_reiserfs/Makefile.am -->
# File Research: sources/local-fs/reiserfsprogs/resize_reiserfs/Makefile.am

Automake build definition for the `resize_reiserfs` utility.

Major responsibilities:
- Builds `resize_reiserfs` as an installed sbin program.
- Compiles `fe.c`, `resize_reiserfs.c`, `do_shrink.c`, and `resize.h`.
- Installs `resize_reiserfs.8` as the manual page.
- Links against `$(top_builddir)/reiserfscore/libreiserfscore.la`.

Dependencies and interactions:
- The resize utility is a thin program over the shared ReiserFS core library.
- Manual page is included in `EXTRA_DIST` for distribution packaging.

Risks and notes:
- No per-target compiler flags are set here; it inherits project-wide configuration.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/resize_reiserfs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/resize_reiserfs/do_shrink.c -->
# File Research: sources/local-fs/reiserfsprogs/resize_reiserfs/do_shrink.c

Offline shrink implementation for `resize_reiserfs`. It moves all formatted and unformatted blocks above the new size boundary into free blocks below the boundary, updates references, shrinks bitmaps, and rewrites superblock accounting.

Major responsibilities:
- Tracks processed/moved internal, leaf, unformatted, and total block counts.
- `quit_resizer()` closes the filesystem and exits with the filesystem left in error state.
- `move_generic_block()` copies a block above the shrink boundary into a free block below it and updates the in-memory bitmap.
- `move_unformatted_block()` wraps generic movement for file data blocks.
- `move_formatted_block()` recursively walks internal/leaf tree blocks and rewrites child pointers and indirect item block pointers.
- `shrink_fs()` coordinates shrink feasibility checks, user confirmation, bitmap opening, FS error-state marking, root movement, bad-block list trimming, bitmap shrinking, and superblock updates.

Important implementation details:
- Shrink refuses when allocated blocks cannot fit after accounting for changed bitmap block count.
- The shrinker prints a beta warning and requires interactive confirmation.
- Before moving, it marks the filesystem state as `FS_ERROR` and writes the superblock so interruption forces fsck.
- Bad-block pseudo-file items are skipped during leaf indirect-pointer relocation, then collected and rewritten after bitmap shrink.
- Superblock free block count is adjusted by removed blocks, bitmap-block delta, and removed bad-block count.

Dependencies and interactions:
- Uses the shared buffer cache, bitmap, bad-block, tree item, and superblock helpers from `reiserfscore`.
- Called by `resize_reiserfs.c` when the target block count is smaller than the current filesystem.
- Relies on `opt_verbose` and other resize globals declared in `resize.h`.

Risks and notes:
- The shrink path is explicitly marked beta and dangerous.
- It recursively descends the full tree, so corrupt child pointers or malformed nodes can abort or miscount.
- `move_generic_block()` treats block number greater than block count as invalid, but equality handling should be checked against valid block range conventions.
- If no free block below the boundary is found, the tool exits and leaves the filesystem needing `reiserfsck`.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/resize_reiserfs/do_shrink.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/resize_reiserfs/fe.c -->
# File Research: sources/local-fs/reiserfsprogs/resize_reiserfs/fe.c

Kernel online-resize frontend for `resize_reiserfs`.

Major responsibilities:
- `resize_fs_online()` finds the mount entry for a device.
- Constructs a `resize=<blocks>` remount option.
- Calls `mount(..., MS_REMOUNT, buf)` to ask the kernel ReiserFS driver to resize the mounted filesystem.

Dependencies and interactions:
- Uses `misc_mntent()` to map device to mount table entry.
- Uses Linux mount flags and libc `mount()`.
- Called by `resize_reiserfs.c` when the target filesystem is mounted and the change is an online resize.

Risks and notes:
- `buf` is 40 bytes and populated with `sprintf`; this is likely enough for signed 64-bit decimal plus prefix, but not bounds-checked.
- Failure paths abort through `die()`.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/resize_reiserfs/fe.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/resize_reiserfs/resize.h -->
# File Research: sources/local-fs/reiserfsprogs/resize_reiserfs/resize.h

Shared header for the resize utility.

Major responsibilities:
- Includes project configuration, I/O, misc, ReiserFS core library, and version banner definitions.
- Selects mount headers depending on glibc.
- Defines `print_usage_and_exit()` and `DIE()` utility macros.
- Declares resize globals: `g_sb_bh`, `g_progname`, option flags, and resize entry points.

Dependencies and interactions:
- Included by `resize_reiserfs.c`, `do_shrink.c`, and `fe.c`.
- Exposes `resize_fs_online()` and `shrink_fs()` across compilation units.
- Pulls `../version.h` for `print_banner()`.

Risks and notes:
- `print_usage_and_exit()` uses `argv[0]` from the including function scope, which works in `main()` but is macro-coupled.
- Uses GNU variadic macro syntax in `DIE()`.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/resize_reiserfs/resize.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/resize_reiserfs/resize_reiserfs.8.in -->
# File Research: sources/local-fs/reiserfsprogs/resize_reiserfs/resize_reiserfs.8.in

Manual page template for `resize_reiserfs`.

Major contents:
- Documents syntax: `resize_reiserfs [-s [+|-]size[K|M|G]] [-j dev] [-fqv] device`.
- Explains offline resize behavior and online growth support.
- Warns that the tool does not resize the underlying partition/device.
- Provides shrink workflow: unmount, shrink filesystem, then shrink device.
- Describes options for size, journal device, force, quiet, and verbosity.
- Lists return values and an example shrink session.
- References `cfdisk(8)`, `reiserfsck(8)`, and `debugreiserfs(8)`.

Dependencies and interactions:
- Version placeholder `@PACKAGE_VERSION@` is filled by the build system.
- Installed by `resize_reiserfs/Makefile.am`.

Risks and notes:
- The return value section says `-1` for failure, while C `main()` typically returns positive `1` for many failures.
- Option text says `-f` skips checks, while code mostly uses force for confirmations and some checks remain enforced.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/resize_reiserfs/resize_reiserfs.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/resize_reiserfs/resize_reiserfs.c -->
# File Research: sources/local-fs/reiserfsprogs/resize_reiserfs/resize_reiserfs.c

Main program for the ReiserFS resize utility. It parses options, opens the filesystem and journal, chooses online/offline resize mode, validates target size, and dispatches to expansion or shrink logic.

Major responsibilities:
- Parses target size strings in `calc_new_fs_size()`, supporting absolute or relative byte values with K/M/G suffixes.
- Reports old/new superblock state through `sb_report()`.
- Conditionally writes dirty buffers through `bwrite_cond()`.
- Expands filesystems in `expand_fs()` by expanding the bitmap, updating free/block counts, marking new bitmap blocks used, and dirtying the bitmap.
- Validates target size in `resizer_check_fs_size()`.
- Coordinates all resize flow in `main()`.

Important implementation details:
- Opens filesystem read-only first, then opens journal, validates journal parameters unless `-k` skip-journal is set.
- Rejects old non-spread bitmap format.
- If mounted, closes the filesystem and calls the online remount frontend.
- Offline resize requires clean/consistent filesystem state.
- Expansion marks the filesystem `FS_ERROR`, updates bitmap/superblock, then final code restores `FS_CONSISTENT`.
- Shrink delegates to `shrink_fs()`.

Dependencies and interactions:
- Uses `resize.h`, shared ReiserFS core open/journal/bitmap/superblock helpers, and `do_shrink.c`/`fe.c`.
- Depends on device-size helpers like `count_blocks()` and `valid_offset()`.

Risks and notes:
- In the getopt switch, case `'j'` sets `jdevice_name = optarg` and falls through into case `'f'`, so specifying `-j` also sets `opt_force = 1`.
- The parser option string includes `n`, but usage/manpage do not document active no-write support; the code leaves it disabled.
- Online path is selected for any mounted filesystem after target validation; shrink validation rejects mounted shrink first.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/resize_reiserfs/resize_reiserfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/tune/Makefile.am -->
# File Research: sources/local-fs/reiserfsprogs/tune/Makefile.am

Automake build definition for `reiserfstune`.

Major responsibilities:
- Builds `reiserfstune` as an installed sbin program from `tune.c` and `tune.h`.
- Installs `reiserfstune.8`.
- Links against `$(top_builddir)/reiserfscore/libreiserfscore.la`.
- Adds install hook symlinks for `tunefs.reiserfs` binary and manpage aliases.

Dependencies and interactions:
- Exposes the same executable under historical/alternate `tunefs.reiserfs` naming.
- Depends on core ReiserFS library for all filesystem manipulation.

Risks and notes:
- Symlink creation uses `$(LN_S)` without explicit replacement logic; packaging/install behavior depends on automake environment and existing files.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/tune/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/tune/reiserfstune.8.in -->
# File Research: sources/local-fs/reiserfsprogs/tune/reiserfstune.8.in

Manual page template for `reiserfstune`.

Major contents:
- Documents journal tuning, journal relocation, bad-block list storage, UUID, label, check interval, last-checked time, max mount count, and mount count.
- Explains current journal device, unavailable journal mode, new journal device, journal size, offset, and transaction size.
- Warns that relocated journal support historically required patched kernels.
- Documents `--make-journal-standard` for converting a non-standard journal back to standard on-main-device layout.
- Provides bad-block replacement/append options.
- Warns about disabling periodic checks.
- Includes example scenarios for moving journals and recovering when an external journal device is lost.

Dependencies and interactions:
- Version placeholder `@PACKAGE_VERSION@` is substituted by the build.
- Installed by `tune/Makefile.am`, with symlinked `tunefs.reiserfs.8`.

Risks and notes:
- Contains several spelling/wording issues, including “tunning”, “filesytem”, and a typo in the bug-report email domain.
- Some option names differ slightly from code naming, e.g. max transaction wording, but intent is clear.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/tune/reiserfstune.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/tune/tune.c -->
# File Research: sources/local-fs/reiserfsprogs/tune/tune.c

Main implementation of `reiserfstune`, the ReiserFS tuning utility. It modifies journal parameters/location, converts non-standard journals, updates v3.6 UUID/label/check metadata, and stores bad-block lists.

Major responsibilities:
- Prints messages and usage.
- Parses long/short options for journals, UUID/label, bad blocks, force, check intervals, mount counts, and version/help.
- Determines when non-standard journal settings can be converted to standard layout.
- Writes standard journal parameters and journal header through `set_standard_journal_params()`.
- Zeroes journal blocks in `zero_journal()`.
- Parses integer/time/check options.
- Adds or replaces bad-block lists through `add_badblocks()`.
- Validates mounted/dirty/journal state before writes.
- Edits v3.6 superblock UUID, label, max mount count, mount count, check interval, and last check time.
- Creates or relocates journals through `reiserfs_create_journal()`.

Important implementation details:
- `should_make_journal_standard()` checks superblock magic, requested device, journal size, max transaction size, and reserved main-device area.
- `add_badblocks()` opens the on-disk bitmap, loads user bad-block bitmap, removes already-listed blocks for append mode, marks unused bad blocks in the filesystem bitmap, and rewrites bad-block tree items.
- The tool refuses to run on mounted filesystems.
- It checks clean unmount/consistency before tuning, and also checks for non-replayed transactions in an opened old journal.
- UUID/label/check metadata is only allowed for format 3.6; format 3.5 rejects those operations.
- If no new journal device is specified and no journal-size/transaction change is requested, it prints current parameters and exits.

Dependencies and interactions:
- Uses `tune.h`, `parse_time.h`, core ReiserFS open/journal/bitmap/bad-block APIs, UUID library when configured, and shared output/confirmation helpers.
- Calls `can_we_format_it()` before using a new journal device.

Risks and notes:
- Static option state uses zero as “not specified”, so explicitly setting mount/check values to zero is not supported despite some signed checks being present.
- In the v3.6 `Mnt_count` branch, the validation mistakenly checks `Max_mnt_count <= 0` before setting mount count.
- Bad-block free-block accounting subtracts `fs_badblocks_bm->bm_set_bits` rather than the local `marked` count after filtering, which deserves scrutiny.
- Many operations are intentionally destructive and guarded by mounted/clean checks plus confirmation for journal zeroing.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/tune/tune.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/tune/tune.h -->
# File Research: sources/local-fs/reiserfsprogs/tune/tune.h

Shared header for `reiserfstune`.

Major responsibilities:
- Includes configuration, I/O, misc helpers, ReiserFS core library, and version banner definitions.
- Conditionally includes `uuid/uuid.h`.
- Defines option bit masks used by `tune.c`: old/new journal, journal size, max transaction size, offset, skip journal, keep old parameters, force, standard journal conversion, and super force.

Dependencies and interactions:
- Included by `tune.c`.
- Provides compile-time linkage to optional libuuid support through configure macros.

Risks and notes:
- Several option constants are defined but unused or tied to disabled code paths, reflecting legacy CLI evolution.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/tune/tune.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/reiserfsprogs/version.h -->
# File Research: sources/local-fs/reiserfsprogs/version.h

Tiny shared version/banner header for ReiserFS tools.

Major responsibilities:
- Defines `print_banner(prog)` as a macro that writes `<program> <VERSION>` to stderr.

Dependencies and interactions:
- Included by resize and tune headers.
- Requires `VERSION` to be defined by build configuration or included headers.

Risks and notes:
- Macro expands directly to `fprintf(stderr, ...)`; callers must include stdio-compatible declarations through surrounding headers.
<!-- END FILE RESEARCH: sources/local-fs/reiserfsprogs/version.h -->