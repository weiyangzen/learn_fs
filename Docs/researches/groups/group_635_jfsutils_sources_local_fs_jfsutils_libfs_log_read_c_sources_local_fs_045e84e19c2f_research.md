# Group Research: group_635_jfsutils_sources_local_fs_jfsutils_libfs_log_read_c_sources_local_fs_045e84e19c2f

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/log_read.c -->
# File Research: sources/local-fs/jfsutils/libfs/log_read.c

This file implements low-level JFS journal page reading for log replay. It owns the 4-page journal buffer cache state (`nextrep`, `logptr[]`, `logp[]`) and exports helpers used by `logredo.c` to find the logical end of the circular log and read records backward.

Main functions:
- `findEndOfLog()` binary-searches log pages 2 through `Log.size - 1` for the highest page sequence/eor pair, handles wrapped page numbers, and backs off from partial long records whose chosen page has only the log page header.
- `pageVal()` loads a page and normalizes it through `setLogpage()`.
- `getLogpage()` returns a cached log page or reads it from `Log.fp`, using `Log.xaddr` only for inline logs.
- `setLogpage()` reconciles mismatched page header/trailer values after interrupted writes, choosing the older/smaller page/eor state, and writes the corrected page back.
- `logRead()` reads one log record descriptor plus optional data from a backward log address, validates record length against a two-page buffer, swaps the descriptor, and returns the address of the previous record.
- `moveWords()` copies 32-bit words backward across log page boundaries, wrapping from page 2 back to the last data page.

Integration points:
- Depends on `Log` and `vopen[]` from `logredo.c`, log layout from `jfs_logmgr.h`, endian helpers, disk I/O through `ujfs_rw_diskblocks()`, and message logging via `fsck_send_msg()`.
- Error paths return `JLOG_*`, `READLOGERROR`, or logredo negative codes from `logredo.h`.

Important invariants:
- Log page 0 is unused and page 1 is the log superblock; replay data starts at page 2.
- `lognumread > Log.size - 2` is treated as log wrap/corruption.
- `ld->aggregate > MAX_ACTIVE` is normalized to 0 for legacy log records that encoded a device number.

Risks and notes:
- `setLogpage()` always writes corrected pages at `Log.xaddr + LOGPNTOB(pno)`, while `getLogpage()` only adds `Log.xaddr` for inline logs. If `setLogpage()` is called for an external log with `Log.xaddr == 0`, this is harmless, but the asymmetry is worth preserving deliberately.
- `moveWords()` updates `*offset` by `4 * nwords` after the second-page copy, where `nwords` is the remaining requested count, not necessarily the number actually copied on the final iteration. This works for the expected record/page constraints but is fragile code.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/log_read.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/log_work.c -->
# File Research: sources/local-fs/jfsutils/libfs/log_work.c

This is the main journal replay work engine. `jfs_logredo()` in `logredo.c` reads records backward; this file decides which committed records matter, applies after-images to pages, rebuilds allocation-state working maps, and installs no-redo filters so older log records cannot overwrite newer recovered state.

Major data structures:
- Commit table: `com[]`, `comhash[]`, `comfree`, tracking committed transaction IDs while replay scans backward.
- Redo page table: `struct doblk`, `blkhash[]`, tracking which portions of each page/extent have already been updated in this replay pass.
- NoRedoFile table: `struct nodofile`, `nodofilehash[]`, suppressing later processing for deleted inodes.
- Extended dtpage list: `struct ExtDtPg`, used to defer freelist rebuilds for directory pages extended during replay.

Main functions:
- `doCommit()` inserts a transaction ID; `findCommit()` tests it; `deleteCommit()` removes it when the transaction start is reached and sets `end_of_transaction`.
- `doAfter()` handles committed `LOG_REDOPAGE` records, skips clean/error volumes and deleted files, calls `updatePage()`, and marks newly allocated dtree/xtree pages in the block map.
- `doNoRedoFile()` installs inode-level no-redo filters.
- `doNoRedoPage()` installs page/tree-root no-redo filters and frees non-root dtree pages in the block map.
- `doNoRedoInoExt()` installs four page filters for a released inode extent, updates the bmap, and clears IAG extent metadata if no newer inode activity was seen.
- `doUpdateMap()` applies committed bmap-only records for PXD/XAD allocation and free operations.
- `dtpg_resetFreeList()` and `dtrt_resetFreeList()` reconstruct directory page/root freelists from slot tables and entry continuation chains.
- `findPageRedo()` looks up or allocates `doblk` records.
- `logredoInit()` initializes commit/hash state, buffer LRU state, no-redo storage, and opens affected volumes.
- `markBmap()` and `markImap()` update persistent maps only where the per-session working maps say the state is not yet determined.
- `saveExtDtPg()` records extended dtree pages for late freelist rebuilding.
- `updatePage()` is the central page after-image applier for inode, btroot xtree/dtree, non-root xtree, non-root dtree, and data records.

Control-flow model:
- Replay is LIFO. The newest log records are processed first, so per-page `doblk` summaries and map `wmap` bits prevent older records from overwriting the final state.
- Redopage data is parsed right-to-left as `<segmentData><offset,length>` segments.
- Inode records update base images, inline data, inline EA, symlink data, inode allocation maps, no-redo filters for zero-link inodes, and bmap state for allocated inode extents.
- Xtree records use low-water marks plus header flags to apply only the newest xad range; `MARKXADNEW` marks newly allocated/extended extents in the bmap and clears transient xad flags.
- Dtree records track 32-byte slots using bit vectors, with special handling for variable-sized non-root dtree pages.
- Directory freelists for extended dtpages are postponed until all older records affecting the previous shorter page form have been processed.

Integration points:
- Uses global `vopen[]`, `bufhdr[]`, `afterdata[]`, `logsup`, and memory fallback state from `logredo.c`.
- Uses `bread()`, `openVol()`, `alloc_storage()`, `dMapGet()`, `iagGet()`, `fsError()`, and `fsck_send_msg()`.
- Depends heavily on JFS on-disk layout headers: dinodes, dtree, xtree, dmap, imap, and log manager structures.

Risks and invariants:
- The correctness invariant is “newest replay decision wins”; `wmap`, `doblk`, NoRedoFile, and NoRedoPage must stay consistent.
- `deleteCommit()` assumes the transaction exists in the hash chain; callers only invoke it after `findCommit()`, which preserves that invariant.
- Allocation fallback can cannibalize bmap workspace; if that happens, logredo may still finish data replay but reports `ENOMEM25` so fsck rebuilds maps.
- Several data format errors intentionally force full fsck or log reformat by returning negative codes.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/log_work.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/logform.c -->
# File Research: sources/local-fs/jfsutils/libfs/logform.c

This file formats a JFS journal for mkfs or logredo recovery. Its single public function, `jfs_logform()`, creates or refreshes inline and external logs.

Behavior:
- Allocates and initializes a `struct logsuper` at log page 1.
- Determines log size from inline log extent parameters or from the external device size, capped at 128 MB.
- Generates a UUID for a new external log or verifies an existing external log UUID.
- Fills log superblock fields: magic, version, `LOGREDONE` state, flags, size, block size, log2 block size, end pointer, UUID, label, and empty active list.
- Writes two initial log pages, including a `LOG_SYNCPT` record, then writes remaining log pages four at a time.
- Initializes log page sequence numbers so `findEndOfLog()` sees a simulated wrap layout after formatting.
- Shows a spinner only when stdout is a terminal, then flushes the device.

Integration points:
- Uses `ujfs_get_dev_size()`, `ujfs_rw_diskblocks()`, `ujfs_flush_dev()`, endian swapping helpers, and UUID functions.
- The exported prototype is declared in `logform.h`.
- Called by mkfs paths and by `recoverExtendFS()` in `logredo.c`.

Risks and notes:
- The external-log UUID verification appears suspicious: after reading the existing log superblock, it prints “Invalid log device” when `uuid_compare(log_sup->uuid, uuid)` returns equality. The comment says it should verify a match, so this condition may be inverted.
- Several early error returns after `calloc()` do not free `log_sup`; this is minor for command-line utilities but visible.
- The assignments to log record type use endian conversion in an unusual direction for constants; on little-endian this is harmless, but big-endian behavior depends on macro definitions and later logpage swapping.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/logform.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/logform.h -->
# File Research: sources/local-fs/jfsutils/libfs/logform.h

This header declares the log formatting API:

- `int jfs_logform(FILE *, int, int, uint, int64_t, int, uuid_t, char *);`

It is protected by `H_LOGFORM` and is included by `logredo.c` for extendfs recovery log reformatting. The parameters correspond to the target device, aggregate block sizing, filesystem flags, inline-log start/length, optional external-log UUID, and optional label.

Note: the closing comment says `H_LORFORM`, a harmless typo.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/logform.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/logredo.c -->
# File Research: sources/local-fs/jfsutils/libfs/logredo.c

This file orchestrates JFS journal replay. It owns global replay state, detects inline versus external logs, validates log and filesystem superblocks, scans the log backward, dispatches record handling to `log_work.c`, flushes recovered pages, updates maps and superblocks, and finalizes the journal.

Major global state:
- `logsup`, `Log`, `vopen[MAX_ACTIVE]`, and `primary_vol`.
- File page buffer cache: `bufhdr[NBUFPOOL]` plus `buffer[]`.
- Log data buffer `afterdata[LOGPSIZE * 2]`.
- Memory fallback state used when bmap workspace allocation fails.
- `use_2ndary_agg_superblock`, `retcode`, and `end_of_transaction`.

Main functions:
- `jfs_logredo()` is the public replay entry point.
- `doMount()` marks a dirty/logredo volume clean when a mount record is reached.
- `openVol()` opens and validates a filesystem associated with a log, checks clean state and log serial, initializes map workspaces, and validates inline-log sizing.
- `updateSuper()` rewrites the filesystem superblock state after replay.
- `rdwrSuper()` reads or writes primary/secondary aggregate superblocks with endian conversion.
- `bflush()` writes modified page-cache buffers to their described PXD extent length.
- `findLog()` classifies the supplied file as a filesystem with inline log, filesystem with external log, or external log device.
- `fsError()` and `logError()` centralize diagnostic messages and mark affected volumes/log state as needing fsck/logredo attention.
- `recoverExtendFS()` repairs crashes during inline-log `extendfs()`, choosing pre-extend or post-extend recovery based on bmap size state.
- `alloc_dmap_bitrec()` and `alloc_storage()` allocate workspace through fsck and optionally reuse bmap storage if normal allocation fails.
- Debug-only helpers provide hex dumps and log descriptor printing.

Replay flow:
1. `findLog()` validates the target and detects whether the log is inline or external.
2. Inline `FM_EXTENDFS` volumes divert into `recoverExtendFS()`.
3. The log superblock is read, swapped, validated, and checked for in-use external logs.
4. Already-redone logs return quickly, updating inline filesystem superblock if needed.
5. `findEndOfLog()` locates the replay start.
6. `logredoInit()` allocates runtime tables and opens affected volumes.
7. Records are read backward with `logRead()` until the sync point target is reached.
8. Record dispatch handles commit, mount, sync point, redopage, noredopage, noredoinoext, and updatemap records.
9. Buffers flush at transaction boundaries and at the end.
10. Extended dtree-page freelists are rebuilt.
11. Allocation maps and superblocks are updated for open volumes.
12. The log active list is cleared and the log superblock is marked `LOGREDONE`.

Integration points:
- `log_read.c` supplies `findEndOfLog()` and `logRead()`.
- `log_work.c` supplies `logredoInit()`, record handlers, and map/page update primitives.
- `logform.c` is used by extendfs recovery.
- `open_by_label.c` is used to locate external logs and active filesystems by UUID.
- `fsck_message.h` supplies detailed diagnostics.

Risks and notes:
- `findLog()` contains a suspicious inline-log test in `openVol()`: `(sb.s_flag & (JFS_INLINELOG == JFS_INLINELOG))` effectively masks with `1`, not `JFS_INLINELOG`; this works only if `JFS_INLINELOG` is bit 0.
- `alloc_storage()` uses `Insuff_memory_for_maps & (available_stg_bytes != 0)` instead of logical `&&`; because the operands are integer flags, it behaves as intended for current values but is brittle.
- External log open handling relies on `O_EXCL` without `O_CREAT`; this is used as an advisory exclusivity signal through `fopen_excl()`, not a POSIX lock.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/logredo.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/logredo.h -->
# File Research: sources/local-fs/jfsutils/libfs/logredo.h

This header defines logredo return codes, replay constants, workspace structures, and public replay APIs.

Contents:
- Error severity notes: positive return codes make fsck continue with full repair; negative return codes also request log reformat.
- Many specific error codes for memory failures, bmap/imap I/O, superblock I/O, journal parsing, bad log versions, invalid log addresses, page update ranges, and unsupported log states.
- Error-type constants used by `fsError()` and `logError()`.
- `PB_READ` and `PB_UPDATE` operation constants.
- `INLINELOG` and `OUTLINELOG` location bits.
- `NBUFPOOL` buffer-cache size.
- `struct dmap_bitmaps`, `struct bmap_wsp`, `struct iag_data`, and `struct imap_wsp`, which hold per-replay working and persistent allocation-map state.
- `struct log_info Log`, describing journal file, serial, location, byte offset, size, block size, UUID, and device number.
- `struct vopen`, the per-active-volume state used across logredo, including open file handle, UUID, superblock-derived geometry, imap workspaces, and bmap workspaces.
- Public prototypes `jfs_logredo()` and `findLog()`.

Integration points:
- Included by `logredo.c`, `log_read.c`, and `log_work.c`.
- Depends on JFS map and inode structures from other headers.

Notes:
- `#define fsimap_iag fsimap_lst.fsimapiag` appears stale or incorrect because `struct fsimap_lst` has no `fsimapiag` member in this header.
- The error-code sign convention is critical for callers: negative means reformat log, positive means run full fsck without necessarily reformatting.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/logredo.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/message.c -->
# File Research: sources/local-fs/jfsutils/libfs/message.c

This file implements `message_user()`, a large switch-based user message printer for OS/2-derived OSO messages and JFS utility/fsck messages.

Behavior:
- Uses `msg_file == OSO_MSG` to choose a small OSO message switch.
- Otherwise prints JFS messages by numeric message ID, including mkfs, fsck, extendfs, defragfs, bad block, mount-state, superblock, map, and recovery diagnostics.
- Formats supplied parameters with `printf()` in the cases that need runtime strings.
- Unknown message numbers are silently ignored.

Integration points:
- Declared in `message.h`.
- Used by user-facing jfsutils command paths separate from `fsck_message.c`, which handles fsck/logredo structured message logging.
- Includes `debug.h` but does not use much beyond shared build context.

Risks and notes:
- `param_cnt` is unused; callers must supply enough `param[]` entries for the selected message number.
- Message IDs are partly symbolic and partly raw numeric literals, reflecting migration from an older message catalog.
- Output is direct stdout/stderr-style `printf()` text, with no localization or catalog lookup in this file.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/message.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/message.h -->
# File Research: sources/local-fs/jfsutils/libfs/message.h

This header declares:

- `message_user(unsigned, char **, unsigned, int);`
- Message-file selectors `OSO_MSG` and `JFS_MSG`.
- Symbolic message IDs for common JFS and OSO messages used by mkfs/fsck/extendfs/defragfs paths.

It does not declare the many raw numeric JFS message IDs handled directly in `message.c`; those remain implicit numeric cases.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/message.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/open_by_label.c -->
# File Research: sources/local-fs/jfsutils/libfs/open_by_label.c

This file locates and opens JFS filesystems or external journal devices by UUID or label. It supports regular block devices, EVMS, md RAID, `/proc/partitions`, and old LVM proc layouts.

Main functions:
- `open_check_label()` opens a candidate device read-only or read/write exclusive according to global `LogOpenMode`, reads either a log superblock or filesystem superblock, and compares UUID or label.
- `walk_dir()` recursively scans a directory tree for block devices, skipping `.`, `..`, and `.nodes`.
- `open_by_label()` tries `/proc/evms/volumes`, `/dev/evms`, `/proc/mdstat`, `/proc/partitions`, and `/proc/lvm/VGs/*/LVs` in that order, returning the first matching opened `FILE *`.

Integration points:
- `logredo.c` uses this to find external journals and active filesystems listed in a journal.
- `LogOpenMode` defaults to `O_RDWR | O_EXCL`, but logdump can set it to `O_RDONLY`.
- Uses `fopen_excl()` from `utilsubs.h`, superblock/logsuper endian swapping, and UUID comparisons.

Risks and notes:
- Several path buffers are fixed at 100 bytes and populated with `strcpy()`, `strcat()`, and `sprintf()`; deep or long device paths can overflow them.
- `uuid_t` is reused as a byte buffer for labels when `is_label` is true, with 16-byte `strncmp()` comparisons.
- The proc paths target older Linux storage stacks; modern systems may not expose EVMS or old LVM proc directories.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/open_by_label.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/super.c -->
# File Research: sources/local-fs/jfsutils/libfs/super.c

This file provides shared superblock and log-superblock validation and I/O helpers.

Main functions:
- `inrange()` tests whether `num` is one of the power-of-two multiples from `low` through `high`.
- `validate_sizes()` currently validates that allocation group size is at least one dmap (`1 << L2BPERDMAP`).
- `ujfs_validate_super()` checks JFS magic, supported version, and size validity.
- `ujfs_put_superblk()` writes primary or secondary aggregate superblock space, zero-padding the full `SIZE_OF_SUPER` region and endian-swapping before disk I/O.
- `ujfs_get_superblk()` reads primary or secondary aggregate superblock and endian-swaps into host order.
- `ujfs_validate_logsuper()` checks log magic and exact log version.
- `ujfs_put_logsuper()` writes the log superblock at log page 1.
- `ujfs_get_logsuper()` reads the log superblock from log page 1.

Integration points:
- Used by mkfs/fsck/log utilities needing common superblock access.
- Disk I/O is through `ujfs_rw_diskblocks()`.
- Error returns use `LIBFS_*` constants from `libjufs.h`.

Notes:
- `ujfs_get_superblk()` swaps the buffer before checking `rc`; if the read failed, it swaps untrusted local contents before returning the error.
- Logsuper helpers operate at `LOGPSIZE`, matching log page 1 for external log devices.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/super.h -->
# File Research: sources/local-fs/jfsutils/libfs/super.h

This header declares the shared superblock/logsuper helpers from `super.c`:

- `ujfs_validate_logsuper()`
- `ujfs_validate_super()`
- `ujfs_put_superblk()`
- `ujfs_get_superblk()`
- `ujfs_put_logsuper()`
- `ujfs_get_logsuper()`
- `inrange()`

It forward-declares `struct superblock` and `struct logsuper`, includes `utilsubs.h` for common types/includes, and uses guard `H_SUPER`.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/super.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/unicode_to_utf8.c -->
# File Research: sources/local-fs/jfsutils/libfs/unicode_to_utf8.c

This file implements UTF-8 and 16-bit Unicode conversion helpers derived from old Linux `fs/nls.c`.

Main functions:
- `Unicode_Character_to_UTF8_Character()` encodes one `uint16_t` code unit into UTF-8 using a table that supports up to 6-byte historical UTF-8 forms.
- `Unicode_String_to_UTF8_String()` encodes a NUL-terminated `uint16_t` string into a UTF-8 byte buffer up to `maxlen`, skipping characters that cannot fit.
- `UTF8_Character_To_Unicode_Character()` decodes one UTF-8 sequence into one `uint16_t`, rejecting invalid continuation bytes and overlong forms.
- `UTF8_String_To_Unicode_String()` decodes a NUL-terminated UTF-8 byte string into a `uint16_t` buffer.

Integration points:
- Declared in `unicode_to_utf8.h`.
- Uses jfsutils integer typedefs from `jfs_types.h`.

Risks and notes:
- The implementation is old UTF-8 and permits 4- to 6-byte sequences even though the output is only `uint16_t`; values above `0xffff` truncate when stored.
- `UTF8_String_To_Unicode_String()` advances `op += size` after decoding one Unicode character, where `size` is bytes consumed, not UTF-16 code units produced. Multi-byte input therefore leaves gaps in the output count/buffer.
- The string conversion routines do not append a terminating NUL to the destination.
- There is no separate output-buffer length for UTF-8 to Unicode conversion.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/unicode_to_utf8.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/unicode_to_utf8.h -->
# File Research: sources/local-fs/jfsutils/libfs/unicode_to_utf8.h

This header declares the four UTF-8/Unicode conversion helpers:

- `Unicode_Character_to_UTF8_Character()`
- `Unicode_String_to_UTF8_String()`
- `UTF8_String_To_Unicode_String()`
- `UTF8_Character_To_Unicode_Character()`

It includes `jfs_types.h` for `uint8_t` and `uint16_t` and uses guard `_UNICODE_TO_UTF8_H`.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/unicode_to_utf8.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/uniupr.c -->
# File Research: sources/local-fs/jfsutils/libfs/uniupr.c

This file contains Unicode uppercase mapping tables for JFS Unicode name handling.

Contents:
- `UniUpperTable[512]` maps the first 512 code points by signed deltas.
- Static range tables cover Greek, Cyrillic, extended Cyrillic, extended Latin/Greek, and wide Latin.
- `UniUpperRange[]` ties range starts/ends to the relevant signed-delta table and terminates with `{0, 0, 0}`.

Integration points:
- Includes `jfs_unicode.h`, which defines `struct UNICASERANGE` and likely consumes `UniUpperTable`/`UniUpperRange`.
- No functions are defined here; it is table data for case-insensitive Unicode comparisons or normalization elsewhere in libfs/fsck.

Notes:
- The mappings are static and limited to the Unicode-era table embedded in this source.
- Signed deltas encode uppercase conversion compactly; zero means no mapping.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/uniupr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/utilsubs.c -->
# File Research: sources/local-fs/jfsutils/libfs/utilsubs.c

This file provides small shared utility functions.

Functions:
- `log2shift(uint32_t n)` returns the base-2 shift for powers of two, or `-1` if `n` is not a power of two.
- `prompt(char *str)` prints a prompt, reads up to 80 bytes from stdin, and returns the first input character.
- `more()` prints a pager-style prompt and returns 1 only when the user enters `x`; otherwise it returns 0 to continue.

Integration points:
- Declared in `utilsubs.h`.
- Used across command-line jfsutils code for sizing and simple interactive prompts.

Risks and notes:
- `prompt()` and `more()` do not handle `fgets()` returning `NULL`; they may return stale/uninitialized stack data on EOF or read error.
- `log2shift(0)` returns 0 because the loop does not execute, even though zero is not a power of two.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/utilsubs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/libfs/utilsubs.h -->
# File Research: sources/local-fs/jfsutils/libfs/utilsubs.h

This header declares small utility APIs and defines `fopen_excl()` inline.

Contents:
- Prototypes for `log2shift()`, `prompt()`, and `more()`.
- `static inline FILE *fopen_excl(const char *path, const char *mode)`, which opens `path` with `O_RDWR | O_EXCL` and wraps the descriptor in `fdopen()`.
- Prototypes for mount/type helpers `Is_Device_Mounted()` and `Is_Device_Type_JFS()` implemented elsewhere.

Notes:
- `fopen_excl()` ignores the requested open mode for the `open()` call and always opens read/write.
- `O_EXCL` without `O_CREAT` is not a portable locking primitive; behavior depends on platform/device semantics.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/libfs/utilsubs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/logdump/Makefile -->
# File Research: sources/local-fs/jfsutils/logdump/Makefile

This is a generated Automake 1.11.1 Makefile for building and installing the `jfs_logdump` utility.

Build configuration:
- Package version is `jfsutils 1.1.15`.
- Builds `sbin_PROGRAMS = jfs_logdump$(EXEEXT)`.
- Sources are `logdump.c` and `helpers.c`.
- Includes `-I$(top_srcdir)/include -I$(top_srcdir)/libfs`.
- Links with `../libfs/libfs.a -luuid`.
- Installs the program under `$(sbindir)` and man page `jfs_logdump.8` under `$(mandir)/man8`.
- Uses `AM_CFLAGS = -Wall -Wstrict-prototypes -fno-strict-aliasing`.

Targets and generated behavior:
- Standard Automake targets for `all`, `install`, `uninstall`, `clean`, `distclean`, `maintainer-clean`, `tags`, `ctags`, `distdir`, and man-page installation.
- Dependency tracking includes `.deps/helpers.Po` and `.deps/logdump.Po`.
- Rebuild hooks invoke `automake --gnu logdump/Makefile` through top-level configure machinery.
- `distdir` includes checks for placeholder man pages generated by missing `help2man`.

Integration points:
- The generated file is derived from `logdump/Makefile.am`.
- It depends on the local static libfs archive, so logdump can reuse journal/superblock/device helpers.

Notes:
- Absolute build paths such as `/data2/jfsutils-1.1.15` are embedded by configure generation.
- As a generated file, source-of-truth edits should normally be made in `Makefile.am` and regenerated.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/logdump/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/jfsutils/logdump/Makefile.am -->
# File Research: sources/local-fs/jfsutils/logdump/Makefile.am

This is the Automake source for the logdump utility build.

Contents:
- Adds include paths for top-level `include` and `libfs`.
- Links `jfs_logdump` with `../libfs/libfs.a -luuid`.
- Installs `jfs_logdump` as an sbin program.
- Distributes/installs `jfs_logdump.8`.
- Builds from `logdump.c` and `helpers.c`.

This file is the maintainable source for the generated `logdump/Makefile`.
<!-- END FILE RESEARCH: sources/local-fs/jfsutils/logdump/Makefile.am -->