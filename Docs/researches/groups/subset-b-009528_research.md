# Research: subset-b-009528

This grouped report covers selected e2fsprogs support-library sources under `lib/blkid`, `lib/et`, `lib/ss`, `lib/uuid`, and one shared helper. Each source file has its own delimited section for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/probe.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/probe.c

## Purpose
`probe.c` is the legacy libblkid content scanner. It verifies cached device entries by opening the block device, reading known superblock offsets, matching a static magic table, and extracting tags such as `TYPE`, `LABEL`, `UUID`, `SEC_TYPE`, `EXT_JOURNAL`, and `MOUNT`.

## Important APIs, Types, and Functions
The externally visible APIs are `blkid_verify()` and `blkid_known_fstype()`, plus a `TEST_PROGRAM` main. Core helpers include `get_buffer()`, `check_mdraid()`, `set_uuid()`, `get_ext2_info()`, filesystem support probes for ext2/3/4/ext4dev/JBD, FAT, NTFS, XFS, Reiser, JFS, UDF/ISO, OCFS, GFS/GFS2, HFS/HFS+, LVM2, Btrfs, LUKS, swap, and small label conversion/checksum helpers.

## Control Flow
`blkid_verify()` first uses cache age, device mtime, and previous verification flags to avoid unnecessary probes. If probing is required, it tries mdraid and then walks `type_array`, reads the 1 KiB window containing each magic string through `get_buffer()`, calls the optional filesystem-specific probe, and updates tags on the `blkid_dev` when a match succeeds. If a cached type fails, it clears all tags and retries a full scan.

## State, Persistence, Dependencies, Risks, and Test Signals
State is held in `blkid_dev` tags and timestamps, cache changed flags, probe buffers, and static Linux filesystem-support caches. Persistence is indirect through `save.c` once cache flags are changed. Dependencies include `blkidP.h`, `probe.h`, libuuid, endian helpers, `/proc/filesystems`, `/lib/modules`, Linux io, and on-disk structure layouts. Risks include stale kernel support detection, trusting packed on-disk fields, partial reads around large offsets, native-endian swap handling, and subtle type ordering in `type_array`. Test signals include the `tst_probe` image corpus, cache revalidation behavior, ext feature discrimination, FAT/NTFS label extraction, LVM2 CRC rejection, and mdraid end-of-device probing.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/probe.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/probe.h

## Purpose
`probe.h` is the private structural contract for `probe.c`. It defines the probe cursor, magic-table entries, filesystem superblock layouts, byte-order helpers, and feature constants needed to identify block-device contents without mounting them.

## Important APIs, Types, and Functions
Key types are `struct blkid_probe`, `blkid_probe_t`, `struct blkid_magic`, and many packed or layout-sensitive structures for ext, XFS, Reiser, JFS, ROMFS, cramfs, swap, FAT, minix, mdraid, HFS/HFS+, OCFS/OCFS2, Oracle ASM, ISO, GFS/GFS2, NTFS, LVM2, and Btrfs. The inline helpers are `blkid_swab16()`, `blkid_swab32()`, `blkid_swab64()`, and `blkid_le*`/`blkid_be*` macros.

## Control Flow
There is no runtime control flow beyond inline byte swapping. The header supplies the exact offsets and field names that `probe.c` casts over raw buffers after a magic match.

## State, Persistence, Dependencies, Risks, and Test Signals
State is entirely caller-owned through `struct blkid_probe` and raw mapped buffers. Dependencies include `blkid/blkid_types.h`, compiler packing support, endian configuration, and architecture-specific i386 byte-swap assembly when available. Risks are high for layout drift, unaligned field access, endian mistakes, and stale filesystem formats. Test signals are successful compilation on big- and little-endian targets, `tst_types` width validation, and probe image tests that exercise labels, UUIDs, and feature flags.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/probe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/read.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/read.c

## Purpose
`read.c` parses the libblkid cache file so callers can resolve known devices without rescanning every block device.

## Important APIs, Types, and Functions
The public entry point is `blkid_read_cache()`. Parsing helpers include `skip_over_blank()`, `skip_over_word()`, `strip_line()`, `parse_start()`, `parse_end()`, `parse_dev()`, `parse_token()`, `parse_tag()`, and `blkid_parse_line()`. A debug-only main dumps parsed devices.

## Control Flow
`blkid_read_cache()` opens the cache, skips reread if mtime is unchanged or in-memory data is dirty, reads lines including backslash continuations, and lets `blkid_parse_line()` build or update a `blkid_dev`. Device names are taken from `<device ...>name</device>`, and attributes such as `DEVNO`, `PRI`, `TIME`, `TYPE`, `LABEL`, and `UUID` are parsed from XML-like attributes.

## State, Persistence, Dependencies, Risks, and Test Signals
The file mutates `blkid_cache` device/tag lists and updates `bic_ftime` while clearing the changed flag after a clean read. It depends on `blkidP.h`, libuuid headers, libc file I/O, and `strtoull` or `strtoul`. Risks include a deliberately shallow XML parser, quote/backslash edge cases, fixed 4096-byte input buffers, and silently continuing after malformed lines. Test signals include the `TEST_PROGRAM`, cache files with comments/continuations, required `TYPE` validation, and round trips with `save.c`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/resolve.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/resolve.c

## Purpose
`resolve.c` implements libblkid convenience lookup APIs that map devices to tag values and tag expressions to device names.

## Important APIs, Types, and Functions
The public functions are `blkid_get_tag_value()` and `blkid_get_devname()`. The test main exercises both modes.

## Control Flow
When no cache is supplied, each function creates a temporary default cache and releases it before returning. `blkid_get_tag_value()` finds a device with `blkid_get_dev()` and duplicates the requested tag value. `blkid_get_devname()` accepts either `(token, value)` or a single `NAME=value` token, treats a token without `=` as a literal device name, then calls `blkid_find_dev_with_tag()`.

## State, Persistence, Dependencies, Risks, and Test Signals
State changes occur through cache reads and any probing triggered by `blkid_find_dev_with_tag()`. Returned strings are heap-owned by the caller. Dependencies include `blkidP.h`, `tag.c`, cache creation, and device lookup code. Risks include NULL handling, ambiguous unescaped `NAME=value` input, and implicit disk probing when cache misses. Test signals are correct UUID/LABEL resolution, literal path passthrough, temporary cache cleanup, and the `TEST_PROGRAM` cases.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/resolve.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/save.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/save.c

## Purpose
`save.c` serializes an in-memory libblkid cache back to disk in the XML-like format parsed by `read.c`.

## Important APIs, Types, and Functions
The public API is `blkid_flush_cache()`. `save_dev()` writes one `<device>` record, including `DEVNO`, `TIME`, optional `PRI`, and all device tags.

## Control Flow
`blkid_flush_cache()` exits early for invalid caches, empty device lists, unchanged caches, unwritable targets, or non-regular temp-file fallbacks. For regular existing files it writes to `filename-XXXXXX`, emits all devices with a type, clears the changed flag on success, optionally links a `.old` backup, and renames the temp file over the cache.

## State, Persistence, Dependencies, Risks, and Test Signals
This is the persistence point for `blkid_cache`. Dependencies include list iteration, `mkstemp()`, `fdopen()`, `fchmod()`, `link()`, and `rename()`. Risks include unescaped tag values in the output format, direct-write fallback for special cache paths, unchecked `fchmod()` when `mkstemp()` fails, and backup-link behavior on unusual filesystems. Test signals include cache read/write round trips, changed-flag behavior, temp rename success, and no output for devices without `TYPE`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/save.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/tag.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/tag.c

## Purpose
`tag.c` owns libblkid tag allocation, mutation, iteration, parsing, and indexed lookup by tag type/value.

## Important APIs, Types, and Functions
Important functions include `blkid_find_tag_dev()`, `blkid_dev_has_tag()`, `blkid_set_tag()`, `blkid_parse_tag_string()`, `blkid_tag_iterate_begin()`, `blkid_tag_next()`, `blkid_tag_iterate_end()`, and `blkid_find_dev_with_tag()`. Internal helpers allocate tags and cache-level tag heads.

## Control Flow
`blkid_set_tag()` duplicates the value, updates or deletes an existing device tag, creates cache tag-head entries as needed, links tags into both the device list and per-name cache list, and maintains direct `bid_type`, `bid_label`, and `bid_uuid` pointers. `blkid_find_dev_with_tag()` reads the cache, searches the tag-name index by priority, verifies stale hits, probes new devices, and finally probes all devices if necessary.

## State, Persistence, Dependencies, Risks, and Test Signals
State spans each device tag list, cache tag-head index, direct common tag pointers, iterator magic, priority fields, and cache changed flags. Dependencies include list macros, cache/probe APIs, `access()`, and `blkid_verify()`. Risks include pointer lifetime coupling between `bit_val` and `bid_*`, iterator invalidation during mutation, duplicated tag-head management, and expensive fallback probing. Test signals include exact tag replacement/deletion, UUID/LABEL lookup by priority, iterator traversal, and cache-change detection.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/tag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/test-blkid-topology.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/test-blkid-topology.c

## Purpose
`test-blkid-topology.c` is a sample/test program for the util-linux blkid v2 compatibility functions implemented in `topology.c`.

## Important APIs, Types, and Functions
The single `main()` uses `blkid_new_probe_from_filename()`, `blkid_probe_get_topology()`, the topology getter family, `blkid_probe_enable_partitions()`, `blkid_do_fullprobe()`, `blkid_probe_lookup_value()`, and `blkid_free_probe()`.

## Control Flow
The program opens a probe for `argv[1]`, prints logical/physical sector and io-size topology, enables partition probing as a compatibility no-op, performs a full probe, and reports whether `TYPE` or `PTTYPE` was found.

## State, Persistence, Dependencies, Risks, and Test Signals
It owns only the probe handle and duplicated lookup strings returned by the library. Dependencies include `<blkid/blkid.h>` and a readable block device or image. Risks are minimal but include missing argument validation and leaked lookup strings. Test signals are successful output on block devices and graceful error exits for failing topology/probe calls.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/test-blkid-topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/test_probe.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/test_probe.in

## Purpose
`test_probe.in` is the shell regression driver for the blkid probe image corpus.

## Important APIs, Types, and Functions
It is a configured shell script using `SRCDIR`, `tst_probe`, `bunzip2`, `dd`, `mkswap`, `cmp`, `diff`, and filesystem result files under `tests/`.

## Control Flow
If no tests are specified, it enumerates `tests/*.img.bz2`. For each test it materializes an image, regenerates native-endian swap images when needed, runs `./tst_probe`, compares output with the expected `.results`, records `.ok` or `.failed`, and exits nonzero if any comparison failed.

## State, Persistence, Dependencies, Risks, and Test Signals
State is stored in `tests/tmp`, `tests/*.out`, `tests/*.ok`, and `tests/*.failed`. Dependencies include compressed fixture images and a host `mkswap`. Risks include host-dependent swap UUID support, native-endian swap output differences, and shell `eval` around optional UUID filtering. Test signals are exact expected-output matches across all fixture filesystem images.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/test_probe.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/topology.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/topology.c

## Purpose
`topology.c` emulates a small subset of util-linux blkid v2 APIs needed by e2fsprogs and xfsprogs while delegating actual content detection to this legacy libblkid cache/probe stack.

## Important APIs, Types, and Functions
It defines private `blkid_struct_probe` and `blkid_struct_topology`. Public functions include `blkid_new_probe_from_filename()`, `blkid_free_probe()`, `blkid_do_fullprobe()`, `blkid_probe_enable_partitions()`, `blkid_probe_lookup_value()`, `blkid_probe_get_topology()`, and topology getter functions.

## Control Flow
A probe stores the filename, fd, optional cache, detected device, and last topology values. Full probing creates a cache and calls `blkid_get_dev()`. Value lookup duplicates a tag value from the detected device. Topology fetch issues Linux block ioctls for alignment, minimum/optimal I/O, and sector sizes, defaulting unsupported values to zero.

## State, Persistence, Dependencies, Risks, and Test Signals
State persists for the probe lifetime and includes an open fd and cache reference. Dependencies include Linux `BLKALIGNOFF`, `BLKIOMIN`, `BLKIOOPT`, `BLKSSZGET`, `BLKPBSZGET`, and libblkid internals. Risks include Linux-only ioctls, no real partition scanning despite the enable API, heap-owned values returned through `data`, and stale topology after device changes. Test signals come from `test-blkid-topology.c`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/tst_types.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/tst_types.c

## Purpose
`tst_types.c` validates that `blkid/blkid_types.h` exposes fixed-width integer typedefs with the sizes required by on-disk structure parsing.

## Important APIs, Types, and Functions
The only function is `main()`, which checks `__u8`, `__s8`, `__u16`, `__s16`, `__u32`, `__s32`, `__u64`, and `__s64`.

## Control Flow
The program sequentially compares each typedef size with the expected byte count, prints a diagnostic and exits `1` on the first mismatch, or prints success and exits `0`.

## State, Persistence, Dependencies, Risks, and Test Signals
There is no persistent state. Dependencies are `sys/types.h` and `blkid/blkid_types.h`. Risks are low; a failure indicates platform configuration breakage that would corrupt `probe.h` structure interpretation. The success message is the direct test signal.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/tst_types.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/version.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/version.c

## Purpose
`version.c` returns the libblkid library version and release date derived from the e2fsprogs version header.

## Important APIs, Types, and Functions
The public functions are `blkid_parse_version_string()` and `blkid_get_library_version()`. Static state is `lib_version` and `lib_date`.

## Control Flow
`blkid_parse_version_string()` walks a version string, ignores dots, accumulates decimal digits, and stops at the first non-digit/non-dot. `blkid_get_library_version()` optionally returns string pointers and returns the parsed integer.

## State, Persistence, Dependencies, Risks, and Test Signals
State is compile-time constant. Dependencies are `<blkid/blkid.h>` and `../../version.h`. Risks include ambiguous numeric encoding for versions with more components or suffixes. Test signals are expected parsed values for `E2FSPROGS_VERSION` and non-NULL returned date/version strings.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/Makefile.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/Makefile.in

## Purpose
`lib/et/Makefile.in` builds, installs, and tests the MIT com_err compatibility library and `compile_et` generator.

## Important APIs, Types, and Functions
It defines `LIBRARY=libcom_err`, objects `error_message.o`, `et_name.o`, `init_et.o`, `com_err.o`, and `com_right.o`, installed headers/share files, shared-library metadata, and targets for `compile_et`, `com_err.pc`, docs, install, uninstall, check, and clean.

## Control Flow
Configure substitution fills build variables. The build compiles static/profile/shared variants through included makefile fragments, creates `compile_et` from `compile_et.sh.in`, generates `com_err.pc`, and `check` regenerates each `.et` test case then diffs generated `.c` and `.h` against checked-in expected files.

## State, Persistence, Dependencies, Risks, and Test Signals
State is generated build output, installed headers/scripts/pkg-config metadata, and test-generated files. Dependencies include top-level make fragments, `config.status`, AWK templates, texinfo tools, and the compiler. Risks include generated-file drift, shared-library ABI flags, and install path substitution errors. Test signals are all `.et` test cases reporting success.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/com_err.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/com_err.c

## Purpose
`com_err.c` provides the formatted error-reporting front end for the com_err library.

## Important APIs, Types, and Functions
Public functions and globals are `com_err_hook`, `com_err_va()`, `com_err()`, `set_com_err_hook()`, and `reset_com_err_hook()`. The internal default handler is `default_com_err_proc()`.

## Control Flow
`com_err()` builds a `va_list` and delegates to `com_err_va()`, which calls the current hook. The default hook prints optional program name, translated error text from `error_message()`, formatted message text, terminal-aware carriage return handling, newline, and flushes stderr. Hook setters return the previous hook and restore defaults for NULL.

## State, Persistence, Dependencies, Risks, and Test Signals
Persistent state is the process-global hook pointer. Dependencies include stdio, termios/isatty when available, `error_message.c`, and com_err headers. Risks include global hook races, stderr formatting differences on tty versus pipe, and caller-supplied printf format correctness. Test signals include correct hook replacement/reset and expected stderr messages for known and unknown error codes.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/com_err.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/com_err.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/com_err.h

## Purpose
`com_err.h` is the public API header for the com_err library and its Kerberos/Heimdal compatibility surface.

## Important APIs, Types, and Functions
It defines `errcode_t`, `struct error_table`, forward-declares `struct et_list`, and declares `com_err()`, `com_err_va()`, `error_message()`, hook functions, `init_error_table()`, `add_error_table()`, `remove_error_table()`, `add_to_error_table()`, `com_right()` variants, `initialize_error_table_r()`, `free_error_table()`, and list lock helpers.

## Control Flow
There is no runtime control flow; the header fixes ABI signatures and format attributes for compile-time checking.

## State, Persistence, Dependencies, Risks, and Test Signals
State is represented by global hook and error-table declarations. Dependencies are stddef, stdarg, compiler attribute support, and matching implementations in `com_err.c`, `error_message.c`, `init_et.c`, and `com_right.c`. Risks include ABI drift across com_err implementations and exposing incomplete `et_list` for compatibility. Test signals are successful builds of generated error tables and users of both MIT and Heimdal APIs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/com_err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/com_err.pc.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/com_err.pc.in

## Purpose
`com_err.pc.in` is the pkg-config template for consumers of libcom_err.

## Important APIs, Types, and Functions
It declares substituted `prefix`, `exec_prefix`, `libdir`, `includedir`, package name, description, version, `Libs`, and `Cflags`.

## Control Flow
`config.status` substitutes configure variables during the make target `com_err.pc`.

## State, Persistence, Dependencies, Risks, and Test Signals
The persistent output is `com_err.pc` installed into `pkgconfig`. Dependencies are configure substitution and correct install directory variables. Risks are stale version strings or mismatched include/library paths. Test signals are successful `pkg-config --libs --cflags com_err` results after installation.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/com_err.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/com_right.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/com_right.c

## Purpose
`com_right.c` adds Heimdal/Kerberos4kth compatibility lookup and registration APIs on top of e2fsprogs com_err data structures.

## Important APIs, Types, and Functions
Public functions are `com_right()`, `com_right_r()`, `initialize_error_table_r()`, and `free_error_table()`. It also defines an internal combined allocation struct containing `et_list` and `error_table`.

## Control Flow
Lookup functions linearly scan an explicit `et_list` for a table whose base range contains the code. `initialize_error_table_r()` appends a dynamically allocated table unless the same message array is already present, and falls back to no registration if allocation fails. `free_error_table()` frees a linked list.

## State, Persistence, Dependencies, Risks, and Test Signals
State is caller-owned `et_list` chains independent of the global `_et_list`. Dependencies are `com_err.h` and `error_table.h`. Risks include no locking for caller lists, `com_right_r()` requiring nonzero buffer length, and compatibility allocation layout assumptions. Test signals come from generated Heimdal-style test case initializers and direct lookups against list-local tables.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/com_right.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/compile_et.sh.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/compile_et.sh.in

## Purpose
`compile_et.sh.in` is the configured shell driver that turns an `.et` error-table source into generated `.h` and `.c` files.

## Important APIs, Types, and Functions
It uses substituted `@AWK@`, `@datadir@/et`, and `@ET_DIR@`, supports `--build-tree`, and invokes `et_h.awk` and `et_c.awk`.

## Control Flow
The script normalizes locale variables to `C`, locates AWK templates in the installed directory or build tree, validates the input `.et`, generates temporary header/source outputs, compares with existing files, and replaces outputs only when contents changed. New generated files are made read-only.

## State, Persistence, Dependencies, Risks, and Test Signals
Persistent state is generated `BASE.h` and `BASE.c`. Dependencies include shell, sed, cmp, mv, chmod, AWK templates, and configure substitution. Risks include the apparent use of `$as_unset` without local definition, whitespace-sensitive `.et` parsing inherited from AWK, and read-only outputs surprising rebuild tools. Test signals are `make check` diffs against test case expected outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/compile_et.sh.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/error_message.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/error_message.c

## Purpose
`error_message.c` resolves numeric `errcode_t` values into human-readable strings from system errno tables, static com_err tables, and dynamically added tables.

## Important APIs, Types, and Functions
Public globals are `_et_list` and `_et_dynamic_list`; public functions are `et_list_lock()`, `et_list_unlock()`, `error_message()`, `add_error_table()`, `remove_error_table()`, and `add_to_error_table()`. Internal helpers manage semaphores, secure debug env handling, and debug output.

## Control Flow
`error_message()` splits a code into table base and offset, handles system errno for base zero, scans static then dynamic lists under a lock, and formats `Unknown code <table> <offset>` into a thread-local buffer when unresolved. Add/remove operations allocate or unlink dynamic list nodes and optionally log debug messages from `COMERR_DEBUG`.

## State, Persistence, Dependencies, Risks, and Test Signals
State includes global static/dynamic table lists, optional semaphore lock, debug mask/file, and thread-local unknown-code buffer. Dependencies include `strerror`, optional `sem_init`, secure getenv/prctl logic, and `error_table_name()`. Risks include static table matching only low 24 bits, lock setup/destructor portability, `init_error_table()` bypassing locks, and short unknown-code buffer assumptions. Test signals are correct system errno text, generated table lookup, add/remove behavior, and debug environment behavior in non-privileged processes.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/error_message.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/error_table.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/error_table.h

## Purpose
`error_table.h` is the private/shared com_err header describing error-table list nodes and table-name encoding constants.

## Important APIs, Types, and Functions
It defines `struct et_list`, declares `_et_list`, defines `ERRCODE_RANGE` and `BITS_PER_CHAR`, and declares `error_table_name()`.

## Control Flow
There is no runtime control flow. The constants define how error table names are encoded into high bits of `errcode_t` and decoded back for diagnostics.

## State, Persistence, Dependencies, Risks, and Test Signals
State is the external `_et_list` global. Dependencies include `errcode_t` and `struct error_table` from `com_err.h`. Risks include mismatched constants with `et_c.awk`, `et_h.awk`, and `et_name.c`, which would make generated codes unresolvable. Test signals are generated `.c/.h` test cases whose bases and table names match expected values.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/error_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/et_c.awk -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/et_c.awk

## Purpose
`et_c.awk` generates the C source file for an `.et` error table.

## Important APIs, Types, and Functions
It parses `error_table`/`et`, `error_code`/`ec`, `prefix`, and `index` directives; computes table bases using the 64-character alphabet and 8-bit error-code range; emits a `text[]` array, `struct error_table`, static fallback link, `initialize_<table>_error_table()`, and Heimdal-compatible `initialize_<table>_error_table_r()`.

## Control Flow
On the table declaration it initializes base arithmetic with high/low chunks to avoid AWK precision limits. For each error code it emits strings, handles continuation lines, fills indexed gaps with reserved messages, and in `END` emits table metadata and registration functions.

## State, Persistence, Dependencies, Risks, and Test Signals
State is AWK variables tracking table name/base/sign/current item count and continuation buffers. Dependencies are AWK numeric behavior and the same encoding constants as `error_table.h`. Risks include regex fragility, precision workarounds, a typo in negative carry variables (`cur_low`/`cur_high`), and continuation edge cases. Test signals are `make check` diffs for simple, continuation, Heimdal, and IMAP generated outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/et_c.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/et_h.awk -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/et_h.awk

## Purpose
`et_h.awk` generates the C header for an `.et` error table.

## Important APIs, Types, and Functions
It emits `#include <et/com_err.h>`, `#define` constants for each error code, `extern` declarations for the generated table and initializer functions, `ERROR_TABLE_BASE_<table>`, and old-name compatibility macros.

## Control Flow
The script computes the same table base as `et_c.awk`, tracks prefixes and explicit indexes, and emits each error-code macro with increasing values. The `END` block writes declarations and compatibility aliases.

## State, Persistence, Dependencies, Risks, and Test Signals
State is AWK arithmetic for current code value and table base. Dependencies are AWK, `com_err.h`, and matching generated source. Risks include duplicated base logic diverging from `et_c.awk`, the same negative carry typo pattern, and limited grammar tolerance. Test signals are exact header diffs in the lib/et check target.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/et_h.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/et_name.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/et_name.c

## Purpose
`et_name.c` decodes an error-table base number back into its short textual table name for unknown-code diagnostics.

## Important APIs, Types, and Functions
The public function is `error_table_name(errcode_t num)`. Static state is a 64-character alphabet and a five-character buffer.

## Control Flow
The function shifts off the low error-code bits, masks the encoded table number, extracts five 6-bit chunks from high to low, maps nonzero chunks to characters, and returns the static buffer.

## State, Persistence, Dependencies, Risks, and Test Signals
State is a process-global static buffer, so calls are not reentrant. Dependencies are `ERRCODE_RANGE` and `BITS_PER_CHAR`. Risks include buffer overwrites across calls and inconsistent names if AWK encoding changes. Test signals are unknown-code strings that include expected table names such as `krb`, `imap`, or `ovk`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/et_name.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/init_et.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/init_et.c

## Purpose
`init_et.c` implements an older com_err table-registration API that dynamically creates an error table from raw messages, base, and count.

## Important APIs, Types, and Functions
The public function is `init_error_table()`. It uses an internal `struct foobar` containing both `et_list` and `error_table`, and appends to external `_et_dynamic_list`.

## Control Flow
The function treats zero base/count or NULL messages as no-op success, allocates the combined node, fills table pointers/base/count, links it at the head of `_et_dynamic_list`, and returns `ENOMEM` on allocation failure.

## State, Persistence, Dependencies, Risks, and Test Signals
State is the global dynamic table list. Dependencies are `com_err.h` and `error_table.h`. Risks include no list locking, no duplicate detection, and allocations that are not removed unless callers use compatible removal APIs. Test signals are legacy users successfully resolving codes registered with `init_error_table()`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/init_et.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/internal.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/internal.h

## Purpose
`internal.h` supplies small private declarations for com_err implementation files.

## Important APIs, Types, and Functions
It includes `errno.h` and conditionally declares `sys_errlist` and `sys_nerr` when `NEED_SYS_ERRLIST` is configured.

## Control Flow
There is no runtime control flow.

## State, Persistence, Dependencies, Risks, and Test Signals
State is limited to external libc globals when needed. Dependencies are platform C library errno support. Risks are portability issues on systems where `sys_errlist` is hidden or has incompatible constness. Test signals are successful compilation of `error_message.c` on configured legacy platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/continuation.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/continuation.c

## Purpose
`continuation.c` is a checked-in expected C output for an `.et` file containing a multi-line continued message.

## Important APIs, Types, and Functions
It defines `text[]`, `et_ovk_error_table`, a static fallback `link`, `initialize_ovk_error_table()`, and `initialize_ovk_error_table_r()`.

## Control Flow
The initializer delegates global registration to the list-aware variant. The list-aware initializer scans for the same `text` array, appends a malloc-backed or static fallback node, and preserves idempotence.

## State, Persistence, Dependencies, Risks, and Test Signals
State is `_et_list` and optional heap/static registration node. Dependencies are generated layout compatibility with com_err. Risks are fallback static link reuse and no explicit locking in generated code. The primary test signal is diff equality with `compile_et` output for the continuation fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/continuation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/continuation.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/continuation.h

## Purpose
`continuation.h` is the expected generated header for the continuation error-table fixture.

## Important APIs, Types, and Functions
It defines `CHPASS_UTIL_PASSWORD_IN_DICTIONARY`, declares `et_ovk_error_table`, `initialize_ovk_error_table()`, `initialize_ovk_error_table_r()`, `ERROR_TABLE_BASE_ovk`, and old compatibility aliases.

## Control Flow
There is no runtime control flow; consumers include it to use the generated numeric constant and initializer.

## State, Persistence, Dependencies, Risks, and Test Signals
State is external and provided by `continuation.c`. Dependencies are `<et/com_err.h>`. Risks are mismatch with generated C if table base or prefix handling changes. Test signal is exact header diff after running `compile_et`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/continuation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal.c

## Purpose
`heimdal.c` is an expected generated C file for a Kerberos-style table with Heimdal-compatible gaps and reserved messages.

## Important APIs, Types, and Functions
It defines a large `text[]` array, `et_krb_error_table` with base `39525376L` and 82 messages, and both global and list-local initializer functions.

## Control Flow
The initializer path matches the generated pattern: avoid duplicate message arrays, allocate a list node or use the static fallback, and append it to the supplied list.

## State, Persistence, Dependencies, Risks, and Test Signals
State is error-table registration in `_et_list` or a caller list. Dependencies include generated com_err structures and Kerberos-style error numbering. Risks include reserved-index drift and duplicate table-name collision with other `krb` fixtures. Test signal is exact regeneration by `compile_et`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal.h

## Purpose
`heimdal.h` is the expected generated header for the Heimdal Kerberos fixture.

## Important APIs, Types, and Functions
It defines many `KRBET_*` error constants, declares `et_krb_error_table`, initializer functions, `ERROR_TABLE_BASE_krb`, and compatibility aliases.

## Control Flow
There is no runtime control flow. The header is consumed by code that wants named constants and explicit table initialization.

## State, Persistence, Dependencies, Risks, and Test Signals
State is in `heimdal.c`. Dependencies are `<et/com_err.h>` and matching generated table base. Risks include constant collisions with `simple.h`, which intentionally uses the same `krb` table base with a different fixture. Test signal is exact header regeneration.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal2.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal2.c

## Purpose
`heimdal2.c` is an expected generated C file for a negative-base `kadm` Kerberos administration error table.

## Important APIs, Types, and Functions
It defines `text[]`, `et_kadm_error_table` with base `-1783126272L` and 68 messages, static `link`, and `initialize_kadm_error_table()` variants.

## Control Flow
Initialization follows the generated idempotent list-append pattern. The table includes explicit reserved messages created from indexed gaps in the source `.et`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is registration in `_et_list` or a caller list. Dependencies include correct negative table-base arithmetic in `et_c.awk` and `et_h.awk`. Risks center on signed AWK/base encoding portability. Test signals are exact generated output and successful lookup of negative-base codes.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal2.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal2.h

## Purpose
`heimdal2.h` is the expected generated header for the negative-base `kadm` fixture.

## Important APIs, Types, and Functions
It defines `KADM_*` constants, declares the generated table and initializer functions, sets `ERROR_TABLE_BASE_kadm`, and provides old compatibility aliases.

## Control Flow
There is no runtime flow. The header validates that macro values progress correctly through negative ranges and explicit index jumps.

## State, Persistence, Dependencies, Risks, and Test Signals
State is external in `heimdal2.c`. Dependencies are `<et/com_err.h>` and AWK base arithmetic. Risks include sign/carry drift between header and C generation. Test signal is exact `compile_et` diff and usable constants for negative error codes.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal3.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal3.c

## Purpose
`heimdal3.c` is a compact expected generated C fixture for a small `h3test` error table.

## Important APIs, Types, and Functions
It defines two text messages, `et_h3test_error_table`, a static fallback link, and `initialize_h3test_error_table()` variants.

## Control Flow
The initializer scans for duplicate `text`, appends a new or fallback node to the target list, and registers globally through `_et_list` when called without `_r`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is the error-table list node. Dependencies are generated com_err ABI. Risks are low but include the common generated-code lack of locking and static fallback reuse. Test signal is exact regeneration from `heimdal3.et`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal3.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal3.h

## Purpose
`heimdal3.h` is the expected generated header for the small `h3test` fixture.

## Important APIs, Types, and Functions
It defines `H3TEST_TEST1`, `H3TEST_TEST2`, declares `et_h3test_error_table` and initializers, and defines table-base compatibility macros.

## Control Flow
There is no runtime control flow.

## State, Persistence, Dependencies, Risks, and Test Signals
State is provided by `heimdal3.c`. Dependencies are `<et/com_err.h>`. Risks are mismatch with C output if base-name generation changes. Test signal is exact header diff in `make check`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/heimdal3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/imap_err.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/imap_err.c

## Purpose
`imap_err.c` is an expected generated C file for an IMAP error table with a negative encoded base.

## Important APIs, Types, and Functions
It defines an IMAP message array, `et_imap_error_table` with base `-1904809472L` and 30 messages, and generated initializer functions.

## Control Flow
The initializer path follows the generated idempotent registration pattern. Messages are indexed contiguously from the table base.

## State, Persistence, Dependencies, Risks, and Test Signals
State is list registration. Dependencies include negative base arithmetic in AWK and com_err structures. Risks include signed-code portability and string drift versus the source `.et`. Test signals are regeneration diffs and successful lookup of IMAP constants.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/imap_err.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/imap_err.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/imap_err.h

## Purpose
`imap_err.h` is the expected generated header for the IMAP negative-base fixture.

## Important APIs, Types, and Functions
It defines `IMAP_*` error constants, declares `et_imap_error_table`, initializer functions, `ERROR_TABLE_BASE_imap`, and old compatibility aliases.

## Control Flow
There is no runtime control flow. It provides compile-time constants for callers and for diff-based generator testing.

## State, Persistence, Dependencies, Risks, and Test Signals
State is external in `imap_err.c`. Dependencies are `<et/com_err.h>`. Risks are macro value drift if signed base logic changes. Test signals are exact generated header diff and usable IMAP constants.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/imap_err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/simple.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/simple.c

## Purpose
`simple.c` is an expected generated C file for a straightforward `krb` error table without the larger Heimdal gaps.

## Important APIs, Types, and Functions
It defines 22 Kerberos messages, `et_krb_error_table`, static fallback `link`, and `initialize_krb_error_table()` variants.

## Control Flow
Generated initialization appends the table to `_et_list` or a supplied list, avoiding duplicate registration by comparing the message-array pointer.

## State, Persistence, Dependencies, Risks, and Test Signals
State is the registered table node. Dependencies are generated com_err ABI and the same `krb` base as other fixtures. Risks include table-name collision in combined tests and lack of locking in generated registration. Test signal is exact diff against regenerated simple fixture.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/simple.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/simple.h

## Purpose
`simple.h` is the expected generated header for the small `krb` fixture.

## Important APIs, Types, and Functions
It defines `KRB_*` constants, declares `et_krb_error_table` and initializer functions, and provides `ERROR_TABLE_BASE_krb`, `init_krb_err_tbl`, and `krb_err_base`.

## Control Flow
There is no runtime control flow.

## State, Persistence, Dependencies, Risks, and Test Signals
State is in `simple.c`. Dependencies are `<et/com_err.h>`. Risks are collision or confusion with the larger `heimdal.h` fixture because both use `krb`. Test signal is exact header regeneration.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/test_cases/simple.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/vfprintf.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/vfprintf.c

## Purpose
`vfprintf.c` is a compatibility fallback for platforms lacking native `vfprintf()`.

## Important APIs, Types, and Functions
It defines `vfprintf(iop, fmt, ap)` in old K&R style and uses `_doprnt()` to implement formatting.

## Control Flow
The function calls `_doprnt(fmt, ap, iop)` and returns `ferror(iop) ? EOF : 0`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is the target `FILE` stream. Dependencies are legacy libc `_doprnt`, stdio, and varargs ABI. Risks are obsolete platform assumptions, nonstandard return semantics compared with modern `vfprintf`, and build conflicts if libc already provides the symbol. Test signals are successful fallback builds on target legacy systems and correct com_err formatted output.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/vfprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/fpopen.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/fpopen.c

## Purpose
`fpopen.c` implements a shell-free popen-like helper that splits a command string into argv and executes it directly with `execvp()`.

## Important APIs, Types, and Functions
The exported function is `fpopen(const char *cmd, const char *mode)`. It supports read mode, write mode, and read mode with stderr merged when mode's second character is `&`.

## Control Flow
The function validates mode, tokenizes `cmd` on spaces into up to `MAX_ARGV` entries, creates a pipe, forks, wires stdin or stdout/stderr in the child, executes `prog`, and returns an `fdopen()` stream for the parent side.

## State, Persistence, Dependencies, Risks, and Test Signals
State is the child process and pipe file descriptors. Dependencies are `fork`, `pipe`, `dup2`, `execvp`, stdio, and simple libc parsing. Risks include no quote/escape handling, leaked `buf`, missing fd closes in parent/child, no wait/pclose equivalent, and no `MAX_ARGV` overflow guard. Test signals are executing simple argv-only commands without shell expansion and reading/writing expected data.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/fpopen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/Makefile.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/Makefile.in

## Purpose
`lib/ss/Makefile.in` builds, installs, and tests the MIT subsystem command interpreter library.

## Important APIs, Types, and Functions
It defines `LIBRARY=libss`, object lists for the runtime library, generated `ss_err` and `std_rqs` sources, `mk_cmds`, installable headers/share files, shared-library metadata, `test_ss`, and the regression `check` target.

## Control Flow
The build generates `mk_cmds` from `mk_cmds.sh.in`, `std_rqs.c` from `std_rqs.ct`, `ss_err.c/h` from `ss_err.et`, and then builds static/shared library variants. `check` builds `test_ss`, runs `test_script`, and diffs output against `test_script_expected`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is generated sources, archives/shared images, installed headers/scripts/pkg-config files, and test output. Dependencies include libcom_err, `compile_et`, `mk_cmds`, yacc/lex outputs for generator internals, and top-level make fragments. Risks include generated dependency ordering, shared-library link flags, and command-table generator drift. Test signal is a clean diff for `test_ss`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/ct_c.awk -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/ct_c.awk

## Purpose
`ct_c.awk` generates C request-table source from the intermediate command-table format produced by `mk_cmds`.

## Important APIs, Types, and Functions
It parses `command_table`, `BOR`, `cmd`, `sub`, `hlp`, `opt`, `EOR`, and line-number records, emitting command-name arrays, extern command prototypes, and a final `ss_request_table`.

## Control Flow
For each request record it starts a static name array, records command aliases, subroutine, help text, and option flags, then emits a request entry in the `END` block with accumulated table data.

## State, Persistence, Dependencies, Risks, and Test Signals
State is AWK arrays indexed by command number for subroutine, flags, and help text. Dependencies are the exact intermediate format generated by `mk_cmds`. Risks include limited escaping, gawk workaround assumptions, and mismatches with `ss_request_entry` layout. Test signals are generated `std_rqs.c` and `test_cmd.c` compiling and `test_ss` passing.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/ct_c.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/ct_c.sed -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/ct_c.sed

## Purpose
`ct_c.sed` is an older sed-based command-table-to-C generator retained alongside the AWK generator.

## Important APIs, Types, and Functions
It transforms command-table markers into C fragments for request names, prototypes, entries, and final request-table declarations.

## Control Flow
The sed script pattern-matches command records and emits C text progressively. It is a text-transformation pipeline rather than executable library code.

## State, Persistence, Dependencies, Risks, and Test Signals
State is sed hold/pattern space during generation. Dependencies are sed behavior and the `mk_cmds` intermediate format. Risks include poorer portability/readability than `ct_c.awk`, fragile quoting, and possible divergence if one generator is changed without the other. Test signals are generated request-table source compiling and matching expected behavior in `test_ss`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/ct_c.sed -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/data.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/data.c

## Purpose
`data.c` owns global data for libss.

## Important APIs, Types, and Functions
It defines the MIT copyright string when not linting, the global invocation table `_ss_table`, and default pager name `_ss_pager_name`.

## Control Flow
There is no runtime control flow.

## State, Persistence, Dependencies, Risks, and Test Signals
Persistent process state is `_ss_table`, which indexes active subsystem invocations, and `_ss_pager_name`, which is initialized lazily by pager code. Dependencies are `ss_internal.h`. Risks include global mutable state without locking and sparse index management. Test signals are successful creation/deletion of invocations and pager selection behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/error.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/error.c

## Purpose
`error.c` adapts com_err reporting to ss subsystem and current-request context.

## Important APIs, Types, and Functions
Public functions are `ss_name()`, `ss_error()`, and compatibility `ss_perror()`.

## Control Flow
`ss_name()` allocates either the subsystem name or `subsystem (request)` when a command is active. `ss_error()` builds that prefix, forwards formatted output to `com_err_va()`, and frees the prefix. `ss_perror()` calls `ss_error()` with a `%s` format.

## State, Persistence, Dependencies, Risks, and Test Signals
State is read from `ss_data.current_request` and subsystem name. Dependencies include `com_err` and `ss_internal.h`. Risks include allocation failure handling gaps in the request-name path and global table validity. Test signals are correctly prefixed errors for unknown commands and active command failures.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/execute_cmd.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/execute_cmd.c

## Purpose
`execute_cmd.c` parses or accepts command argv arrays and dispatches them to matching request-table functions.

## Important APIs, Types, and Functions
Public functions are `ss_execute_command()` and `ss_execute_line()`. Internal functions are `check_request_table()` and `really_execute_command()`.

## Control Flow
`ss_execute_line()` trims leading whitespace, optionally executes shell escapes prefixed by `!`, parses the line with `ss_parse()`, and dispatches. Dispatch scans each request table and each command alias; on match it records argc/argv/current request in `ss_data`, calls the command function, and clears `current_request`.

## State, Persistence, Dependencies, Risks, and Test Signals
State includes current invocation argc/argv/current_request and shell escape flags. Dependencies are `ss_parse()`, request-table layout, `system()`, and com_err-generated error codes. Risks include shell escape exposure unless disabled, no abbreviation expansion despite fields, and command handlers relying on transient argv memory. Test signals include `test_ss` command execution, unknown-command errors, quoted parsing, and escape-disabled behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/execute_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/get_readline.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/get_readline.c

## Purpose
`get_readline.c` optionally loads readline/editline support at runtime for libss interactive sessions.

## Important APIs, Types, and Functions
Public function is `ss_get_readline()`. Internal `ss_release_readline()` tears down a loaded handle. It probes libraries from `SS_READLINE_PATH` or a default colon-separated list.

## Control Flow
When `HAVE_DLOPEN` is enabled and no handle is loaded, it tries each library with `dlopen()`, resolves `readline`, `add_history`, redisplay and completion functions, sets readline global name/completion hooks when available, and stores a shutdown callback.

## State, Persistence, Dependencies, Risks, and Test Signals
State is stored in `ss_data` function pointers and `readline_handle`. Dependencies include `dlopen`, `dlsym`, `ss_safe_getenv()`, and optional readline-compatible ABI. Risks include ABI mismatch across libreadline/libedit versions, environment path trust limited by secure getenv, and silent fallback to stdio. Test signals are interactive prompt history/completion when a supported library is present and clean fallback when absent.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/get_readline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/help.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/help.c

## Purpose
`help.c` implements ss command help lookup and management of per-invocation info directories.

## Important APIs, Types, and Functions
Public functions are `ss_help()`, `ss_add_info_dir()`, and `ss_delete_info_dir()`.

## Control Flow
`ss_help()` lists requests for bare `help`, validates one-topic usage, searches configured info directories for `<topic>.info`, forks a pager with the file on stdin, and waits for it. Directory add validates with `opendir()` and appends to the invocation list; delete removes a matching string.

## State, Persistence, Dependencies, Risks, and Test Signals
State is `ss_data.info_dirs`. Dependencies include filesystem access, fork/wait, `ss_page_stdin()`, and ss error reporting. Risks include help filename construction without escaping, memory leaks in delete path for removed strings, waiting for wrong child behavior in loops, and no pager error propagation. Test signals are help listing, topic lookup through added directories, and expected `NO_INFO_DIR` or not-found errors.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/help.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/invocation.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/invocation.c

## Purpose
`invocation.c` creates and destroys ss subsystem invocation records.

## Important APIs, Types, and Functions
Public functions are `ss_create_invocation()` and `ss_delete_invocation()`.

## Control Flow
Creation allocates or grows `_ss_table`, initializes the generated ss error table, finds an unused index, fills `ss_data` fields including prompt, request-table list, info dirs, flags, and optional readline support. Deletion frees prompt, request tables, info directories, optional readline resources, and the `ss_data` object.

## State, Persistence, Dependencies, Risks, and Test Signals
State is global `_ss_table` and per-invocation `ss_data`. Dependencies include generated `initialize_ss_error_table()`, optional `ss_get_readline()`, and request tables. Risks include unchecked allocations, not clearing `_ss_table[sci_idx]` on delete, one-based sparse indexing, and no thread safety. Test signals are `test_ss` startup/shutdown, standard request-table addition, and repeated invocation lifecycle tests.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/invocation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/list_rqs.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/list_rqs.c

## Purpose
`list_rqs.c` prints a formatted list of available ss requests through the configured pager.

## Important APIs, Types, and Functions
The public command handler is `ss_list_requests()`.

## Control Flow
It blocks SIGINT, starts a pager pipe with `ss_pager_create()`, writes a heading, walks all request tables and visible entries, formats command aliases with help strings, closes the pager stream, waits for the child when forking is enabled, and restores the signal handler.

## State, Persistence, Dependencies, Risks, and Test Signals
State is read from `ss_data.rqt_tables`. Dependencies include pager code, request flags, signal APIs, and stdio. Risks include formatting overflow assumptions around `BUFSIZ`, possible wait-for-any-child behavior, and signal restoration issues. Test signals are `?` or `list_requests` output in `test_ss` and hidden commands respecting `SS_OPT_DONT_LIST`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/list_rqs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/listen.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/listen.c

## Purpose
`listen.c` implements the interactive ss read-execute loop, quit handling, SIGINT recovery, and optional readline completion support.

## Important APIs, Types, and Functions
Public functions are `ss_listen()`, `ss_abort_subsystem()`, `ss_quit()`, and, when `HAVE_DLOPEN`, `ss_rl_completion()`. Internal helpers include prompt and interrupt signal handlers plus command-name completion generation.

## Control Flow
`ss_listen()` sets current invocation state, installs SIGINT/SIGCONT handling, reads lines via readline or `fgets()`, adds history, executes the line, reports unknown requests, and exits on EOF or `abort`. SIGINT longjmps back to the prompt. Completion iterates request tables and command aliases.

## State, Persistence, Dependencies, Risks, and Test Signals
State includes static `current_info`, `listen_jmpb`, `sig_cont`, and per-invocation abort/exit fields. Dependencies include signals, setjmp, readline pointers, and `ss_execute_line()`. Risks include non-reentrant static state, longjmp across library frames, signal-handler safety, and global current-info completion assumptions. Test signals are Ctrl-C recovery, EOF handling, `quit`, unknown-command diagnostics, and readline completion.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/listen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/mit-sipb-copyright.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/mit-sipb-copyright.h

## Purpose
`mit-sipb-copyright.h` centralizes the MIT Student Information Processing Board copyright/license block for generated or shared ss sources.

## Important APIs, Types, and Functions
It contains no C declarations or functions.

## Control Flow
There is no runtime control flow.

## State, Persistence, Dependencies, Risks, and Test Signals
There is no state. Dependencies are only legal/source inclusion conventions. Risks are license text drift if generators or source templates expect this exact header. Test signals are successful inclusion in generated sources and preserved copyright text.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/mit-sipb-copyright.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/mk_cmds.sh.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/mk_cmds.sh.in

## Purpose
`mk_cmds.sh.in` is the configured shell wrapper for the ss command-table compiler.

## Important APIs, Types, and Functions
It locates generator support files through installed data directories or `_SS_DIR_OVERRIDE`, validates arguments, and drives the command-table conversion pipeline.

## Control Flow
After configure substitution, the wrapper checks for input, chooses the directory containing `ct_c.awk`/`ct_c.sed` and compiled helper tools, strips `.ct` to derive the root name, and emits generated C source for command tables.

## State, Persistence, Dependencies, Risks, and Test Signals
Persistent output is generated request-table C files such as `std_rqs.c` and `test_cmd.c`. Dependencies include shell, configured generator paths, AWK/sed templates, and build-tree override behavior. Risks include path substitution errors and divergence between installed and build-tree generator assets. Test signals are `std_rqs.c` generation and `test_ss` regression success.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/mk_cmds.sh.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/pager.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/pager.c

## Purpose
`pager.c` provides the ss pager abstraction used for request lists and help text.

## Important APIs, Types, and Functions
Public functions are `ss_safe_getenv()`, `ss_pager_create()`, and `ss_page_stdin()`. Internal helper `write_all()` supports fallback output.

## Control Flow
`ss_pager_create()` either forks a child connected to a pipe and returns the write end, or opens `/dev/tty` in no-fork builds. `ss_page_stdin()` closes extra fds, resets SIGINT handling, obtains `PAGER` securely or defaults to `more`, execs it, and falls back to copying stdin to stdout if exec fails.

## State, Persistence, Dependencies, Risks, and Test Signals
State is global `_ss_pager_name` and child pipe descriptors. Dependencies include fork/pipe/exec, secure getenv/prctl behavior, signals, and `more`. Risks include limited fd close range, child wait handled by callers, environment suppression in privileged contexts, and fallback output losing pager behavior. Test signals are help/list output paged through `PAGER` and fallback display when no pager exists.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/pager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/parse.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/parse.c

## Purpose
`parse.c` tokenizes ss command lines into argv arrays.

## Important APIs, Types, and Functions
The public function is `ss_parse()`. It uses `enum parse_mode` with `WHITESPACE`, `TOKEN`, and `QUOTED_STRING`.

## Control Flow
The parser walks the input in place, allocates/grows a NULL-terminated argv array, splits on spaces/tabs, treats quotes as grouping delimiters, converts doubled quotes inside quoted strings to a literal quote, and reports unbalanced quotes via `ss_error()`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is the caller's mutable command buffer and returned argv array. Dependencies include realloc/malloc and ss error reporting. Risks include no backslash escaping, destructive input mutation, unchecked realloc failure after the first allocation, and NULL return handling by callers. Test signals are `test_ss` scripts with quoted and spaced arguments and unbalanced-quote diagnostics.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/prompt.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/prompt.c

## Purpose
`prompt.c` gets and sets the interactive prompt for an ss invocation.

## Important APIs, Types, and Functions
Public functions are `ss_set_prompt()` and `ss_get_prompt()`.

## Control Flow
`ss_set_prompt()` frees the existing prompt and stores the caller-provided new prompt pointer. `ss_get_prompt()` returns the current pointer from `ss_data`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is `ss_data.prompt`. Dependencies are `ss_internal.h`. Risks include ownership transfer being implicit, potential free of non-malloc strings if caller misuses the API, and no NULL validation. Test signals are changed prompts in interactive sessions and correct prompt returned by getter.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/prompt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/request_tbl.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/request_tbl.c

## Purpose
`request_tbl.c` manages the ordered list of request tables attached to an ss invocation.

## Important APIs, Types, and Functions
Public functions are `ss_add_request_table()` and `ss_delete_request_table()`.

## Control Flow
Add counts existing tables, reallocates space for a new entry plus NULL terminator, clamps insertion position, shifts entries down, inserts the new table, and returns status via `code_ptr`. Delete compacts all entries not equal to the requested pointer and reports whether anything was removed.

## State, Persistence, Dependencies, Risks, and Test Signals
State is `ss_data.rqt_tables`. Dependencies are request-table layout and generated ss error codes. Risks include a likely allocation-size bug using `sizeof(ssrt)` instead of pointer size, delete setting success when nonmatching entries exist rather than when a match is removed, and no duplicate handling. Test signals include adding standard requests after test commands and deleting tables in lifecycle tests.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/request_tbl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/requests.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/requests.c

## Purpose
`requests.c` implements small built-in ss request handlers.

## Important APIs, Types, and Functions
Public handlers are `ss_self_identify()`, `ss_subsystem_name()`, `ss_subsystem_version()`, and `ss_unimplemented()`.

## Control Flow
The first three handlers print subsystem identity data from `ss_data`. `ss_unimplemented()` reports `SS_ET_UNIMPLEMENTED` through `ss_perror()`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is read-only access to subsystem name/version and generated error codes. Dependencies include `ss_internal.h` and stdio. Risks are low; handlers ignore argv and rely on a valid invocation index. Test signals are built-in commands printing expected name/version and unimplemented commands reporting the generated error.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/requests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/ss.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/ss.h

## Purpose
`ss.h` is the public header for the MIT subsystem command library.

## Important APIs, Types, and Functions
It defines `ss_request_entry`, `ss_request_table`, `ss_rp_options`, flags such as `SS_OPT_DONT_LIST`, and public functions for invocation lifecycle, command execution, table management, prompt management, built-ins, errors, and optional readline.

## Control Flow
There is no runtime control flow. The header establishes command function prototypes through `__SS_PROTO` and printf attributes for `ss_error()`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is exposed through opaque integer invocation IDs and request-table pointers. Dependencies include generated `<ss/ss_err.h>` and compiler attribute support. Risks include ABI compatibility with generated command-table C files and const-correctness tradeoffs from legacy K&R style. Test signals are successful compilation of generated `std_rqs.c`, `test_cmd.c`, and consumers including `test_ss.c`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/ss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/ss.pc.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/ss.pc.in

## Purpose
`ss.pc.in` is the pkg-config template for libss consumers.

## Important APIs, Types, and Functions
It declares substituted install prefixes, package name, description, version, library flags, and include flags.

## Control Flow
`config.status` substitutes variables during the `ss.pc` make target.

## State, Persistence, Dependencies, Risks, and Test Signals
Persistent output is installed `ss.pc`. Dependencies include correct configure variables and libss/libcom_err install layout. Risks include incomplete dependency flags if consumers also need com_err or dlopen libraries. Test signals are successful `pkg-config` output and downstream compile/link of a simple ss program.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/ss.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/ss_internal.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/ss_internal.h

## Purpose
`ss_internal.h` defines libss private data structures and internal function prototypes.

## Important APIs, Types, and Functions
Key types include `pointer`, `BOOL`, abbreviation structures, `ss_abbrev_info`, and `ss_data`. Macros include `ss_info()` and `ss_current_request()`. It declares internal helpers for parsing, paging, request listing, command execution, info dirs, and readline completion.

## Control Flow
There is no runtime control flow. It defines the in-memory contract consumed by all ss implementation files.

## State, Persistence, Dependencies, Risks, and Test Signals
State is global `_ss_table`, `_ss_pager_name`, generated `ss_et_msgs`, and per-invocation `ss_data`. Dependencies include `ss.h`, stdio/string/stdlib, and optional signal compatibility macros. Risks include exposing mutable internals across files, unimplemented abbreviation fields, pointer ownership ambiguity, and no synchronization. Test signals are coherent behavior across invocation, parser, listener, pager, and request-table modules.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/ss_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/test_ss.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/test_ss.c

## Purpose
`test_ss.c` is the regression and demonstration program for libss.

## Important APIs, Types, and Functions
It uses generated `test_cmds`, standard `ss_std_requests`, `ss_create_invocation()`, `ss_add_request_table()`, `ss_execute_line()`, `ss_listen()`, and defines the sample handler `test_cmd()`.

## Control Flow
`main()` parses `-R` and `-f`, creates an invocation named `test_ss`, adds standard requests after test commands, prints a banner, then executes one request, sources a command file, or enters interactive listening. `source_file()` reads commands, skips comments, optionally suppresses echo for lines prefixed by `-`, executes each line, and counts failures.

## State, Persistence, Dependencies, Risks, and Test Signals
State is the invocation and test script input. Dependencies include generated command table from `test_cmd.ct` and libss/libcom_err. Risks include limited option handling, fixed 256-byte command buffer, and output text coupling to expected files. Test signals are `make check` diffing `test_out` against `test_script_expected`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/test_ss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/Makefile.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/Makefile.in

## Purpose
`lib/uuid/Makefile.in` builds, installs, documents, and tests the e2fsprogs libuuid implementation.

## Important APIs, Types, and Functions
It defines object/source lists for clear, compare, copy, generate, parse, pack/unpack, unparse, and uuid_time; shared-library metadata; manpage substitution targets; generated `uuid.h`, `uuid_types.h`, `uuid.pc`; and test utilities `tst_uuid` and `uuid_time`.

## Control Flow
The build generates headers and manpages through configure substitution, compiles library variants, links test/debug utilities, installs headers, library, manpages, symlinked manpage aliases, and pkg-config metadata. `check` runs `tst_uuid`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is generated headers/docs, archives/shared images, and test binaries. Dependencies include top-level make fragments, `config.status`, substitution helpers, and optional platform features used by `gen_uuid.c`. Risks include generated header ordering, installed manpage symlink behavior, and ABI version settings. Test signal is successful `tst_uuid`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/clear.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/clear.c

## Purpose
`clear.c` implements `uuid_clear()`, the libuuid API for setting a UUID to the nil value.

## Important APIs, Types, and Functions
The public function is `uuid_clear(uuid_t uu)`.

## Control Flow
The function calls `memset(uu, 0, 16)`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is the caller-provided UUID buffer. Dependencies are `string.h` and `uuidP.h`. Risks are minimal but include callers passing invalid buffers. Test signals are nil UUID comparisons and `uuid_is_null()` returning true after clearing.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/clear.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/compare.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/compare.c

## Purpose
`compare.c` implements lexicographic UUID comparison.

## Important APIs, Types, and Functions
The public function is `uuid_compare(const uuid_t uu1, const uuid_t uu2)`. The `UUCMP` macro compares corresponding fields after unpacking.

## Control Flow
The function unpacks both UUID byte arrays into `struct uuid` fields and compares time_low, time_mid, time_hi, clock_seq, and node bytes in order, returning -1, 0, or 1.

## State, Persistence, Dependencies, Risks, and Test Signals
No persistent state is used. Dependencies include `uuidP.h` and `uuid_unpack()`. Risks are mainly semantic: ordering is field-based UUID order, not raw memcmp byte order. Test signals are equality returning zero and stable ordering for known UUID pairs.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/compare.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/configure.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/configure.in

## Purpose
`configure.in` is a small autoconf input for standalone or subconfigured libuuid feature detection.

## Important APIs, Types, and Functions
It calls `AC_INIT(gen_uuid.c)`, requires autoconf 2.12, checks headers such as `stdlib.h`, `unistd.h`, network interface headers, checks `srandom`, and outputs `Makefile`.

## Control Flow
Autoconf expands the macros into a configure script that probes platform headers/functions used by libuuid generation code.

## State, Persistence, Dependencies, Risks, and Test Signals
Persistent output is configured make/build definitions. Dependencies are autoconf and platform C headers. Risks include this old configure input diverging from top-level e2fsprogs configuration and missing modern feature tests. Test signals are generated `Makefile` and successful compilation of `gen_uuid.c`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/configure.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/copy.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/copy.c

## Purpose
`copy.c` implements `uuid_copy()`, copying one UUID byte array to another.

## Important APIs, Types, and Functions
The public function is `uuid_copy(uuid_t dst, const uuid_t src)`.

## Control Flow
The function calls `memcpy(dst, src, 16)`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is the caller-provided source and destination buffers. Dependencies are `string.h` and `uuidP.h`. Risks are minimal, with standard `memcpy` overlap caveats. Test signals are identical parsed/unparsed UUIDs after copy and compare returning zero.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/copy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/gen_uuid.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/gen_uuid.c

## Purpose
`gen_uuid.c` implements portable DCE-compatible UUID generation for random UUIDs, time-based UUIDs, and an automatic front end that chooses the best available source.

## Important APIs, Types, and Functions
Public functions are `uuid__generate_time()`, `uuid_generate_time()`, `uuid__generate_random()`, `uuid_generate_random()`, and `uuid_generate()`. Core helpers include `get_random_fd()`, `get_random_bytes()`, `get_node_id()`, `get_clock()`, `read_all()`, `close_all_fds()`, and `get_uuid_via_daemon()`.

## Control Flow
Random generation prefers `/dev/urandom` or nonblocking `/dev/random`, then mixes libc PRNG and optional thread-id `jrand48` data, and sets version/variant bits. Time generation tries `uuidd` for serialized or bulk UUIDs, otherwise discovers a hardware node id or random multicast node, obtains a locked timestamp/clock sequence from `/var/lib/libuuid/clock.txt`, sets version/variant fields, and packs the UUID.

## State, Persistence, Dependencies, Risks, and Test Signals
State includes static random fd, PRNG seeds, cached node id, thread-local clock adjustment/last timestamp/state fd, and persisted clock sequence file. Dependencies include Unix random devices, network interface ioctls, fcntl locks, optional Unix-domain uuidd, fork/exec, syscalls, and `uuid_pack`/`uuid_unpack`. Risks include fallback entropy quality, clock file permission/locking failures, static state races without TLS, daemon startup assumptions, and platform-specific network MAC discovery. Test signals include version 1 and version 4 bit layout, uniqueness under rapid generation, behavior without `/dev/urandom`, uuidd bulk path, and `tst_uuid`.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/gen_uuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/gen_uuid_nt.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/gen_uuid_nt.c

## Purpose
`gen_uuid_nt.c` provides the Windows/NT implementation of `uuid_generate()` using operating-system UUID APIs.

## Important APIs, Types, and Functions
Public function is `uuid_generate(uuid_t out)`. Internal `Nt5()` inspects the TEB/PEB OS major version to choose behavior.

## Control Flow
For NT 5 and later it calls `UuidCreate()` and copies the resulting `UUID` bytes. For older systems it calls `UuidCreateSequential()` so time/node based UUID behavior is preserved where needed.

## State, Persistence, Dependencies, Risks, and Test Signals
There is no library-managed persistent state. Dependencies are Windows RPC UUID APIs and internal TEB/PEB layout declarations. Risks include relying on undocumented `NtCurrentTeb()`/PEB offsets, Windows version detection drift, and byte layout compatibility with libuuid's `uuid_t`. Test signals are successful Windows builds and generated UUIDs with valid variant/version fields.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/gen_uuid_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/isnull.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/isnull.c

## Purpose
`isnull.c` implements the nil UUID predicate.

## Important APIs, Types, and Functions
The public function is `uuid_is_null(const uuid_t uu)`.

## Control Flow
The function scans all 16 bytes and returns `0` on the first nonzero byte or `1` if all bytes are zero.

## State, Persistence, Dependencies, Risks, and Test Signals
There is no persistent state. Dependencies are `uuidP.h`. Risks are minimal, limited to invalid caller buffers. Test signals are `uuid_clear()` followed by true, and generated UUIDs returning false.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/isnull.c -->
