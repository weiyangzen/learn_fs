# Group Research: group_1772_squashfs_tools_sources_local_fs_squashfs_tools_squashfs_tools_unsqu_ebfc34a6d1ca

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs.c

Core `unsquashfs`/`sqfscat` entry point. It owns global extraction state, CLI option parsing, filesystem opening/validation, read/decompression/write threading, path filtering, listing, pseudo-file generation, and final summary/exit status.

Key responsibilities:
- Maintains global runtime knobs: processor count, progress flags, strict/ignore error behavior, xattr filters, destination path, max depth, listing/cat/pseudo modes, forced uid/gid, and filesystem block metadata.
- Implements bounded thread-safe queues and cache structures used by the reader, inflator, writer, progress, and info paths.
- Reads Squashfs metadata via `read_fs_bytes()`, `read_block()`, `read_metadata()`, `read_inode_data()`, and `read_directory_data()`, including start-offset handling and endian/compression handling through `comp`.
- Restores extracted filesystem objects: regular files, symlinks, devices, FIFOs, sockets, hard links, directories, timestamps, modes, ownership, sparse holes, and xattrs.
- Resolves extract/exclude path trees using exact, wildcard, or POSIX regex matching. It canonicalizes relative symlink traversal, prevents excessive symlink depth, tracks directory loops by inode number, and supports sticky excludes prefixed with `"... "`.
- Implements `sqfscat` mode by resolving requested paths to regular files and writing file contents to stdout.
- Implements pseudo output mode in two passes: first emits pseudo metadata and computes byte offsets, then cats regular file payloads after a `START OF DATA` marker.
- Parses options for both `unsquashfs` and `sqfscat`, including memory sizing, queue sizing, xattr policy, help dispatch, pager setup, `SQFS_CMDLINE` logging, offsets, time override, stat/mkfs-time, and extract/exclude file ingestion.
- Main flow: initialize defaults, parse mode-specific options, open filesystem, read superblock from v4/v3/v2/v1 handlers, validate compressor and block sizing, initialize threads, read filesystem tables, resolve filters, optionally pre-scan for progress totals, then scan/extract/list/cat/pseudo.

Concurrency model:
- `reader()` reads compressed blocks requested by `cache_get()`.
- `inflator()` decompresses compressed cache entries.
- `writer()` writes extracted files and directory attributes; `cat_writer()` streams file contents.
- `progress_thread()` periodically renders progress.
- Shared caches use mutexes/condition variables and mark entries pending/error/ready.

Important dependencies:
- Version-specific readers from `unsquash-*.c` through the `squashfs_operations` table.
- `compressor.c` abstraction for decompression and compressor option validation.
- `xattr.h` for `write_xattr()`, `has_xattrs()`, regex filters, and pseudo xattr printing.
- `uid_gid.c`, `limit.c`, `memory.c`, `print_pager.c`, `date.c`, and checksum/sort helpers.

Notable edge handling:
- Avoids signed-int overflows for queue/cache sizing and memory conversions.
- Serializes `lseek()+read()` using `pos_mutex`.
- Handles EINTR for read/write loops.
- Treats fatal/non-fatal extraction failures according to `-ignore-errors`, `-strict-errors`, and `-no-exit-code`.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs.h

Primary shared header for `unsquashfs` and version-specific unsquash readers.

Defines:
- Common includes, `TRUE`/`FALSE`, `TABLE_HASH()`, and `MAXIMUM_READ_SIZE`.
- Unified `struct super_block` containing Squashfs v4 fields plus legacy uid/gid fields.
- In-memory normalized inode model: block list location, data size, fragment metadata, uid/gid/mode/time/type, symlink target, sparse flag, and xattr index.
- `squashfs_operations`, the dispatch table used by `unsquashfs.c` to support multiple Squashfs on-disk versions.
- Directory, queue, cache, file-entry, path-filter, path-stack, and directory-loop/hardlink lookup structures.
- Path matching constants for exact/wildcard/regex and extract/exclude/link nodes.
- Bit-table macros for directory loop detection and lookup table macros for hard-link resolution.

Exports:
- Global extraction state used by helper modules.
- Core read/write/progress/debug helpers from `unsquashfs.c`.
- Version-reader entry points from `unsquash-1.c`, `unsquash-2.c`, `unsquash-3.c`, `unsquash-4.c`, and shared helpers from `unsquash-123*.c`.
- Date parsing hook `exec_date()`.

This header is the ABI glue between the generic extraction engine and Squashfs-version-specific metadata decoders.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_error.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_error.h

Small error-policy adapter for `unsquashfs`.

Defines:
- `INFO()` routed through `progressbar_info()` so informational output cooperates with the progress bar.
- `EXIT_UNSQUASH()` as unconditional fatal `BAD_ERROR()`.
- `EXIT_UNSQUASH_IGNORE()` as fatal unless `ignore_errors` is set, in which case it logs through `ERROR()`.
- `EXIT_UNSQUASH_STRICT()` as non-fatal logging unless `strict_errors` is set, in which case it aborts.

The macros centralize how CLI flags alter extraction error behavior without spreading policy checks throughout the code.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_error.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_help.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_help.c

Help text and pager-backed help renderer for `unsquashfs` and `sqfscat`.

Key contents:
- Option-name, option-argument, section-name, and full text arrays for both programs.
- Full documented sections for extraction, information/listing, xattrs, runtime, help, miscellaneous options, environment variables, exit codes, extra documentation links, and available decompressors.
- Generic helpers to print all help, print option matches by regex, print section names, print exact/regex section matches, report invalid options, and print option-specific parse errors.
- Public wrappers: `unsquashfs_help_all()`, `unsquashfs_section()`, `unsquashfs_option()`, `unsquashfs_help()`, `unsquashfs_invalid_option()`, `unsquashfs_option_help()`, and matching `sqfscat_*` functions.
- `display_compressors()` writes the compiled decompressor list.

Dependencies:
- `print_pager.h` for `launch_pager()`, `delete_pager()`, `autowrap_print()`, and column sizing.
- `compressor.h` for `DECOMPRESSORS`.
- `unsquashfs_help.h` xattr default strings so help reflects build-time xattr support.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_help.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_help.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_help.h

Public interface and build-conditional help strings for `unsquashfs_help.c`.

Defines:
- `NOXOPT_STR` and `XOPT_STR`, computed from `XATTR_SUPPORT`, `XATTR_OS_SUPPORT`, and `XATTR_DEFAULT`, to annotate whether `-xattrs` or `-no-xattrs` is default, unsupported, or missing OS support.

Exports:
- Help, section, option, invalid-option, and option-help functions for both `unsquashfs` and `sqfscat`.
- `display_compressors()`.

No state is stored here; it is a declaration/build-policy header.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_help.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_info.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_info.c

Signal-driven runtime status helper for extraction.

Key behavior:
- Tracks the current pathname via static `pathname`.
- `update_info()` replaces the tracked pathname; `disable_info()` frees and clears it.
- `dump_state()` disables the progress bar, prints queue/cache status for reader, inflate, writer, data cache, and fragment cache, then restores progress.
- `info_thrd()` waits for `SIGQUIT` and `SIGHUP`: first `SIGQUIT` prints the current pathname, and a subsequent signal within the waiting interval triggers a full queue/cache dump.
- `init_info()` starts the info thread.

Dependencies:
- `wait_for_signal()` from `signals.h`.
- Queue/cache dump functions and progress controls from `unsquashfs.c`.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_info.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_info.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_info.h

Minimal header for the extraction info thread.

Exports:
- `disable_info()`
- `update_info(char *)`
- `init_info()`

Used by `unsquashfs.c` to initialize interactive status reporting and update the current extraction pathname.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_info.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_xattr.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_xattr.c

Unsquashfs-side xattr helpers that are independent of OS xattr writing.

Key functions:
- `has_xattrs()` checks both inode xattr index validity and whether the filesystem has an xattr table.
- `print_xattr_name_value()` emits pseudo-file xattr assignments, preserving printable values directly and encoding non-printable/backslash bytes using `0t` octal escapes.
- `print_xattr()` loads an xattr id with `get_xattr()`, validates bounds, applies exclude/include regex filters, and writes pseudo xattr records as `<pathname> x <name>=<value>`.
- `xattr_regex()` compiles extended regexes for include/exclude options and reports invalid patterns fatally.

Dependencies:
- `read_xattrs.c` APIs declared in `xattr.h` for loading/freeing xattr lists.
- Global `sBlk`, strict-error policy, and output write helpers from `unsquashfs`.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_xattr_system.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_xattr_system.c

OS-backed xattr restoration for `unsquashfs` builds with xattr system support.

Key function:
- `write_xattr(pathname, xattr)` loads the inode's xattr list, applies include/exclude regex filters, and writes each permitted xattr using `lsetxattr()`.

Important behavior:
- Non-root users may write only `user.*` namespace xattrs; first non-user failure emits guidance and suppresses repeated messages.
- `ENOTSUP` disables further xattr output after warning that the destination filesystem does not support xattrs.
- `ENOSPC`/`EDQUOT` messages are capped by `NOSPACE_MAX` to avoid repeated per-file noise.
- Filesystem corruption is fatal if the inode xattr index exceeds `sBlk.xattr_ids`.
- Strict/ignore behavior is routed through `EXIT_UNSQUASH_STRICT()` and `EXIT_UNSQUASH_IGNORE()`.

Uses `xattr_compat.h` to normalize Linux/BSD/macOS no-follow xattr APIs.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_xattr_system.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/version.mk -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/version.mk

Two-line Makefile fragment containing git-archive substitution placeholders:

- `HASH := $Format:%h$`
- `FULLDATE := $Format:%ci$`

It is used by the build to derive version/date metadata when the source is exported through git archive.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/version.mk -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/virt_disk_pos.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/virt_disk_pos.c

Thread-safe virtual-to-disk position map for `mksquashfs` write-position tracking.

Key state:
- Global positions `vpos`, `dpos`, and `marked_vpos`.
- Static hash table `vd_hashtable[VIRT_DISK_HASH_SIZE]`.
- Mutex/condition pair for coordinating waiters on virtual-position mappings.

Functions:
- `add_virt_disk(virt, disk)` inserts a virtual-to-real disk mapping and signals a waiter if it is waiting for that virtual offset.
- `get_virt_disk(virt)` returns an existing mapping or aborts as an internal bug.
- `get_virt_disk_wait(virt)` blocks until the requested virtual mapping is inserted, then returns the disk position.

The table is append-only; there is no deletion path.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/virt_disk_pos.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/virt_disk_pos.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/virt_disk_pos.h

Header for physical and virtual output position management in `mksquashfs`.

Defines inline helpers for:
- Physical disk position: `set_dpos()`, `get_dpos()`, `get_and_inc_dpos()`, and aligned increment for `struct file_buffer`.
- Virtual position: `set_vpos()`, `get_vpos()`, `get_and_inc_vpos()`, `inc_vpos()`, `mark_vpos()`, `unmark_vpos()`, `get_marked_vpos()`, `is_vpos_marked()`.
- Combined position reset with `set_pos()`.

Marker semantics:
- `marked_vpos == 0` means no saved write position.
- `marked_vpos == 1` means mark requested but no increment has captured the previous value yet.
- Other values are saved virtual positions.

Also defines the virtual/disk hash table size, hash macro, `struct virt_disk`, and prototypes for map operations implemented in `virt_disk_pos.c`.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/virt_disk_pos.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/xattr.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/xattr.c

Mksquashfs-side extended attribute collection, normalization, deduplication, encoding, and table writing.

Key responsibilities:
- Converts system, tar, pseudo, global `-xattrs-add`, and action-generated xattrs into Squashfs xattr IDs.
- Maintains compressed xattr metadata table, uncompressed staging cache, xattr id table, saved append state, duplicate-value hash table, duplicate-id hash table, and global xattr-add list.
- Determines xattr prefix/type using `prefix_table` and stores both full names and prefix-stripped names.
- Chooses inline vs out-of-line value storage. Values above `XATTR_INLINE_MAX` or lists exceeding `XATTR_TARGET_MAX` are pushed out-of-line more aggressively.
- Deduplicates whole xattr lists and individual large values via checksum/hash plus full comparison.
- Writes final compressed xattr metadata and xattr id table using `write_xattrs()`.
- Supports append mode by importing existing xattrs with `get_xattrs()`, and by `save_xattrs()`/`restore_xattrs()` on abort.
- Parses xattr literals for `xattrs-add` and pseudo/actions: raw/binary, `0s` base64, `0x` hex, and `0t` escaped text.
- Sorts and merges global, pseudo, and action xattr-add lists, rejecting duplicate final names.
- Filters invalid `user.*` xattrs on non-file/non-directory inode types.

Important exported functions include:
- `xattr_get_prefix()`, `read_xattrs()`, `get_xattrs()`, `write_xattrs()`, `save_xattrs()`, `restore_xattrs()`, `xattr_regex()`, `base64_decode()`, `xattr_parse()`, `xattrs_add()`, `sort_xattr_add_list()`, and `add_xattrs()`.

Dependencies:
- `mksquashfs` globals and helpers for compression, table output, checksums, pathname generation, and xattr action evaluation.
- `read_xattrs.c`, tar xattr support, pseudo/action modules, `virt_disk_pos`, and merge-sort macros.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/xattr.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/xattr.h

Shared xattr data model and API declarations for both `mksquashfs` and `unsquashfs`.

Defines:
- Squashfs xattr flags/prefix masks and inline/out-of-line size policy constants.
- Format-prefix constants for base64, binary, hex, and escaped text xattr values.
- `struct xattr_list`, `struct dupl_id`, `struct prefix`, and `struct xattr_add`.

When `XATTR_SUPPORT` is enabled:
- Declares xattr table generation, reading, restoration, regex, parsing, pseudo, printing, and system write functions.
- Provides a no-op `write_xattr()` if xattr metadata support exists but OS write support is absent.

When `XATTR_SUPPORT` is disabled:
- Provides stubs that reject filesystems containing xattrs for mksquashfs append/import, return invalid xattr ids, disable printing/restoration, and report unsupported pseudo xattrs.

Also defines:
- `xattrs_supported()` and `XATTR_DEF` according to build-time xattr support, OS support, and default policy.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/xattr_compat.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/xattr_compat.h

Compatibility shim for platforms whose xattr API uses `XATTR_NOFOLLOW`, notably Apple-style xattr calls.

When `XATTR_NOFOLLOW` is defined, maps:
- `lsetxattr(path, name, value, size, flags)` to `setxattr(..., 0, flags | XATTR_NOFOLLOW)`
- `llistxattr(path, buf, size)` to `listxattr(..., XATTR_NOFOLLOW)`
- `lgetxattr(path, name, value, size)` to `getxattr(..., 0, XATTR_NOFOLLOW)`

On platforms already providing Linux-style `l*xattr` calls, this header adds no definitions.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/xattr_compat.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/xattr_system.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/xattr_system.c

Mksquashfs-side OS xattr reader.

Primary function:
- `read_xattrs_from_system(dir_ent, filename, xattrs)` lists xattr names with `llistxattr()`, filters them, reads values with `lgetxattr()`, and returns a populated `struct xattr_list` array.

Filtering order:
- Exclude actions from `eval_xattr_exc_actions()`.
- Global exclude regex `xattr_exclude_preg`.
- Include actions from `eval_xattr_inc_actions()`.
- Global include regex `xattr_include_preg`.

Error behavior:
- `ENOTSUP` or no xattrs returns zero silently.
- `ERANGE` on list/value retrieval retries because xattrs may have changed.
- Other list/value failures log and ignore xattrs for that file.
- Unknown Squashfs xattr prefixes are logged and skipped.

Uses `xattr_compat.h` for no-follow API portability.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/xattr_system.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/xz_wrapper.c -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/xz_wrapper.c

Compressor plugin for Squashfs XZ/LZMA2 support using liblzma.

Key features:
- Supports optional BCJ filters: x86, PowerPC, IA64, ARM, ARM Thumb, SPARC, ARM64, and RISC-V.
- Provides fallback filter IDs for older liblzma headers missing ARM64 or RISC-V constants.
- Parses `-Xbcj` and `-Xdict-size` compressor options.
- Post-validates dictionary size after block size is known; it must be <= block size, >= 8192, and representable in XZ headers as `2^n` or `2^n + 2^(n+1)`.
- Dumps, extracts, and displays compressor options stored in the filesystem.
- Initializes one or more filter pipelines: plain LZMA2 and, for data blocks, one pipeline per selected BCJ filter.
- `xz_compress()` tries all configured pipelines and chooses the smallest successful compressed output.
- `xz_uncompress()` decodes with a fixed `MEMLIMIT` and verifies all input bytes were consumed.
- `xz_usage()` emits compressor-specific help.
- Exports `xz_comp_ops`, the `struct compressor` vtable used by the compressor registry.

Important liblzma usage:
- `lzma_lzma_preset()`
- `lzma_stream_buffer_encode()`
- `lzma_stream_buffer_decode()`
- `lzma_filter_encoder_is_supported()`
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/xz_wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/xz_wrapper.h -->
# File Research: sources/local-fs/squashfs-tools/squashfs-tools/xz_wrapper.h

Private data structures and endian helpers for the XZ compressor wrapper.

Defines:
- Big-endian `SQUASHFS_INSWAP_COMP_OPTS()` for stored compressor options; no-op on little-endian builds.
- `MEMLIMIT` as 32 MiB for decompression.
- `struct bcj` for named BCJ filters and selection state.
- `struct filter` for a liblzma filter chain, scratch buffer, and compressed length.
- `struct xz_stream` for per-compressor stream state, selected filter list, dictionary size, and LZMA options.
- `struct comp_opts` containing on-disk XZ compressor options: dictionary size and BCJ flags.

Included by `xz_wrapper.c`; not a broad public API.
<!-- END FILE RESEARCH: sources/local-fs/squashfs-tools/squashfs-tools/xz_wrapper.h -->