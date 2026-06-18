# Group Research: group_1866_xfsdump_sources_local_fs_xfsdump_invutil_invutil_c_sources_local_fs_83045e5a744c

Scope verified against `Docs/research_subset_a.md`: `sources/local-fs/xfsdump` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/invutil/invutil.c -->
# File Research: sources/local-fs/xfsdump/invutil/invutil.c

Implements the `xfsinvutil` command-line entry point and non-interactive inventory pruning logic. It parses options for interactive mode, force mode, fstab checking, mountpoint pruning, UUID pruning, session pruning, media-label filtering, debug, and lock waiting.

Core behavior:
- Initializes program/version globals and inventory base path through `inv_setup_base()`.
- Validates mutually exclusive option combinations.
- Parses prune dates with many accepted `strptime` formats and stores them as `time32_t`, with overflow detection.
- Traverses and prunes the inventory database hierarchy: `fstab` -> inventory index files -> storage object files.
- Uses mmap-backed in-place mutation for inventory files, then truncates or unlinks files when entries are removed.
- Uses advisory locking via `INVLOCK` in `open_and_lock()`.

Important functions:
- `main()` dispatches command mode.
- `ParseDate()` converts user dates to inventory-compatible 32-bit timestamps.
- `CheckAndPruneFstab()` removes duplicate fstab entries and entries whose index files become empty.
- `CheckAndPruneInvIndexFile()` removes inaccessible storage-object references and empty index files.
- `CheckAndPruneStObjFile()` marks sessions pruned based on date, session UUID, and optional media label.
- `uses_specified_mf_label()` limits pruning to sessions using a matching media label.
- `mntpnt_equal()` allows matching either full `host:path` strings or just mountpoint paths.

Dependencies:
- XFS inventory structs from `inv_priv.h`.
- `uuid_*` APIs for filesystem/session IDs.
- shared globals from `invutil.h`.
- `timeutil.h` for `ctime32`.

Notable risks/assumptions:
- Inventory files are treated as trusted binary layouts; mmap pointer arithmetic assumes valid offsets.
- Some allocations are unchecked, such as path construction helpers.
- Pruning modifies files in place and relies on locks to avoid xfsdump/xfsrestore races.
- `open_and_lock()` lock wait semantics depend on `INVLOCK` macro behavior.
- `CheckAndPruneStObjFile()` advances to the next `StObjhdr` after loop increment even on the last iteration, relying on mapped layout tolerance.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/invutil/invutil.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/invutil/invutil.h -->
# File Research: sources/local-fs/xfsdump/invutil/invutil.h

Shared header for `xfsinvutil` command and interactive inventory utility modules.

Defines:
- String buffer constants `STR_LEN` and `GEN_STRLEN`.
- `SYSCALL_FAILED` and `LOCK_BUSY` return codes for `open_and_lock()`.
- `Open_t`, describing read/write/unsafe modes for files and directories.

Exports:
- program globals: `g_programName`, `g_programVersion`, `inventory_path`.
- mode globals: `debug`, `force`, `wait_for_locks`.
- inventory path helpers, pruning functions, mmap/read/write helpers, listing functions, interactive entry point, and mountpoint comparison.

Role:
- Central coordination header tying command-line pruning, interactive UI, and inventory storage-object traversal together.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/invutil/invutil.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/invutil/list.c -->
# File Research: sources/local-fs/xfsdump/invutil/list.c

Implements a doubly linked list plus parent/child relationships for the ncurses inventory menu.

Core behavior:
- `node_create()` allocates a `node_t` and `data_t`, initializing visibility, expansion, delete/import/commit state, file/data indexes, displayed text, operation table, parent, and children.
- `list_add()` inserts after a previous node and registers the new node as a child of its parent.
- `list_del()` detaches a node from the list.
- `free_all_children()` recursively frees descendants.
- `mark_all_children_commited()` marks a subtree as committed after a parent operation is written to inventory state.

Notable details:
- Deleted nodes have their displayed text first byte set to `D`.
- `parent_add_child()` grows the child pointer array with `realloc`.
- `node_free()` frees text, children array, data, and node.

Risks:
- `node_create()` leaks `newnode` if `newdata` allocation fails.
- `parent_add_child()` does not handle `realloc` failure.
- Ownership is manual: display text and child arrays are freed by node cleanup, but payload data referenced by `data_idx` is managed elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/invutil/list.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/invutil/list.h -->
# File Research: sources/local-fs/xfsdump/invutil/list.h

Declares the menu list abstraction used by `invutil`.

Key types:
- `node_t`: doubly linked list node with opaque `data`.
- `data_t`: menu metadata, including indentation level, hidden/expanded/deleted/imported/committed flags, file index, display text, operation table, parent/children, child count, and data index into mmap-backed file records.

Exports list and node helpers:
- `node_create`, `node_free`
- `list_add`, `list_del`
- `free_all_children`
- `mark_all_children_commited`

Role:
- Provides the common tree/list model used by menu rendering, storage-object menus, and commit/delete operations.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/invutil/list.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/invutil/menu.c -->
# File Research: sources/local-fs/xfsdump/invutil/menu.c

Implements the ncurses menu event loop for interactive `xfsinvutil`.

Core behavior:
- `put_all_options()` renders all non-hidden nodes and highlights the current node.
- `put_helpscreen()` creates a temporary reversed-color help window listing key bindings.
- `menu()` drives keyboard navigation and operation dispatch.

Navigation:
- Up/down: previous/next visible node, also bound to `k`/`j`.
- Right/left: child/parent traversal, also bound to `l`/`h`.
- `?` or F1: help.
- Other keys are matched against `menukey_t` bindings.

Integration:
- Uses global `mainmenu`, `infowin`, `redraw_screen`, and `redraw_options`.
- Calls per-node operation hooks for highlight/unhighlight and keyed actions.
- Handles `ERR` with `errno == EINTR` by switching to recreated `mainmenu`, supporting terminal resize handling elsewhere.

Notable issue:
- `if(current == NULL && current->data == NULL)` should likely be `||`; as written it dereferences `current` if `current == NULL`.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/invutil/menu.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/invutil/screen.c -->
# File Research: sources/local-fs/xfsdump/invutil/screen.c

Provides small ncurses screen helpers.

Functions:
- `put_line()` writes a padded/truncated line to a window with left, center, or right alignment and optional attributes.
- `hitanykey()` prompts in the footer and waits for one keypress.
- `get_string()` prompts on the last line and reads bounded input with echo enabled.

Role:
- Shared rendering/input support for the interactive menu code.

Notable details:
- `put_line()` caps output width to 255 characters and uses a static 256-byte buffer.
- `get_string()` ignores its `win` parameter and always uses `stdscr`.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/invutil/screen.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/invutil/stobj.c -->
# File Research: sources/local-fs/xfsdump/invutil/stobj.c

Implements interactive handling of inventory storage-object files. Storage objects contain session headers, sessions, streams, and media-file records.

Core behavior:
- Opens storage-object files with exclusive locks and mmap write access.
- Builds hierarchical menu nodes for sessions, streams, and media files.
- Displays detailed info for highlighted sessions/streams/media files.
- Maps delete/undelete/select/commit actions to inventory record mutations.
- Marks session headers pruned by setting `sh_pruned`.
- Unlinks a storage-object file on close if every session is pruned.

Key functions:
- `generate_stobj_menu()` walks mapped storage-object records and creates hidden child menu nodes.
- `open_stobj()` opens, stats, mmaps, duplicates file name, and registers file metadata.
- `close_all_stobj()` closes all opened storage-object files and unlinks fully pruned ones.
- `stobjsess_commit()` commits deletion state back into `invt_seshdr_t.sh_pruned`.
- `stobj_prune()` tests whether an interactive node should be auto-marked for pruning by mountpoint/UUID/date.
- highlight handlers populate the info window with fields from inventory records.

Data model:
- Global `stobj_file` array stores mmap address, size, fd, counter, filename, and per-record pointers.
- `stobjsess_t` pairs session headers with session bodies for menu callbacks.

Risks/assumptions:
- Binary offsets in inventory records are trusted.
- Uses global mutable state and is not thread-safe.
- Some snprintf length calculations are tight but generally include fixed label lengths.
- File unlink is deferred until close and based solely on `sh_pruned` state.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/invutil/stobj.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/invutil/stobj.h -->
# File Research: sources/local-fs/xfsdump/invutil/stobj.h

Declares storage-object interactive menu APIs.

Exports:
- menu generation and file lifecycle: `generate_stobj_menu`, `open_stobj`, `close_stobj_file`, `close_all_stobj`.
- highlight handlers for sessions, streams, and media files.
- select, commit, prune, undelete, and delete callbacks.

Role:
- Connects storage-object-specific menu operations to the generic `cmenu` and `list` infrastructure.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/invutil/stobj.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/librmt/Makefile -->
# File Research: sources/local-fs/xfsdump/librmt/Makefile

Builds `librmt.la`, the remote tape support library.

Key details:
- Includes top-level `include/builddefs`.
- Sets `LTLDFLAGS` empty to force a static-only libtool library build.
- Lists `rmtlib.h` and all `rmt*.c`/`isrmt.c` implementation files.
- Default target builds dependencies and library.
- `install` and `install-dev` depend on default but perform no extra install commands in this file.

Role:
- Packages the `/etc/rmt` protocol wrappers used by dump/restore tape I/O.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/librmt/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/librmt/isrmt.c -->
# File Research: sources/local-fs/xfsdump/librmt/isrmt.c

Implements `isrmt(fd)`.

Behavior:
- Returns true when `fd >= REM_BIAS`.
- Remote descriptors are represented by adding `REM_BIAS` to an internal remote-unit index.

Role:
- Lets wrapper functions choose local syscall path versus remote protocol path.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/librmt/isrmt.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtabort.c -->
# File Research: sources/local-fs/xfsdump/librmt/rmtabort.c

Implements `_rmt_abort(fildes)`.

Behavior:
- Closes read and write pipe descriptors for a remote unit.
- Resets pipe slots to `-1`.
- Resets remote host type to `-1`.
- Emits a debug message if enabled.

Role:
- Central cleanup path after fatal remote protocol or pipe errors.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtabort.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtaccess.c -->
# File Research: sources/local-fs/xfsdump/librmt/rmtaccess.c

Implements `rmtaccess(path, amode)`.

Behavior:
- If `_rmt_dev(path)` says the path is remote, returns success without contacting the host.
- Otherwise delegates to local `access(2)`.

Implication:
- Remote access checks are deferred to remote open/operation time.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtaccess.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtclose.c -->
# File Research: sources/local-fs/xfsdump/librmt/rmtclose.c

Implements `rmtclose(fildes)`.

Behavior:
- Local descriptors call `close(2)`.
- Remote descriptors clear remembered host type, send `C\n`, read status, then abort/close pipes.
- Returns remote status or `-1` if command send fails.

Role:
- Provides close-like semantics for local and remote tape descriptors.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtclose.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtcommand.c -->
# File Research: sources/local-fs/xfsdump/librmt/rmtcommand.c

Implements `_rmt_command(fildes, buf)`.

Behavior:
- Writes a complete text command to the remote process pipe.
- On short/failing write, aborts the remote unit and sets `errno = EIO`.
- Emits debug logging.

Role:
- Shared command-send primitive for all remote operations.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtcommand.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtcreat.c -->
# File Research: sources/local-fs/xfsdump/librmt/rmtcreat.c

Implements `rmtcreat(path, mode)`.

Behavior:
- For remote device paths, calls `rmtopen(path, 1 | O_CREAT, mode)`.
- For local paths, calls `creat(2)`.

Role:
- Compatibility wrapper mirroring `creat(2)` while supporting remote tape paths.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtcreat.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtdev.c -->
# File Research: sources/local-fs/xfsdump/librmt/rmtdev.c

Implements `_rmt_dev(path)`.

Behavior:
- A path is considered remote only if it contains a colon followed by `/dev/`.
- Returns 1 for remote, 0 otherwise.

Important distinction:
- `rmtopen()` treats any path containing `:` as remote, while `_rmt_dev()` is stricter and only recognizes `:/dev/`.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtdev.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtfstat.c -->
# File Research: sources/local-fs/xfsdump/librmt/rmtfstat.c

Implements `rmtfstat(fildes, struct stat *buf)`.

Behavior:
- Local descriptors call `fstat(2)`.
- Remote descriptors send `Z<fd>\n`, read a byte count from `_rmt_status()`, then copy up to `sizeof(struct stat)` bytes into the caller buffer.
- Extra remote bytes are drained.

Notable assumption:
- The code comments acknowledge that direct binary copying of `struct stat` is non-portable and depends on compatible layout/padding.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtfstat.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtioctl.c -->
# File Research: sources/local-fs/xfsdump/librmt/rmtioctl.c

Implements local/remote tape `ioctl` support, mainly `MTIOCTOP` and `MTIOCGET`.

Core behavior:
- Local descriptors call `ioctl(2)`.
- Remote `MTIOCTOP` maps Linux tape op codes to IRIX or fallback standard op codes when needed, sends `I<op>\n<count>\n`, and returns remote status.
- Remote `MTIOCGET` sends `S`, reads binary tape status, interprets it as IRIX, Linux 32-bit, or Linux 64-bit layout based on detected remote host and returned size.
- Performs heuristic byte swapping if fields look byte-swapped.
- Converts IRIX status bits into Linux `GMT_*` generic status bits.

Dependencies:
- Remote host type is set by `rmtopen()` via remote `uname`.
- Uses `swap.h` macros for integer byte swapping.
- Uses Linux `<sys/mtio.h>` structures and constants.

Risks/assumptions:
- Supports only known Linux and IRIX status layouts.
- `mtop_*map` arrays are size `MT_MAX`; incoming `mt_op` values are used as indexes without explicit bounds checks.
- Binary protocol remains architecture-sensitive despite conversion logic.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtisatty.c -->
# File Research: sources/local-fs/xfsdump/librmt/rmtisatty.c

Implements `rmtisatty(fd)`.

Behavior:
- Remote descriptors always return 0.
- Local descriptors call `isatty(3)`.

Role:
- Simple compatibility wrapper for code paths that use `isatty`.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtisatty.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtlib.h -->
# File Research: sources/local-fs/xfsdump/librmt/rmtlib.h

Private header for `librmt`.

Defines:
- `REM_BIAS` descriptor bias for remote descriptors.
- `BUFMAGIC` command/status buffer size.
- `MAXUNIT` maximum remote tape units, set to 4.
- Macros for read/write pipe arrays and remote host table.
- Default `RSH_PATH` and `RMT_PATH`.
- Remote host IDs for Linux, IRIX, unknown, and undefined.
- Message levels and prototypes.

Exports globals:
- `_rmt_Ctp[MAXUNIT][2]`
- `_rmt_Ptc[MAXUNIT][2]`
- `_rmt_host[MAXUNIT]`

Role:
- Defines the remote descriptor model and shared protocol support primitives for all wrapper files.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtlib.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtlseek.c -->
# File Research: sources/local-fs/xfsdump/librmt/rmtlseek.c

Implements `rmtlseek(fildes, offset, whence)`.

Behavior:
- Local descriptors call `lseek(2)`.
- Remote descriptors send `L<offset>\n<whence>\n` and return `_rmt_status()`.

Notable detail:
- Serializes `off_t` as `long`, which may truncate on platforms where `off_t` exceeds `long`.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtlseek.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtmsg.c -->
# File Research: sources/local-fs/xfsdump/librmt/rmtmsg.c

Implements debug/warning message control for `librmt`.

Behavior:
- `RMTDEBUG` environment variable can enable warnings or debug.
- `rmt_turnonmsgs()` enables messages programmatically.
- `_rmt_msg()` prints to stderr when current debug code is high enough.

Risk:
- `_rmt_msg()` uses `vsprintf` into a fixed 256-byte static buffer, so overly long formatted messages can overflow.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtmsg.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtopen.c -->
# File Research: sources/local-fs/xfsdump/librmt/rmtopen.c

Implements `rmtopen(path, oflag, mode)` and the remote connection setup.

Core behavior:
- Local paths without `:` call `open(2)`.
- Paths with `:` are parsed as remote paths and opened through `rsh` plus remote `/etc/rmt`.
- Remote descriptor returned to caller is internal unit index OR’d with `REM_BIAS`.
- Finds a free slot in the fixed `MAXUNIT` pipe arrays.
- Parses path form with optional user and host.
- Uses `RSH` and `RMT` environment variables to override default remote programs.
- Detects remote host type by running remote `uname` via `popen`.
- Forks an `rsh` child with pipes connected to stdin/stdout.
- Sends `O<device>\n<oflag>\n` and requires successful remote status.

Security/robustness notes:
- Uses legacy `rsh`, not ssh.
- Remote host detection command is built as a shell string for `popen`.
- Fixed-size buffers constrain host/device/login fields.
- `rmtopen()` treats any colon in the path as remote, broader than `_rmt_dev()`.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtopen.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtread.c -->
# File Research: sources/local-fs/xfsdump/librmt/rmtread.c

Implements `rmtread(fildes, buf, nbyte)`.

Behavior:
- Local descriptors call `read(2)`.
- Remote descriptors send `R<nbyte>\n`, read status as byte count, then read that many bytes from the remote pipe.
- On pipe read failure, aborts and sets `errno = EIO`.

Notable implementation detail:
- The read loop mutates `nbyte` to the last read count and passes `rc` as the requested size each time; this still aims to accumulate `rc` bytes but is awkward and depends on short-read behavior not causing overread into the destination.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtread.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtstatus.c -->
# File Research: sources/local-fs/xfsdump/librmt/rmtstatus.c

Implements `_rmt_status(fildes)`.

Protocol:
- Reads one newline-terminated status line from the remote process.
- `A<number>` means success and returns the numeric value.
- `E<errno>` means recoverable error; sets `errno` and drains one error-message line.
- `F<errno>` means fatal error; sets `errno`, drains one line, aborts the connection.
- Any unexpected status aborts and sets `EIO`.

Role:
- Central parser for `/etc/rmt` status replies.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtstatus.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtwrite.c -->
# File Research: sources/local-fs/xfsdump/librmt/rmtwrite.c

Implements `rmtwrite(fildes, buf, nbyte)`.

Behavior:
- Local descriptors call `write(2)`.
- Remote descriptors send `W<nbyte>\n`, write the payload to the pipe, then return remote status.
- Short/failing payload writes abort and set `errno = EIO`.

Role:
- Remote tape write wrapper matching `write(2)`-style usage.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/librmt/rmtwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/m4/Makefile -->
# File Research: sources/local-fs/xfsdump/m4/Makefile

Build-system Makefile for m4/autoconf macro files.

Key details:
- Lists libtool macro files in `CONFIGURE`.
- Lists package-specific m4 files in `LSRCFILES`.
- Default target does nothing beyond build-rule integration.
- `realclean` depends on `distclean` and removes generated libtool macro files.

Role:
- Maintains macro source distribution and cleanup behavior.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/m4/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/man/Makefile -->
# File Research: sources/local-fs/xfsdump/man/Makefile

Top-level manpage Makefile.

Behavior:
- Includes build definitions from parent.
- Defines `SUBDIRS = man8`.
- Default builds subdirectories.
- Install and install-dev recurse into subdirectories through pattern rules.

Role:
- Delegates manual page build/install handling to `man/man8`.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/man/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/man/man8/Makefile -->
# File Research: sources/local-fs/xfsdump/man/man8/Makefile

Makefile for section 8 administrator manpages.

Behavior:
- Sets `MAN_SECTION = 8`.
- Discovers man pages with `$(shell echo *.8)`.
- Installs to `$(PKG_MAN_DIR)/man8`.
- `install` creates destination directory and invokes `$(INSTALL_MAN)`.
- `install-dev` is empty.

Role:
- Packages xfsdump/xfsrestore administrative documentation.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/man/man8/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/po/Makefile -->
# File Research: sources/local-fs/xfsdump/po/Makefile

Localization Makefile.

Behavior:
- Sets POT file to `$(PKG_NAME).pot`.
- Defines supported `LINGUAS = de pl`.
- Builds `.pot` and `.mo` files by default.
- Uses `$(LOCALIZED_FILES)` as gettext input.
- `install` invokes `$(INSTALL_LINGUAS)`.
- `install-dev` and `install-lib` are empty.

Role:
- Integrates German and Polish translations into the package build.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/po/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/release.sh -->
# File Research: sources/local-fs/xfsdump/release.sh

Bash release automation script for xfsdump.

Modes/options:
- `--kup` uploads final tarball/signature with `kup`.
- `--no-commit` skips release commit/tag.
- `--last-head` identifies previous release commit for announcement email content.
- `--for-next` prepares for-next branch announcement instructions.
- `--help` prints usage.

Release flow:
- Optionally edits `VERSION`.
- Sources `./VERSION` and computes `version`.
- Updates `doc/CHANGES`, `configure.ac`, and `debian/changelog`.
- Shows diff, prompts for confirmation, commits with signoff, and creates signed annotated tag.
- Runs `make realclean`, removes old tar/signature files, runs `make dist`.
- Creates uncompressed tar copy, signs it with GPG, verifies signature, renames `.asc` to `.sign`.
- Optionally uploads with `kup`.
- Generates announcement mail template using git log, shortlog, diffstat, and contributor script.

Risks/assumptions:
- Mutates working tree and requires clean-enough git state.
- Requires `$EDITOR`, `gpg`, `make`, `git`, `less`, optional `kup`, and optional `neomutt`.
- Uses `set -e`, but interactive commands and external editor behavior remain manual.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/release.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/restore/Makefile -->
# File Research: sources/local-fs/xfsdump/restore/Makefile

Builds the `xfsrestore` command.

Key structure:
- Defines common headers/sources symlinked from `../common`.
- Defines inventory headers/sources symlinked from `../inventory`.
- Local restore-only sources include `bag.c`, `content.c`, `dirattr.c`, `inomap.c`, `mmap.c`, `namreg.c`, `node.c`, `tree.c`, and `win.c`.
- Links against UUID, handle, attr, remote tape, and pthread libraries.
- Adds `-DRESTORE`, and optionally `-DHAVE_FALLOCATE`.
- Default target builds dependencies and `xfsrestore`.

Install behavior:
- Installs binary under root sbin.
- Also installs/symlinks into package sbin unless both directories are the same filesystem entry.
- Development install is empty.

Role:
- Assembles restore program from shared dump/restore infrastructure, inventory support, librmt, and restore-local modules.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/restore/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/restore/bag.c -->
# File Research: sources/local-fs/xfsdump/restore/bag.c

Implements a small intrusive “bag” collection abstraction for restore code.

Data structure:
- Circular doubly linked list.
- Caller embeds `bagelem_t` inside payload objects.
- Each element stores loaded flag, owning bag, search key, payload pointer, and links.

Functions:
- `bag_alloc()` allocates and zeroes a bag.
- `bag_insert()` inserts a caller-provided element at the head, records key and payload.
- `bag_remove()` removes an element, returns its key/payload, and zeroes the embedded element.
- `bag_find()` linearly searches by key and returns the matching embedded element plus payload.
- `bagiter_init()` initializes a stable iterator over current bag contents.
- `bagiter_next()` returns next element and payload; callers may remove returned elements before continuing.
- `bag_free()` zeroes all embedded elements and frees the bag object.

Complexity:
- Insert/remove are O(1).
- Find and iteration are O(n).

Assumptions:
- Assertions enforce correct ownership/loading in debug-enabled builds.
- Not thread-safe.
- `bag_free()` clears embedded elements but does not free caller-owned payload objects.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/restore/bag.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/restore/bag.h -->
# File Research: sources/local-fs/xfsdump/restore/bag.h

Declares the intrusive bag abstraction used by restore code.

Key types:
- `bagelem_t`: embedded element owned by a bag while loaded.
- `bag_t`: collection head.
- `bagiter_t`: iterator state with bag, last element, and next element.

API:
- `bag_alloc`
- `bag_insert`
- `bag_remove`
- `bag_find`
- `bagiter_init`
- `bagiter_next`
- `bag_free`

Contract:
- Users embed `bagelem_t` into their own objects.
- Users should not inspect or mutate `bagelem_t` internals directly.
- Payload lifetime remains caller-owned.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/restore/bag.h -->