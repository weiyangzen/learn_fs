# Group Research: group_1342_ocfs2_tools_sources_local_fs_ocfs2_tools_github_workflows_package_y_e9c574432da7

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/.github/workflows/package.yml -->
# File Research: sources/local-fs/ocfs2-tools/.github/workflows/package.yml

## Role

This GitHub Actions workflow is a minimal packaging smoke job for `ocfs2-tools`.

## Behavior

It runs on pushes and pull requests targeting `master`, checks out the repository on `ubuntu-latest`, and creates `ocfs2-tools.tar.gz` with `tar -cvf ocfs2-tools.tar.gz *`.

## Dependencies And Risks

The workflow does not build, test, install dependencies, or upload the generated tarball as an artifact. The archive command excludes dotfiles such as `.github` because it uses `*`, and the file extension says `.gz` even though `tar -cvf` does not gzip.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/.github/workflows/package.yml -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/Config.make.in -->
# File Research: sources/local-fs/ocfs2-tools/Config.make.in

## Role

`Config.make.in` is the Autoconf-substituted make configuration template included by the project build system after `configure` generates `Config.make`.

## Build Variables

It exports package/version fields, install prefixes, root install prefixes, Python execution directory, toolchain commands, install commands, warning flags, `CFLAGS`, `CPPFLAGS`, `LDFLAGS`, vendor identity, and library flags for `com_err`, `uuid`, `aio`, `readline`, `glib`, `blkid`, and Python.

## Feature Gates

It carries configure decisions into makefiles, including `HAVE_BLKID`, `LIBDLM_FOUND`, `BUILD_OCFS2CONSOLE`, `BUILD_DEBUGOCFS2`, Corosync/controld support, Pacemaker/CMAN/CMAP/FSDLM support, debug mode, debug executables, and dynamic/static build mode for fsck and control tools.

## Notable Constraints

The template appends common warnings to caller-provided `CFLAGS`. Downstream makefiles depend on these substitutions being present, so configure failures or stale generated `Config.make` can change which OCFS2 tools are built.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/Config.make.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/Makefile

## Role

The top-level `Makefile` orchestrates the full `ocfs2-tools` build, distribution packaging, pkg-config installation, and cleanup.

## Build Graph

It includes `Preamble.make`, defines build ordering across subdirectory tiers, and ensures `include` builds before internal libraries, `libocfs2` builds after those libraries, and command/tool directories build after `libocfs2`.

The main tool tier includes fsck, mkfs, mounted, tunefs, debugfs, cluster control, heartbeat control, mount, controld, image/info/monitor tools, extras, fswreck, and defragfs. `ocfs2console` is conditionally added, and `vendor` is always added last.

## Distribution And Install

It defines pkg-config templates, Debian packaging files, project distribution files, `dist` archive creation, `distclean`, and installation of generated `.pc` files into `$(libdir)/pkgconfig`.

## Platform Notes

The file detects SUSE packaging conventions to select Python GTK package names, chkconfig dependencies, and Python bytecode compilation behavior. RPM build tooling is discovered dynamically.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/autogen.sh -->
# File Research: sources/local-fs/ocfs2-tools/autogen.sh

## Role

`autogen.sh` regenerates the Autoconf configure script and immediately runs configure for `ocfs2-tools`.

## Behavior

It enables `set -e`, removes `autom4te.cache`, runs `autoconf`, then executes `./configure "$@"` with any caller-provided arguments.

## Risk Areas

It does not run `autoheader`, `automake`, or `libtoolize`; this project expects a mostly hand-written make/autoconf setup. Because it runs configure directly, failures in dependency detection stop the script.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/autogen.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/configure.in -->
# File Research: sources/local-fs/ocfs2-tools/configure.in

## Role

`configure.in` is the Autoconf input for `ocfs2-tools`. It validates the host and dependency environment, computes project version variables, probes optional cluster/GUI/debug features, and declares generated output files.

## Core Configuration

The script requires Autoconf 2.54, initializes against `libocfs2/bitmap.c`, sets package name `ocfs2-tools`, and defines version `1.8.9` plus optional extra version suffix. It rejects non-Linux hosts and requires GCC.

If `CFLAGS` is unset, it applies `-O2` by default or `-g`/`-ggdb` for `--enable-debug`. It initializes compiler, preprocessor, install, symlink, ranlib, and `ar` discovery, then sets root install directories from `--with-root-prefix`.

## Required Dependencies

Required probes include:

- `com_err` through pkg-config or `-lcom_err` plus `et/com_err.h`.
- `uuid` through `-luuid` plus `uuid/uuid.h`.
- `libaio` through `-laio` plus `libaio.h`.
- `readline` through `-lreadline` plus `readline/readline.h`.
- GLib 2.2.3 or newer.

The script also tests whether GLib and `com_err` can be linked statically, which controls whether static fsck or cluster-control builds are allowed.

## Optional Feature Gates

The configure logic sets build flags for:

- `BUILD_DEBUGOCFS2` if readline is available.
- Dynamic vs static fsck/control tools with `--enable-dynamic-fsck` and `--enable-dynamic-ctl`.
- Pacemaker, CMAN, Corosync/OpenAIS CPG, OpenAIS checkpoint, libdlmcontrol, libdlm, FSDLM, CMAP, and `ocfs2_controld`.
- Python 2.3+, Python headers, PyGTK/gobject, blkid, and optional `ocfs2console`.

## Generated Files

It generates `Config.make`, pkg-config files, many man pages, vendor specs/sysconfig docs, optional `ocfs2console` files, and `defragfs.ocfs2/defragfs.ocfs2.8`.

## Notable Limitations

The build system is tied to Linux, GCC, legacy Python 2-era GUI tooling, and older cluster stack APIs. Several optional cluster components degrade to warnings, so a configure success does not imply every tool will be built.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/configure.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debian/po/POTFILES.in -->
# File Research: sources/local-fs/ocfs2-tools/debian/po/POTFILES.in

## Role

This Debian gettext file lists templates that should be included in debconf translation extraction.

## Contents

It contains one entry, marking `ocfs2-tools.templates` as `[type: gettext/rfc822deb]`.

## Impact

Debian packaging translation updates depend on this file to know that debconf template text is translatable.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debian/po/POTFILES.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debian/rules -->
# File Research: sources/local-fs/ocfs2-tools/debian/rules

## Role

`debian/rules` is the Debian package build script for `ocfs2-tools`.

## Build Flow

It includes quilt integration, runs `./configure` with debug disabled, dynamic control/fsck enabled, `/usr` prefix paths, and `/usr/share/man` man path, then builds with `make`.

## Install And Packaging

The install target stages into `debian/tmp`, copies vendor init/default files into Debian package names, runs `dh_install`, installs init scripts for `o2cb` and `ocfs2`, installs docs/examples/changelog, then performs Debian helper steps for stripping, compression, debconf, permissions, shared libraries, Python support, control file generation, checksums, and package build.

## Cleanup

The clean target unpatches quilt patches, removes Debian helper state, generated init/default files, vendor spec output, console shared objects, runs `make distclean`, and updates debconf translations.

## Risk Areas

This is an older debhelper-style rules file using `dh_clean -k`, `dh_pysupport`, and quilt makefile inclusion. Modern Debian tooling may require updates.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debian/rules -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/Makefile

## Role

This makefile builds and distributes the `debugfs.ocfs2` administrative debugger.

## Build Inputs

It compiles `main.c`, `commands.c`, `dump.c`, `utils.c`, `journal.c`, block/inode/path search helpers, lock dump helpers, system-directory stats, and network stats. It installs the binary under `$(root_sbindir)` and builds the `debugfs.ocfs2.8` man page.

## Libraries

It links against `libocfs2`, `libo2cb`, GLib, `com_err`, readline, AIO, and conditionally `libdlm_lt` and `libcmap` when configured.

## Distribution

The distribution list includes all source/header files, `README`, and the man-page template. It creates an `include` directory in distribution archives.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/commands.c -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/commands.c

## Role

`commands.c` is the command dispatcher and command implementation layer for `debugfs.ocfs2`. It owns the global debugfs session state (`gbls`), maps command names to handlers, opens/closes OCFS2 devices or image files, translates user file specifications, and invokes the lower-level dump/search/journal helpers.

## Command Surface

The command table implements filesystem inspection and diagnostic commands including `open`, `close`, `stats`, `stat`, `ls`, `cat`, `dump`, `rdump`, `bmap`, `icheck`, `locate`/`ncheck`/`findpath`, `logdump`, `hb`, `slotmap`, `group`, `grpextents`, `gd_free_bits`, `extent`, directory-index commands, xattr/refcount commands, live filesystem/DLM lock dump commands, network stats, `controld dump`, `lcd`, `cd`, `chroot`, `curdev`, `help`, and quit aliases.

## Device And Filespec Handling

`do_open()` opens a block device or `o2image` file with read-only or read-write flags, permits heartbeat devices, disables ECC checks, handles backup superblock selection, allocates a block buffer, caches root/system/heartbeat/slotmap/journal block numbers, and resets current working directory to `/`.

Filespecs can be pathnames, relative names, system-directory paths via `//`, raw inode forms like `<123>`, or lock names decoded through libocfs2. Most commands validate that translated block numbers are below `gbls.max_blocks`.

## Metadata And Data Operations

The file reads inodes, directories, extent blocks, group descriptors, slot maps, heartbeat files, journals, xattr blocks, refcount trees, and directory-index structures, then delegates formatting to `dump.c` and traversal helpers in `utils.c`.

`dump` and `cat` use `dump_file()`. `rdump` recursively extracts a subtree to a mounted native directory. `bmap` walks extent trees to translate logical file blocks to physical block numbers. `icheck` delegates reverse block ownership lookup to `find_block_inode()`.

## Live Kernel Diagnostics

`fs_locks`, `dlm_locks`, and `net_stats` can read live debugfs files or saved captures. They support filtering lock names, dumping LVBs, showing only busy locks, and repeated network-stat sampling.

## Mutation

Most commands are read-only, but `gd_free_bits -s` can record computed contiguous free-bit information back into group descriptors and therefore requires the debugfs process to have opened the filesystem with `-w`.

## Risk Areas

Command parsing is simple GLib whitespace splitting, so quoting is not shell-like. The code depends heavily on global mutable state and a single reusable block buffer. Write-capable paths are intentionally narrow but operate on metadata, so `-w` use is risky on mounted or damaged filesystems.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/commands.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/debugfs.ocfs2.8.in -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/debugfs.ocfs2.8.in

## Role

This is the manual page template for `debugfs.ocfs2`.

## Documented Interface

It documents interactive mode, command-file mode (`-f`), one-shot command mode (`-R`), backup superblock selection (`-s`), image mode (`-i`), read-write mode (`-w`), no-prompt mode, version/help, trace/log control (`-l`), and standalone lockname encode/decode modes.

## Filespec Semantics

The man page defines path resolution for inode numbers or locknames in angle brackets, absolute filesystem paths, paths relative to debugfs current directory, and `//` paths relative to the OCFS2 system directory.

## Command Documentation

The page lists and describes all supported debug commands: block mapping, file dump/cat, directory navigation/listing, metadata stats, journal dump, group/extent inspection, directory-index inspection, xattrs, refcount trees, heartbeat/slotmap/system-directory dumps, live OCFS2/DLM lock state, o2net stats, inode-to-path and block-to-inode searches, and recursive dumping.

## Notable Notes

It states that `gd_free_bits -s` requires `debugfs.ocfs2 -w`, and that live lock/net commands require debugfs mounted at `/sys/kernel/debug` unless reading saved files.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/debugfs.ocfs2.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/dump.c -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/dump.c

## Role

`dump.c` contains the formatting layer for `debugfs.ocfs2`. It turns OCFS2 and JBD2 on-disk structures into human-readable diagnostic text.

## Structures Dumped

It prints superblocks, inodes, local allocators, truncate logs, extent lists and blocks, chain lists, group descriptors, group free extents, directory entries and directory block trailers, directory-index roots/leaves/entry lists/free-space records, heartbeat blocks, slot maps, xattrs, refcount blocks/records, fragmentation summaries, and block checksums/ECC.

## Journal Support

It formats JBD2 headers, superblocks, descriptor blocks, commit blocks, revoke blocks, OCFS2 metadata blocks found inside journals, and unknown journal ranges that are probably file data.

## Checksum Handling

`dump_block_check()` prints stored CRC/ECC and validates known metadata blocks by swapping to disk format, recomputing metadata ECC, swapping back, and preserving the original block check contents.

## Dependencies

It relies on libocfs2 byte-order helpers, feature flag string helpers from `utils.c`, GLib strings, and `gbls.fs` for block size, checksum validation, and directory trailer interpretation.

## Risk Areas

This file mostly formats data, but some routines temporarily mutate buffers for byte swapping or directory-entry name termination. Callers must provide buffers that can be safely modified and restored.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/dump.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/dump_dlm_locks.c -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/dump_dlm_locks.c

## Role

`dump_dlm_locks.c` reads and formats live or captured o2dlm lock-resource state from debugfs.

## Input Format

It opens `/sys/kernel/debug/o2dlm/<uuid>/locking_state` through shared debugfs helpers, or a user-specified saved file. It parses records beginning with `NAME:`, `LRES:`, `RMAP:`, `LOCK:`, and optional `LVBX:`.

## Parsed Model

The file builds an in-memory `lockres` with owner, state flags, last-use data, in-flight locks, AST reservations, references, migration/list flags, reference map, optional LVB text, and separate granted/converting/blocked lock queues.

## Output

It decodes DLM lock levels, pending actions, lock-resource states, list membership, reference maps, raw LVB data, and per-lock queue rows with node, current/convert levels, cookie, refs, AST/BAST state, and pending actions.

## Risk Areas

The parser supports only current protocol version 1 for lock resources and locks. Newer kernel debugfs formats are rejected with a diagnostic. Filtering removes matched names from the requested lock list, so duplicate filters are not preserved.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/dump_dlm_locks.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/dump_fs_locks.c -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/dump_fs_locks.c

## Role

`dump_fs_locks.c` reads and formats live or captured OCFS2 filesystem lock state from debugfs.

## Input Sources

It opens `/sys/kernel/debug/ocfs2/<uuid>/locking_state` unless a saved file path is supplied. It supports selected lockname filters, optional LVB dumping, and a busy-lock-only mode.

## Protocol Handling

The parser reads a hexadecimal protocol version up to `CURRENT_PROTO` 4, parses the base lock record, and, for protocol versions above 1, parses PR/EX wait and acquisition statistics.

## Output

For each selected lock resource it prints lock mode, lock flags, read/write holder counts, pending AST/unlock actions, requested/blocking modes, optional raw LVB bytes, decoded metadata LVBs for metadata locks, and timing statistics such as gets, failures, total waits, max/average wait, last wait, disk refreshes, and first wait.

## Risk Areas

The code silently skips additional unknown fields after the known record portion, which preserves forward compatibility for appended fields but not structural format changes. It depends on kernel internal lock constants mirrored in `ocfs2_internals.h`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/dump_fs_locks.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/dump_net_stats.c -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/dump_net_stats.c

## Role

`dump_net_stats.c` reads and prints o2net per-node send/receive timing statistics from debugfs or a saved stats file.

## Input Format

It reads `/sys/kernel/debug/o2net/stats` by default or a user-provided file. Each record carries a protocol version, node number, send count, acquire/send/wait nanosecond totals, receive count, and process-time total.

## Output

It prints per-node send and receive message rates and microseconds-per-message breakdowns for acquire, transmit, wait, total send, and receive processing. With an interval, it computes deltas against the previous sample and repeats until count is exhausted or interrupted.

## Risk Areas

Only protocol version 1 is understood. The function still requires debugfs discovery even when a saved path is supplied. Counts and timing are derived from cumulative kernel counters, so counter resets or malformed captures can produce misleading deltas.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/dump_net_stats.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/find_block_inode.c -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/find_block_inode.c

## Role

`find_block_inode.c` implements the `icheck` backend: given one or more physical block numbers, it tries to identify the inode or allocator metadata that owns each block.

## Algorithm

It initializes a block-status array, locates the global bitmap inode, marks computed reserved blocks such as the superblock zone and group descriptor zones, scans the bitmap to classify free blocks, then scans all inodes.

For valid inodes in the current filesystem generation, it checks whether the queried block is the inode block itself, a chain allocator group descriptor, an extent block, or a data block within a leaf extent. For regular data blocks it records the logical block offset.

## Output

It delegates final rows to `dump_icheck()`, reporting used/free/unknown status, owning inode, and optional data offset.

## Risk Areas

The scan is exhaustive and can be expensive on large filesystems. It ignores invalid-generation or non-valid inodes and treats some metadata ownership through computed layout rules rather than direct reverse references.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/find_block_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/find_inode_paths.c -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/find_inode_paths.c

## Role

`find_inode_paths.c` implements pathname reconstruction for `locate`, `ncheck`, and `findpath`.

## Algorithm

It recursively walks directory entries from the filesystem root, builds path strings up to 4096 bytes, skips `.` and `..`, compares each entry’s inode against the requested inode list, and prints matches through `dump_inode_path()`.

`findall` controls whether traversal stops after one path per requested inode or continues to find all visible paths.

## Dependencies

It uses libocfs2 directory iteration, OCFS2 file-type values, and shared debugfs output/error helpers.

## Risk Areas

The search is a directory-tree traversal, so it can be expensive and can miss unreachable/orphaned inodes. It has a hard path length guard and aborts traversal on allocation or path-length failure.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/find_inode_paths.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/commands.h -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/commands.h

## Role

This header exposes the command dispatcher interface for `debugfs.ocfs2`.

## API

It declares:

- `do_command(char *cmd)` for parsing and executing one debugfs command line.
- `handle_signal(int sig)` for SIGTERM/SIGINT cleanup.

## Dependencies

The declarations are implemented in `commands.c` and used by `main.c`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/commands.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/dump.h -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/dump.h

## Role

`dump.h` declares the formatting API used by `debugfs.ocfs2` command handlers and journal/path/block helpers.

## Data Types

It defines helper contexts for directory listing (`list_dir_opts`) and directory-block walking (`dirblocks_walk`).

## API Coverage

The header declares dump routines for superblocks, inodes, local allocators, truncate logs, extents, chains, groups, directory entries/blocks, directory indexes, JBD2 journal structures, slot maps, heartbeat blocks, inode paths, block mapping, icheck output, checksums, xattrs, fragmentation, and refcount blocks/records.

## Role In Architecture

It separates command logic from output formatting, letting `commands.c`, `journal.c`, `stat_sysdir.c`, and search helpers share the same presentation code.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/dump.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/dump_dlm_locks.h -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/dump_dlm_locks.h

## Role

This header defines user-space representations and constants for dumping DLM lock resources.

## Contents

It mirrors DLM lock-resource state flags, queue identifiers (`GRANTED`, `CONVERTING`, `BLOCKED`), and structures for a lock resource and individual locks.

`struct lockres` holds owner/state/counters, optional refmap/LVB strings, and lock queues. `struct lock` holds mode, convert mode, node, AST/BAST flags, pending operation flags, refs, cookie, and list linkage.

## API

It declares `dump_dlm_locks()`, which reads live or saved DLM lock state and prints selected lock resources.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/dump_dlm_locks.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/dump_fs_locks.h -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/dump_fs_locks.h

## Role

This header declares the filesystem lock-state dumping entry point.

## API

`dump_fs_locks(char *uuid_str, FILE *out, char *path, int dump_lvbs, int only_busy, struct list_head *locklist)` reads OCFS2 lock state from live debugfs or a saved path, optionally dumps LVBs, filters to busy locks, and filters to selected lock names.

## Dependencies

The implementation depends on lock constants and metadata LVB structures from `ocfs2_internals.h`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/dump_fs_locks.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/dump_net_stats.h -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/dump_net_stats.h

## Role

This header defines the o2net stats record used by the debugfs network statistics command.

## Data Model

`struct net_stats` stores validity, send count, acquire/send/wait timing totals, receive count, and processing-time total for one node.

## API

It declares `dump_net_stats(FILE *out, char *path, int interval, int count)` for single-shot or repeated network-stat dumps.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/dump_net_stats.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/find_block_inode.h -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/find_block_inode.h

## Role

This header declares the block-owner reverse lookup function used by `icheck`.

## API

`find_block_inode(ocfs2_filesys *fs, uint64_t *blkno, int count, FILE *out)` accepts a filesystem handle, an array of queried block numbers, a count, and output stream.

## Implementation

The function is implemented in `find_block_inode.c`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/find_block_inode.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/find_inode_paths.h -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/find_inode_paths.h

## Role

This header declares the inode-to-path lookup function used by `locate`, `ncheck`, and `findpath`.

## API

`find_inode_paths(ocfs2_filesys *fs, char **args, int findall, uint32_t count, uint64_t *blkno, FILE *out)` traverses directories looking for names pointing at the requested inode block numbers.

## Implementation

The function is implemented in `find_inode_paths.c`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/find_inode_paths.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/journal.h -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/journal.h

## Role

This header exposes journal-reading support for `debugfs.ocfs2`.

## API

It declares `read_journal(ocfs2_filesys *fs, uint64_t blkno, FILE *out)`, which reads a journal inode and prints decoded JBD2 and OCFS2 metadata contents.

## Implementation

The function is implemented in `journal.c`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/journal.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/main.h -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/main.h

## Role

`main.h` is the central include and shared state definition for `debugfs.ocfs2`.

## Shared State

`struct dbgfs_gbls` stores program name, write/image/interactive flags, current device, open `ocfs2_filesys`, current/root directories, active command name, reusable block buffer, filesystem size limits, root/system/heartbeat/slotmap block numbers, and per-slot journal inode block numbers.

`struct dbgfs_opts` stores parsed command-line options before they are applied to global state.

## Includes And Macros

It enables GNU and large-file APIs, includes libc, GLib, readline, Linux type headers, libocfs2 headers, and all debugfs module headers. It defines fatal/warning macros, `min`/`max`, and a swap helper.

## Architectural Impact

Because most modules include this file, it centralizes dependencies and makes `gbls` the dominant cross-module coordination mechanism.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/main.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/ocfs2_internals.h -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/ocfs2_internals.h

## Role

This header mirrors selected OCFS2 kernel-internal lock and LVB definitions for debug-only user-space inspection.

## Contents

It defines DLM lock modes, LVB length, OCFS2 lock flags, AST action values, unlock action values, LVB version constants, and two metadata LVB layouts used by older and newer OCFS2 versions.

## Usage

`dump_fs_locks.c` and `dump_dlm_locks.c` use these definitions to decode lock state and metadata lock value blocks.

## Risk Areas

The file intentionally duplicates kernel-internal definitions. If the kernel debugfs protocol or LVB layout changes, this copy can become stale.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/ocfs2_internals.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/stat_sysdir.h -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/stat_sysdir.h

## Role

This header declares the system-directory statistics dump function.

## API

`show_stat_sysdir(ocfs2_filesys *fs, FILE *out)` prints the superblock and all objects in the OCFS2 system directory.

## Implementation

The function is implemented in `stat_sysdir.c`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/stat_sysdir.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/utils.h -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/utils.h

## Role

`utils.h` declares shared utility functions and helper structs used across `debugfs.ocfs2`.

## Data Types

It defines recursive dump options, a list-node wrapper for strings, and an enum selecting chain traversal behavior: dump group descriptors, dump free-bit summaries, or record free-bit summaries.

## API Coverage

The header declares feature-flag formatting helpers, journal flag formatting, nanosecond time formatting, pager helpers, inode/lockname/path translation, file dump/read helpers, permission/time string formatting, recursive dump, argument cleanup, contiguous free-bit analysis, debugfs path/file helpers, string-list operations, extent and chain traversal, and block-type detection.

## Role In Architecture

It is the shared support layer between command handlers, dump formatting, live debugfs readers, and recursive extraction.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/utils.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/journal.c -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/journal.c

## Role

`journal.c` reads an OCFS2 journal inode and decodes its contents for `logdump`.

## Flow

`read_journal()` opens the journal inode as a cached inode, allocates a journal superblock buffer and a 1 MiB read buffer, reads the journal file sequentially, dumps the journal superblock from block 0, then scans remaining blocks.

`scan_journal()` distinguishes JBD2 blocks by magic number, known OCFS2 metadata blocks by `ocfs2_detect_block()`, and unknown ranges as probable data.

## Output

It delegates JBD2 block formatting, OCFS2 metadata formatting, and unknown-range reporting to `dump.c`.

## Risk Areas

The code reads sequentially and decodes journal contents as present, not as a replay engine. It depends on current block size and byte-order interpretation matching the journal format.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/journal.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/main.c -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/main.c

## Role

`main.c` is the process entry point for `debugfs.ocfs2`. It parses top-level options, initializes error tables and signals, handles special modes, opens an optional device, and runs command-file or interactive command execution.

## Top-Level Modes

It supports:

- Trace/log mask mode with `-l`.
- Lockname decode mode with `-d`/`--decode`.
- Lockname encode mode with `-e`/`--encode`.
- Normal debugfs command mode with optional device, `-f` command file, `-R` one-shot command, `-i` image mode, `-s` backup superblock, `-w` write mode, and `-n` no prompt.

## Command Loop

For normal mode, it optionally synthesizes an `open` command for the requested device, executes one-shot commands, opens command files, prints version unless prompt is disabled, then reads commands from the file or readline and passes them to `do_command()`.

## Log Control

It can read or set OCFS2/o2cb trace masks through newer sysfs paths, older sysfs paths, or the legacy proc file.

## Risk Areas

The long-option table maps `"write"` to `'?'` instead of `'w'`, so long `--write` follows the help/version path while short `-w` works. The program uses global state, signal-triggered cleanup, and simple command-line parsing.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/main.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/stat_sysdir.c -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/stat_sysdir.c

## Role

`stat_sysdir.c` implements `stat_sysdir`, a full dump of the OCFS2 superblock and system directory objects.

## Behavior

It prints the current device, dumps the superblock and superblock inode, verifies the system directory, then iterates entries under `//`. For each system object except `..`, it reads the inode, prints metadata, traverses associated extents/chains/local alloc/truncate logs as appropriate, and lists child entries for system directories.

If the object is the slot map system file, it reads and dumps either the extended or classic slot map.

## Dependencies

It reuses directory iteration, inode dumping, chain/extent traversal, slot-map reading, and the global reusable block buffer.

## Risk Areas

The function performs broad metadata traversal and can generate large output. It assumes system-directory entries are readable and formatted enough for the shared dump routines.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/stat_sysdir.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/utils.c -->
# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/utils.c

## Role

`utils.c` provides shared helpers for `debugfs.ocfs2`: feature flag formatting, time formatting, pager integration, inode/path parsing, file extraction, recursive dumps, free-space analysis, debugfs discovery, string-list management, and extent/chain traversal.

## Filespec And Output Helpers

It decodes angle-bracket inode/lockname strings, resolves `//` paths to the system directory, opens `$PAGER` for interactive output, formats inode permissions and times, and normalizes GLib split arguments by moving empty strings to the end.

## File Extraction

`dump_file()` reads a cached inode, writes regular file contents in 1 MiB chunks, handles symlinks, and optionally preserves mode, ownership, and timestamps. `rdump_inode()` recursively recreates regular files, symlinks, and directories under a native destination directory.

## Metadata Traversal

`traverse_extents()` recursively dumps extent trees. `traverse_chains()` walks chain records and either dumps group descriptors, dumps free-bit summaries, or writes computed contiguous-free-bit values back into group descriptors.

## Live Debugfs Support

`get_debugfs_path()` validates `/sys/kernel/debug` or `/debug` as debugfs. `open_debugfs_file()` opens debugfs files under subsystem/UUID paths and maps common failures to OCFS2/o2cb error codes.

## Risk Areas

Some helpers write to native files/directories during dump extraction, and `RECORD_GD_FREE_BITS` writes metadata through libocfs2. Several operations rely on global `gbls.fs` even when an `fs` parameter is passed.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/debugfs.ocfs2/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/defragfs.ocfs2/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/defragfs.ocfs2/Makefile

## Role

This makefile builds the `defragfs.ocfs2` online defragmentation tool.

## Build Inputs

It compiles `main.c`, `record.c`, and `libdefrag.c`, with headers under `include/`. It defines `VERSION`, installs under `$(root_sbindir)`, and builds the `defragfs.ocfs2.8` man page.

## Linkage

The target uses the project `$(LINK)` rule without adding extra local libraries in this makefile; required libc/kernel interfaces are used directly by the object files.

## Distribution

The distribution list includes source files, headers, and the man-page template, and creates an `include` directory in the distribution archive.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/defragfs.ocfs2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/defragfs.ocfs2/defragfs.ocfs2.8.in -->
# File Research: sources/local-fs/ocfs2-tools/defragfs.ocfs2/defragfs.ocfs2.8.in

## Role

This is the manual page template for `defragfs.ocfs2`, the online defragmenter for OCFS2 filesystems.

## Documented Interface

It documents targets as regular files, directories, or mounted OCFS2 block devices. Directory targets recursively process files; device targets resolve the mount point and process that tree.

Options include:

- `-c` count files that should be processed.
- `-v` verbose/stat-only detail mode.
- `-l` low I/O mode.
- `-g` resume recorded progress.
- `-h` help.

## Notes

The page states that `lost+found` is skipped, other device mount points are not crossed, active-file defrag is discouraged due to DLM lock contention, and fragmented or insufficient free space can limit improvement.

## Mismatch

The man page says `-v` never defragments the target, but the implementation treats `-v` as detail output and still performs defrag unless combined with other behavior.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/defragfs.ocfs2/defragfs.ocfs2.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/defragfs.ocfs2/include/libdefrag.h -->
# File Research: sources/local-fs/ocfs2-tools/defragfs.ocfs2/include/libdefrag.h

## Role

`libdefrag.h` declares small support functions and print macros for `defragfs.ocfs2`.

## API

It declares `do_malloc()`, `do_read()`, `do_write()`, and `do_csum()`.

## Macros

It defines standardized error/status print macros for generic errors, file messages, errno-backed file errors, and message-plus-errno reports.

## Notes

The include guard misspells “defrag” as `__LIB_DEFERAG_H__`, but it is internally consistent.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/defragfs.ocfs2/include/libdefrag.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/defragfs.ocfs2/include/o2defrag.h -->
# File Research: sources/local-fs/ocfs2-tools/defragfs.ocfs2/include/o2defrag.h

## Role

`o2defrag.h` defines constants, option flags, and ioctl fallback definitions for `defragfs.ocfs2`.

## Contents

It defines the OCFS2 filesystem type string, mode flags for detail/statistic/resume/low-I/O behavior, file target kind constants, open file descriptor count for `nftw`, root UID, output scheduling constants, record interval, program name, and the fallback `OCFS2_IOC_MOVE_EXT` ioctl number.

## Data Types

`struct o2defrag_opt` maps a mode bit to its option string, and `declare_opt()` initializes table entries.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/defragfs.ocfs2/include/o2defrag.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/defragfs.ocfs2/include/record.h -->
# File Research: sources/local-fs/ocfs2-tools/defragfs.ocfs2/include/record.h

## Role

`record.h` defines the resume-record model for interrupted `defragfs.ocfs2` runs.

## Data Model

`struct resume_record` stores mode flags, the inode number where traversal should resume, argument count, and a list of target paths. `struct argv_node` stores one target path and list linkage.

The resume file is named `.ocfs2.defrag.record` under `/tmp`.

## API

It declares record dump, record-file path setup, record allocation/freeing, record fill/store/load/move/remove helpers, and argument-node freeing.

## Risk Areas

The record file stores raw struct header bytes plus variable strings and a checksum, so format portability depends on local ABI assumptions.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/defragfs.ocfs2/include/record.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/defragfs.ocfs2/libdefrag.c -->
# File Research: sources/local-fs/ocfs2-tools/defragfs.ocfs2/libdefrag.c

## Role

`libdefrag.c` implements small utility functions for `defragfs.ocfs2`.

## Functions

`do_malloc()` wraps zeroed allocation and exits on failure. `do_read()` and `do_write()` loop until the requested byte count is completed, retrying `EAGAIN` and `EINTR` and returning a negative errno on hard errors.

`do_csum()` computes an Internet-checksum-like 16-bit folded checksum over an arbitrary byte buffer, handling odd alignment and endianness.

## Usage

The record subsystem uses these helpers for allocation, robust record-file I/O, and resume-record checksum validation.

## Risk Areas

Pointer arithmetic is performed on `void *` in the I/O helpers, which is a GNU C extension rather than strict ISO C.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/defragfs.ocfs2/libdefrag.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/defragfs.ocfs2/main.c -->
# File Research: sources/local-fs/ocfs2-tools/defragfs.ocfs2/main.c

## Role

`defragfs.ocfs2/main.c` implements the online OCFS2 file defragmenter. It validates targets, walks directories, invokes the OCFS2 move-extents ioctl, tracks progress, and supports interrupted-run resume records.

## Target Handling

Targets may be block devices, directories, or regular files. Block devices are resolved to their first OCFS2 mount point through `/etc/mtab`. Files/directories are verified to be on an OCFS2 filesystem using `statfs64()` and `OCFS2_SUPER_MAGIC`, and directory targets use `nftw64()` with `FTW_PHYS | FTW_MOUNT` to avoid symlink following and crossing mounts.

## Defrag Operation

Regular files are skipped if empty, blockless, not owned by the current non-root user, not regular, or under `lost+found`. Defragmentation opens the file read-write and calls `ioctl(fd, OCFS2_IOC_MOVE_EXT, &me)` with `OCFS2_MOVE_EXT_FL_AUTO_DEFRAG` over the file size.

## Modes

`-c` counts candidate regular files, `-v` enables detailed output, `-l` periodically yields the scheduler, `-g` resumes from a stored record, and `-h` prints help. Progress is printed per file with success/failure counts.

## Resume Behavior

The traversal periodically stores a resume record every `RECORD_EVERY_N_FILES` or when SIGTERM/SIGINT sets `should_stop`. On resume, the tool skips entries until the stored inode is seen, then continues.

## Risk Areas

The man page and implementation differ for `-v`: code still defragments in detail mode. Resume by inode number can be fragile if directory contents change. The tool prints version on every run and uses `/etc/mtab`, which may be less authoritative than `/proc/self/mounts` on modern systems.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/defragfs.ocfs2/main.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/defragfs.ocfs2/record.c -->
# File Research: sources/local-fs/ocfs2-tools/defragfs.ocfs2/record.c

## Role

`record.c` implements persistent resume records for `defragfs.ocfs2`.

## Storage Format

The record file defaults to `/tmp/.ocfs2.defrag.record`. It stores the fixed header portion of `struct resume_record`, then null-terminated target paths, then a checksum over the preceding bytes. The maximum record size is 2 MiB.

## Operations

It can fill records from argv, move list ownership between records, dump the reconstructed command, store records with `fsync()`, validate checksums on load, rebuild argv-node lists, free records/nodes, and remove the record file after completion.

## Risk Areas

`free_record()` iterates while deleting list entries with `list_for_each`, which is unsafe compared with the safe variant used elsewhere. The on-disk format embeds native integer and struct layout assumptions, so it is intended for same-host resume rather than durable interchange.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/defragfs.ocfs2/record.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/documentation/samples/cluster.conf -->
# File Research: sources/local-fs/ocfs2-tools/documentation/samples/cluster.conf

## Role

This is a sample OCFS2/O2CB cluster configuration.

## Contents

It defines a cluster named `webcluster` with global heartbeat mode and three nodes:

- `node7` at `192.168.0.107`, node number 7, port 7777.
- `node6` at `192.168.0.106`, node number 6, port 7777.
- `node10` at `192.168.0.110`, node number 10, port 7777.

It also defines three heartbeat regions for the cluster by UUID-like region identifiers.

## Usage

The file is installed as a Debian example by `debian/rules` and included in distribution archives.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/documentation/samples/cluster.conf -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/extras/Makefile

## Role

This makefile builds uninstalled developer/diagnostic helper programs for OCFS2.

## Programs

It defines uninstalled targets for hardlink discovery, duplicate extent discovery, inode path lookup, random bit setting, lock resource decode/encode, journal dirty marking, allocation fragmentation discovery, group computation, metadata ECC checking, and slotmap resizing.

## Build Pattern

Each helper has a single C file, object list, and link rule. All helpers link against the static `../libocfs2/libocfs2.a`, `com_err`, and AIO.

## Distribution

All helper source files are included in `DIST_FILES`, but the programs are not installed through normal install rules.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/extras/Makefile -->