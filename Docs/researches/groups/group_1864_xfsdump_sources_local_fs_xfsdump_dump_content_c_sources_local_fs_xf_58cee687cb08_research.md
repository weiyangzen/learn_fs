# Group Research: xfsdump dump/content, inode map, var, include, inventory helpers

Scope checked against `Docs/research_subset_a.md`: `sources/local-fs/xfsdump` is included. Internal group report path was not present in this checkout, so this report is based on the prompt file list and complete reads of all listed files.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/dump/content.c -->
# File Research: sources/local-fs/xfsdump/dump/content.c

`content.c` is the main xfsdump content engine. It owns dump initialization, incremental/resume decision logic, inode map integration, per-stream dump execution, media-file lifecycle, inventory updates, directory/non-directory serialization, extended attribute serialization, HSM hooks, and quota snapshot handling.

Key responsibilities:
- Parses dump-specific options from `GETOPT_CMDSTRING`, including level, subtree, resume, base session UUID, inventory update suppression, media erase, media alert program, extended attributes, HSM offline mode, skip-unchanged-dirs, exclude files, and max dump file size.
- Resolves the source filesystem via `fs_info`, confirms it is mounted, verifies the mountpoint is the filesystem root via `check_rootdir`, opens the root, obtains root `xfs_bstat`, and builds a JDM filesystem handle.
- Consults the inventory to determine incremental base sessions and interrupted same-level sessions for resume ranges.
- Calls `inomap_build` to classify inodes and calculate stream startpoints, then calls `var_skip` to remove xfsdump’s own state directory from the dump if it lives on the target filesystem.
- Initializes content header fields such as dump level, flags, root inode, inomap metadata, incremental/resume UUIDs, and checksum/format capabilities.
- Allocates per-stream `context_t` buffers for file headers, extent headers, directory entries, extended attributes, symlink reads, HSM file context, and inomap iteration context.

Main data structures:
- `mark_t`: wraps a drive-layer mark with an xfsdump `startpt_t`; committed marks update restart positions in the stream content header.
- `context_t`: per-stream state and scratch buffers, including media file size, committed mark count, current progress inode, completion flag, first media label, and media begin/end protocol state.
- `extent_group_context_t`: holds `XFS_IOC_GETBMAPX` state for regular-file extent dumping.
- `pds_t`: per-drive progress/status phase for status-line reporting.

Dump flow:
- `content_stream_dump` drives one stream. It writes an inomap to every media file, optionally writes the directory dump on stream 0, then iterates non-directories from the current startpoint.
- For each media file it calls `Media_mfile_begin`, writes content, places marks, writes a null file header, ends the media file with `Media_mfile_end`, and updates inventory media-file records.
- When drives support multiple media files, streams synchronize before dumping session inventory and writing a stream terminator.

File serialization:
- Directories are dumped by `dump_dirs` and `dump_dir`, using bulkstat and `getdents_wrap`. Directory entries are serialized by `dump_dirent`, with compatibility support for old v1 dirent headers.
- Regular files are dumped by `dump_file_reg`. It splits large files into extent groups, sets media marks at restart boundaries, writes file and extent headers, handles holes explicitly, aligns large/realtime extents, reads file data, and zero-pads short reads to match already-written extent headers.
- Special files and symlinks are dumped by `dump_file_spec`; symlinks store their target as a data extent.
- Extended attributes are dumped via `jdm_attr_list` and `jdm_attr_multi` across non-root, root, and secure namespaces. Records are built in `dump_extattr_buildrecord` and terminated by a null extattr header.
- Header writers calculate checksums before byte-order translation via `xlate_*` helpers.

Media handling:
- `Media_mfile_begin` is a state-machine/coroutine style routine with `goto` phases for positioning, erase, media change, and write.
- It handles blank media, foreign/corrupt data, overwrite prompts, stream terminators, append restrictions, removable media change prompts, media labels, and alert-program execution.
- `Media_mfile_end` flushes writes and updates the next expected begin state (`BES_ENDOK`, `BES_ENDEOM`, or invalid).

Inventory and completion:
- `create_inv_session` opens inventory database/session/stream records.
- `inv_cleanup`, registered with `atexit`, closes stream/session/database tokens and marks interrupted streams.
- `content_complete` reports final dump size and removes temporary quota files only on complete dumps.

Security and maintenance notes:
- `save_quotas` builds and executes an `xfs_quota` command with `sprintf` and `system`; mountpoints and generated paths flow into a shell command, making this a command-injection-sensitive path if untrusted names can reach it.
- `media_change_alert_program` is also executed with `system`, intentionally user-controlled by option.
- Many allocations are checked with `assert`, so release builds may not handle allocation failure gracefully.
- Heavy global state (`sc_*`) means the module assumes the established xfsdump process/thread model rather than being reentrant.
- Media synchronization uses sleep polling on global counters and flags.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/dump/content.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/dump/getopt.h -->
# File Research: sources/local-fs/xfsdump/dump/getopt.h

This header centralizes the xfsdump command-line option string and symbolic option-letter constants for modules that call `getopt`.

Key content:
- `GETOPT_CMDSTRING` contains the full recognized option grammar, including options with required arguments.
- Defines option constants for content, drive, media, global logging, inventory, stack sizing, checksums, compatibility, and operator interaction.
- Content-relevant options include `GETOPT_LEVEL`, `GETOPT_SUBTREE`, `GETOPT_RESUME`, `GETOPT_BASED`, `GETOPT_NOINVUPDATE`, `GETOPT_ERASE`, `GETOPT_ALERTPROG`, `GETOPT_NOEXTATTR`, `GETOPT_DUMPASOFFLINE`, `GETOPT_NOUNCHANGEDDIRS`, `GETOPT_EXCLUDEFILES`, and `GETOPT_MAXDUMPFILESIZE`.

Important dependency:
- Multiple modules rely on this one option string so each parser can skip options it does not own while still preserving global getopt behavior.

Maintenance note:
- This file is a coordination point: changing one option letter can affect several modules even when only one module handles the option.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/dump/getopt.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/dump/inomap.c -->
# File Research: sources/local-fs/xfsdump/dump/inomap.c

`inomap.c` builds and serializes the inode-selection map used by xfsdump. It decides which inodes participate in a dump, prunes unnecessary directory hierarchy, estimates data volume, and chooses stream startpoints for parallel dumps.

Main phases in `inomap_build`:
- Syncs the filesystem so bulkstat sees current inode state.
- Counts inode groups with `inogrp_iter`, initializes the in-memory map, and pre-populates a segment for each inode group so later subtree traversal can set states in any order.
- Phase 1 constructs the initial dump list. For full dumps it iterates all inodes with `bigstat_iter`; for subtree dumps it recursively descends requested paths with `diriter`.
- Phase 2 prunes unchanged support directories if they do not contain changed descendants, unless `skip_unchanged_dirs` already avoided support-directory inclusion.
- Phase 3 calculates non-directory stream startpoints from estimated dump sizes.

Map model:
- Uses `hnk_t` hunks containing `seg_t` segments. Each segment covers `INOPERSEG` inodes, with three bitmap planes (`lobits`, `mebits`, `hibits`) encoding one of eight `MAP_*` states.
- Keeps a parallel inode-to-generation map (`i2gseg_t`) for directory entry generation numbers.
- `seg_addr_t` contexts cache hunk/segment/inode offsets for faster repeated lookup and iteration.

Inode states:
- `MAP_INO_UNUSED`: no known inode.
- `MAP_DIR_NOCHNG` / `MAP_NDR_NOCHNG`: in use but not dumped.
- `MAP_DIR_CHANGE` / `MAP_NDR_CHANGE`: selected for dump.
- `MAP_DIR_SUPPRT`: unchanged directory still needed to reconstruct hierarchy.
- Reserved states 6 and 7 are unused.

Selection logic:
- `cb_add` compares inode mtime/ctime against incremental and resume base times.
- Resume ranges are treated specially so previously undumped portions can still be included.
- Regular non-directories may be excluded by max dump file size unless they are quota files.
- Files with `XFS_XFLAG_NODUMP` are excluded only when `allowexcludefiles_pr` is true.
- HSM hooks can estimate dump size or offsets for offline/dual-residency files.

Startpoint logic:
- `cb_spinit` divides total estimated non-directory bytes plus header overhead by stream count.
- `cb_startpt` uses heuristics (`TOO_SHY`, `TOO_BOLD`) to either keep a file in the current stream, begin the next stream at a file boundary, or split a very large file at a block-aligned offset.
- `quantity2offset` converts “real data bytes behind this point” into a file offset by reading extent maps.

Serialization:
- `inomap_writehdr` fills content inode header fields with hunk count, segment count, directory count, non-directory count, first/last inode, and estimated data size.
- `inomap_dump` writes each hunk through the drive layer after byte-order translation with `xlate_hnk`.

Potential issues:
- `inomap_build` passes a freshly allocated context from `inomap_alloc_context()` into phase 3 without freeing it afterward.
- The `else if (resumed)` branch in `cb_add` contains `assert(changed)` in a path reached only when the preceding `if (changed)` failed, which looks logically inconsistent or obsolete.
- Size estimates are intentionally rough for normal files and affect stream balancing and max-size pruning.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/dump/inomap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/dump/inomap.h -->
# File Research: sources/local-fs/xfsdump/dump/inomap.h

This header declares the inode map interface shared between dump content code and the inomap implementation.

Key API:
- `inomap_build`: constructs the in-memory inode map, prunes non-selected inodes/directories, and returns stream startpoints.
- `inomap_getsz`: returns serialized hunk size.
- `inomap_skip`: marks selected inodes as not dumped, used by `var_skip`.
- `inomap_writehdr`: copies inomap metadata into the content inode header.
- `inomap_dump`: writes the map to media.
- `inomap_alloc_context`, `inomap_reset_context`, `inomap_free_context`: manage iterator/search contexts.
- `inomap_get_state`, `inomap_get_gen`: query selected inode state and generation.
- `inomap_next_nondir`, `inomap_next_dir`: generator-style iteration over selected non-directories/directories.

Data format:
- Defines `MAP_*` state values.
- Defines `seg_t`, which stores a base inode and three 64-bit state bitmaps.
- Defines `hnk_t`, a fixed-size hunk of map segments plus `maxino`; `nextp` remains only for binary compatibility.

Important invariant:
- The comments describe “two bits” in one place, but the actual implementation and later comment use three bit planes for eight states.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/dump/inomap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/dump/var.c -->
# File Research: sources/local-fs/xfsdump/dump/var.c

`var.c` manages xfsdump’s persistent state directory and prevents that directory from being included in dumps of the same filesystem.

Main functions:
- `var_create`: creates each component of `XFSDUMP_DIRPATH`, logging the path and stopping on first component-creation failure.
- `var_create_component`: calls `mkdir(path, 0755)` and, for newly created directories, attempts `chown(path, 0, 0)`.
- `var_skip`: obtains the filesystem UUID containing `XFSDUMP_DIRPATH` with `fs_getid`, compares it with the dump target UUID, and if they match recursively reports all inodes under the xfsdump state directory to a callback.
- `var_skip_recurse`: walks the directory tree with `lstat64`, `opendir`, `readdir`, and `open_pathalloc`, invoking the callback with each inode.

Integration:
- `content_init` calls `var_create()` before inventory work.
- After `inomap_build`, `content_init` calls `var_skip(&fsid, inomap_skip)` so xfsdump’s own inventory/state files are removed from the dump map.

Maintenance notes:
- Recursive traversal follows directory structure using `lstat64`; symlinks are reported but not descended.
- Errors opening/statting paths are logged and skipped rather than aborting the dump.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/dump/var.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/dump/var.h -->
# File Research: sources/local-fs/xfsdump/dump/var.h

This small header declares the `/var/[lib/]xfsdump` helper abstraction.

Exports:
- `var_create(void)`: ensure xfsdump’s state directory path exists.
- `var_skip(uuid_t *dumped_fsidp, void (*cb)(xfs_ino_t ino))`: if the state directory is on the filesystem being dumped, call back for every inode below it so those inodes can be excluded.

Dependency:
- Requires `uuid_t` and `xfs_ino_t` from included project/system headers before use.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/dump/var.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/include/Makefile -->
# File Research: sources/local-fs/xfsdump/include/Makefile

This makefile defines the `include` subdirectory build metadata.

Key content:
- Sets `TOPDIR = ..` and includes `$(TOPDIR)/include/builddefs`.
- Declares public/local headers `HFILES = swab.h swap.h`.
- Declares local source/config/build helper files in `LSRCFILES`, including `builddefs.in`, `buildmacros`, `buildrules`, `config.h.in`, and `install-sh`.
- Defines empty `default install install-dev` targets, then includes `$(BUILDRULES)`.

Role:
- This directory primarily contributes headers and build infrastructure rather than compiled objects.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/include/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/include/builddefs.in -->
# File Research: sources/local-fs/xfsdump/include/builddefs.in

`builddefs.in` is an autoconf-substituted make include that centralizes package metadata, tool paths, library paths, platform flags, gettext settings, and shared build rules.

Key variables:
- Build mode: `DEBUG`, `OPTIMIZER`, `CFLAGS`, `LOADERFLAGS`, `MALLOCLIB`.
- Libraries: `LIBRMT`, `LIBXFS`, `LIBATTR`, `LIBPTHREAD`, `LIBUUID`, `LIBCURSES`, `LIBHANDLE`.
- Package metadata: name, user/group, release, version, platform, distribution.
- Install paths: sbin, root sbin, root lib, include, man, docs, locale.
- Tools: compiler, awk, sed, tar, zip, make, sort, shell, libtool, makedepend, gettext utilities, rpm tooling.
- Feature toggles: curses, shared libs, gettext, zipped manpages, fallocate.

Platform behavior:
- Linux sets `_GNU_SOURCE`, `_FILE_OFFSET_BITS=64`, and `__linux__` dependency flags.
- Darwin, IRIX, and FreeBSD get platform-specific preprocessor/linker settings.

Important build rule:
- `CFLAGS` is assembled from external flags, generated global flags, platform flags, and local flags.
- Includes `buildmacros` and defines `_FORCE` for always-rebuilt targets.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/include/builddefs.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/include/config.h.in -->
# File Research: sources/local-fs/xfsdump/include/config.h.in

`config.h.in` is the generated configuration header template.

Key content:
- Defines `BITS_PER_LONG` from autoconf-provided `SIZEOF_LONG`.
- Provides `umode_t` if the platform lacks it.
- Wraps gettext support: if `ENABLE_GETTEXT` is defined, `_()` maps to `gettext`; otherwise localization macros become pass-through no-ops.
- Includes `<locale.h>`.
- Defines IRIX device major/minor conversion helpers and `IRIX_MKDEV`.
- Provides fallback `min`, `max`, and `NBBY`.

Role:
- Supplies cross-platform compatibility macros used by xfsdump source and on-media translation code.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/include/config.h.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/include/install-sh -->
# File Research: sources/local-fs/xfsdump/include/install-sh

`install-sh` is a bash install helper emulating BSD install with xfsdump packaging extensions.

Supported modes:
- Create a directory with `-d`.
- Install one file to a target file or directory.
- Install multiple files to a directory.
- Create a symlink with `-S`.
- Install libtool-built libraries with `-T` submodes such as `so_dot_version`, `so_dot_current`, `so_base`, and `old_lib`.

Environment behavior:
- `DIST_ROOT` or `DESTDIR` prefixes installation targets.
- `DIST_MANIFEST` records manifest entries.
- If `DIST_MANIFEST` is set without `DIST_ROOT`, the script records manifest entries but suppresses actual copy/link/mkdir/chmod/chown actions.
- Manifest records use `f`, `d`, or `l` lines for files, directories, and symlinks.

Ownership behavior:
- `_chown` tries `chown owner:group target`.
- Non-root failures can be suppressed with a one-time warning marker at `$DIST_ROOT/.chown.quiet`.
- When installing into `DIST_ROOT` as non-root, `CHOWN=true` disables ownership changes.

Maintenance/security notes:
- The script uses many unquoted variable expansions (`$dir`, `$f`, `$target`, etc.), so paths with spaces or shell metacharacters are fragile.
- It sources `./$libtool_lai` for `-T`, which is expected in build tooling but should not be pointed at untrusted files.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/include/install-sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/include/swab.h -->
# File Research: sources/local-fs/xfsdump/include/swab.h

`swab.h` provides byte-swapping primitives for 16-, 32-, and 64-bit XFS integer types.

Key content:
- Defines expression-style swap macros `___swab16`, `___swab32`, and `___swab64`.
- Defines constant-form macros `___constant_swab16`, `___constant_swab32`, and `___constant_swab64`.
- Provides fallback architecture hooks `__arch__swab16/32/64`, pointer forms, and in-place forms when no arch-specific versions are defined.
- Defines public `__swab16`, `__swab32`, and `__swab64` using `__builtin_constant_p` for compile-time folding.
- Provides inline functions `__fswab16`, `__swab16p`, `__swab16s`, and equivalents for 32/64-bit values.
- Supports `__SWAB_64_THRU_32__` to implement 64-bit swapping using two 32-bit swaps.

Dependency:
- Assumes XFS/Linux-style integer typedefs such as `__u16`, `__u32`, and `__u64` are already available.

Portability note:
- Uses GNU C statement expressions and `__builtin_constant_p`, so it is compiler-extension-dependent.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/include/swab.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/include/swap.h -->
# File Research: sources/local-fs/xfsdump/include/swap.h

`swap.h` builds higher-level integer conversion macros on top of `swab.h`.

Key behavior:
- Includes `<xfs/xfs.h>` and `<swab.h>`.
- Detects big-endian hosts as `XFS_NATIVE_HOST`.
- Defines `ARCH_NOCONVERT` as native/no-conversion and `ARCH_CONVERT` as either no-convert on big-endian or convert on little-endian.
- Provides `INT_SWAP16`, `INT_SWAP32`, and `INT_SWAP64` unless `HAVE_SWABMACROS` supplies alternatives.
- `INT_SWAP(type, var)` chooses swap width by `sizeof(type)`.
- `INT_GET(ref, arch)` reads either directly or byte-swapped.
- `INT_SET(ref, arch, valueref)` writes either directly or byte-swapped, with a constant-value optimization.
- `INT_XLATE(buf, p, dir, arch)` abstracts decode vs encode direction.

Role:
- Used by architecture translation helpers to read/write on-media xfsdump structures consistently across host byte order.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/include/swap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/inventory/Makefile -->
# File Research: sources/local-fs/xfsdump/inventory/Makefile

This makefile declares the inventory subsystem source inventory and hooks it into the shared build system.

Key content:
- Sets `TOPDIR = ..` and includes `$(TOPDIR)/include/builddefs`.
- `LSRCFILES` lists inventory implementation files and headers: `inv_api.c`, `inv_core.c`, `inv_fstab.c`, `inv_idx.c`, `inv_mgr.c`, `inv_oref.c`, `inv_oref.h`, `inv_priv.h`, `inv_stobj.c`, `inv_files.c`, `inventory.h`, `getopt.h`, and `testmain.c`.
- Defines empty `default install install-dev` targets.
- Includes `$(BUILDRULES)`.

Role:
- Provides build metadata for the inventory library/component consumed by dump content code for incremental/resume tracking.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/inventory/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/inventory/getopt.h -->
# File Research: sources/local-fs/xfsdump/inventory/getopt.h

This header provides a smaller getopt command string for inventory-related tooling.

Key content:
- `GETOPT_CMDSTRING` is `"gwrqdL:u:l:s:t:v:m:f:i"`.
- Defines option constants for dump destination, level, subtree, verbosity, dump label, media label, resume, and inventory print.
- Comments document which subsystem owns each option.

Notable mismatch:
- The command string includes letters such as `g`, `w`, `r`, `q`, `d`, `u`, `t`, and `m`, but this header only defines a subset of symbolic constants.
- It defines `GETOPT_MEDIALABEL` as `'M'`, but the command string shown here contains lowercase `m`, not uppercase `M`. This may reflect legacy/test usage or drift from the main dump getopt header.

Role:
- Used by inventory-specific code/tests rather than the main dump command parser.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/inventory/getopt.h -->