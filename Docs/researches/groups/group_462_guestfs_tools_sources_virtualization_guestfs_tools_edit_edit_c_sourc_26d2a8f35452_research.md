# Group Research: group_462_guestfs_tools_sources_virtualization_guestfs_tools_edit_edit_c_sourc_26d2a8f35452

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/guestfs-tools` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/edit/edit.c -->
# File Research: sources/virtualization/guestfs-tools/edit/edit.c

`virt-edit` command implementation. It creates a writable libguestfs handle, parses common disk/domain/mount/key options, launches the appliance, mounts the guest either via inspection or explicit `-m`, then edits one or more guest files.

Key behavior:
- Supports `-a`, `-d`, `--format`, `--blocksize`, `--key`, `--keys-from-stdin`, `--connect`, `-m`, `-b`, and `-e/--expr`.
- Defaults to inspector-based mounting; `-m` disables inspection.
- Preserves compatibility with old syntax by treating pre-filename arguments as disks or domains when no explicit drive options were given.
- For Windows guests, translates guest paths through `windows_path`.
- Actual edits are delegated to shared helpers:
  - `edit_file_perl` for noninteractive Perl expression editing.
  - `edit_file_editor` for `$EDITOR`-based editing.
- Supports backup extension creation through `backup_extension`.
- Shuts down libguestfs cleanly after edits.

Important dependencies: `guestfs.h`, common `options.h`, `display-options.h`, `windows.h`, and `file-edit.h`.

Research relevance: this file is a user-facing guest filesystem mutation tool. It demonstrates libguestfs write-mode setup, guest root discovery, Windows path normalization, and safe delegation of in-guest file replacement logic.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/edit/edit.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/edit/test-virt-edit-docs.sh -->
# File Research: sources/virtualization/guestfs-tools/edit/test-virt-edit-docs.sh

Shell test for `virt-edit` documentation. It sources the shared test helpers, enables `set -e` and `set -x`, honors `skip_if_skipped`, and runs `podcheck.pl` against `virt-edit.pod`.

It validates that the POD documentation for `virt-edit` is internally consistent and checks common option documentation via `--path $top_srcdir/common/options`.

Research relevance: documentation validation fixture; no filesystem behavior beyond test harness integration.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/edit/test-virt-edit-docs.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/edit/test-virt-edit.sh -->
# File Research: sources/virtualization/guestfs-tools/edit/test-virt-edit.sh

Functional shell test for `virt-edit`. It creates a writable qcow2 overlay backed by the Fedora phony guest image, edits `/etc/test3`, and validates content and metadata.

Coverage:
- Creates `test.qcow2` with `guestfish disk-create`, backing `../test-data/phony-guests/fedora.img`.
- Simulates interactive editing by setting `EDITOR='echo newline >>'`.
- Verifies `virt-cat` output includes the appended line.
- If Perl exists, tests noninteractive `-e 's/^[a-f]/$lineno/'`.
- Verifies edited file mode, UID, and GID remain `0600`, `10`, and `11`, guarding RHBZ#788641 behavior.
- Removes the temporary image.

Research relevance: confirms content mutation and metadata preservation for in-guest file edits.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/edit/test-virt-edit.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/filesystems/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/filesystems/Makefile.am

Automake rules for `virt-filesystems`.

Build contents:
- Program: `virt-filesystems`.
- Sources: `filesystems.c`, `utils.c`, `utils.h`.
- Includes common utils, structs, libguestfs, options, windows, include, and local gnulib paths.
- Links common option/windows/struct/utils libraries, libguestfs, libxml2, libvirt, gettext, and `../gnulib/lib/libgnu.la`.

Documentation:
- Generates `virt-filesystems.1` and website HTML from `virt-filesystems.pod` via `PODWRAPPER`.

Tests:
- `test-docs.sh`
- `test-virt-filesystems.sh`
- Valgrind targets, including local guest iteration.

Research relevance: captures build-time dependency boundaries for the filesystem inventory tool.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/filesystems/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/filesystems/filesystems.c -->
# File Research: sources/virtualization/guestfs-tools/filesystems/filesystems.c

Implementation of `virt-filesystems`, a read-only inventory tool for guest filesystems, partitions, block devices, and LVM objects.

Major behavior:
- Creates a read-only libguestfs handle.
- Parses output selection options: `--filesystems`, `--extra`, `--parts`, `--blkdevs`, `--lvs`, `--vgs`, `--pvs`, `--all`.
- Supports output shaping: `--long`, `--csv`, `--human-readable`, `--uuid`, `--fs-version`, `--no-title`.
- Requires at least one `-a` or `-d` drive source and rejects extra positional arguments.
- Launches libguestfs but does not mount an OS root for inspection.

Inventory paths:
- `do_output_filesystems`: uses `guestfs_list_filesystems`, filters `swap` and `unknown` unless `--extra`, canonicalizes devices, optionally probes label, UUID, FS version, size, and parents.
- `do_output_lvs`: lists logical volumes and derives VG parent from LV path.
- `do_output_vgs`: uses `guestfs_vgs_full`, emits VG UUID and resolves PV parents.
- `do_output_pvs`: caches `guestfs_pvs_full`, emits canonical PV paths.
- `do_output_partitions`: lists partitions, resolves parent block device, and optionally reads MBR IDs for msdos partition tables.
- `do_output_blockdevs`: lists block devices and RAID parents where applicable.

Output implementation:
- CSV mode writes rows immediately with local CSV quoting.
- Text mode buffers all rows, tracks max column widths, and prints aligned columns at the end.
- Empty fields render as `-` in text mode.
- Human-readable sizes use gnulib `human_readable`.

Notable details:
- RAID parent detection is a simple `/dev/md[0-9]+` test.
- VG parent resolution compares PV UUIDs while ignoring punctuation in `guestfs_vgpvuuids`.
- Filesystem size probing tries statvfs via temporary read-only mount when possible, otherwise falls back to block device size.
- XFS FS version support comes from local `get_filesystem_version`.

Research relevance: central guest storage topology reporting tool, useful for understanding libguestfs enumeration APIs and device relationship formatting.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/filesystems/filesystems.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/filesystems/test-docs.sh -->
# File Research: sources/virtualization/guestfs-tools/filesystems/test-docs.sh

Documentation test for `virt-filesystems`. It uses the shared test harness, honors skips, and invokes `podcheck.pl` on `virt-filesystems.pod` with common options documentation in scope.

Research relevance: verifies user-facing manpage/POD consistency for the storage inventory command.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/filesystems/test-docs.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/filesystems/test-virt-filesystems.sh -->
# File Research: sources/virtualization/guestfs-tools/filesystems/test-virt-filesystems.sh

Functional test for `virt-filesystems` against the Fedora phony guest image.

Checks:
- Default output lists mountable filesystems only, sorted:
  `/dev/VG/LV1`, `/dev/VG/LV2`, `/dev/VG/LV3`, `/dev/VG/Root`, `/dev/sda1`.
- `--all --long --uuid -h --no-title` includes unique names for VG, LVs, block device, and partitions.
- Runs through `$VG`, allowing valgrind wrapping.

Research relevance: confirms default filtering and `--all --long` object coverage.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/filesystems/test-virt-filesystems.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/filesystems/utils.c -->
# File Research: sources/virtualization/guestfs-tools/filesystems/utils.c

Shared helper for `virt-filesystems` and `virt-inspector`.

Function:
- `get_filesystem_version(guestfs_h *g, const char *dev, const char *fs_type)`

Current implementation:
- Only handles XFS when `GUESTFS_HAVE_XFS_INFO2` is available.
- Calls `guestfs_xfs_info2`.
- Reads `meta-data.crc`:
  - `0` maps to XFS version `"4"`.
  - `1` maps to XFS version `"5"`.
- Suppresses libguestfs errors during optional probing.
- Returns `NULL` when version is unknown.

Research relevance: small filesystem feature probe used to enrich reporting without making unsupported version detection fatal.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/filesystems/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/filesystems/utils.h -->
# File Research: sources/virtualization/guestfs-tools/filesystems/utils.h

Header for shared filesystem utility helpers.

Exports:
- `const char *get_filesystem_version(guestfs_h *g, const char *dev, const char *fs_type);`

Contract:
- Currently intended for XFS version reporting.
- May return `NULL` if no known version can be determined.

Research relevance: public local interface between `filesystems`, `inspector`, and the shared utility implementation.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/filesystems/utils.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/format/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/format/Makefile.am

Automake rules for `virt-format`.

Build contents:
- Program: `virt-format`.
- Source: `format.c`.
- Includes common utils, libguestfs, options, fish, include, and local gnulib paths.
- Links options, utils, libguestfs, libxml2, libvirt, gettext, and `libgnu.la`.

Documentation:
- Generates `virt-format.1` and website HTML from `virt-format.pod`.

Tests:
- `test-virt-format-docs.sh`
- `test-virt-format.sh`
- Valgrind check target.

Research relevance: build wiring for destructive disk formatting tool.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/format/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/format/format.c -->
# File Research: sources/virtualization/guestfs-tools/format/format.c

Implementation of `virt-format`, a destructive tool that erases and optionally repartitions/formats guest disk images.

Major behavior:
- Uses writable libguestfs handle.
- Accepts only `-a` disk inputs, not domains.
- Enables discard `besteffort` for added drives.
- Options include `--filesystem`, `--label`, `--lvm`, `--partition`, `--wipe`, `--format`, and `--blocksize`.
- Warns in usage text that all disk data is erased.

Formatting process:
1. Adds drives and launches libguestfs.
2. Checks whether `wipefs` API is available.
3. Erases filesystem signatures and partition tables with `wipefs` plus `zero`, or wipes whole devices with `zero_device` when `--wipe` is used.
4. Attempts `blkdiscard` for host space reclamation but ignores failures.
5. Rescans partition tables and LVM metadata.
6. Retries once with a fresh libguestfs handle if rescan fails.
7. Optionally partitions each disk:
   - Default chooses MBR under 2 TiB, GPT otherwise.
   - For MBR, sets partition type byte based on LVM or filesystem.
8. Optionally creates PV/VG/LV from `--lvm`.
9. Optionally creates filesystem via `guestfs_mkfs_opts_argv`, with label support.
10. Syncs and shuts down.

Notable helper:
- `parse_vg_lv` accepts `/dev/VG/LV` or `VG/LV`, rejects malformed names.

Research relevance: demonstrates libguestfs block-device destructive operations, partition-table recreation, LVM provisioning, filesystem creation, discard, and retry handling for kernel rescan instability.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/format/format.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/format/test-virt-format-docs.sh -->
# File Research: sources/virtualization/guestfs-tools/format/test-virt-format-docs.sh

Documentation test for `virt-format`. It runs `podcheck.pl` against `virt-format.pod` and includes common options documentation.

Research relevance: confirms manpage/POD consistency for a destructive storage command.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/format/test-virt-format-docs.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/format/test-virt-format.sh -->
# File Research: sources/virtualization/guestfs-tools/format/test-virt-format.sh

Functional test for `virt-format`.

Steps:
- Removes stale `test-virt-format.img`.
- Creates a guestfish `bootrootlv` test image.
- Runs `virt-format --filesystem=ext3 --format=raw -a test-virt-format.img`.
- Verifies `virt-filesystems` reports only `/dev/sda1`.
- Removes temporary image.

Research relevance: smoke-tests destructive reformatting and validates result through the inventory tool.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/format/test-virt-format.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/get-kernel/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/get-kernel/Makefile.am

Automake rules for OCaml-based `virt-get-kernel`.

Structure:
- Always distributes OCaml interface/source files and `dummy.c`.
- Builds `virt-get-kernel` only under `HAVE_OCAML`.
- Uses `dummy.c` as the C source anchor for an OCaml-linked binary.
- Defines OCaml package flags for `str`, `unix`, `guestfs`, gettext when available, and multiple common OCaml helper libraries.
- Links through `ocaml-link.sh`, selecting bytecode or native objects depending on `HAVE_OCAMLOPT`.

Documentation and tests:
- Generates `virt-get-kernel.1` and website HTML from POD.
- Runs `test-virt-get-kernel-docs.sh`.

Research relevance: records mixed C/OCaml build integration for a guest kernel extraction tool.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/get-kernel/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/get-kernel/dummy.c -->
# File Research: sources/virtualization/guestfs-tools/get-kernel/dummy.c

Minimal C source used for OCaml-based tools with no real C implementation files.

Content:
- Defines `enum { foo = 1 };`

Research relevance: build-system placeholder, not runtime logic.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/get-kernel/dummy.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/get-kernel/test-virt-get-kernel-docs.sh -->
# File Research: sources/virtualization/guestfs-tools/get-kernel/test-virt-get-kernel-docs.sh

Documentation test for `virt-get-kernel`. It sources shared test helpers, honors skips, and validates `virt-get-kernel.pod` with common option docs.

Research relevance: documentation fixture for the OCaml guest kernel extraction tool.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/get-kernel/test-virt-get-kernel-docs.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/Makefile.am

Automake rules for local vendored gnulib subset.

Builds:
- `noinst_LTLIBRARIES = libgnu.la`

Sources include:
- Argument matching, bit rotation, C-locale character classification, error fallback, `getprogname`, hash table, human-readable sizes, ignored return value helper, allocation overflow checks, and `xstrtol` variants.

Comment notes that this directory contains dependencies originally from gnulib and is intended to eventually disappear, likely by migration to `common/utils`.

Research relevance: compatibility and utility substrate used by multiple guestfs tools.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/argmatch.c -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/argmatch.c

Gnulib argument string matcher.

Key functions:
- `argmatch`: matches an input string against a null-terminated argument list, allowing unambiguous abbreviations.
- Ambiguity can be resolved through value equivalence in `vallist`.
- Returns index, `-1` for invalid, `-2` for ambiguous.
- `argmatch_invalid`: prints invalid or ambiguous argument message.
- `argmatch_valid`: prints valid arguments, grouping adjacent synonyms.
- `__xargmatch_internal`: failure-reporting wrapper that calls a supplied exit function.
- `argmatch_to_argument`: maps a value back to its first argument string.

Includes a `TEST` block for backup-option matching.

Research relevance: generic CLI parsing helper for constrained option values.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/argmatch.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/argmatch.h -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/argmatch.h

Header and macro framework for `argmatch`.

Exports:
- Core functions and macros: `ARGMATCH`, `XARGMATCH`, `ARGMATCH_VALID`, `ARGMATCH_TO_ARGUMENT`.
- `argmatch_exit_fn` and external `argmatch_die`.
- `ARGMATCH_DEFINE_GROUP`, a large macro that generates typed group-specific choice, value, argument, valid-list, doc-column, and usage functions.

Generated group behavior:
- Supports exact and unambiguous abbreviated matches.
- Treats multiple strings with equal typed values as synonyms.
- Can print localized valid argument lists and usage documentation.
- Wraps failures through `argmatch_invalid` and `argmatch_die`.

Research relevance: type-safe macro layer over string-to-enum style command option parsing.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/argmatch.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/bitrotate.h -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/bitrotate.h

Inline bit-rotation helpers for unsigned integer types.

Functions:
- `rotl64`, `rotr64` when `UINT64_MAX` exists.
- `rotl32`, `rotr32`.
- `rotl_sz`, `rotr_sz`.
- `rotl16`, `rotr16`.
- `rotl8`, `rotr8`.

Research relevance: small utility used by the hash table’s pointer hashing path.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/bitrotate.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/c-ctype.h -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/c-ctype.h

Locale-independent character classification helpers.

Purpose:
- Mirrors common `<ctype.h>` functions but hardwires C/POSIX locale behavior.
- Supports ASCII and EBCDIC variants; errors out for unsupported character sets.
- Accepts values in `unsigned char` or `char` range without requiring caller casts.

Functions:
- `c_isalnum`, `c_isalpha`, `c_isascii`, `c_isblank`, `c_iscntrl`, `c_isdigit`, `c_isgraph`, `c_islower`, `c_isprint`, `c_ispunct`, `c_isspace`, `c_isupper`, `c_isxdigit`.
- `c_tolower`, `c_toupper`.

Research relevance: stable parsing helper; used where locale-sensitive `ctype.h` behavior would be incorrect.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/c-ctype.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/error.c -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/error.c

Fallback implementation of GNU/glibc-style `error` and `error_at_line`, compiled only when `HAVE_ERROR_H` is absent.

Key behavior:
- Maintains `error_print_progname`, `error_message_count`, and `error_one_per_line`.
- Flushes stdout before printing errors.
- Prints program name from `getprogname`.
- Optionally appends system error text for `errnum`.
- Exits when `status` is nonzero.
- `error_at_line` can suppress duplicate file/line messages when `error_one_per_line` is set.
- Contains platform handling for Windows fd checks and strerror variants.

Research relevance: portability layer for consistent command-line diagnostics across platforms.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/error.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/error.h -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/error.h

Declaration header for GNU-style error reporting.

Exports:
- `error`
- `error_at_line`
- `error_print_progname`
- `error_message_count`
- `error_one_per_line`

Research relevance: common diagnostic API used by guestfs tools.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/error.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/getprogname.h -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/getprogname.h

Compatibility header for `getprogname`.

Behavior:
- If `HAVE_GETPROGNAME` is not defined, provides inline `getprogname()` returning `program_invocation_short_name`.

Research relevance: gives common code a stable program-name API for usage and diagnostics.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/getprogname.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/hash.c -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/hash.c

Generic chained hash table implementation.

Core design:
- Table has prime-sized bucket array.
- Each bucket head is embedded in the bucket array; collisions use linked overflow entries.
- Overflow entries are recycled through a free list.
- Optional obstack allocation is supported when `USE_OBSTACK` is enabled.

Key APIs implemented:
- Information: bucket count, used buckets, entry count, max bucket length, validation, statistics.
- Lookup and walking: `hash_lookup`, `hash_get_first`, `hash_get_next`, `hash_get_entries`, `hash_do_for_each`.
- Allocation: `hash_initialize`, `hash_clear`, `hash_free`.
- Resizing: `hash_rehash`.
- Mutation: `hash_insert_if_absent`, `hash_insert`, `hash_remove`, deprecated `hash_delete`.

Important implementation details:
- Default tuning grows when used-bucket ratio exceeds `0.8`, with growth factor `1.414`.
- Default shrink is disabled.
- Custom hashers and comparators are optional; defaults use pointer hashing/comparison.
- Pointer hashing rotates address bits to reduce low-bit alignment artifacts.
- Rehash has rollback logic if allocation fails during transfer.
- `NULL` entries are unsupported and abort insertion.

Research relevance: reusable container utility for guestfs tools and common gnulib-derived infrastructure.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/hash.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/hash.h -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/hash.h

Public API for the generic hash table.

Defines:
- `Hash_tuning`
- Opaque `Hash_table`
- Callback types:
  - `Hash_hasher`
  - `Hash_comparator`
  - `Hash_data_freer`
  - `Hash_processor`

Documents:
- Table statistics and lookup APIs.
- Traversal constraints: do not resize or generally modify during traversal.
- Initialization behavior and tuning semantics.
- Ownership behavior for `data_freer`.
- Insert/remove semantics, including no duplicate and no `NULL` entry support.

Research relevance: contract for the hash table implementation.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/hash.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/human.c -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/human.c

Human-readable size formatting and block-size option parsing.

Main functions:
- `human_readable`: converts a `uintmax_t` quantity from one block size to another with rounding, grouping, autoscaling, and SI suffix options.
- `human_options`: parses block-size specifications into options and block size.

Formatting behavior:
- Uses exact integer arithmetic where possible.
- Falls back to `long double` when exact integer scaling is not straightforward.
- Supports rounding styles: ceiling, nearest, floor.
- Supports locale decimal point, grouping, and thousands separators.
- Supports base 1000 or base 1024, suffixes up to Y/yotta-style scale, optional `B`/`iB`.

Parsing behavior:
- Reads explicit spec or environment variables `BLOCK_SIZE` / `BLOCKSIZE`.
- Defaults to `512` under `POSIXLY_CORRECT`, otherwise `DEFAULT_BLOCK_SIZE` of `1024`.
- Uses `argmatch` for `human-readable` and `si`.
- Uses `xstrtoumax` for numeric suffix parsing.

Research relevance: used by `virt-filesystems -h` and similar tools for stable size presentation.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/human.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/human.h -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/human.h

Public interface for human-readable size formatting.

Defines:
- `LONGEST_HUMAN_READABLE` buffer bound.
- Option flags for rounding, grouping, autoscaling, base selection, spacing, SI suffixes, and byte suffixes.
- `human_readable`
- `human_options`

Research relevance: shared formatting contract for disk/filesystem sizes.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/human.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/ignore-value.h -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/ignore-value.h

Macro helper for intentionally ignoring return values from functions annotated with `warn_unused_result`.

Behavior:
- For affected GCC versions, stores expression result in a temporary via `__typeof__` and discards it.
- For clang and other compilers, falls back to `(void)(x)`.

Research relevance: portability/helper macro for explicit unchecked-result cases.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/ignore-value.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/xalloc-oversized.h -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/xalloc-oversized.h

Allocation overflow detection macro.

Exports:
- `xalloc_oversized(n, s)`

Behavior:
- Returns true if `n * s` would overflow size calculations or exceed reliable pointer-difference bounds.
- Uses compiler builtins for GCC where available.
- Falls back to division-based overflow checks.

Research relevance: guards array allocation sizing, notably in the hash table.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/xalloc-oversized.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/xstrtol.c -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/xstrtol.c

Macro-parameterized implementation of robust string-to-integer parsing.

Behavior:
- Defaults to `long int`/`strtol`/`xstrtol` unless included with macros redefining target type and conversion function.
- Rejects negative input for unsigned target types.
- Returns `strtol_error` flags instead of only relying on `errno`.
- Supports valid suffix checking.
- Supports suffix scaling:
  - `b` = 512
  - `B` = 1024 legacy
  - `c` = no scale
  - `k/K`, `M/m`, `G/g`, `T/t`, `P`, `E`, `Z`, `Y`
  - optional `B` or `iB` second suffix when valid suffix list contains `0`.
- Detects scaling overflow and clamps to min/max.

Research relevance: common safe parser for numeric command-line arguments and block-size-like values.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/xstrtol.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/xstrtol.h -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/xstrtol.h

Header for robust string-to-integer parsers.

Defines:
- `enum strtol_error` values:
  - `LONGINT_OK`
  - `LONGINT_OVERFLOW`
  - `LONGINT_INVALID_SUFFIX_CHAR`
  - combined overflow/suffix error
  - `LONGINT_INVALID`

Declares:
- `xstrtol`
- `xstrtoul`
- `xstrtoll`
- `xstrtoull`
- `xstrtoimax`
- `xstrtoumax`

Research relevance: parse-status contract for gnulib numeric conversion helpers.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/xstrtol.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/xstrtoul.c -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/xstrtoul.c

Unsigned long instantiation of `xstrtol.c`.

Macro setup:
- `__strtol` = `strtoul`
- `__strtol_t` = `unsigned long int`
- `__xstrtol` = `xstrtoul`
- min/max = `0` / `ULONG_MAX`

Research relevance: generated parser variant for unsigned long values.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/xstrtoul.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/xstrtoull.c -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/xstrtoull.c

Unsigned long long instantiation of `xstrtol.c`.

Macro setup:
- `__strtol` = `strtoull`
- `__strtol_t` = `unsigned long long int`
- `__xstrtol` = `xstrtoull`
- min/max = `0` / `ULLONG_MAX`

Research relevance: generated parser variant for unsigned long long values.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/xstrtoull.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/xstrtoumax.c -->
# File Research: sources/virtualization/guestfs-tools/gnulib/lib/xstrtoumax.c

`uintmax_t` instantiation of `xstrtol.c`.

Macro setup:
- `__strtol` = `strtoumax`
- `__strtol_t` = `uintmax_t`
- `__xstrtol` = `xstrtoumax`
- min/max = `0` / `UINTMAX_MAX`

Research relevance: generated parser variant used by human-readable block-size parsing.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/gnulib/lib/xstrtoumax.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/Makefile.am -->
# File Research: sources/virtualization/guestfs-tools/inspector/Makefile.am

Automake rules for `virt-inspector`.

Build contents:
- Program: `virt-inspector`.
- Sources include `inspector.c` plus shared `../filesystems/utils.c` and `utils.h`.
- Includes common utils, structs, libguestfs, filesystem utils, options, fish, include, and gnulib paths.
- Links options, structs, utils, libguestfs, libxml2, libvirt, gettext, and `libgnu.la`.

Distributed fixtures:
- Example XML files for Debian, Fedora, RHEL 6, Ubuntu, Windows.
- Expected XML outputs for multiple phony/test guest images.
- Inspector tests, LUKS/LVM tests, docs test, xmllint test.

Documentation:
- Installs `virt-inspector.rng` and example XML under docs.
- Generates manpage and website HTML from POD.

Research relevance: build and test manifest for OS inspection XML generation.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/example-debian.xml -->
# File Research: sources/virtualization/guestfs-tools/inspector/example-debian.xml

Example `virt-inspector` XML for a Debian 5 x86_64 guest.

Contents:
- Root: `/dev/debian5x64.home.annexia.org/root`
- OS: Linux, Debian, product `5.0.6`
- Package format/manager: `deb` / `apt`
- Hostname included.
- Mountpoints include `/`, `/tmp`, `/usr`, `/var`, `/boot`, `/home`.
- Filesystems include ext3 LVs, swap LV, and ext2 `/dev/sda1`, with UUIDs.
- Applications section is shortened but demonstrates package entries.
- Includes a base64 PNG icon.

Research relevance: documentation fixture showing expected inspector schema for Debian with LVM-heavy layout.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/example-debian.xml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/example-fedora.xml -->
# File Research: sources/virtualization/guestfs-tools/inspector/example-fedora.xml

Example `virt-inspector` XML for Fedora 18 x86_64.

Contents:
- Root: `/dev/fedora/root`
- OS: Linux, Fedora, product `Fedora release 18 (Spherical Cow)`
- Package format/manager: `rpm` / `yum`
- Mountpoints: `/` and `/boot`.
- Filesystems: ext4 root, swap, ext4 boot with UUIDs.
- Applications section is shortened but shows RPM package metadata.
- Includes a base64 PNG icon.

Research relevance: documentation fixture for RPM/yum Linux inspection output.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/example-fedora.xml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/example-rhel-6.xml -->
# File Research: sources/virtualization/guestfs-tools/inspector/example-rhel-6.xml

Example `virt-inspector` XML for RHEL 6.3 i386.

Contents:
- Root: `/dev/vg_rhel6x32/lv_root`
- OS: Linux, RHEL, product `Red Hat Enterprise Linux Server release 6.3 (Santiago)`
- Package format/manager: `rpm` / `yum`
- Hostname included.
- Mountpoints: `/` and `/boot`.
- Filesystems: ext4 root LV, swap LV, ext4 boot partition.
- Applications section is shortened but shows RPM metadata.
- Includes a very large base64 PNG icon.

Research relevance: documentation fixture for RHEL inspection, LVM root layout, and large icon output.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/example-rhel-6.xml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/example-ubuntu.xml -->
# File Research: sources/virtualization/guestfs-tools/inspector/example-ubuntu.xml

Example `virt-inspector` XML for Ubuntu 13.04 x86_64.

Contents:
- Root: `/dev/sda1`
- OS: Linux, Ubuntu, product `Ubuntu 13.04`
- Package format/manager: `deb` / `apt`
- Mountpoint: `/`
- Filesystems: ext4 root and swap partition with UUIDs.
- Applications section is shortened but demonstrates Debian package fields.

Research relevance: documentation fixture for simple Ubuntu partition layout.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/example-ubuntu.xml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/example-windows.xml -->
# File Research: sources/virtualization/guestfs-tools/inspector/example-windows.xml

Example `virt-inspector` XML for Windows Server 2012 Datacenter.

Contents:
- Root: `/dev/sda2`
- OS name/distro: `windows`
- Architecture: `x86_64`
- Product variant: `Server`
- Major/minor: `6.2`
- Windows fields: `windows_systemroot` and `windows_current_control_set`.
- Mountpoint: `/`
- Filesystem: NTFS with UUID.
- Drive mappings: `C` to `/dev/sda2`, `D` to `/dev/sda3`.
- Empty applications element.

Research relevance: documentation fixture for Windows-specific inspector fields and drive mapping output.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/example-windows.xml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/expected-archlinux.img.xml -->
# File Research: sources/virtualization/guestfs-tools/inspector/expected-archlinux.img.xml

Expected inspector output for an Arch Linux test image.

Contents:
- Root: `/dev/sda1`
- OS: Linux, Arch Linux, x86_64
- Major/minor versions are `0`.
- Package format/manager: `pacman`.
- Hostname: `archlinux.test`
- osinfo: `archlinux`
- Single ext4 root filesystem with fixed test UUID.
- One test package with epoch, version, release, arch, URL, and description.

Research relevance: regression oracle for Arch/pacman inspection behavior.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/expected-archlinux.img.xml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/expected-coreos.img.xml -->
# File Research: sources/virtualization/guestfs-tools/inspector/expected-coreos.img.xml

Expected inspector output for a CoreOS test image.

Contents:
- Root: `/dev/sda5`
- OS: Linux distro `coreos`
- Product: `CoreOS 899.13.0`
- Major/minor: `899` / `13`
- Hostname: `coreos.invalid`
- Build ID: `2016-03-23-0120`
- osinfo: `coreos899.13`
- Mountpoints: `/` on `/dev/sda5`, `/usr` on `/dev/sda3`.
- Filesystems: ext4 `USR-A` and `ROOT` labels with fixed test UUIDs.
- Empty applications element.

Research relevance: regression oracle for CoreOS-specific inspection fields, labels, and split `/usr` layout.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/expected-coreos.img.xml -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/expected-debian.img.xml -->
# File Research: sources/virtualization/guestfs-tools/inspector/expected-debian.img.xml

Expected inspector output for a Debian test image.

Contents:
- Root: `/dev/debian/root`
- OS: Linux, Debian, x86_64
- Product: `5.0.1`
- Package format/manager: `deb` / `apt`
- Hostname: `debian.invalid`
- osinfo: `debian5`
- Mountpoints include `/`, `/usr`, `/var`, `/boot`, `/home`.
- Filesystems are ext2 LVs plus `/dev/sda1` labeled `BOOT`, with fixed test UUIDs.
- Applications include three test packages with version, release, arch, URL, source package, summary, and multiline description.

Research relevance: regression oracle for Debian inspection, LVM mountpoint mapping, labels, package metadata, and multiline description serialization.
<!-- END FILE RESEARCH: sources/virtualization/guestfs-tools/inspector/expected-debian.img.xml -->