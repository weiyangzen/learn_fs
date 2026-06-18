# Group Research: group_1872_xfsprogs_sources_local_fs_xfsprogs_db_rdump_c_sources_local_fs_xfsp_7854f796540e

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/local-fs/xfsprogs`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/rdump.c -->
# File Research: sources/local-fs/xfsprogs/db/rdump.c

Implements the `xfs_db` `rdump` command, which recovers files from an XFS filesystem image into a host directory.

Key responsibilities:
- Registers `rdump [-s] [paths...] dest_directory`.
- Walks the XFS namespace with `path_walk`, `listdir`, `libxfs_iget`, and a recursive path buffer.
- Recreates directories, regular files, symlinks, and special files in the destination tree.
- Copies file data by reading written extents directly from the data or realtime device.
- Preserves mode, owner, timestamps, XFS file attributes, project IDs, extent-size hints, CoW extent-size hints, xflags, and extended attributes where possible.
- Translates ondisk xattr namespaces to Linux xattr namespaces and skips parent-pointer attrs.
- Tracks degraded metadata restoration with `lost_mask` and reports aggregate warnings at the end.

Important behavior:
- `-s` enables strict mode: many metadata/data-copy failures become fatal instead of warnings.
- Dumping a single directory copies its children directly into the destination directory.
- Directory recursion ignores `.` and `..` and enforces `PATH_MAX`/`FILENAME_MAX`.
- Sparse/unwritten extents are skipped and final size is restored with `ftruncate`.
- Remote xattr values are fetched with `libxfs_attr_rmtval_get`.
- Symlink attributes/timestamps use `AT_SYMLINK_NOFOLLOW`.
- ACL xattrs copied to non-XFS targets are warned as likely untranslatable.

Dependencies:
- Relies on `libxfs` inode, bmap, symlink, attr, transaction, and buffer APIs.
- Uses `listxattr.h` xattr walking and `libfrog/file_attr.h` for path-based file attribute setting.
- Uses global `mp`, `iocur_top`, `exitcode`, `strict_errors`, and `lost_mask`.

Notable risks:
- Recovery is best-effort by default, so non-strict runs can silently produce incomplete data while only printing warnings.
- The xattr error check after `fsetxattr` compares `ret` to `EOPNOTSUPP` instead of checking `errno`; that can miss the intended lost-xattr classification.
- File contents are copied from raw written extents and do not reconstruct holes beyond final truncation.
- Host filesystem support and process privileges strongly affect fidelity of ownership, flags, ACLs, xattrs, devices, and symlink metadata.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/rdump.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/rtgroup.c -->
# File Research: sources/local-fs/xfsprogs/db/rtgroup.c

Defines `xfs_db` support for realtime group metadata types.

Key responsibilities:
- Registers the `rtsb` command when the mounted filesystem has realtime groups.
- Defines field tables for realtime superblock (`rtsb`), realtime group bitmap (`rgbitmap`), and realtime group summary (`rgsummary`) structures.
- Provides size/count helpers for displaying realtime metadata blocks.
- Seeks to the realtime superblock at `XFS_RTSB_DADDR` via `set_rt_cur`.

Important behavior:
- `rtsb_init` only exposes the command for filesystems with realtime groups.
- `rtwords_count` subtracts the `xfs_rtbuf_blkinfo` header for rtgroup-enabled filesystems before counting bitmap/summary words.
- `rtsb_size` reports the current filesystem block size in bits.

Dependencies:
- Uses `type`, `field`, `io`, `sb`, and realtime buffer type definitions.
- Depends on `xfs_has_rtgroups`, `set_rt_cur`, `mp`, and `typtab`.

Notable risks:
- The field layouts must match ondisk realtime group structures exactly.
- `rtsb_f` assumes `TYP_RTSB` is registered in the active type table.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/rtgroup.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/rtgroup.h -->
# File Research: sources/local-fs/xfsprogs/db/rtgroup.h

Header for `xfs_db` realtime group display support.

Key responsibilities:
- Declares field tables for realtime superblock, realtime group bitmap, and realtime group summary objects.
- Declares `rtsb_init` and `rtsb_size`.

Dependencies:
- Consumed by `rtgroup.c` and the type registry in `type.c`.

Notable risks:
- Any enum/type-table changes for realtime metadata must keep these declarations and `type.c` synchronized.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/rtgroup.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/sb.c -->
# File Research: sources/local-fs/xfsprogs/db/sb.c

Implements `xfs_db` superblock field decoding and the `sb`, `uuid`, `label`, and `version` commands.

Key responsibilities:
- Registers commands for selecting allocation-group superblocks, reading/writing filesystem UUIDs, reading/writing labels, and displaying/updating selected version bits.
- Defines the superblock field table, including conditional metadata-directory and realtime-group fields.
- Reads and validates superblocks with magic/version/in-progress checks.
- Checks log cleanliness before UUID-changing operations and clears the log with the new UUID.
- Updates all AG superblocks, and realtime superblock label/UUID when present.
- Handles metauuid feature transitions when changing/restoring UUIDs on CRC filesystems.
- Prints feature names from the mounted superblock state.

Important behavior:
- Mutating commands require non-readonly expert mode.
- UUID writes refuse filesystems needing repair and require a clean log.
- `uuid rewrite`, `uuid restore`, `uuid nil`, explicit UUIDs, and generated UUIDs are supported.
- Label writes truncate to `XFSLABEL_MAX`, and `--`, `""`, or `''` mean empty label.
- `version` supports legacy feature enabling for `extflg`, `log2`, `attr1`, `attr2`, and `projid32bit`; V5 mutation is mostly blocked.
- Printing UUID/label checks all AG backup superblocks and warns on mismatch.

Dependencies:
- Uses libxfs superblock conversion, version helpers, log recovery/clear helpers, realtime superblock helpers, and global debugger state.
- Depends on `mp`, `x`, `iocur_top`, `typtab`, `expert_mode`, and `exitcode`.

Notable risks:
- These commands intentionally mutate filesystem identity and feature fields; misuse can make a filesystem inconsistent.
- `get_sb` has early returns after `push_cur`; several error paths do not `pop_cur`, relying on command process behavior rather than strict local cleanup.
- `version_f` explicitly documents incomplete V5 feature support.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/sb.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/sb.h -->
# File Research: sources/local-fs/xfsprogs/db/sb.h

Header for `xfs_db` superblock command and field support.

Key responsibilities:
- Declares superblock field tables.
- Declares `sb_init`, `sb_logcheck`, and `sb_size`.

Dependencies:
- Used by command initialization, field display, and log-safety paths.

Notable risks:
- Public declarations are small but central to `uuid` and label mutation safety.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/sb.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/sig.c -->
# File Research: sources/local-fs/xfsprogs/db/sig.c

Small SIGINT handling layer for `xfs_db`.

Key responsibilities:
- Installs a SIGINT handler in `init_sig`.
- Tracks interruption state in `gotintr`.
- Provides helpers to block/unblock SIGINT, clear the flag, and query whether SIGINT was seen.

Important behavior:
- Uses `sigaction` with `sa_sigaction` but does not set `SA_SIGINFO`.
- `blockint`/`unblockint` manipulate a process signal mask containing only SIGINT.

Dependencies:
- Uses libc signal APIs and `libxfs.h`.

Notable risks:
- `gotintr` is a plain `int`, not `volatile sig_atomic_t`; signal-handler correctness is minimal.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/sig.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/sig.h -->
# File Research: sources/local-fs/xfsprogs/db/sig.h

Header for `xfs_db` SIGINT helpers.

Key responsibilities:
- Declares `blockint`, `clearint`, `init_sig`, `seenint`, and `unblockint`.

Dependencies:
- Used by command loops or long-running operations needing interrupt polling.

Notable risks:
- Exposes only global interrupt state, with no per-operation context.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/sig.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/strvec.c -->
# File Research: sources/local-fs/xfsprogs/db/strvec.c

Implements NULL-terminated string vector helpers.

Key responsibilities:
- Allocates new vectors with space for a trailing NULL.
- Adds duplicated strings, copies vectors, frees vectors, and prints vector contents.
- Uses xfsprogs allocation wrappers and `dbprintf`.

Important behavior:
- `add_strvec` reallocates the vector to append one duplicated string.
- `copy_strvec` duplicates every source entry.
- `print_strvec` emits entries without separators.

Dependencies:
- Uses `xmalloc`, `xrealloc`, `xstrdup`, `xfree`, and `dbprintf`.

Notable risks:
- Functions assume input vectors are non-NULL and properly NULL-terminated.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/strvec.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/strvec.h -->
# File Research: sources/local-fs/xfsprogs/db/strvec.h

Header for NULL-terminated string vector utilities.

Key responsibilities:
- Declares allocation, append, copy, free, and print helpers.

Dependencies:
- Used by command parsing or output code needing string-vector ownership helpers.

Notable risks:
- API does not encode vector length, so callers must maintain NULL termination.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/strvec.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/symlink.c -->
# File Research: sources/local-fs/xfsprogs/db/symlink.c

Defines field decoding for CRC-enabled remote symlink blocks.

Key responsibilities:
- Computes symlink block display size and target-data count.
- Defines the `symlink_crc` header field table: magic, offset, bytes, crc, uuid, owner, block number, lsn, and data.
- Validates symlink magic before reporting size/count.

Important behavior:
- `symlink_count` bounds displayed data to the filesystem block size if `sl_bytes` is too large.
- `symlink_size` returns header plus target byte count only for valid symlink magic.

Dependencies:
- Uses `xfs_dsymlink_hdr`, global `mp`, field/type helpers, and CRC field types.

Notable risks:
- Comment notes no support for multiple contiguous block symlinks in this display path.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/symlink.h -->
# File Research: sources/local-fs/xfsprogs/db/symlink.h

Header for CRC symlink block field support.

Key responsibilities:
- Declares symlink CRC field/header tables and `symlink_size`.

Dependencies:
- Used by `type.c` and symlink field-printing paths.

Notable risks:
- Must remain aligned with ondisk remote symlink header layout.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/symlink.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/text.c -->
# File Research: sources/local-fs/xfsprogs/db/text.c

Implements raw text/hex display for current `xfs_db` buffers.

Key responsibilities:
- `print_text` dumps the current IO buffer.
- Formats offsets, hex bytes, and printable alphanumeric characters in 16-byte rows.
- Replaces non-alphanumeric bytes with `.`.

Dependencies:
- Uses `iocur_top`, `dbprintf`, and libc `isalnum`.

Notable risks:
- The ASCII side only shows `isalnum` characters, so punctuation and whitespace are hidden even if printable.
- `dbprintf(".", *s)` passes an unused argument, harmless but imprecise.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/text.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/text.h -->
# File Research: sources/local-fs/xfsprogs/db/text.h

Header for text display support.

Key responsibilities:
- Declares `print_text`.

Dependencies:
- Used by the type registry for `text`, realtime bitmap, and summary display modes.

Notable risks:
- Minimal API depends on global current-buffer state.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/text.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/timelimit.c -->
# File Research: sources/local-fs/xfsprogs/db/timelimit.c

Implements the `xfs_db` `timelimit` command.

Key responsibilities:
- Prints supported inode timestamp, quota timer, and quota grace-period limits.
- Supports classic and bigtime limits.
- Supports raw, pretty `ctime`, and compact single-line output.
- Auto-selects classic vs bigtime based on filesystem feature flags.

Important behavior:
- Grace periods are always printed as integer values, even in pretty mode.
- `--classic`, `--bigtime`, `--pretty`, and `--compact` are parsed manually.

Dependencies:
- Uses XFS time conversion constants/helpers and `xfs_has_bigtime(mp)`.

Notable risks:
- Output label for grace maximum is `dqgrace.min` instead of `dqgrace.max`, likely a typo in `show_limits`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/timelimit.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/type.c -->
# File Research: sources/local-fs/xfsprogs/db/type.c

Maintains the `xfs_db` data type registry and dispatches read/write/fuzz operations by type.

Key responsibilities:
- Registers the `type` command.
- Defines three type tables: non-CRC, CRC, and sparse-inode CRC variants.
- Maps type names to handlers, field tables, buffer ops, CRC offsets, and optional CRC setter callbacks.
- Switches current object type via `set_iocur_type`.
- Provides generic handlers for structured objects, strings, data blocks, and text.

Important behavior:
- CRC tables expose newer types such as rmapbt, refcountbt, realtime rmap/refcount, rtgroup bitmap, and rtgroup summary.
- `handle_struct` supports read, write, and fuzz.
- Text objects are read-only; block/string fuzzing is explicitly unsupported here.
- `type` with no argument prints the current type and supported type names.

Dependencies:
- Pulls together field tables and buffer ops from most `db` metadata modules and libxfs verifier definitions.
- Uses global `cur_typ`, `typtab`, and `iocur_top`.

Notable risks:
- Type enum ordering is asserted against table positions; any enum/table mismatch breaks dispatch.
- Type availability differs across active table variants, so callers must choose the correct table for filesystem features.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/type.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/type.h -->
# File Research: sources/local-fs/xfsprogs/db/type.h

Core type-system header for `xfs_db`.

Key responsibilities:
- Defines `typnm_t` enum values for all recognized object types.
- Defines action constants `DB_READ`, `DB_WRITE`, and `DB_FUZZ`.
- Defines `typ_t`, including type name, action dispatcher, field table, buffer ops, CRC offset policy, and CRC setter.
- Declares type registry globals and handler functions.

Dependencies:
- Shared by type registry, print/write/fuzz paths, and field modules.

Notable risks:
- Enum order is a contract with `type.c` tables.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/type.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/write.c -->
# File Research: sources/local-fs/xfsprogs/db/write.c

Implements expert-mode `xfs_db` write support for structured fields, raw data blocks, and strings.

Key responsibilities:
- Registers `write` only in expert mode.
- Dispatches writes through the current type handler.
- Supports `-c` to write corrupt data with bad CRC and `-d` to write invalid data while recalculating CRC.
- Converts input values from quoted strings, octal escapes, hex blobs, UUID-like hyphenated hex, and numeric literals.
- Writes bitfields with `setbitval`.
- Provides raw block operations: left/right shift, left/right rotate, sequence, random, and fill.
- Writes null-terminated string data for symlink/string mode.

Important behavior:
- Refuses writes when libxfs was opened readonly.
- Temporarily swaps buffer verifier ops to bypass or recalculate CRCs for corrupt/invalid data modes.
- `write_struct` resolves field paths with `flist_scan`/`flist_parse`, computes bit length, writes, persists, and prints the changed field.
- Data mode subcommands accept abbreviated names based on significant-character counts.
- Random fill uses `lrand48`, seeded by `clock()` during initialization.

Dependencies:
- Depends on current IO buffer/type, field metadata, flist parsing, bit manipulation, verifier callbacks, and `write_cur`.

Notable risks:
- Intended for destructive expert use; invalid combinations can corrupt metadata.
- Several block mutators report too-large lengths but continue operating.
- `write_block` checks `cmd->len_arg < argc` when parsing `from`/`to`, which appears to gate those arguments on the wrong command metadata field.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/write.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/write.h -->
# File Research: sources/local-fs/xfsprogs/db/write.h

Header for `xfs_db` write support.

Key responsibilities:
- Declares `write_init`, `write_block`, `write_struct`, and `write_string`.

Dependencies:
- Used by the type registry and command initialization.

Notable risks:
- Exposes write entry points that assume global current-buffer/type state and expert-mode command gating elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/write.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/xfs_admin.sh -->
# File Research: sources/local-fs/xfsprogs/db/xfs_admin.sh

Shell wrapper implementing legacy `xfs_admin` behavior through `xfs_db`, `xfs_io`, and `xfs_repair`.

Key responsibilities:
- Parses admin options for lazycount, extflg, log2, label, feature upgrades, projid32bit, realtime device, UUID, and version.
- Selects online query/update paths with `xfs_io` for mounted filesystems when supported.
- Requires offline access for destructive or upgrade operations.
- Invokes `xfs_db -x` for expert metadata edits and `xfs_repair` for upgrade-style changes.

Important behavior:
- Uses `findmnt` to detect mounted XFS filesystems.
- Supports optional external log device argument.
- `-V` delegates version output to `xfs_db`.

Dependencies:
- External commands: `findmnt`, `xfs_db`, `xfs_io`, `xfs_repair`, and `expr`.

Notable risks:
- Builds command strings and executes them with `eval`; arguments with shell metacharacters rely on quoting discipline.
- `require_online` is defined but not meaningfully set by parsed options in this script.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/xfs_admin.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/xfs_metadump.sh -->
# File Research: sources/local-fs/xfsprogs/db/xfs_metadump.sh

Shell wrapper for running `xfs_db` metadump mode.

Key responsibilities:
- Parses metadump options and translates them into `xfs_db` options plus a `metadump` command.
- Supports source and target operands.
- Delegates `-V` to `xfs_db`.

Important behavior:
- Runs `xfs_db -i -p xfs_metadump -c "metadump... target" source`.
- Passes log/realtime/force/debug-ish options through DB option variables.

Dependencies:
- External `xfs_db`.

Notable risks:
- Option strings are assembled with shell concatenation and unquoted expansions, so unusual filenames/options can be fragile.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/xfs_metadump.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/xfs_ncheck.sh -->
# File Research: sources/local-fs/xfsprogs/db/xfs_ncheck.sh

Shell wrapper for legacy `xfs_ncheck` functionality via `xfs_db`.

Key responsibilities:
- Parses inode filters, summary/verbose options, force, log device, and version.
- Runs `xfs_db` readonly with `blockget -ns` followed by `ncheck`.

Important behavior:
- Requires exactly one filesystem/device operand.
- `-V` delegates version output to `xfs_db`.

Dependencies:
- External `xfs_db`.

Notable risks:
- Includes `b:` in the `getopts` string but has no `b)` case.
- Assembles command strings with unquoted shell expansions.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/xfs_ncheck.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/Makefile -->
# File Research: sources/local-fs/xfsprogs/libxfs/Makefile

Build rules for the static `libxfs.la` userspace library.

Key responsibilities:
- Defines package headers, internal headers, C sources, dummy C/C++ header-compile tests, and extra objects.
- Forces a static libtool build.
- Adds optional compile flags for `memfd_create` and nonblocking `getrandom`.
- Links against pthread, realtime, and libfrog libraries.
- Provides header installation targets for exported XFS headers.
- Generates dependency files, including extra dummy object dependencies.

Important behavior:
- `DEBUG = -DNDEBUG` intentionally avoids linking repair with a debug libxfs.
- Dummy C and C++ files test user-exported header compilability.
- Dependency includes are skipped under `NODEP`.

Dependencies:
- Includes top-level xfsprogs `builddefs` and `BUILDRULES`.
- Source list covers buffer/cache, transactions, allocation, btrees, attrs, dirs, realtime groups, metadir, parent pointers, and staging helpers.

Notable risks:
- Build correctness depends on long source/header lists staying synchronized with libxfs implementation growth.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/buf_mem.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/buf_mem.c

Implements memory-backed `xfs_buftarg` support using xfiles and direct `mmap`.

Key responsibilities:
- Initializes xmbuf page-size block geometry and mmap-count limits.
- Allocates and frees memory-backed buffer targets.
- Maps xfile pages directly into `xfs_buf` objects.
- Integrates with the generic cache via xmbuf cache operations.
- Verifies memory-backed daddrs against xfile size.
- Finalizes ephemeral buffers by punching stale pages or running structure verifiers.
- Detaches memory-backed buffers from transactions without disk writeback.

Important behavior:
- Only system page-size blocks are supported.
- `/proc/sys/vm/max_map_count` is used to cap simultaneous mappings; fallback is 1024.
- When mapping pressure or ENOMEM occurs, `xmbuf_unmap_early` causes buffers to unmap on cache put and remap on get.
- Direct-mapped buffers are marked uptodate and unchecked after mmap.

Dependencies:
- Uses xfile, cache, kmem, libxfs buffer, transaction, verifier, and fallocate/mmap APIs.

Notable risks:
- Caller is expected to provide concurrency management.
- Mapping count handling switches global behavior for all xmbufs once pressure is detected.
- Verifier failures in `xmbuf_finalize` indicate memory/software corruption in ephemeral metadata staging.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/buf_mem.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/buf_mem.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/buf_mem.h

Header for memory-backed libxfs buffer targets.

Key responsibilities:
- Declares xmbuf block size/shift globals and lifecycle functions.
- Provides `xfs_buftarg_is_mem`.
- Declares daddr verification, transaction detach, finalization, and byte-count helpers.

Dependencies:
- Depends on `xfile` and libxfs buffer/transaction types.

Notable risks:
- `xfs_buftarg_is_mem` treats non-NULL `bt_xfile` as the complete discriminator for memory targets.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/buf_mem.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/cache.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/cache.c

Generic pthread-protected hash/MRU cache used by libxfs buffer targets.

Key responsibilities:
- Creates/destroys caches with hash buckets and MRU lists.
- Looks up, allocates, references, dereferences, purges, flushes, and reports cache nodes.
- Enforces maximum cache size with `cache_shake`.
- Parks dirty/unflushable nodes on a special dirty MRU priority.
- Supports optional cache operations for hash, compare, alloc, flush, release, bulk release, get, and put.

Important behavior:
- Cache miss allocation grows the cache if all reclaim priorities fail.
- Nodes are removed from MRU while referenced and reinserted on final put.
- `CACHE_MISCOMPARE_PURGE` can purge stale mismatched entries during lookup.
- Purge mode may reclaim dirty nodes; normal memory-pressure reclaim will not.
- Debug code can abort on refcount/list invariant violations when enabled.

Dependencies:
- Uses libxfs list helpers, pthread mutexes, and caller-provided cache operation callbacks.

Notable risks:
- Locking order spans hash, node, MRU, and global mutexes; misuse by callbacks can deadlock.
- `cache_report` divides by `cache->c_count` in MRU/hash summaries after only checking hit/miss activity.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/defer_item.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/defer_item.c

Userspace deferred-operation item implementation for libxfs.

Key responsibilities:
- Provides defer add/finish/cancel operation types for extent frees, realtime extent frees, AGFL frees, rmap updates, realtime rmap updates, refcount updates, realtime refcount updates, bmap updates, logged attrs, and exchange mappings.
- Sorts deferred items by AG/rtgroup or inode where needed.
- Holds group intent references across deferred transaction rolls.
- Finishes each item by calling the corresponding libxfs operation.
- Requeues partially completed operations with `-EAGAIN`.
- Provides log intent space calculation helpers even though userspace does not log actual intents.

Important behavior:
- Intent/done creation and abort functions are dummies because libxfs tools do not perform kernel logging.
- Realtime and data-section rmap/refcount updates use separate defer operation types to avoid AGF/realtime metadata lock mixing.
- Bmap map intents pre-account delayed blocks and undo that on cancellation.
- Attribute intents initialize per-operation attr state machines and run `xfs_attr_set_iter`.

Dependencies:
- Deeply tied to libxfs allocation, rmap, refcount, bmap, attr, exchange-map, group, rtgroup, and transaction code.

Notable risks:
- Correct cancellation is essential because many items own group references and slab-cache allocations.
- Requeue behavior depends on callee mutation of remaining block counts.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/defer_item.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/defer_item.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/defer_item.h

Header for libxfs deferred operation adapters.

Key responsibilities:
- Declares defer-add entry points for bmap, attr, exchange maps, extent free, rmap, and refcount intents.
- Defines attr defer operation enum.
- Declares log intent space calculation helpers.

Dependencies:
- Used by libxfs transaction and metadata update paths.

Notable risks:
- Interfaces expose kernel-like deferred operation concepts without exposing actual log intent objects.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/defer_item.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/init.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/init.c

Core libxfs initialization, mount setup, buffer-target setup, and teardown.

Key responsibilities:
- Opens data, log, and realtime devices with readonly/direct/exclusive/create semantics.
- Checks mounted/writable device state according to libxfs flags.
- Initializes global runtime support: page shift, ondisk structure checks, xmbuf, RCU, radix tree, directory startup, and slab-like caches.
- Creates data/log/realtime buffer targets and cache objects.
- Supports write-failure injection through `LIBXFS_DEBUG_WRITE_CRASH`.
- Initializes mount geometry, feature flags, btree maxlevels, DA geometry, transaction reservations, per-AG structures, realtime fields, rtgroups, and metadata directory root.
- Performs device size checks unless debugger mode allows continuing.
- Flushes dirty buffers and device write caches, reporting corrupt/lost writes.
- Unmounts and destroys libxfs global resources.

Important behavior:
- Tools can run with fake device numbers for regular files.
- Realtime setup validates incompatibilities such as reflink with realtime extent size > 1.
- Extremely high AG or rtgroup counts are guarded by read probes and can be limited in debugger mode.
- V1 inodes and V1 directories are refused.
- `libxfs_umount` purges the buffer cache before flushing devices and freeing perag/rtgroup state.

Dependencies:
- Uses platform/device helpers, cache, kmem caches, libxfs mount/sb/geometry, transactions, btrees, metadir, realtime, xfile, and buffer APIs.

Notable risks:
- Many paths call `exit(1)` or `abort()` on fatal setup failures.
- Device/mount safety depends on platform mounted/writable detection.
- Teardown order is important because buffers, per-AGs, rtgroups, and metadata inodes reference each other.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/init.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/init.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/init.h

Small initialization header.

Key responsibilities:
- Declares global `use_xfs_buf_lock`.
- Forward-declares `struct stat`.

Dependencies:
- Included by libxfs implementation files that need global buffer-lock mode.

Notable risks:
- Most libxfs init interfaces are declared elsewhere; this header is intentionally narrow.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/init.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/inode.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/inode.c

Userspace inode allocation, loading, flushing, metadata-inode lookup, release, and ownership initialization helpers.

Key responsibilities:
- Creates newly allocated in-core inodes with `libxfs_icreate`.
- Flushes dirty in-core inode state to an inode buffer with verifier and CRC updates.
- Implements a minimal `libxfs_iget` that allocates an inode, maps it, and reads ondisk state unless a new V3 inode can be initialized directly.
- Validates and loads metadata files with expected file mode/metatype.
- Releases inode fork memory and frees in-core inode objects.
- Provides `inode_init_owner` behavior for uid/gid/mode inheritance.

Important behavior:
- New V3 non-ikeep inodes get a random generation without reading disk.
- Local data and attr forks are verified before inode flush.
- Metadata-directory files must be marked as metadir inodes with matching metatype.
- No persistent inode cache lookup is implemented; objects are allocated per `iget`.

Dependencies:
- Uses inode buffer, fork, bmap, transaction, allocation, directory, metadir, and random helpers.

Notable risks:
- Assertions enforce fork extent/nblock invariants before flush.
- Minimal userspace cache means callers must manage inode lifetime carefully.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/ioctl_c_dummy.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/ioctl_c_dummy.c

Dummy C compilation test for exported XFS userspace headers.

Key responsibilities:
- Includes `include/xfs.h`, `include/handle.h`, and `include/jdm.h`.

Dependencies:
- Built as an extra object from the libxfs Makefile.

Notable risks:
- No runtime logic; failure indicates exported header incompatibility with C compilation.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/ioctl_c_dummy.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/ioctl_cxx_dummy.cpp -->
# File Research: sources/local-fs/xfsprogs/libxfs/ioctl_cxx_dummy.cpp

Dummy C++ compilation test for exported XFS userspace headers.

Key responsibilities:
- Includes `include/xfs.h`, `include/handle.h`, and `include/jdm.h` inside `extern "C"`.

Dependencies:
- Built as an extra C++ object from the libxfs Makefile.

Notable risks:
- No runtime logic; failure indicates exported header incompatibility with C++ compilation.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/ioctl_cxx_dummy.cpp -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/iunlink.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/iunlink.c

Userspace helpers for logging/updating XFS per-AG unlinked inode list pointers.

Key responsibilities:
- Updates an inode cluster buffer’s `di_next_unlinked` field safely.
- Verifies the old ondisk pointer before replacement.
- Logs the exact inode buffer byte range modified.
- Reloads the next unlinked inode and sets its in-core previous pointer.

Important behavior:
- Stale inode buffers are not relogged to avoid clearing stale state.
- Updating to the same non-NULL next pointer is treated as corruption.
- `xfs_iunlink_reload_next` verifies the reloaded inode has zero links.

Dependencies:
- Uses libxfs inode mapping/loading, transaction buffer logging, AG/perag state, and tracepoints.

Notable risks:
- This maintains a linked list in metadata; stale old pointers indicate corruption.
- Header-side lookup is stubbed out, so this path does not provide a real inode-cache lookup.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/iunlink.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/iunlink.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/iunlink.h

Header for userspace unlinked-inode list support.

Key responsibilities:
- Provides a stub `xfs_iunlink_lookup` returning NULL.
- Declares `xfs_iunlink_log_inode` and `xfs_iunlink_reload_next`.

Dependencies:
- Used by transaction/unlink handling code.

Notable risks:
- Consumers must not expect kernel-style lookup behavior from `xfs_iunlink_lookup`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/iunlink.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/kmem.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/kmem.c

Userspace implementation of simple kernel-like memory/cache allocation helpers.

Key responsibilities:
- Creates/destroys `kmem_cache` descriptors.
- Allocates and zero-allocates fixed-size cache objects.
- Implements `kvmalloc`, `krealloc`, and `kasprintf`.

Important behavior:
- Allocation failures print an error and exit the process.
- `LIBXFS_LEAK_CHECK` causes `kmem_cache_destroy` to report nonzero outstanding allocations.
- `krealloc(ptr, 0, ...)` explicitly frees and returns NULL to match Linux behavior.

Dependencies:
- Uses libc malloc/calloc/realloc/free/vasprintf and global `progname`.

Notable risks:
- Constructors stored in `kmem_cache` are not invoked in allocation paths.
- Allocation counters are incremented but freeing must occur through matching cache-free code elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/kmem.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/libxfs_api_defs.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/libxfs_api_defs.h

Namespace mapping header for exposing kernel-derived XFS functions through libxfs names.

Key responsibilities:
- Maps many `xfs_*` symbols to `libxfs_*` symbols with preprocessor defines.
- Covers attr, bmap, btree, buffer, directory, quota, inode, metadir, parent pointer, perag, allocation, rmap, refcount, realtime, superblock, symlink, transaction, verifier, and geometry APIs.
- Defines exported attr namespace aliases.

Important behavior:
- Kept separate so internal and external libxfs headers can share mappings without circular dependencies.
- Comment requests the list remain alphabetized, though realtime sections include repeated mappings.

Dependencies:
- Included wherever kernel-style source wants to call libxfs-renamed implementations.

Notable risks:
- Macro aliasing is broad and can obscure which implementation is actually linked.
- Duplicate realtime mappings and ordering drift can make maintenance error-prone.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/libxfs_api_defs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/libxfs_io.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/libxfs_io.h

Userspace libxfs buffer I/O interface definitions.

Key responsibilities:
- Defines `xfs_buftarg`, buffer target flags, write-failure injection, and flush interface.
- Defines `xfs_bufkey`, `xfs_buf_map`, `xfs_buf_ops`, and `xfs_buf`.
- Declares cached, uncached, mapped, read, write, release, lock, priority, delwri, flush, purge, and zeroing buffer APIs.
- Provides inline wrappers for single-map get/read and checksum update/verify helpers.
- Defines buffer flags and daddr conversion helpers.

Important behavior:
- Buffer verifiers carry read/write/structure callbacks.
- `xfs_buftarg_trip_write` can call `platform_crash` after configured writes.
- Memory-backed targets are represented via non-NULL `bt_xfile`.
- `xfs_buf_hold` increments the cache node refcount directly.

Dependencies:
- Shared by most libxfs code using buffers, devices, cache, transactions, and verifiers.

Notable risks:
- Direct refcount manipulation in inline helpers requires careful cache discipline.
- The userspace `xfs_buf` structure is a compatibility model, not the kernel buffer implementation.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/libxfs_io.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/linux-err.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/linux-err.h

Userspace adaptation of Linux error-pointer helpers.

Key responsibilities:
- Defines `MAX_ERRNO`, `IS_ERR_VALUE`, `ERR_PTR`, `PTR_ERR`, `IS_ERR`, `IS_ERR_OR_NULL`, `ERR_CAST`, and `PTR_ERR_OR_ZERO`.

Dependencies:
- Used by userspace ports of kernel code that return encoded error pointers.

Notable risks:
- Assumes Linux-style high-address error pointer encoding is acceptable in userspace.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/linux-err.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/listxattr.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/listxattr.c

Walks all extended attributes of an XFS inode and calls a callback for each entry.

Key responsibilities:
- Handles shortform, leaf-format, and node-format attr forks.
- Extracts local values directly and reports remote values as name plus length with NULL value pointer.
- Loads attr fork extents before walking non-local attrs.
- Traverses attr dabtree nodes to the leftmost leaf, then follows leaf sibling links.
- Uses a bitmap loop detector for node/leaf traversal.

Important behavior:
- Shortform attrs are walked from in-core fork data.
- Leaf entries report namespace flags, name, namelen, value pointer, and valuelen.
- Node walk verifies node magic, level progression, nonzero count, and repeated-block avoidance.
- Remote attr consumers must fetch values separately.

Dependencies:
- Uses libxfs attr leaf/node readers, attr fork extent loading, bitmap helpers, transactions, and inode attr helpers.

Notable risks:
- Corrupt dabtrees return `EFSCORRUPTED`; callbacks must preserve traversal invariants.
- A commented-out `xfs_failaddr_t` hints verifier-style diagnostics are not used here.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/listxattr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/listxattr.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/listxattr.h

Header for libxfs xattr walking.

Key responsibilities:
- Defines `xattr_walk_fn` callback signature.
- Declares `xattr_walk`.

Dependencies:
- Used by `db/rdump.c` and any other userspace code needing attr enumeration.

Notable risks:
- Callback receives optional value pointer; remote attrs provide length without inline value data.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/listxattr.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/logitem.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/logitem.c

Minimal userspace buffer and inode log item support for libxfs transactions.

Key responsibilities:
- Defines buffer and inode log item slab caches.
- Finds matching buffer log items already attached to a transaction.
- Initializes buffer log items and marks buffer byte ranges dirty.
- Initializes inode log items.
- Implements inode log item precommit handling that applies timestamp/version/bigtime/hint fixes and pins the inode cluster buffer.
- Provides inode log item sorting by inode number for deterministic precommit lock ordering.

Important behavior:
- Buffer log item ops are mostly empty because userspace does not write a real journal.
- `xfs_buf_item_log` marks the buffer item dirty but does not maintain a detailed bitmap here.
- Inode precommit upgrades bigtime-capable inodes, clears invalid realtime extent-size/cowextsize hint combinations, attaches inode cluster buffers late, and rolls dirty flags into `ili_fields`.
- Late inode-buffer attachment preserves AGI/AGF/inode-cluster lock ordering.

Dependencies:
- Uses transaction item lists, libxfs buffers, inode mapping, inode fork/buffer code, spin locks, and log item infrastructure.

Notable risks:
- Correct precommit ordering is critical to avoid lock-order inversions with unlinked inode and directory transactions.
- This is a compatibility subset of kernel log item behavior; callers must not assume full journal semantics.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/logitem.c -->