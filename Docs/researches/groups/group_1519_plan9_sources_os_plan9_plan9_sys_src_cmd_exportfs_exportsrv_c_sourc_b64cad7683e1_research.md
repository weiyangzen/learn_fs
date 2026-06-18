# Group Research: group_1519_plan9_sources_os_plan9_plan9_sys_src_cmd_exportfs_exportsrv_c_sourc_b64cad7683e1

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/plan9`.

This group covers Plan 9 user-space filesystem/server utilities: `exportfs`, an `ext2srv` 9P server, `faces`, fax tools, standalone command utilities, and parts of Fossil's 9P service layer.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/exportfs/exportsrv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/exportfs/exportsrv.c

Implements the core 9P request handlers for `exportfs`. It translates 9P messages into local Plan 9 filesystem operations using `Fid` and `File` state from `exportfs.h`.

Key behavior:
- Negotiates `Tversion`, rejecting non-`9P2000` clients and bounding `messagesize`.
- Rejects `Tauth`; this export path does not require per-session auth.
- Implements attach/walk/clunk/stat/create/remove/wstat locally, including pseudo mount point setup when `srvfd` is active.
- Dispatches potentially blocking `Topen`, `Tread`, and `Twrite` to worker processes through `slave()` and `blockingslave()`.
- Enforces read-only mode both in the central `slave()` gate and in mutating handlers.
- Supports `Tflush` by recording `flushtag`, optionally posting a note to an interruptible worker, then emitting a flush reply.

Important implementation details:
- `clonefid()` forcibly replaces an existing newfid if needed, closing its file descriptor before reallocation.
- `Xwalk()` implements partial walk semantics and prevents walking above the exported root by returning `Exmnt`.
- `Xstat()` rewrites the returned qid path to `f->f->qidt->uniqpath`, preserving exportfs' synthetic path identity.
- `slaveopen()` detects `QTMOUNT` and starts a nested exportfs via `openmount()`.
- `slaveread()` uses `preaddir()` when directory filtering is active through `patternfile`.

Risks and invariants:
- Several comments acknowledge races because the server relies on shared-memory workers and sparse locking.
- Worker interruption is note-based and only active during selected blocking syscalls.
- `openmount()` forks and execs `/bin/exportfs`, so mount traversal depends on the external executable and inherited fd setup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/exportfs/exportsrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/exportfs/pattern.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/exportfs/pattern.c

Adds include/exclude pattern support for exported directory reads. Patterns are loaded from `patternfile` into regular-expression arrays.

Key behavior:
- `exclusions()` reads lines beginning with `+ ` or `- ` and compiles them with Plan 9 regexp support.
- Include patterns are treated as required matches: if a path fails any include regexp, it is excluded.
- Exclude patterns remove paths that match.
- `preaddir()` wraps directory reads to filter entries and maintain directory offsets in the `Fid` structure.

Important implementation details:
- Directory offset handling is intentionally strict: offset zero rewinds the cached directory buffer, while any non-current offset fails.
- `preaddir()` keeps an un-emitted entry in the cache if `convD2M()` reports insufficient output space.
- Paths are converted through `makepath(f->f, d->name)` before filtering, and root is normalized to `/`.

Risks and invariants:
- `excludefile()` assumes `include` and `exclude` are initialized when filtering is enabled.
- Filtering can make directory offsets synthetic because skipped entries do not advance the returned byte count.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/exportfs/pattern.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ext2srv/chat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ext2srv/chat.c

Provides logging and panic helpers for `ext2srv`.

Key behavior:
- `chat()` writes formatted diagnostic output only when global `chatty` is non-zero.
- `mchat()` always writes formatted output to stderr.
- `panic()` prefixes messages with `argv0` and process id, includes `%r`, then exits with status `panic`.

Dependencies:
- Used by the ext2 server request handlers, filesystem implementation, and buffer cache for diagnostics.
- Relies on Plan 9 varargs formatting and `write(2, ...)`.

Risks and invariants:
- Fixed 1024-byte buffers truncate long formatted messages through `vseprint()`.
- `panic()` terminates the process and is used for invariant violations such as exhausted buffers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ext2srv/chat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ext2srv/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ext2srv/dat.h

Defines `ext2srv`'s shared data model: ext2 on-disk structures, server state, constants, and error numbers.

Key contents:
- Ext2 superblock, group descriptor, inode, and directory entry structures.
- Ext2 constants for magic, block sizes, root inode, valid state, inode block pointers, and file type bits.
- `Iobuf`, the block cache entry used by `iobuf.c`.
- `Xfs`, the open ext2 device/filesystem state, including computed block size, group layout, inode layout, and cache-related metadata.
- `Xfile`, the per-Plan-9-fid state attached through lib9p `Fid->aux`.
- `Ext2`, a typed wrapper around cached superblock, group descriptor, or bitmap blocks.

Important relationships:
- `Xfile` stores `inbr`, `pinbr`, inode block address, and inode offset; most ext2 operations use this instead of holding an inode object.
- `DESC_ADDR` and `DESC_OFFSET` map group numbers to descriptor blocks and descriptor slots.
- Error enum indexes are paired with strings in `errstr.h`.

Risks and invariants:
- The on-disk structures are defined with native C fields and assume the Plan 9 build target's layout matches the expected ext2 little-endian representation.
- Only classic ext2 fields are modeled; newer ext2/ext3/ext4 extensions are outside this server's scope.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ext2srv/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ext2srv/errstr.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ext2srv/errstr.h

Maps `ext2srv` internal error enum values from `dat.h` to human-readable 9P error strings.

Key behavior:
- Defines `errmsg[]` with designated entries for format errors, I/O failures, permission failures, missing filesystem devices, no space, corrupt filesystem, and unclean filesystem state.
- `xfssrv.c` exposes these strings through `xerrstr()`.

Risks and invariants:
- The array must remain aligned with the error enum in `dat.h`.
- Unknown enum values fall back to `no such error` in `xerrstr()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ext2srv/errstr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ext2srv/ext2fs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ext2srv/ext2fs.c

Implements the lib9p `Srv` callbacks for the ext2 filesystem server. It is the 9P-facing layer over the lower-level ext2 code in `ext2subs.c`.

Key behavior:
- `rattach()` maps an attach `aname` to an `Xfs`, loads inode 2, and creates the root qid.
- `rclone()` copies `Xfile` state into a new fid.
- `rwalk1()` handles single-element walks, including `.`, `..`, root handling, and directory lookup through `get_file()`.
- `rstat()` and `rwstat()` convert between Plan 9 `Dir` structures and ext2 inode/directory metadata.
- `rread()` dispatches to `readdir()` or `readfile()`.
- `rwrite()` allows writes only to regular files.
- `ropen()` handles `OTRUNC` through `truncfile()`.
- `rcreate()` creates files or directories, then mutates the fid to refer to the new inode.
- `rremove()` delegates to ext2 `unlink()`.

Important implementation details:
- `response()` centralizes conversion from global `errno` to lib9p `respond()`.
- Walk errors restore `pinbr` so failed walks do not corrupt parent tracking.
- Directory permissions derive from the parent mode and requested Plan 9 permissions.

Risks and invariants:
- Uses a global `errno` defined in `xfssrv.c`, not C library `errno`.
- Commented permission checks indicate incomplete security enforcement for remove and related operations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ext2srv/ext2fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ext2srv/ext2subs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ext2srv/ext2subs.c

Contains the main ext2 implementation for `ext2srv`: superblock handling, inode and block mapping, directory operations, file I/O, allocation, deletion, truncation, and bit operations.

Key behavior:
- Loads optional UID/GID maps from passwd/group-like files and maps numeric ext2 ids to Plan 9 names.
- `ext2fs()` validates the superblock, rejects unclean filesystems, computes layout parameters, and marks the filesystem not clean while mounted unless read-only.
- `CleanSuper()` marks the filesystem valid again when the last `Xfs` reference is dropped.
- `get_inode()`, `get_file()`, and `getname()` locate inodes and names using inode table and directory entries.
- `dostat()` and `dowstat()` translate stat and rename/mode/mtime updates.
- `readfile()` and `writefile()` perform block-level file I/O, including fast symlink reads.
- `readdir()` emits Plan 9 directory entries through `convD2M()`.
- `bmap()` resolves direct, indirect, double-indirect, and triple-indirect blocks.
- `getblk()`, `inode_getblk()`, and `block_getblk()` allocate blocks on write.
- `new_block()` and `new_inode()` update ext2 bitmaps, group counts, and superblock counts.
- `create_file()`, `create_dir()`, `add_entry()`, `unlink()`, `delete_entry()`, and `empty_dir()` maintain directory contents and link counts.
- `free_block_inode()`, `free_block()`, `free_inode()`, and `truncfile()` reclaim ext2 resources.

Important implementation details:
- Allocation strategy is derived from Linux ext2 code and attempts locality near goal blocks or parent inode group.
- Directory operations only iterate direct directory blocks up to `EXT2_NDIR_BLOCKS`.
- The server updates inode times and marks cached blocks dirty through `dirtybuf()`.

Risks and invariants:
- The code assumes classic ext2 layout and does not include journaling or modern ext4 feature negotiation.
- Several corruption checks set `Ecorrupt`, but recovery is limited.
- `new_inode()` contains a suspicious comparison where the same field is compared to itself when selecting a directory group, which may reduce allocation quality.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ext2srv/ext2subs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ext2srv/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ext2srv/fns.h

Declares the cross-file API for `ext2srv`.

Key contents:
- Logging, panic, error conversion, and UID/GID map loading.
- `Xfs` and `Xfile` lifecycle helpers.
- 9P-facing ext2 operations such as inode lookup, file lookup, stat conversion, read/write/readdir, create, unlink, truncate, and wstat.
- Allocation and bitmap helpers for ext2 blocks and inodes.
- Buffer cache operations from `iobuf.c`.

Important relationships:
- Bridges the lib9p callbacks in `ext2fs.c` with the ext2 implementation in `ext2subs.c`.
- Includes legacy or unused declarations such as FAT-oriented names, indicating shared ancestry with other filesystem servers.

Risks and invariants:
- Function prototypes use old-style spacing and shared globals, matching the Plan 9 codebase style.
- Maintaining this header requires keeping it synchronized with multiple implementation files because there are no module-level private headers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ext2srv/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ext2srv/iobuf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ext2srv/iobuf.c

Implements the fixed-size block buffer cache for `ext2srv`.

Key behavior:
- Maintains 100 `Iobuf` headers and hash buckets keyed by block address modulo `HIOB`.
- `getbuf()` returns a busy cached buffer or reuses the least recently used non-busy buffer from the tail.
- Dirty buffers are written back before reuse.
- `putbuf()` decrements busy count and moves the buffer to the LRU head.
- `syncbuf()` writes all dirty buffers.
- `purgebuf()` drops all buffers for a given `Xfs` and clears hash chains.
- `xread()` and `xwrite()` perform block-sized I/O at `addr * block_size`.

Important implementation details:
- Cache buffers are allocated at `EXT2_MAX_BLOCK_SIZE`; actual reads and writes use the filesystem block size.
- The LRU list is updated even for buffers that may still be referenced by other callers after busy count changes.

Risks and invariants:
- No explicit locking appears in this cache; correctness depends on the server's threading model and usage discipline.
- `getbuf()` panics when all buffers are busy.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ext2srv/iobuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ext2srv/xfile.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ext2srv/xfile.c

Manages open ext2 filesystem instances (`Xfs`) and per-fid state objects (`Xfile`).

Key behavior:
- `getxfs()` opens the device or default file, reuses an existing `Xfs` by qid/name, or allocates a new one and initializes ext2 via `ext2fs()`.
- `refxfs()` decrements references and, on last close, marks the superblock clean, syncs buffers, purges buffers, and closes the device fd.
- `xfile()` retrieves, allocates, cleans, or clunks `Xfile` state attached to lib9p fids.
- `clean()` releases the root's filesystem reference and resets per-fid state.

Important implementation details:
- Reuse is guarded by `xlock`; free `Xfile` reuse is guarded by `freelock`.
- `xfile(fid, Asis)` returns nil if the underlying `Xfs` has been closed.
- Only root fids hold `Xfs` references; cloned or walked fids share the attached root reference model.

Risks and invariants:
- `getxfs()` removes a failed new `Xfs` from the head list but does not free all partially allocated fields in every path.
- Filesystem cleanliness depends on the final root fid being clunked and `refxfs()` running.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ext2srv/xfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ext2srv/xfssrv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ext2srv/xfssrv.c

Provides the `ext2srv` program entry point and server setup.

Key behavior:
- Parses flags for 9P debug, verbose logging, default device file, group/passwd maps, stdio serving, and read-only mode.
- Initializes the block cache with `iobuf_init()`.
- Serves either on stdio with `srv(&ext2srv)` or posts/mounts a named service with `postmountsrv()`.
- `xerrstr()` maps internal error numbers to strings from `errstr.h`.

Important implementation details:
- Defaults service name to `ext2`.
- If not verbose, stderr is redirected to `#c/cons`.
- `rdonly` controls device open mode and suppresses superblock dirtying in `ext2fs()`.

Risks and invariants:
- The commented notify handler indicates intended but disabled sync-on-note behavior.
- Uses global `errno` as the server error channel.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ext2srv/xfssrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/faces/dblook.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/faces/dblook.c

Small diagnostic program for the `faces` database lookup logic.

Key behavior:
- Expects `name domain`.
- Calls `findfile(&f, domain, name)` and prints the resolved face image path.
- Provides a stub `killall()` because shared face database code may call it on fatal conditions.

Dependencies:
- Reuses `faces.h` and `facedb.c` behavior.

Risks and invariants:
- Does not initialize graphics display state; it only exercises path lookup, not image loading.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/faces/dblook.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/faces/facedb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/faces/facedb.c

Implements face image lookup, file caching, domain translation, and image loading for the `faces` mail notifier.

Key behavior:
- Caches text file reads for `.machinelist` and `.dict` lookups with mtime and short read-time windows.
- `translatedomain()` rewrites domains through regexp entries in `.machinelist`.
- `tryfindpicture()` maps `domain/user` entries in `.dict` to image files.
- `tryfindfiledir()` recursively searches face directories, deferring `48x48x*` directories in preferred depth order and ignoring `512x*`.
- `findfile()` searches `$home/lib/face`, `/lib/face`, parent domains, and unknown fallbacks.
- Maintains a `Facefile` cache for loaded image and mask data.
- `readface()` loads old ascii face files, Plan 9 images, greyscale images, and masks suitable for drawing.
- `findbit()` attaches the resolved image/mask to a `Face`, or creates a yellow fallback tile.

Important implementation details:
- Face cache entries are ref-counted, and deleted entries are retained up to `Nsave` to avoid expensive reloads.
- Greyscale images may be inverted into masks and drawn through black.
- Unknown faces set `f->unknown`, allowing UI overlay of the domain.

Risks and invariants:
- Recursive directory traversal can be expensive, hence the local caches.
- The code assumes `display` is initialized before image-loading paths are used.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/faces/facedb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/faces/faces.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/faces/faces.h

Shared header for the `faces` mail notifier.

Key contents:
- String slots for user, domain, show path, and digest.
- `Facesize` fixed at 48 pixels.
- `Face` structure with image/mask pointers, identity strings, recency/time state, unknown flag, and backing `Facefile`.
- `Facefile` cache structure with image, mask, mtime, read time, refcount, filename, and next pointer.
- Global mail directory state and prototypes across UI, plumbing, database, and utility files.

Important relationships:
- `Face.bit` and `Face.mask` usually alias `Facefile.image` and `Facefile.mask`, except for fallback/error images.
- `maildirs` and `nmaildirs` are owned by `plumb.c` but consumed by `main.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/faces/faces.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/faces/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/faces/main.c

Main GUI and process orchestration for the Plan 9 `faces` mail notifier.

Key behavior:
- Initializes draw state, colors, arrow masks, fonts, mouse, plumbing, and maildir configuration.
- Maintains an array of `Face*` entries, with visible window bounds `first` and `last`.
- Draws date/time, face icons, user labels, message times, unknown-domain overlays, and scroll arrows.
- Runs separate processes for minute clock updates and mouse handling; the main process receives faces through `nextface()`.
- Supports history mode, initial mailbox loading, scroll navigation, deletion handling, and click-to-show mail.

Important implementation details:
- Layout uses fixed 48x48 face cells and computed `nacross`/`ndown` based on window size.
- `facetime()` switches from `HH:MM` to `Mon DD` after 18 hours.
- `addface()` inserts new faces at index zero and shifts the displayed grid by screen copy operations.
- `delface()` removes and compacts entries while redrawing only affected cells.
- `killall()` posts notes to sibling processes before exit.

Risks and invariants:
- Display access is guarded by Plan 9 display locks after `display->locking = 1`.
- Geometry assumes the window can hold at least one face; very small windows may create tight layout edge cases.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/faces/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/faces/plumb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/faces/plumb.c

Handles mail event input and show-mail output for `faces`.

Key behavior:
- `initplumb()` opens `send` and `seemail` plumber ports; if `seemail` is unavailable, it tails `/sys/log/mail`.
- `showmail()` sends a plumb message telling mail tools to display a message path.
- `nextface()` returns the next new `Face`, processing plumb `new` and `delete` messages or log lines.
- Deduplicates messages by digest with `alreadyseen()`.
- Parses sender names into user/domain using `@` and `!` conventions.
- Parses mail log dates and upas/fs info files for startup loading.
- `dirface()` constructs a `Face` from a stored `/mail/fs` message `info` file.

Important implementation details:
- `maildirs` is a dynamic list of accepted mail roots.
- Log fallback recognizes both `delivered user From` and `remote local!user From` records.
- `tweakdate()` shortens display dates relative to the current day.

Risks and invariants:
- Fallback log tailing sleeps when no new data is available.
- `setname()` lowercases the sender buffer in place, so callers must pass owned mutable strings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/faces/plumb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/faces/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/faces/util.c

Memory allocation helpers for `faces`.

Key behavior:
- `emalloc()` allocates and zeroes memory or exits on failure.
- `erealloc()` reallocates or exits on failure.
- `estrdup()` duplicates a string or exits on failure.

Risks and invariants:
- These helpers terminate the whole process rather than propagating allocation failures.
- `estrdup()` logs only the first ten characters of the failed source string.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/faces/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/factor.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/factor.c

Simple integer factorization utility implemented with floating-point arithmetic.

Key behavior:
- Factors command-line operands or newline-separated stdin values.
- Prints the original number, then one factor per indented line, then a blank line.
- Removes factors 2, 3, 5, and 7 first.
- Uses a wheel increment table to test candidate divisors after small primes.

Important implementation details:
- Inputs are parsed with `atof()` and stored as `double`.
- Divisibility is tested with `modf(n/d, &quot) == 0`.
- Trial division stops once the divisor exceeds `sqrt(n)+1`.

Risks and invariants:
- Precision is limited by `double`, so very large integers may factor incorrectly.
- The utility is oriented toward traditional Plan 9 command-line use, not arbitrary precision factoring.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/factor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/fax2modem.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/fax2modem.c

Parses Class 2 fax modem status responses and updates `Modem` state.

Key behavior:
- `initfaxmodem()` initializes fax mode and phase.
- `parameters()` parses comma-separated numeric response payloads after `:`.
- Handlers process `+FCON`, `+FTSI`, `+FDCS`, `+FCFR`, `+FPTS`, `+FET`, and `+FHNG`.
- Stores remote station id, negotiated page parameters, page result, end-of-page signal, and hangup cause.

Important implementation details:
- `fcon()` advances from phase A to phase B.
- `ftsi()` strips quoted modem station id text and stores it once.
- `fhng()` returns `Rhangup`, unlike most fax responses which return `Rcontinue`.

Risks and invariants:
- Parameter arrays are filled without explicit upper-bound checks against malformed long responses.
- Fax behavior depends on modem response syntax matching expected Class 2 strings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/fax2modem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/fax2receive.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/fax2receive.c

Receives fax pages from a Class 2 modem and writes them into spool files.

Key behavior:
- `page()` sends `AT+FDR`, waits for `CONNECT`, creates the page file, sends DC2, and reads page data until DLE ETX.
- DLE escaping is handled by treating doubled DLE as data and DLE ETX as page termination.
- Buffered page data is written to `m->pagefd`.
- After page data, waits for `OK` or `ERROR`.
- `receive()` loops pages, validates `FPTS`/`FET`/`FHNG`, retries failed pages, and handles multi-document sessions.
- `faxreceive()` initializes fax modem state and assumes the call has already been answered with `+FCON`.

Important implementation details:
- Page files are named and headered by `createfaxfile()`.
- New documents are logged but remain queued due to a noted limitation.
- Hangup code zero is success; other hangup codes become attention errors.

Risks and invariants:
- The page receive buffer is 100 KB and flushed when full.
- Cleanup of failed document pages is commented out.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/fax2receive.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/fax2send.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/fax2send.c

Sends one or more fax page files through a Class 2 modem.

Key behavior:
- Initializes fax modem state and waits for initial `OK` after dialing.
- Enables XON/XOFF flow control through the modem control fd.
- Opens each fax page, sends geometry with `AT+FDT=...`, waits for `CONNECT`, and streams data.
- Doubles DLE bytes in outgoing page data.
- Polls modem input between buffers to handle CAN, XON, XOFF, and unexpected bytes.
- Ends each page with DLE ETX, waits for `OK`, sends `AT+FET`, and validates `FPTS`.

Important implementation details:
- Uses rough software flow-control timing for problematic modems.
- On error, disables flow control, closes the page `Biobuf`, sends `AT+FK`, and consumes a short response.
- Page counter advances across all input files.

Risks and invariants:
- Error label cleanup assumes `m->bp` is valid on paths after `openfaxfile()`.
- Modem-specific behavior is encoded in protocol timing and flow-control comments.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/fax2send.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/file.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/file.c

Handles fax page file creation and parsing for send/receive paths.

Key behavior:
- `setpageid()` formats spool page names as `spool/time.pid.page`.
- `createfaxfile()` creates a received page file, writes Plan 9 picture-style metadata, remote station id, and `FDCS` parameters.
- `gsopen()` recognizes Ghostscript fax output by its `PC Research, Inc` header and sets default fax geometry.
- `picopen()` parses `TYPE=ccitt-g31`, `WINDOW=`, and `FDCS=` headers from Plan 9 fax picture files.
- `openfaxfile()` tries Ghostscript format first, then picture format.

Important implementation details:
- Width values are mapped through a five-entry table to Class 2 width codes.
- Send-side page geometry is only fully validated on page one.

Risks and invariants:
- Header parsing uses simple line and comma scanning; malformed files generally set protocol/system errors.
- The code expects CCITT G31 data.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/modem.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/modem.c

Low-level modem command, input buffering, response parsing, and flow-control helpers for fax tools.

Key behavior:
- Defines a response table mapping terse/verbose modem strings to result codes and optional fax response handlers.
- `initmodem()` stores data fd, control fd, type, and local id.
- `rawmchar()` reads buffered modem bytes, using `dirfstat()` length to avoid blocking when no bytes are ready.
- `getmchar()` waits for a single byte with timeout.
- `getmline()` reads CRLF-terminated response lines while ignoring XON/XOFF bytes.
- `command()` writes AT commands with carriage return.
- `response()` reads lines until one matches the result table, invoking fax-specific handlers when needed.
- `xonoff()` writes `x0` or `x1` to the control fd.

Important implementation details:
- Response matching is prefix-based against verbose strings.
- Fax status lines such as `+FPTS` can be consumed as intermediate `Rcontinue` events until a final response appears.

Risks and invariants:
- `response()` returns `Rnoise` on timeout or unmatched input after clearing the response buffer.
- `rawmchar()` depends on modem fd directory length semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/modem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/modem.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/modem.h

Shared fax modem interface and state definition.

Key contents:
- `Modem` structure for modem fds, response/error buffers, fax session state, page file state, input buffering, `Biobuf` page input, and negotiated FDCS parameters.
- Result code enum for modem responses.
- Error code enum for user-facing retry/protocol/system states.
- Valid-bit enum for page responses and opened file metadata.
- Function prototypes across fax modem parsing, receive, send, file handling, modem I/O, and logging helpers.

Important relationships:
- `valid` is a bitmask spanning modem responses (`Vfdcs`, `Vftsi`, `Vfpts`, `Vfet`, `Vfhng`) and file metadata (`Vwd`, `Vtype`).
- `fax2send.c` and `fax2receive.c` share the same `Modem` state and error reporting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/modem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/receive.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/receive.c

Command-line entry point for receiving a fax from stdin/stdout-connected modem service.

Key behavior:
- Parses `-v` for logging and `-s dir` for spool directory.
- Initializes a single `Modem` on fd 0 with no control fd.
- Calls `faxreceive()`.
- On successful receive, logs the result and execs `receiverc` with document id, success flag, page count, and optional FTSI.

Important implementation details:
- Default spool is `/mail/faxqueue`.
- Default post-receive script is `/sys/lib/fax/receiverc`.
- `receivedone()` does not run the script on receive failure.

Risks and invariants:
- If `exec(receiverc, argv)` fails after a successful receive, the process exits with `can't exec`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/receive.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/receiverc -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/receiverc

Plan 9 rc script run after fax reception.

Key behavior:
- Rebinds fax queue through `9fs fs` so mail actions operate as if on the file server.
- Reads recipients from `/mail/faxqueue/faxrecipients`.
- For normal received faxes, mails the reception metadata and a `page -w spool/id.*` command to recipients.
- Contains special handling for weekday or weekend New York Times faxes from a specific `FTSI`, copying pages into `/n/fs/lib/nyt` and removing spool pages.
- Falls back to mailing postmaster for unexpected argument counts.

Important implementation details:
- Arguments are expected as `time Y|N pages [ftsi]`.
- Page extension formatting handles one to three digit page numbers.

Risks and invariants:
- Hard-coded local policy for NYT fax routing and file-server paths.
- Removes `/srv/fs` before mounting the file server namespace.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/receiverc -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/send.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/send.c

Command-line entry point for sending fax page files.

Key behavior:
- Parses `-v`.
- Requires a phone number and at least one page file.
- Builds a telco address with `netmkaddr(number, "telco", "fax!9600")`.
- Dials the modem service, initializes `Modem`, and calls `faxsend()`.
- Logs success or failure to syslog category `fax`.

Important implementation details:
- The modem data fd and control fd come from `dial()`.
- On send failure, prints the modem error and exits with that error string so queue systems can retry based on status.

Risks and invariants:
- Assumes the telco service and fax modem are available through Plan 9 networking.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/send.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/subr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fax/subr.c

Common logging and error helpers for fax tools.

Key behavior:
- `verbose()` writes syslog messages when `vflag` is set.
- `error()` prints a formatted fatal message to stderr, optionally echoes to stdout, and exits.
- `seterror()` writes a user-facing retry/system/protocol error string into `m->error`.
- `faxrlog()` logs receive status, timestamp, success flag, page count, and optional FTSI.

Important implementation details:
- Error strings intentionally include `Retry, ...` for queue integration.
- `Esys` includes `%r` in the stored modem error.

Risks and invariants:
- `faxxlog()` is declared in `modem.h` but not implemented in this file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fax/subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fcp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fcp.c

Parallel file copy utility.

Key behavior:
- Copies one file to a target file or multiple files into a target directory.
- Rejects directory sources and same-file copies.
- Spawns up to 16 worker processes sharing memory to copy fixed 8 KB chunks with `pread()` and `pwrite()`.
- Preserves mode, mtime, uid, and/or gid depending on `-x`, `-u`, and `-g`.
- On worker failure, posts `failure` notes to other workers.

Important implementation details:
- Shared global `off` is protected by `QLock`; `nextoff()` assigns disjoint chunks to workers.
- Destination is created with source permissions masked to 0777.
- `samefile()` compares qid, dev, and type to avoid self-overwrite.

Risks and invariants:
- The parent waits for all children returned by `wait()`, not only the spawned worker pids.
- Sparse or special file behavior is not explicitly preserved beyond data and selected metadata.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/file.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/file.c

Plan 9 `file` command implementation for classifying file content and optional MIME type output.

Key behavior:
- Reads up to 6000 bytes, builds character and Unicode script histograms, and classifies gross content as ascii, latin, UTF, extended ascii, null/binary.
- Checks a sequence of recognizers: magic at offset 0, string prefixes, ELF, Plan 9 executable headers, IFF/RIFF, offset magic, offset strings, email/mbox, tar, HTML, compiler intermediates, source code heuristics, Plan 9 fonts/images, RTF, MSDOS executables, ascii face files, entropy-based compressed/encrypted data, and English text.
- Supports `-m` MIME output.
- Handles directories and non-ordinary special files before reading content.

Important implementation details:
- `long0tab`, `longofftab`, `file_string`, and `offstrs` are the primary magic tables.
- `wordfreq()` recognizes language keywords for C/Alef/Fortran/Limbo/assembler heuristics.
- `isp9bit()` parses old and new Plan 9 image headers, including compressed image prefixes and subfont trailers.
- `print_utf()` reports script names for Unicode-heavy text.
- Uses `crackhdr()` from `mach.h` to identify native executable formats.

Risks and invariants:
- Many recognizers are heuristic and order-dependent.
- MIME output is sometimes a coarse fallback such as `application/octet-stream`.
- `ismung()` names low-entropy distribution over high bits as compressed/encrypted based on a small sample.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fmt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fmt.c

Paragraph formatting utility.

Key behavior:
- Reads stdin or listed files, parses words with indentation, and emits wrapped lines.
- Supports `-i indent`, `-j` to disable joining original lines, and `-l`/`-w` for line width.
- Respects `$tabstop` for indentation width.
- Maintains paragraph breaks via blank-line sentinel words.
- Adds two spaces after sentence-ending punctuation except short uppercase abbreviations.

Important implementation details:
- `indentof()` computes leading spaces/tabs and preserves current indent on whitespace-only lines.
- `parseline()` builds a dynamic `Word**` list for the whole input.
- `printwords()` wraps by UTF rune length, indent changes, width, and `join` policy.

Risks and invariants:
- The entire input's word list is accumulated before printing.
- Allocation failures are not checked in `addword()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fortune.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fortune.c

Random fortune-line picker with optional persistent index.

Key behavior:
- Opens a supplied fortune file or `/sys/games/lib/fortunes`.
- If using the default file, uses `/sys/games/lib/fortunes.index` when current, or creates/updates it.
- Old index path selects a random 4-byte offset and reads that line.
- No-index path uses reservoir sampling while optionally writing offsets to a new index.
- Prints the selected line or a misfortune message on failure.

Important implementation details:
- Index offsets are stored little-endian in four bytes.
- If an existing index has length zero, it is treated as being rewritten by another process and ignored.

Risks and invariants:
- `choice` is a fixed 2048-byte buffer and long fortune lines may overflow through `strcpy()`.
- Index format is limited to 32-bit offsets.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fortune.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9.h

Shared declarations and data structures for Fossil's 9P service layer.

Key contents:
- `Msg`, representing an in-flight 9P request/reply, connection membership, flush links, and read/write queue state.
- `Con`, representing a 9P connection with negotiated message size, state, auth status, message queues, write queue, and fid hash/list.
- `Fid`, representing a 9P fid with locks, open flags, filesystem/file references, qid, uid/uname, directory buffer, exclusive lock, and auth RPC state.
- Connection flags for none auth, auth bypass, permission bypass, wstat privilege, and IP checking.
- Connection state enum and fid/open flag enums.
- Prototypes for Fossil 9P modules, CLI, console, user/group lookup, listener/server setup, and logging.

Important relationships:
- `Fid` ties protocol identity to Fossil `Fsys` and `File` references.
- `Con` owns fid lookup and message/write queues; individual modules use its locks.
- `rFcall` dispatch table is defined in `9p.c`.

Risks and invariants:
- Many structures are shared across concurrent Fossil threads and require disciplined locking.
- Incomplete types keep module internals hidden while still allowing pointers in shared structs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9auth.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9auth.c

Implements Fossil's 9P authentication helpers around Plan 9 factotum RPC.

Key behavior:
- `authRead()` drives `auth_rpc(..., "read", ...)`, copies challenge data to clients, and on `ARdone` extracts `AuthInfo`, records `cuname`, and maps it to a uid.
- `authWrite()` feeds client auth data into the auth RPC.
- `authCheck()` validates attach authentication, including `NOFID` attach policy, auth fid matching, completion of auth protocol, uid mapping, and connection `aok` state.

Important implementation details:
- Console connections can attach without normal auth.
- `ConNoneAllow` and already-authenticated connections allow attaching as `none`.
- Auth fid must be `QTAUTH`, have matching `uname`, and target the same `Fsys`.
- Once an auth fid completes, the attach fid's `uname` is replaced with the authenticated `cuname`.

Risks and invariants:
- `authCheck()` uses `afid->alock` rather than a fid write lock because protocol progress can be required.
- Unknown users cause attach failure even after successful cryptographic authentication.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9dir.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9dir.c

Converts Fossil directory entries to 9P stat records and streams directory reads.

Key behavior:
- Allocates `DirBuf` around a `DirEntryEnum` for one-entry buffering.
- `dirDe2M()` converts Fossil `DirEntry` metadata into Plan 9 `Dir`, mapping Fossil mode bits to qid and mode flags.
- UID/GID/MUID strings are resolved through `unameByUid()`, with `(<uid>)` fallback formatting.
- `dirRead()` handles offset-zero rewind and then fills output with packed directory entries until full.

Important implementation details:
- A pending directory entry is retained if the caller's buffer is too small for `convD2M()`.
- Directory offsets are mostly ignored except for rewind.

Risks and invariants:
- `dirBufAlloc()` can fail if the directory was removed underneath the fid.
- `dirDe2M()` allocates fallback names and frees them after packing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9excl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9excl.c

Implements in-memory timed exclusive-open tracking for Fossil 9P fids.

Key behavior:
- `exclAlloc()` checks for an existing exclusive lock on `(Fsys, qid.path)` and rejects it unless expired.
- New exclusive locks live for five minutes and are attached to the opening fid.
- `exclUpdate()` extends an active lock and detects broken or expired locks.
- `exclFree()` removes and frees a fid's exclusive lock.
- `exclInit()` initializes the global lock.

Important implementation details:
- Expired lock records are marked by clearing `fsys`, then a new lock is allocated.
- Locks are process-local and stored in a global doubly-linked list.

Risks and invariants:
- Timed exclusivity depends on clients continuing I/O to refresh the lock.
- This is not a persistent on-disk lock mechanism.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9excl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9fid.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9fid.c

Manages Fossil 9P fid allocation, lookup, locking, reference counts, and cleanup.

Key behavior:
- Maintains a small free list of `Fid` objects and global counters.
- `fidGet()` looks up existing fids or creates new ones for `FidFCreate`, hashes them into the connection, and locks them for read or write.
- `fidPut()` decrements references and unlocks or frees invalidated fids.
- `fidClunk()` removes a fid from connection hash/list and frees it when references drop to zero.
- `fidClunkAll()` clunks every fid on a connection, used during version reset.

Important implementation details:
- `fidLock()` also takes the filesystem epoch read lock for established fids, preventing epoch changes during file operations.
- `FidOCreate` temporarily prevents accidental access during creation before the fid lock is acquired.
- `fidFree()` releases `File`, `DirBuf`, exclusive lock, auth RPC, `Fsys`, uid/uname/cuname, and locks.

Risks and invariants:
- `fidUnHash()` asserts refcount zero, so clunk paths require careful sequencing.
- Epoch lock pairing is embedded in fid lock/unlock, which makes all callers depend on this convention.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9fid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9fsys.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9fsys.c

Implements Fossil's named filesystem registry and a large console command surface for configuring, opening, inspecting, repairing, and controlling filesystems.

Key behavior:
- Maintains global `Fsys` list with name, device, Venti host, open `Fs`, Venti session, refcount, and policy flags.
- Provides `fsysGet()`, `fsysPut()`, `fsysGetRoot()`, permission policy accessors, and filesystem epoch lock wrappers used by 9P code.
- Parses and prints Fossil mode strings.
- CLI commands cover config/open/unconfig/venti/close, sync/halt/unhalt, snapshots, snapshot timing and cleanup, vac, df, remove, clri, create, stat, wstat, check, epoch, low-level block and label edits, block freeing, and clearing entries/pointers.
- `fsysOpen()` dials Venti unless disabled, computes cache size, opens the disk with `fsOpen()`, records noauth/noperm/wstat/noatime flags, and reloads users for main.
- `fsysCheck()` wires `Fsck` callbacks for optional repair operations and halts/unhalts around checking.
- `fsysInit()` installs formatters and registers CLI commands.

Important implementation details:
- `ventihost()`, `myDial()`, and `myRedial()` centralize Venti address handling and logging.
- `fsysXXX()` dispatches commands either to a named filesystem, `all`, or the current console filesystem.
- Low-level commands operate under `fs->elk` and use cache/block label primitives directly.
- `freemem()` can size cache based on Plan 9 `#c/swap` when `mempcnt` is configured.

Risks and invariants:
- `fsysClose()` is explicitly disabled and tells operators to halt and kill Fossil instead.
- Several commands can directly mutate on-disk labels/blocks, so they are operator repair tools, not safe user APIs.
- `fsysConfig()` appears to look up an existing filesystem using `part` rather than `name`, which is worth checking before modification.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9fsys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9lstn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9lstn.c

Implements Fossil's console `listen` command and network listener lifecycle.

Key behavior:
- Tracks active listeners by address in a global doubly-linked list.
- `lstnAlloc()` announces an address, records listener state, and starts a `lstnListen` thread.
- `lstnListen()` accepts incoming connections and passes accepted fds to `conAlloc()`.
- `cmdLstn()` lists listeners, adds a listener, or disables one with `-d`.
- Supports listener flags `-I` for IP checking and `-N` to allow unauthenticated none attaches.

Important implementation details:
- Closing a listener's announce fd causes the listener loop to fail and free the listener.
- The listener thread name is set to `listen`.

Risks and invariants:
- Duplicate address listen attempts are rejected.
- Accept failures are logged but do not immediately stop the listener loop.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9lstn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9p.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9p.c

Implements Fossil's 9P request handlers and dispatch table.

Key behavior:
- Enforces read/write/execute permissions with owner, group, other, `none`, noworld, and no-permission-check policy handling.
- Validates filenames against empty, `.`, `..`, and control characters.
- `rTwstat()` implements detailed Plan 9 wstat semantics for mode, qid consistency, mtime, length, uid, gid, name, and permission checks.
- `rTstat()` packs normal file stats or synthetic auth-file stats.
- `rTread()` and `rTwrite()` handle normal files, directories, and auth fids.
- `rTopen()` and `rTcreate()` validate modes, read-only state, permissions, exclusive locks, truncation, append semantics, and qid/iounit replies.
- `rTwalk()` implements clone and multi-element walk semantics with partial-walk success handling.
- `rTremove()` and `rTclunk()` share clunk/remove handling, including `ORCLOSE`.
- `rTattach()` parses `aname` into filesystem and subpath, enforces IP/auth policy, and attaches to a root file.
- `rTauth()` starts factotum p9any server auth and returns a `QTAUTH` fid.
- `rTversion()` resets connection fids, negotiates message size/version, and supports `9PEoF` moribund shutdown.

Important implementation details:
- `parseAname()` defaults to `main/active`.
- `conIPCheck()` checks remote addresses via `/mnt/ipok/ok`, mounting `/srv/ipok` if needed.
- Directory reads use `dirRead()` from `9dir.c`; auth reads/writes use `9auth.c`.
- Exclusive locks are refreshed on read/write.

Risks and invariants:
- Many handlers rely on `fidGet()` to hold both fid locks and filesystem epoch locks.
- `rTwstat()` is intentionally strict and rejects attempts to change immutable stat fields.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9p.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9ping.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9ping.c

Microbenchmark utility for repeated small reads or writes against a file descriptor or file.

Key behavior:
- Parses `-n count`, `-s size` with optional `k`, `m`, or `g` suffix, `-r`, and `-w`.
- Opens an optional target file or uses fd 0.
- Repeats `pread()` or `pwrite()` at offset zero `n` times and records elapsed microseconds between operations.
- Prints average, min, max, and standard deviation.

Important implementation details:
- Size is restricted to 1 through 1 MiB.
- Timing uses `nsec()` and converts to microseconds.

Risks and invariants:
- Does not initialize write buffer contents.
- The benchmark repeatedly uses offset zero, so it measures latency/cache behavior rather than sequential throughput.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/9ping.c -->