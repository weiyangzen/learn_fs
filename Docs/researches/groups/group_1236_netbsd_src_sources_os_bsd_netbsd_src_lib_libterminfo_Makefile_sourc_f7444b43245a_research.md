# Group Research: group_1236_netbsd_src_sources_os_bsd_netbsd_src_lib_libterminfo_Makefile_sourc_f7444b43245a

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Read verification matched the prompt for all 29 listed files, totaling 9,590 lines.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/Makefile

Builds NetBSD `libterminfo`, installing `term.h` into `/usr/include` and building the core source set `term.c`, `ti.c`, `setupterm.c`, `curterm.c`, `tparm.c`, `tputs.c`, plus generated `hash.c`.

When `SMALLPROG` is not defined, it enables `TERMINFO_COMPILE`, `TERMINFO_DB`, and `TERMINFO_COMPAT`, adding `compile.c` so the library can read CDB terminfo databases and compile environment-provided descriptions. Small-program builds intentionally depend only on embedded compiled terminal descriptions.

It always builds termcap compatibility through `termcap.c`, installs `termcap.h`, and creates library symlinks for `libtermcap` and `libtermlib` variants pointing at `libterminfo`.

It includes `Makefile.hash` for generated hash/compiled terminal artifacts and generates `terminfo.5` from `genman`, `terminfo.5.in`, `term.h`, and `termcap_map.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/compile.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/compile.c

Implements in-library compilation of textual terminfo entries into the private `TIC` representation, then flattens that representation into the binary format consumed by `term.c`.

Key routines include `_ti_compile`, `_ti_flatten`, `_ti_freetic`, `_ti_get_token`, `_ti_grow_tbuf`, `_ti_find_cap`, `_ti_find_extra`, `_ti_store_extra`, and encoding helpers for indexed flags, numbers, and strings.

The parser recognizes terminfo header name/alias/description fields, boolean tokens, numeric tokens using `#`, string tokens using `=`, cancellation via trailing `@`, comments/obsolete `OT` fields, and optional user-defined capabilities controlled by `TIC_EXTRA`.

`encode_string` translates terminfo escapes, control notation, octal escapes, newline folding, and escaped delimiters into stored NUL-terminated strings. It warns on invalid/unprintable forms when `TIC_WARNING` is set.

With `TERMINFO_COMPAT`, `_ti_promote` upgrades old v1 entries to v3 when numeric values exceed 16-bit storage, preserving aliases and extras with the version suffix naming scheme.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/compile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/curterm.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/curterm.c

Maintains the global current terminal state for the classic terminfo API: `cur_term`, `ttytype`, `ospeed`, and `PC` integration.

`_ti_setospeed` maps `termios` output speed from a file descriptor into the legacy short speed index used by padding code.

`set_curterm` swaps the global `cur_term`, updates padding globals, computes output speed, and fills `ttytype` with name, aliases, and description for ncurses-compatible consumers.

`del_curterm` frees all dynamically allocated terminal storage, including decoded area, arrays, user definitions, parameter buffer, and the `TERMINAL` object itself.

`termname` and `longname` return the current terminal name and description, with `longname` returning an empty string if no description is stored.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/curterm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/genhash -->
# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/genhash

Shell generator for `hash.c`, deriving perfect-hash lookup tables from `term.h`.

For each capability class, it extracts `enum TIFLAG`, `enum TINUM`, and `enum TISTR` `TICODE_*` names, emits `_ti_flagids`, `_ti_numids`, and `_ti_strids`, and invokes `nbperf` to generate hash functions.

The generated C exposes `_ti_flagid/_ti_numid/_ti_strid` for index-to-name lookup and `_ti_flagindex/_ti_numindex/_ti_strindex` for name-to-index lookup.

Inputs default to `term.h`; tools are configurable through `TOOL_AWK`, `TOOL_NBPERF`, and `TOOL_SED`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/genhash -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/genman -->
# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/genman

Shell generator for the installed `terminfo.5` manual page.

It reads `terminfo.5.in`, `term.h`, and `termcap_map.c`, builds sorted tables of boolean, numeric, and string capabilities, and substitutes `@BOOLCAPS@`, `@NUMCAPS@`, and `@STRCAPS@` placeholders.

For each long capability name, it derives the `TICODE_*` code, the corresponding two-character termcap code when one exists, and the description comment embedded near the public macro in `term.h`.

The output is an mdoc page marked as generated.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/genman -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/genterms -->
# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/genterms

Shell generator for embedded compiled terminal descriptions used as built-in fallbacks by `term.c`.

It emits a generated C header preamble and runs `tic -Sx` against the NetBSD terminfo source database for a fixed small set: `ansi`, `dumb`, `vt100`, `vt220`, `wsvt25`, and `xterm`.

Inputs are controlled by `TOOL_TIC`, `NETBSDSRCDIR`, and `TERMINFO`.

This is central to small or rescue-style builds where runtime database access is absent or disabled.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/genterms -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/genthash -->
# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/genthash

Shell generator for `termcap_hash.c`, the perfect-hash support file for two-character termcap compatibility lookups.

It extracts IDs from `_ti_cap_flagids`, `_ti_cap_numids`, and `_ti_cap_strids` arrays in `termcap_map.c`, then invokes `nbperf` to create `_t_flaghash`, `_t_numhash`, and `_t_strhash`.

The generated file includes only private terminfo dependencies and is consumed by `termcap.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/genthash -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/setupterm.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/setupterm.c

Implements terminal setup entry points `ti_setupterm`, `setupterm`, and the curses-facing `use_env`.

`ti_setupterm` resolves the terminal name from its argument or `$TERM`, allocates a `TERMINAL`, loads its definition with `_ti_getterm`, sets file descriptor and output speed, rejects generic/hardcopy terminals, and initializes `lines`/`columns`.

Window size comes first from `TIOCGWINSZ`; when `use_env(true)` is active, `LINES` and `COLUMNS` override POSIX-style.

Error handling follows terminfo conventions: when `errret` is null, failures call `errx`; otherwise they store status codes and return `ERR`.

`setupterm` wraps `ti_setupterm` and installs the result as `cur_term`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/setupterm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/term.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/term.c

Loads compiled terminal descriptions into a `TERMINAL` object.

`_ti_readterm` decodes private binary terminfo records, allocating/resetting boolean, numeric, string, and user-defined capability arrays, and normalizing absent/cancelled values when requested.

With `TERMINFO_DB`, `_ti_dbgetterm` opens CDB databases, first trying `<path>.cdb` and then raw `<path>`, follows alias records, validates the requested name against stored aliases, and records `_ti_database`.

With `TERMINFO_COMPILE`, `_ti_findterm` can compile `$TERMINFO` or translated `$TERMCAP` environment values directly before consulting `$TERMINFO_DIRS`, `$HOME/.terminfo`, and `/usr/share/misc/terminfo`.

`_ti_getterm` prefers v3-compatible names under `TERMINFO_COMPAT`, then normal lookup, then embedded `compiled_terms`.

This file is the main bridge between external terminfo storage, embedded fallbacks, and the public accessor APIs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/term.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/term.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/term.h

Public terminfo header defining return constants, capability indexes, public access macros, `TERMINAL` exposure, and exported APIs.

It defines three large capability enums: `TIFLAGS`, `TINUMS`, and `TISTRS`, with maxima `TIFLAGMAX`, `TINUMMAX`, and `TISTRMAX`.

For each capability, it provides terminal-specific macros such as `t_columns(t)` and global-current macros such as `columns`, mapping through `cur_term`.

It declares the classic APIs: `setupterm`, `set_curterm`, `del_curterm`, `termname`, `longname`, `tigetflag`, `tigetnum`, `tigetstr`, `tparm`, `tiparm`, `tputs`, `putp`, and termcap conversion `captoinfo`.

It also declares thread-friendlier NetBSD-specific `ti_*` forms that accept an explicit `TERMINAL *`, including `ti_setupterm`, `ti_getflag`, `ti_getnum`, `ti_getstr`, `ti_tiparm`, `ti_puts`, and `ti_putp`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/term.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/term_private.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/term_private.h

Private header shared by `libterminfo`, `tic`, and related tools.

Documents the internal terminfo binary format: type 1 old records, type 2 aliases, and type 3 records with 32-bit numeric capability storage. All database numbers are little-endian.

Defines sentinel values for absent and cancelled booleans, numerics, and strings, plus validation macros used across loaders and accessors.

Defines internal `TERMINAL`, `TERMUSERDEF`, `TBUF`, and `TIC` structures. `TERMINAL` intentionally exposes arrays so public macros in `term.h` can work.

Declares private lookup, compile, flatten, and parameter-analysis functions, and provides inline little-endian decode/encode helpers for record parsing and generation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/term_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/termcap.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/termcap.c

Implements termcap compatibility on top of the terminfo engine.

`tgetent` calls `setupterm`, manages the prior current terminal, and populates legacy globals `PC`, `UP`, and `BC`.

`tgetflag`, `tgetnum`, and `tgetstr` hash two-character termcap IDs through generated tables from `termcap_map.c`/`termcap_hash.c`, then fall back to user-defined capabilities.

`tgoto` delegates cursor parameter expansion to `tiparm` with termcap argument order converted to terminfo order.

Under `TERMINFO_COMPILE`, `captoinfo` translates colon-delimited termcap descriptions into comma-delimited terminfo descriptions, including padding conversion, termcap `%` command conversion, `tc` to `use`, and default basic control capabilities.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/termcap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/termcap.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/termcap.h

Public compatibility header for the historical termcap API.

Declares legacy globals `PC`, `ospeed`, `BC`, and `UP`.

Declares `tgetent`, `tgetflag`, `tgetnum`, `tgetstr`, `tgoto`, and `tputs`.

This header is intentionally small and forwards consumers into `libterminfo`’s compatibility layer rather than defining independent data structures.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/termcap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/termcap_map.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/termcap_map.c

Static mapping table source for termcap compatibility.

Defines `TENTRY` records mapping two-character termcap IDs to `TICODE_*` capability indexes for booleans, numerics, and strings.

Consumed directly by `termcap.c`, scanned by `genthash` to generate perfect hashes, and scanned by `genman` to populate termcap-code columns in `terminfo.5`.

This file is data-centric: behavior comes from the generated hashes and the lookup logic in `termcap.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/termcap_map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/terminfo.5.in -->
# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/terminfo.5.in

Template mdoc manual page for terminfo source syntax and NetBSD implementation details.

Documents entry layout, name/alias/description header lines, comma-separated capabilities, boolean/numeric/string forms, supported escapes, string length behavior, and delay syntax.

Documents parameter expansion commands such as `%p`, `%P`, `%g`, `%i`, arithmetic/logical operators, formatting forms, string length, and conditionals.

Contains placeholders for generated boolean, numeric, and string capability tables.

Documents NetBSD’s CDB-backed compiled description lookup, compatibility behavior for `.cdb` suffixes, `$TERMINFO`, `$TERMCAP`, `$TERMINFO_DIRS`, `$HOME/.terminfo`, and `/usr/share/misc/terminfo`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/terminfo.5.in -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/ti.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/ti.c

Provides direct capability accessor APIs.

`ti_getflag`, `ti_getnum`, and `ti_getstr` look up long terminfo names through generated `_ti_*index` functions, then search user-defined capabilities when the name is not built in.

`tigetflag`, `tigetnum`, and `tigetstr` wrap those routines using global `cur_term`.

Return conventions distinguish absent and cancelled capabilities using sentinel values from `term_private.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/ti.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/tparm.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/tparm.c

Implements terminfo parameter expansion for `tparm`, `tiparm`, and explicit-terminal `ti_tiparm`.

The core interpreter `_ti_tiparm` parses `%` commands, maintains a stack, supports numeric and string parameters, dynamic variables `a-z`, terminal-persistent static variables `A-Z`, arithmetic, bitwise and logical operations, formatting, `%i`, constants, string length, and nested conditionals.

`_ti_parm_analyse` pre-scans a string to determine which of up to nine parameters should be read as strings rather than integers.

Buffers are stored per `TERMINAL` when available; non-explicit APIs use a static `dumbterm`, preserving legacy non-thread-safe behavior.

Notable maintenance concern: stack bookkeeping is manual and safety depends on descriptor-controlled command streams staying within intended bounds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/tparm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/tputs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/tputs.c

Outputs terminal strings while honoring terminfo padding delays.

`_ti_calcdelay` parses leading or embedded delay syntax, including fractional tenths, affected-line multiplication via `*`, and mandatory delays via `/`.

`_ti_outputdelay` emits pad characters based on legacy output speed timing.

`_ti_puts` writes strings through a caller-provided output function and handles embedded `$<...>` delay markers.

`ti_puts` uses terminal-local speed and pad character, enabling delays for bell, flash, and terminals that need padding. `ti_putp`, `tputs`, and `putp` are compatibility wrappers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libterminfo/tputs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libukfs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libukfs/Makefile

Builds `libukfs`, the user-kernel filesystem access library.

Sources are `ukfs.c` and `ukfs_disklabel.c`; public header `ukfs.h` installs under `/usr/include/rump`.

Links against `librump`, `librumpvfs`, and `libpthread`, and compiles with `_KERNTYPES`.

Installs the `ukfs.3` manual page.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libukfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libukfs/ukfs.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libukfs/ukfs.c

Implements `libukfs`, allowing direct filesystem access through NetBSD rump kernels without normal host filesystem syscalls.

Core state lives in `struct ukfs`: mount pointer, rump LWP, optional caller-specific pointer, device fd, device/mount/cwd strings, and partition descriptor.

Mount flow initializes rump, optionally parses partition/offset suffixes, locks device file ranges, registers ETFS block devices, creates mount paths, mounts the requested VFS, creates a dedicated rump LWP, and stores cwd state.

Partition support recognizes `%DISKLABEL:<letter>%` and `%OFFSET:start,end%`, with `%PART` explicitly rejected as deprecated. Disklabel probing reads early device bytes and uses `ukfs_disklabel.c`.

Most file operations wrap rump syscalls after `PRECALL`, which switches into the filesystem’s rump LWP context, chroots to the mount path, and restores the previous LWP afterward. APIs cover directory iteration, open/read/write/close, create, mknod, fifo, mkdir, remove, rmdir, link, symlink, readlink, rename, chdir, stat/lstat, chmod/chown/chflags, and times.

It also supports dynamic rump filesystem module loading with `dlopen`, retrying deferred loads to satisfy dependencies, and querying supported VFS types via rump `sysctl`.

Important coupling: callers must respect `ukfs_release` semantics for unmounting, ETFS removal, device lock release, LWP release, and partition refcount cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libukfs/ukfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libukfs/ukfs.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libukfs/ukfs.h

Public API for `libukfs`.

Defines opaque types `struct ukfs`, `struct ukfs_dircookie`, and `struct ukfs_part`, the default mount path `/ukfs`, release flags, and ABI versioning through `UKFS_VERSION` plus `ukfs_init()`.

Declares mounting APIs for generic mounts and disk-backed mounts, lifecycle release, directory APIs, file I/O APIs, creation/removal/linking APIs, metadata mutation and query APIs, and cwd support.

Exposes partition helpers and magic suffix constants for disklabel and offset probing, including `UKFS_DEVICE_ARGVPROBE` for command-line device argument handling.

Also declares module loading, VFS type enumeration, mount pointer access, caller-specific storage, and recursive directory creation utility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libukfs/ukfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libukfs/ukfs_disklabel.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libukfs/ukfs_disklabel.c

Contains local copies of disklabel scanning and checksum routines so `libukfs` does not depend on NetBSD-only `libutil`.

`ukfs__disklabel_scan` scans a buffer in 4-byte increments for matching disklabel magic values in native or byte-swapped order, validates partition count, and verifies checksum.

`ukfs__disklabel_dkcksum` computes the XOR checksum over the disklabel through the active partition table, applying byte swapping when needed.

Used by `ukfs_part_probe` to resolve `%DISKLABEL:<letter>%` device suffixes into byte offsets and sizes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libukfs/ukfs_disklabel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libukfs/ukfs_int_disklabel.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libukfs/ukfs_int_disklabel.h

Private local copy of the stable on-disk NetBSD disklabel structure.

Defines `UKFS_MAXPARTITIONS`, `UKFS_DISKMAGIC`, `struct ukfs__disklabel`, and nested partition records with size, offset, filesystem type, fragment, and filesystem-specific fields.

Keeps only the disklabel definitions needed by `libukfs` partition probing, avoiding broad NetBSD header dependencies.

Declares `ukfs__disklabel_scan` and `ukfs__disklabel_dkcksum`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libukfs/ukfs_int_disklabel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libusbhid/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libusbhid/Makefile

Builds `libusbhid` from `descr.c`, `parse.c`, `usage.c`, and `data.c`.

Installs public header `usbhid.h` into `/usr/include` and manual aliases for descriptor retrieval, parser lifecycle, item lookup, report sizing, usage lookup, and data get/set helpers.

When shared data installation is enabled, installs `usb_hid_usages` into `/usr/share/misc`.

This is a compact userland helper library for USB HID report descriptors and report data.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libusbhid/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libusbhid/data.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libusbhid/data.c

Implements bit-level extraction and insertion for HID report fields.

`hid_get_data` reads a field at `hid_item_t.pos` with `report_size` bits, assembles little-endian bytes, masks the field, and sign-extends when the logical minimum is negative.

`hid_set_data` writes a caller-provided integer into the field position, masking to report size and preserving surrounding bits.

Both functions depend entirely on correctly parsed `hid_item_t` metadata and assume the caller supplies a report buffer large enough for the target field.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libusbhid/data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libusbhid/descr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libusbhid/descr.c

Handles HID report descriptor acquisition and ownership.

`hid_get_report_desc` uses `USB_GET_REPORT_DESC` ioctl on a USB device fd and wraps the returned descriptor data in a library-owned `report_desc_t`.

`hid_use_report_desc` copies caller-provided descriptor bytes into an allocated `struct report_desc`.

`hid_dispose_report_desc` releases that allocated descriptor.

The actual `struct report_desc` layout comes from private `usbvar.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libusbhid/descr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libusbhid/parse.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libusbhid/parse.c

Implements a USB HID report descriptor parser.

`hid_start_parse` initializes parser state over a `report_desc_t`, filtering by item kind bitmask and report ID. `hid_end_parse` frees parser state and any pushed global state stack.

`hid_get_item` repeatedly calls the raw parser until it finds an item matching the requested report ID, or reaches EOF/error.

`hid_get_item_raw` parses HID short and long items, tracks global/local/main item state, report IDs, collection nesting, usage ranges, variable item expansion, report bit positions, and pushed/popped global state.

Public helpers `hid_report_size` compute report byte size for a kind/report ID, and `hid_locate` finds a non-constant item by usage.

Maintenance notes: parser allocation paths are minimal and descriptor-derived state controls loop expansion, so callers should treat descriptors as untrusted input and validate return values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libusbhid/parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libusbhid/usage.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libusbhid/usage.c

Loads and queries the HID usage-name database.

`hid_init` reads `/usr/share/misc/usb_hid_usages` by default, parsing usage pages and per-page usages into dynamically grown arrays. Names are normalized by replacing whitespace and dots with underscores.

`hid_usage_page` maps a page number to a name, returning hex text for unknown pages.

`hid_usage_in_page` maps a combined page/usage value to a usage name, supporting wildcard format entries in the table.

`hid_parse_usage_page` and `hid_parse_usage_in_page` perform reverse lookup from names, with `page:usage` hex fallback for combined usage parsing.

Error handling is process-fatal for missing/malformed usage table data, consistent with the historical library style.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libusbhid/usage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libusbhid/usbhid.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libusbhid/usbhid.h

Public `libusbhid` header.

Defines opaque `report_desc_t` and `hid_data_t`, item kinds `hid_input`, `hid_output`, `hid_feature`, `hid_collection`, and `hid_endcollection`.

Defines `hid_item_t`, carrying HID global fields, local fields, collection metadata, item kind, flags, absolute bit position, and parser stack linkage.

Provides `HID_PAGE` and `HID_USAGE` macros for combined usage values.

Declares descriptor acquisition, parser lifecycle, item iteration, report sizing, usage lookup/parsing, and report data get/set APIs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libusbhid/usbhid.h -->