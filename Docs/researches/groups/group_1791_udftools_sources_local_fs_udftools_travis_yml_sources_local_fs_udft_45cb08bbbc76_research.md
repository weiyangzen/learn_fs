# Group Research: group_1791_udftools_sources_local_fs_udftools_travis_yml_sources_local_fs_udft_45cb08bbbc76

Scope verified against `Docs/research_subset_a.md`: `sources/local-fs/udftools` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/.travis.yml -->
# File Research: sources/local-fs/udftools/.travis.yml

Travis CI matrix for broad portability coverage of the C/autotools project.

It builds across:
- GCC 4.4 through 8, plus default distro GCC.
- Clang 3.3 through 7, plus default distro Clang.
- TinyCC on 64-bit Ubuntu variants.
- Ubuntu `precise`, `trusty`, `xenial`, `bionic`, and `focal`.
- `x86`, `x86_64`, `x32`, `powerpc`, and `arm` targets.

For 32-bit jobs it installs `:i386` readline/libc packages and multilib compilers. For cross-compiled PowerPC/ARM jobs it installs cross compilers and `qemu-user`, sets `--host`, static linking, and a QEMU runner variable.

Build script flow:
- Selects fallback compiler name if requested compiler binary is missing.
- Sets strict `CFLAGS`: `-W -Wall -Werror -g`, optionally `-O2`, with compiler-version-specific exceptions.
- Adds `-pedantic` except for old GCC cases where it is not usable as an error.
- Runs `./autogen.sh`, `./configure $CONFIGURE_FLAGS`, then `make`.

Special path:
- A Coverity Scan job runs only on master non-PR builds with an encrypted token and Coverity addon configuration.
- Normal script exits early if `COVERITY_SCAN_TOKEN` is present, letting Travis Coverity integration drive the build.

Notable details:
- CI intentionally tests old compilers and obsolete Ubuntu releases using old-release apt sources.
- The matrix stresses warning cleanliness, portability, and endian/word-size cases more than runtime tests.
<!-- END FILE RESEARCH: sources/local-fs/udftools/.travis.yml -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/Makefile.am -->
# File Research: sources/local-fs/udftools/Makefile.am

Top-level Automake orchestration.

Builds subdirectories in this order:
`libudffs`, `mkudffs`, `cdrwtool`, `pktsetup`, `udffsck`, `udfinfo`, `udflabel`, `wrudf`, and `doc`.

Installs documentation files through `dist_doc_DATA`: `AUTHORS`, `COPYING`, `NEWS`, and `README`.

Adds `autogen.sh` and `Doxyfile` to the distribution tarball through `EXTRA_DIST`.

No runtime behavior; this is root build/distribution glue.
<!-- END FILE RESEARCH: sources/local-fs/udftools/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/autogen.sh -->
# File Research: sources/local-fs/udftools/autogen.sh

Short bootstrap script for regenerating autotools files.

Flow:
- Removes `autom4te.cache` and generated `libtool` trees.
- Runs `aclocal`.
- Runs `libtoolize --force --copy`.
- Runs `autoheader`.
- Runs `automake --add-missing --copy`.
- Runs `autoconf`.

No argument parsing or error handling beyond shell command exit behavior.
<!-- END FILE RESEARCH: sources/local-fs/udftools/autogen.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/cdrwtool/Makefile.am -->
# File Research: sources/local-fs/udftools/cdrwtool/Makefile.am

Builds the `cdrwtool` binary.

Sources include local cdrwtool files:
- `main.c`
- `options.c`
- `cdrwtool.c`
- `options.h`
- `cdrwtool.h`

It also directly compiles mkudffs implementation files:
- `../mkudffs/mkudffs.c`
- `../mkudffs/defaults.c`
- `../mkudffs/file.c`

Links against `$(top_builddir)/libudffs/libudffs.la` and includes headers from `$(top_srcdir)/include`.

Key role: makes `cdrwtool` a CD-RW/DVD formatting tool that can also build/write UDF structures by reusing mkudffs internals.
<!-- END FILE RESEARCH: sources/local-fs/udftools/cdrwtool/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/cdrwtool/cdrwtool.c -->
# File Research: sources/local-fs/udftools/cdrwtool/cdrwtool.c

Implements low-level MMC/SCSI CD/DVD writer operations through Linux `CDROM_SEND_PACKET` ioctls.

Main capabilities:
- Build and send generic packet commands with optional request-sense reporting.
- Poll `TEST_UNIT_READY` after long operations and report progress from sense data.
- Read and set write-parameter mode pages.
- Write blocks with `GPCMD_WRITE_10`.
- Blank rewritable media.
- Format media using modern FORMAT UNIT code 1, with fallback to legacy code 7.
- Read disc and track/rzone information.
- Reserve tracks, close tracks, and close sessions.
- Read drive buffer capacity.
- Set CD write speed.
- Lock/unlock drive door and validate media status.
- Print disc/track/write-parameter summaries.

Important helpers:
- `wait_cmd_sense` and `wait_cmd` centralize packet ioctl setup.
- `wait_for_unit_ready` handles long blank/format/close completion.
- `set_write_mode` edits mode page 5 fields from `write_params_t`.
- `make_write_page` translates `struct cdrw_disc` CLI settings into write mode fields.
- `cdrw_init_disc` sets defaults: fixed packets, 32-block packets, mode 2, speed 12x.

Dependencies:
- Linux CD-ROM headers and ioctls.
- Endian helpers from `libudffs.h`.
- Shared `struct cdrw_disc` and `write_params_t` from `cdrwtool.h`.

Notable quirks:
- `get_write_mode` reconstructs only one byte of `packet_size` from the four-byte mode-page field.
- Fixed-packet file tail padding uses `memset(&buf[ret], 0, size - ret - 1)`, leaving one byte outside the zero-fill range.
- Numeric device/media inputs are trusted after parsing; most validation relies on the drive rejecting invalid packet commands.
<!-- END FILE RESEARCH: sources/local-fs/udftools/cdrwtool/cdrwtool.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/cdrwtool/cdrwtool.h -->
# File Research: sources/local-fs/udftools/cdrwtool/cdrwtool.h

Shared declarations and data layouts for `cdrwtool`.

Defines:
- Default CD-ROM device path: `/dev/scd1`.
- Command wait timeouts for packet commands, sync, blank/format.
- Immediate-operation policy macros.
- Blank modes, write modes, CD-ROM block size, packet size, and default speed.
- `write_params_t`, representing MMC write-parameter page fields.
- `struct cdrw_disc`, the CLI/runtime state for device actions and embedded `struct udf_disc`.

Packed-ish drive data structures:
- `disc_info_t`
- `track_info_t`
- `opc_table_t`
- `disc_capacity_t`

The disc and track info structures use endian-sensitive bitfield layouts gated by `WORDS_BIGENDIAN`.

Exports all cdrwtool operations used by `main.c` and `options.c`, including mode sense/select, blank/format, write, reserve/close, speed, info printing, and initialization.

Key role: bridges user options, Linux cdrom packet commands, and UDF generation state.
<!-- END FILE RESEARCH: sources/local-fs/udftools/cdrwtool/cdrwtool.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/cdrwtool/main.c -->
# File Research: sources/local-fs/udftools/cdrwtool/main.c

Main program for `cdrwtool`.

Startup flow:
- Initializes `struct cdrw_disc`, embedded `struct udf_disc`, and default UDF revision 1.50.
- Parses command-line options.
- Opens the CD/DVD device read-write nonblocking, falling back to read-only for `EROFS`.
- Installs a UDF writer callback that writes full 32-block packets through `write_blocks`.
- Validates media and drive locking.
- Reads buffer capacity and current write mode.
- Sets write speed.
- Dispatches exactly one requested operation.

Supported dispatch paths:
- Print write parameters and/or disc/track info.
- Set write mode.
- Close track or session.
- Quick setup.
- Blank disc.
- Format disc.
- Write a UDF session.
- Write an arbitrary file.
- Reserve a track.

`quick_setup` is the destructive high-level setup path:
- Prompts the user before proceeding.
- Fast blanks the disc.
- Reads disc/track geometry.
- Computes capacity from lead-out MSF data.
- Formats fixed-packet media or reserves a variable-packet track.
- Configures sparable partitioning and UDF allocation bitmap defaults.
- Builds VRS, anchors, partitions, VDS, and writes UDF structures to the disc.

`mkudf_session` is a narrower UDF-writing path using an explicit block count.

Notable details:
- `write_func` batches UDF descriptor/data writes into 32-block packets for packet media.
- The quick setup path sets the application identifier to `*Linux cdrwtool <version>`.
- Device lock cleanup is attempted before every return path after opening.
<!-- END FILE RESEARCH: sources/local-fs/udftools/cdrwtool/main.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/cdrwtool/options.c -->
# File Research: sources/local-fs/udftools/cdrwtool/options.c

Command-line parser for `cdrwtool`.

Defines long and short options for:
- Help.
- Device selection.
- Get/set write parameters.
- Blank mode: `full` or `fast`.
- Format block count.
- Run mkudffs on a track.
- UDF revision selection.
- Write speed.
- Fixed/variable packet mode.
- Quick setup with optional block count.
- Reserve track.
- Close track/session.
- Packet size.
- Border/session setting.
- Write type: `mode1` or `mode2`.
- Input file and write offset.
- Detailed disc info.

`usage` prints package name/version and iterates the long option table.

`parse_args` mutates `struct cdrw_disc` and device path directly. Most numeric values are parsed with `strtol`/`strtoul`. UDF revision is bounded to `0x0150` through `0x0201` and checked with `udf_set_version`.

Notable quirks:
- Long option names include spaces, matching historical usage text more than conventional GNU long-option style.
- Most numeric options have no range or trailing-character validation.
- The short option string includes `C` for close session even though the long option table only maps `"close track"` to `c`.
<!-- END FILE RESEARCH: sources/local-fs/udftools/cdrwtool/options.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/cdrwtool/options.h -->
# File Research: sources/local-fs/udftools/cdrwtool/options.h

Small public header for `cdrwtool` option handling.

Declares:
- `usage(void)`
- `parse_args(int, char *[], struct cdrw_disc *, const char **)`

Includes `<getopt.h>` for option handling.

Defines `OPT_HELP` as a long-option token in the `0x1000` range. Comments reserve token ranges for short options, long switches, and long settings.

No runtime logic.
<!-- END FILE RESEARCH: sources/local-fs/udftools/cdrwtool/options.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/configure.ac -->
# File Research: sources/local-fs/udftools/configure.ac

Autoconf input for udftools version `2.3`.

Configuration responsibilities:
- Requires Autoconf 2.64.
- Initializes package metadata and `include/config.h`.
- Enables Automake and Libtool.
- Requires a C99-capable compiler.
- Disables shared libraries.
- Checks for `ln -s` and `mkdir -p`.
- Detects readline through pkg-config first, falling back to `AC_CHECK_LIB` and header checks.
- Checks inline support, endian layout, and large-file support.
- Detects udev via pkg-config and exposes `UDEVDIR`.
- Defines Automake conditionals for readline and udev support.

Generated Makefiles:
- Root
- `libudffs`
- `mkudffs`
- `cdrwtool`
- `pktsetup`
- `udffsck`
- `udfinfo`
- `udflabel`
- `wrudf`
- `doc`

Key role: central portability/build feature detection for all tools.
<!-- END FILE RESEARCH: sources/local-fs/udftools/configure.ac -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/include/bswap.h -->
# File Research: sources/local-fs/udftools/include/bswap.h

Endian conversion helper header.

Provides:
- Constant byte-swap macros for 16/32/64-bit values.
- Inline byte-swap functions for 16/32/64-bit values.
- Pointer-based byte-swap macros/functions.
- `le*_to_cpu`, `be*_to_cpu`, `cpu_to_le*`, and `cpu_to_be*` families.
- Constant and pointer variants of those conversions.

Behavior is controlled by `WORDS_BIGENDIAN` from `config.h`:
- On big-endian hosts, little-endian conversions swap and big-endian conversions are identity.
- On little-endian hosts, little-endian conversions are identity and big-endian conversions swap.

Key role: keeps on-disk UDF/ECMA little-endian structures portable across host architectures.

Notable detail: pointer helpers cast directly to integer pointers, so callers must be aware of alignment/aliasing constraints.
<!-- END FILE RESEARCH: sources/local-fs/udftools/include/bswap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/include/ecma_167.h -->
# File Research: sources/local-fs/udftools/include/ecma_167.h

Packed on-disk structure definitions based on ECMA-167 3rd edition.

Defines core ECMA/UDF building blocks:
- `dchars`, `dstring`, `charspec`, `timestamp`, `regid`.
- Volume Structure Descriptors and standard identifiers.
- Boot descriptors.
- Extent descriptors and descriptor tags.
- Volume descriptor sequence structures: PVD, AVDP, VDP, IUVD, PD, LVD, USD, TD, LVID.
- Partition maps.
- Logical block addresses and short/long/extended allocation descriptors.
- File set descriptors.
- Partition header descriptors.
- File identifier descriptors.
- ICB tags, indirect/terminal entries.
- File entries and extended file entries.
- Extended attribute structures.
- Space bitmap and unallocated space entries.
- Allocation extent flags and file permission constants.

Most structures are marked `packed, may_alias` to match disk layout and tolerate byte-level access.

Key role: authoritative local representation of ECMA-167 disk descriptors used by mkudffs, libudffs, cdrwtool, and related utilities.

No functions or behavior; this is format vocabulary.
<!-- END FILE RESEARCH: sources/local-fs/udftools/include/ecma_167.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/include/libudffs.h -->
# File Research: sources/local-fs/udftools/include/libudffs.h

Main shared libudffs header.

Defines filesystem construction flags:
- Space accounting variants: freed/unallocated bitmap/table.
- Character encoding modes.
- Strategy 4096 and blank-terminal behavior.
- Closed/VAT/EFE/no-write modes.
- Boot-area preserve/erase/MBR modes.

Defines the in-memory UDF planning model:
- `struct udf_disc`: global UDF build state, descriptor pointers, partition maps, VAT state, metadata maps, root extent list, write callback, IDs, permissions, and counters.
- `struct udf_extent`: typed contiguous block range in the build plan.
- `struct udf_desc`: descriptor attached to an extent.
- `struct udf_data`: payload list for a descriptor.

Defines MBR boot-area structures and constants.

Exports APIs implemented by:
- `crc.c`: `udf_crc`.
- `extent.c`: extent/descriptor/data list management.
- `unicode.c`: encode/decode helpers for UDF strings.
- `misc.c`: app name, UUID extraction, strict integer parsing, random value, EINTR-safe I/O.

Key role: common contract between mkudffs, cdrwtool, and libudffs.
<!-- END FILE RESEARCH: sources/local-fs/udftools/include/libudffs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/include/osta_udf.h -->
# File Research: sources/local-fs/udftools/include/osta_udf.h

Packed UDF-specific definitions based on OSTA UDF 2.60.

Defines:
- UDF compressed Unicode charspec constants.
- Standard entity identifier strings.
- Identifier suffix layouts for domain, UDF, implementation, and application IDs.
- Logical Volume Integrity implementation-use structure.
- Implementation Use Volume Descriptor implementation-use structure.
- UDF type 2 partition maps.
- Virtual, sparable, and metadata partition maps.
- VAT layouts for UDF 1.50 and UDF 2.00+.
- Sparing table and sparing entry layouts.
- Metadata file type constants.
- Allocation descriptor implementation-use flags.
- UDF-specific strategy and real-time file type constants.
- UDF-defined extended attributes.
- UDF-defined stream identifiers.
- OS class and OS identifier constants, including Linux/FreeBSD/NetBSD values.

Key role: supplements ECMA-167 with UDF profile-specific identifiers and structures required by mkudffs and UDF metadata tools.

No runtime behavior.
<!-- END FILE RESEARCH: sources/local-fs/udftools/include/osta_udf.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/libudffs/Makefile.am -->
# File Research: sources/local-fs/udftools/libudffs/Makefile.am

Builds internal Libtool library `libudffs.la`.

Sources:
- `crc.c`
- `extent.c`
- `misc.c`
- `unicode.c`
- shared headers from `../include`

Links `@LTLIBOBJS@` and uses `-I$(top_srcdir)/include`.

Key role: shared non-installed library for UDF CRCs, extent planning, encoding, and miscellaneous helpers.
<!-- END FILE RESEARCH: sources/local-fs/udftools/libudffs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/libudffs/crc.c -->
# File Research: sources/local-fs/udftools/libudffs/crc.c

Implements UDF CRC-16 calculation.

Core behavior:
- Uses a static 256-entry table for the ITU-T V.41 polynomial used by OSTA UDF.
- `udf_crc(data, size, crc)` iterates bytes and updates the supplied CRC seed.

The file also contains optional `TEST` and `GENERATE` compile-time sections:
- `TEST` contains a small hard-coded CRC check.
- `GENERATE` can generate a CRC table for a supplied polynomial.

Key role: descriptor CRC computation for UDF tags and descriptor bodies.
<!-- END FILE RESEARCH: sources/local-fs/udftools/libudffs/crc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/libudffs/extent.c -->
# File Research: sources/local-fs/udftools/libudffs/extent.c

Implements in-memory extent, descriptor, and data-list management for UDF construction.

The file begins with an extensive explanation of:
- Volume space versus partition space.
- ECMA on-disk extents versus in-memory `udf_extent`.
- How extents, descriptors, and data payloads compose the planned output.

Main functions:
- `next_extent`, `prev_extent`: scan extent lists by space type.
- `next_extent_size`, `find_next_extent_size`, `prev_extent_size`: find aligned free/typed extents of sufficient size.
- `find_extent`: find the extent containing a block.
- `set_extent`: split existing extents and assign a type to a requested range.
- `remove_extent`: unlink and free an extent.
- `next_desc`, `find_desc`, `set_desc`: maintain ordered descriptor lists within an extent.
- `append_data`: append payloads to a descriptor and grow length.
- `alloc_data`: allocate a `udf_data` wrapper and optional zeroed payload.

Error handling:
- Allocation failures and out-of-space conditions print with `appname` and call `exit(1)`.

Key role: shared allocator/planner primitive used heavily by mkudffs structure generation.
<!-- END FILE RESEARCH: sources/local-fs/udftools/libudffs/extent.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/libudffs/misc.c -->
# File Research: sources/local-fs/udftools/libudffs/misc.c

Shared utility functions for udftools.

Defines global `const char *appname` used by error reporting.

Functions:
- `gen_uuid_from_vol_set_ident`: decodes the UDF Volume Set Identifier and derives a 16-byte text UUID-like value from its first characters, with fallback byte-hex encoding when non-hex characters appear.
- `strtou32`: strict unsigned 32-bit parser using signed `strtoll` to catch underflow and leading whitespace.
- `strtou16`: strict unsigned 16-bit parser layered on `strtou32`.
- `randu32`: reads from `/dev/urandom` when possible, otherwise seeds and combines libc `rand`.
- `read_nointr`: retries `read` on `EINTR`.
- `write_nointr`: retries `write` on `EINTR`.

Notable behavior:
- The I/O wrappers retry only interrupted calls; they do not loop to satisfy a full requested byte count.
- `randu32` is suitable for identifiers, not cryptographic protocol guarantees.
<!-- END FILE RESEARCH: sources/local-fs/udftools/libudffs/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/libudffs/unicode.c -->
# File Research: sources/local-fs/udftools/libudffs/unicode.c

UDF compressed Unicode and d-string conversion routines.

Functions:
- `decode_utf8`: decodes UDF compressed Unicode with compression ID 8 or 16 into UTF-8, including UTF-16 surrogate handling.
- `encode_utf8`: encodes UTF-8 input into UDF compressed Unicode, choosing 8-bit compression when possible and 16-bit otherwise.
- `decode_locale`: decodes UDF compressed Unicode into the current locale via wide-character conversion.
- `encode_locale`: encodes current-locale strings into UDF compressed Unicode.
- `decode_string`: decodes ECMA d-strings using the encoding flags on `struct udf_disc`.
- `encode_string`: encodes into ECMA d-string format and stores the payload length in the final field byte.

Supported output/input modes are controlled by `FLAG_UTF8`, `FLAG_LOCALE`, `FLAG_UNICODE8`, and `FLAG_UNICODE16`.

Error behavior:
- Buffer-size and invalid-format cases generally return `(size_t)-1`.
- Some invalid locale/UTF-8 conversion cases print an error with `appname` and exit.

Key role: all label, identifier, and file-name encoding/decoding for UDF descriptors.
<!-- END FILE RESEARCH: sources/local-fs/udftools/libudffs/unicode.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/mkudffs/Makefile.am -->
# File Research: sources/local-fs/udftools/mkudffs/Makefile.am

Builds the `mkudffs` sbin program.

Sources:
- `main.c`
- `mkudffs.c`
- `defaults.c`
- `file.c`
- `options.c`
- local headers
- shared ECMA/OSTA/libudffs headers

Links against `$(top_builddir)/libudffs/libudffs.la`.

Includes shared headers from `$(top_srcdir)/include`.

Install hooks:
- Creates `mkfs.udf` symlink to `mkudffs` in `sbindir`.
- Removes that symlink on uninstall.

Key role: build and install compatibility glue for the UDF filesystem creation tool.
<!-- END FILE RESEARCH: sources/local-fs/udftools/mkudffs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/mkudffs/defaults.c -->
# File Research: sources/local-fs/udftools/mkudffs/defaults.c

Static default templates for mkudffs.

Defines:
- `default_media`: maps media type enum values to default sizing/profile groups.
- `default_sizing`: alignment, proportional sizing, and minimum-size rules for VDS, LVID, sparing table, sparing space, and partition space across media classes.
- Default primary volume descriptor.
- Default logical volume descriptor.
- Default implementation-use descriptor payload.
- Default unallocated space descriptor.
- Default terminating descriptor.
- Default logical volume integrity descriptor and implementation-use payload.
- Default sparing table and sparable partition map.
- Default VAT 1.50 and VAT 2.00+ structures.
- Default virtual partition map.
- Default file set descriptor.
- Default file entry and extended file entry.
- Default implementation-use extended attribute.
- Default MBR with one IFS partition entry and boot signature.

Most multi-byte fields are initialized with constant endian-conversion macros so templates are already in on-disk byte order.

Key role: central source of canonical descriptor defaults copied and customized by mkudffs generation code.
<!-- END FILE RESEARCH: sources/local-fs/udftools/mkudffs/defaults.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/mkudffs/defaults.h -->
# File Research: sources/local-fs/udftools/mkudffs/defaults.h

Declarations for mkudffs default templates.

Exports:
- Default media mapping and sizing tables.
- Descriptor templates for PVD, LVD, IUVD, PD, USD, TD, LVID, sparing table, partition maps, VATs, FSD, FE/EFE, implementation-use extended attributes.
- Default MBR template.

No logic; consumers copy these structures and patch per-filesystem values.
<!-- END FILE RESEARCH: sources/local-fs/udftools/mkudffs/defaults.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/mkudffs/file.c -->
# File Research: sources/local-fs/udftools/mkudffs/file.c

Implements mkudffs file, directory, extended-attribute, and allocation helpers.

Descriptor tagging:
- `query_tag` computes descriptor tags for existing `udf_desc` objects, including CRC and tag checksum.
- `udf_query_tag` computes a descriptor tag from raw components and a data list.

Directory/FID insertion:
- `insert_desc` appends a FID payload to a directory, either in-ICB or through short/long allocation descriptors.
- `insert_fid` builds a File Identifier Descriptor, sets ICB references, copies unique ID low bits into allocation descriptor implementation-use data, updates link counts, and updates parent sizes.
- `compute_ident_length` pads FID length to a four-byte boundary.

File/data creation:
- `insert_data` appends data to in-ICB FE/EFE files and updates information/object sizes.
- `udf_create` allocates blocks, creates FE or EFE descriptors, initializes timestamps and unique IDs, sets file type/flags, inserts into parent directories, and increments LVID file/dir counters.
- `udf_mkdir` wraps `udf_create` for directories and creates the unnamed parent backlink entry.

Extended attributes:
- `insert_ea` adds ECMA extended attributes in the required ordering groups: ECMA-defined, implementation-use, and application-use.
- It creates the EA header when needed, maintains implementation/application attribute offsets, handles UDF 1.50 offset semantics, and retags the EA header.

Allocation helpers:
- Implements bit scanning helpers for UDF space bitmaps.
- `udf_alloc_bitmap_blocks` finds aligned free runs in bitmap descriptors and clears bits to allocate.
- `udf_alloc_table_blocks` consumes or splits short allocation descriptors in unallocated/freed space tables.
- `udf_alloc_blocks` updates LVID free-space count and dispatches allocation through freed bitmap/table, unallocated bitmap/table, or VAT append mode.

Key role: constructs the file-tree-level UDF metadata used for root directories, VAT files, stream-like objects, and allocation accounting.

Notable details:
- Supports both FE and EFE paths behind `FLAG_EFE`.
- Supports strategy 4096 by allocating two blocks and using strategy type 4096 metadata.
- Allocation failures are fatal.
<!-- END FILE RESEARCH: sources/local-fs/udftools/mkudffs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/mkudffs/file.h -->
# File Research: sources/local-fs/udftools/mkudffs/file.h

Header for mkudffs file/directory helpers.

Declares:
- Tag query helpers.
- File and directory creation APIs.
- Data, FID, and extended-attribute insertion APIs.
- Block allocation API.

Inline helpers:
- `clear_bits`: clears a run of bits in a space bitmap.
- `query_iuvdiu`: returns the implementation-use payload inside the first IUVD.
- `query_lvidiu`: returns the implementation-use payload inside the LVID after free-space and size tables.

Key role: exposes file-level UDF construction utilities to mkudffs generation code.
<!-- END FILE RESEARCH: sources/local-fs/udftools/mkudffs/file.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/udftools/mkudffs/main.c -->
# File Research: sources/local-fs/udftools/mkudffs/main.c

Main program and output writer for `mkudffs`.

Device/image probing:
- `valid_offset` checks whether a byte offset can be read.
- `get_blocks` determines block count from explicit options, block ioctls, floppy ioctls, regular file size, or binary search over readable offsets.
- `detect_blocksize` uses `BLKSSZGET` to choose a suitable logical block size when not specified.
- `is_whole_disk` inspects sysfs to distinguish whole block devices from partitions or stacked devices.
- `is_removable_disk` reads sysfs `removable`.

Writing:
- `write_func` iterates planned extents and descriptors.
- It seeks to descriptor block offsets, concatenates descriptor data payloads, block-aligns them, writes unless `FLAG_NO_WRITE` is set, and optionally zeroes reserved/unallocated boot-area ranges unless boot-area preservation is requested.

Main flow:
- Ensures standard fds exist.
- Sets locale.
- Initializes `struct udf_disc`.
- Parses command-line options.
- Opens the target device/image with `O_EXCL`.
- Determines block size and block count.
- Selects default boot-area behavior: preserve, MBR, or erase.
- Prints target metadata: filename, label, UUID, block size, block count, UDF revision, and optional start block.
- Calls generation helpers: `split_space`, `setup_mbr`, `setup_vrs`, `setup_anchor`, `setup_partition`, and `setup_vds`.
- Prints VAT block if present and dumps space layout.
- Emits warnings for tiny filesystems, weak Volume Set Identifier UUID data, and partition-target Apple compatibility.
- Creates a new image file when the target does not exist and block count was specified.
- Writes the built UDF structures, fsyncs, and closes.

Key role: ties CLI options, device geometry, filesystem layout generation, and final output I/O into the `mkudffs` executable.
<!-- END FILE RESEARCH: sources/local-fs/udftools/mkudffs/main.c -->