# Group Research: group_1209_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_time_zic_c_sources_os_0ad913235100

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Every listed source file was read completely and summarized separately.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/zic.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/time/zic.c

## Purpose
Implements `zic`, the timezone compiler that reads tzdb `.zi` source files and optional leap-second files, then emits TZif timezone files and links under the target timezone directory.

## Main Entry Points
- `main()` parses command-line options, reads leap and timezone input files, associates rules with zones, changes into the output directory, emits each zone, creates links, and handles `localtime`/`posixrules` compatibility links.
- `infile()` reads input line by line, tokenizes fields, dispatches `Rule`, `Zone`, `Link`, `Leap`, and `Expires` records, and handles zone continuation lines.
- `outzone()` expands a zone’s rules into transition/type tables and calls `writezone()`.
- `writezone()` writes TZif v2/v3/v4 data blocks, including 32-bit and 64-bit sections, leap second tables, type records, abbreviation strings, and the trailing POSIX TZ string.

## Parsing And Data Model
The file models tzdb source records with `struct rule`, `struct zone`, and `struct link`. Rules encode year ranges, month/day selectors, transition time basis, DST save value, and abbreviation variable text. Zones encode standard offset, rule reference or fixed save value, format string, continuation end time, and associated rule slices. Links are collected and sorted before filesystem creation.

Parsing helpers include `getfields()` for comments, whitespace, and quoted fields; `gethms()`/`getsave()` for offsets and DST-save parsing; `rulesub()` for year/month/day/time rule fields; `getleapdatetime()`/`inleap()`/`inexpires()` for leap records; and `namecheck()` for portable zone/link names.

## TZif Generation
`outzone()` computes a bounded year range from referenced rules, leap years, truncation options, bloat mode, and POSIX string availability. It materializes transition instants with `rpytime()`, chooses time types with `addtype()`, builds abbreviations with `doabbr()` and `addabbr()`, and optionally trims trailing transitions that can be represented by the POSIX TZ footer.

`writezone()` sorts and merges transitions, applies leap-second corrections, truncates data using `-r`/`-R`, creates a 32-bit range and full 64-bit range, decides when TZif v4 is required, remaps/omits unused types, writes headers in network byte order, emits transitions/types/leaps/std-wall/ut-local indicators, then appends the POSIX string.

## Filesystem Behavior
Output uses randomized temporary names via `random_dirent()` and `open_outfile()`, then atomically renames with `rename_dest()`. Directory creation is handled by `mkdirs()` unless `-D` disables it. `dolink()` tries hard links, then symlinks with relative target synthesis, then byte-for-byte copies. Link creation detects duplicate link names, self-links, chains, and cycles.

## Options And Compatibility
Supports `-b slim|fat`, `-d`, `-D`, `-g`, `-l`, `-L`, `-m`, `-p`, `-r`, `-R`, `-t`, `-u`, `-v`, plus ignored historical `-s`/`-y`. “Fat” output preserves older-client compatibility behavior; “slim” may omit redundant 32-bit content and transition tails. Verbose mode emits compatibility warnings for older zic/TZif consumers.

## Dependencies
Depends on NetBSD libc/toolchain configuration, `private.h`, `tzfile.h`, POSIX file APIs, optional `getrandom`, gettext, `setmode/getmode`, pwd/group lookup, symlink/hardlink support, signal handling, and tzdb constants such as `TZ_MAX_TYPES`, `TZ_MAX_CHARS`, `TZ_MAGIC`, and calendrical macros.

## Risks And Notes
The code is global-state heavy: parsed rules/zones/links, transition arrays, leap arrays, output options, diagnostics, and abbreviation tables are process globals. Correctness depends on overflow-checked arithmetic (`oadd`, `tadd`, `omul`), careful handling of leap-second truncation, correct std/wall/UT transition conversion, and preserving legacy TZif behavior for old readers. Link handling is intentionally defensive because link targets may themselves be links or unavailable until later passes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/time/zic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/tls/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/tls/Makefile.inc

## Purpose
Adds libc TLS support sources to the NetBSD libc build.

## Build Behavior
Includes `bsd.own.mk`, extends `.PATH` with the local directory and `${ARCHDIR}/tls`, adds `tls.c` to `SRCS`, and compiles it with `_LIBC_SOURCE` and GNU11 mode.

## Dependencies
Relies on the parent libc make infrastructure for `${.PARSEDIR}`, `${ARCHDIR}`, and per-file `CPPFLAGS`.

## Risks And Notes
This file is purely build glue. Architecture-specific TLS support is found through `${ARCHDIR}/tls`; this include only guarantees the generic `tls.c` is compiled with libc-private settings.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/tls/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/tls/tls.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/tls/tls.c

## Purpose
Provides libc-side static TLS setup and fallback runtime-loader TLS allocation/free routines for architectures using TLS variant I or II.

## Main Entry Points
- `__libc_static_tls_setup()` scans program headers, skips dynamic executables, allocates a TLS block/TCB, and installs the TCB with `__lwp_settcb()` or `_lwp_setprivate()`.
- `_rtld_tls_allocate()` allocates TLS storage for the initial thread via `mmap()` and later threads via `calloc()`, lays out variant-I or variant-II TCB/TLS memory, and copies the TLS init image.
- `_rtld_tls_free()` frees TLS storage with `munmap()` for the initial thread block or `free()` for later allocations.
- `__libc_tls_get_addr()` is a weak TLS lookup stub that aborts.

## Control Flow
`dl_iterate_phdr()` invokes `__libc_static_tls_setup_cb()`, which detects `PT_INTERP` to avoid static setup for dynamic programs and records the `PT_TLS` image address, file size, memory size, and alignment. Static setup allocates a TCB only when no interpreter is present.

## Dependencies
Depends on ELF program header iteration, `struct tls_tcb`, TLS variant macros, mmap/calloc/free, LWP private pointer APIs, and libc namespace/weak alias machinery.

## Risks And Notes
Allocation failure exits the process with status 127 using direct `write()`/`_exit()`, avoiding malloc-dependent error handling. Layout is ABI-sensitive: variant I places the TCB before TLS data, while variant II places it after a rounded TLS allocation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/tls/tls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/uuid/Makefile.inc

## Purpose
Adds the DCE 1.1 compatible UUID implementation to libc.

## Build Behavior
Extends `.PATH` to `${.CURDIR}/uuid`, adds comparison, creation, nil, equality, parse, hash, nil-test, stream encode/decode, and string conversion sources to `SRCS`, and installs `uuid.3` with manual-page links for all UUID APIs.

## Dependencies
Uses the parent libc build system and the public `uuid.3` manual page as the central documentation target.

## Risks And Notes
This file is build metadata only; it defines the public API surface by listing sources and MLINKS.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_compare.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_compare.c

## Purpose
Implements `uuid_compare()`, a DCE-style ordering comparison for two `uuid_t` values.

## Behavior
Sets `status` to `uuid_s_ok` when provided. Treats equal pointers as equal, treats `NULL` as a nil UUID, and orders nil UUIDs before non-nil UUIDs. Non-null UUIDs are compared field-by-field in UUID logical order: `time_low`, `time_mid`, `time_hi_and_version`, clock sequence bytes, then node bytes.

## Dependencies
Depends on `uuid_is_nil()`, `memcmp()`, `uuid.h`, and libc namespace support.

## Risks And Notes
The comparison is structural rather than raw-memory order, avoiding host padding issues. `time_low` subtraction is widened to `int64_t` before reduction to `-1/0/1`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_compare.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_create.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_create.c

## Purpose
Implements `uuid_create()` by delegating UUID generation to the system `uuidgen()` call.

## Behavior
Calls `uuidgen(u, 1)` to generate one UUID. Reports `uuid_s_ok` on success and `uuid_s_no_memory` on failure.

## Dependencies
Depends on `uuidgen()` and `uuid.h`.

## Risks And Notes
The failure status is annotated as an approximation. The function assumes the caller supplied a valid `uuid_t *`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_create.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_create_nil.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_create_nil.c

## Purpose
Implements `uuid_create_nil()`, producing the all-zero UUID.

## Behavior
Zeroes the caller-provided `uuid_t` with `memset()` and reports `uuid_s_ok` when `status` is non-null.

## Dependencies
Depends on `string.h`, `uuid.h`, libc namespace support, and weak aliasing to `_uuid_create_nil`.

## Risks And Notes
No null check is performed for the output UUID pointer; callers must pass valid storage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_create_nil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_equal.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_equal.c

## Purpose
Implements `uuid_equal()`, returning whether two UUIDs represent the same UUID.

## Behavior
Sets status to `uuid_s_ok`. Equal pointers are equal. A `NULL` UUID pointer is treated as nil, so `NULL` equals a nil UUID and not a non-nil UUID. Non-null UUIDs are compared byte-for-byte over `sizeof(uuid_t)`.

## Dependencies
Depends on `uuid_is_nil()`, `memcmp()`, and `uuid.h`.

## Risks And Notes
Byte comparison assumes `uuid_t` has deterministic representation for all fields, including no meaningful uninitialized padding in valid values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_equal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_from_string.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_from_string.c

## Purpose
Implements `uuid_from_string()`, parsing canonical UUID text into a `uuid_t`.

## Behavior
`NULL` or empty input creates a nil UUID. Otherwise the function defaults status to `uuid_s_invalid_string_uuid`, requires a 36-character canonical dashed form, rejects old dotted UUID syntax, scans 11 hex fields with `sscanf()`, then validates known variant bit patterns. On valid parse, status becomes `uuid_s_ok`; unsupported variant encodings produce `uuid_s_bad_version`.

## Dependencies
Depends on `uuid_create_nil()`, `strlen()`, `sscanf()`, and `uuid.h`.

## Risks And Notes
The scanner checks only the first dash explicitly before relying on the format string; malformed strings of the correct length generally fail conversion count. Parsed time fields are native-order struct fields, while sequence and node bytes are parsed as byte values.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_from_string.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_hash.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_hash.c

## Purpose
Implements `uuid_hash()`, returning a compact 16-bit hash value for a UUID.

## Behavior
Sets status to `uuid_s_ok`. Returns the low 16 bits of `time_low` for non-null UUIDs and `0` for `NULL`.

## Dependencies
Depends on `uuid.h`.

## Risks And Notes
This is a simple compatibility hash, not a collision-resistant hash. It assumes the frequently changing low time bits provide acceptable distribution for DCE API callers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_is_nil.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_is_nil.c

## Purpose
Implements `uuid_is_nil()`, testing whether a UUID is the nil UUID.

## Behavior
Sets status to `uuid_s_ok`. Treats a `NULL` pointer as nil. Otherwise compares the UUID against a static zero-initialized `uuid_t`.

## Dependencies
Depends on `memcmp()`, `uuid.h`, and weak aliasing to `_uuid_is_nil`.

## Risks And Notes
The static initializer zeros the whole object through C initialization rules. As with `uuid_equal()`, this relies on valid `uuid_t` object representation being safe for byte comparison.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_is_nil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_stream.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_stream.c

## Purpose
Provides endian-specific UUID encode/decode helpers for 16-byte octet streams.

## Main Entry Points
- `uuid_enc_le()` and `uuid_dec_le()` encode/decode UUID time fields as little-endian, followed by raw clock sequence and node bytes.
- `uuid_enc_be()` and `uuid_dec_be()` do the same with big-endian time fields.

## Dependencies
Depends on machine endian helpers `le32enc`, `le16enc`, `le32dec`, `le16dec`, `be32enc`, `be16enc`, `be32dec`, and `be16dec`.

## Risks And Notes
These helpers are documented as convenience functions outside the core DCE RPC API. Callers must provide at least 16 bytes of buffer storage and valid UUID pointers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_stream.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_to_string.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_to_string.c

## Purpose
Implements `uuid_to_string()`, allocating a canonical dashed lowercase hex UUID string.

## Behavior
Sets status to `uuid_s_ok`. If the output string pointer itself is null, it returns without work. A null UUID input is formatted as nil. Uses `asprintf()` to allocate the result and reports `uuid_s_no_memory` if allocation fails.

## Dependencies
Depends on `asprintf()`, `uuid.h`, and standard formatting.

## Risks And Notes
The caller owns the allocated string. The API does not clear `*s` before `asprintf()`, so callers should not assume it changes on every failure mode except the direct allocation result.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_to_string.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/Makefile.inc

## Purpose
Adds Yellow Pages/NIS client support sources and manpage links to libc.

## Build Behavior
Extends `.PATH` with architecture-specific and generic `yp` directories, adds XDR helpers, binding logic, client procedures, and error conversion sources to `SRCS`, and installs `ypclnt.3` links for the exported YP client APIs.

## Dependencies
Relies on NetBSD libc make infrastructure and RPC/YP headers from the source tree.

## Risks And Notes
This file defines the set of libc YP entry points compiled into libc; actual behavior is in the listed C files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/local.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/local.h

## Purpose
Declares private shared YP libc symbols used across the YP client implementation.

## Contents
Declares `__yp_unbind()` and `_yp_invalid_domain()`, plus shared globals for timeout, error retry count, bind retry count, and cached default domain.

## Dependencies
Requires `struct dom_binding` from YP/RPC headers and NetBSD `__BEGIN_DECLS`/`__END_DECLS`.

## Risks And Notes
This header exposes mutable globals shared by the YP implementation, so retry and timeout behavior can be affected across calls.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/local.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/xdryp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/xdryp.c

## Purpose
Implements XDR serialization/deserialization routines for NetBSD’s YP/NIS protocol structures and exported Sun-compatible YP XDR API.

## Main Entry Points
Includes XDR functions for domain/map/owner strings, DBM `datum`, request structs (`ypreq_key`, `ypreq_nokey`, `ypreq_xfr`), bind responses, map parameters, push responses, value/key responses, master/order/maplist responses, maplist linked lists, IP addresses, and `xdr_ypall()` streaming callbacks.

## Control Flow
Most functions validate arguments with `_DIAGASSERT`, then serialize fields in protocol order using `xdr_string`, `xdr_bytes`, `xdr_opaque`, `xdr_enum`, `xdr_u_int`, and `xdr_pointer`. `xdr_ypall()` loops over streamed boolean “more” markers, decodes each key/value response into stack buffers, and invokes the caller callback until the server ends or callback asks to stop.

## Dependencies
Depends on RPC/XDR libc support, `rpcsvc/yp_prot.h`, `rpcsvc/ypclnt.h`, socket/IP structures, NetBSD weak aliases, and deprecated warning annotations for older buggy string routines.

## Risks And Notes
Some routines intentionally do not strictly match the RPC `.x` definition because they preserve historical Sun YP API behavior. `xdr_ypall()` uses fixed `YPMAXRECORD` stack buffers, so record-size limits are central to safety.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/xdryp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/yp_all.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/yp_all.c

## Purpose
Implements `yp_all()`, streaming all key/value pairs from a YP map through a user callback.

## Behavior
Validates domain, map name, and callback. Binds to the domain, creates a TCP RPC client to the bound YP server, sends a `YPPROC_ALL` request with `ypreq_nokey`, decodes the stream with `xdr_ypall()`, destroys the client, unbinds the domain binding, and maps RPC failure to `YPERR_RPC`.

## Dependencies
Depends on `_yp_dobind()`, `__yp_unbind()`, `xdr_ypreq_nokey`, `xdr_ypall`, RPC client APIs, and shared `_yplib_timeout`.

## Risks And Notes
Unlike the other per-key procedures, this creates a separate TCP client rather than using the cached UDP client. It emits `warnx()` on TCP client creation failure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/yp_all.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/yp_first.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/yp_first.c

## Purpose
Implements `yp_first()` and `yp_next()` for iterating key/value records in a YP map.

## Behavior
Both functions validate output pointers, domain, map, and key inputs; initialize outputs to null/zero; bind to the domain; issue `YPPROC_FIRST` or `YPPROC_NEXT`; retry by marking `dom_vers = -1` on RPC errors; convert protocol status through `ypprot_err()`; allocate NUL-terminated copies of returned key/value data; free XDR memory; unbind; and clean partial outputs on failure.

## Dependencies
Depends on `_yp_dobind()`, `__yp_unbind()`, `_yplib_timeout`, `_yplib_nerrs`, `_yplib_bindtries`, `xdr_ypreq_nokey`, `xdr_ypreq_key`, `xdr_ypresp_key_val`, and `ypprot_err()`.

## Risks And Notes
Returned key/value data may be binary but is copied with an extra trailing NUL for compatibility. If allocating the value fails after key allocation, cleanup releases the partial key.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/yp_first.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/yp_maplist.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/yp_maplist.c

## Purpose
Implements `yp_maplist()`, retrieving the list of maps served for a YP domain.

## Behavior
Validates the domain and output pointer, binds to the domain, calls `YPPROC_MAPLIST`, retries after RPC failures by invalidating the binding version, stores the returned linked list in `*outmaplist`, unbinds, and returns protocol status via `ypprot_err()`.

## Dependencies
Depends on `_yp_dobind()`, `__yp_unbind()`, `xdr_ypdomain_wrap_string`, `xdr_ypresp_maplist`, and retry globals.

## Risks And Notes
The code intentionally does not call `xdr_free()` for the response because ownership of the returned maplist is transferred to the caller.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/yp_maplist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/yp_master.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/yp_master.c

## Purpose
Implements `yp_master()`, returning the master server name for a YP map.

## Behavior
Validates output pointer, domain, and map. Binds, calls `YPPROC_MASTER`, retries on RPC failure using binding invalidation, converts protocol status, duplicates the returned master string on success, frees XDR-owned response memory, unbinds, and clears output on failure.

## Dependencies
Depends on `_yp_dobind()`, `__yp_unbind()`, `xdr_ypreq_nokey`, `xdr_ypresp_master`, `ypprot_err()`, and `strdup()`.

## Risks And Notes
The caller owns `*outname`. Allocation failure is reported as `YPERR_RESRC`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/yp_master.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/yp_match.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/yp_match.c

## Purpose
Implements `yp_match()`, retrieving a value for a key from a YP map, with a small optional in-process cache.

## Behavior
Validates output pointers, domain, map, key, and key length. Binds to the domain, checks the cache for the default domain, sends `YPPROC_MATCH` on a miss, retries on RPC failure, copies returned value into a newly allocated NUL-terminated buffer, optionally caches successful default-domain results, frees XDR response memory, unbinds, and clears output on failure.

## Cache
With `YPMATCHCACHE`, `_yplib_cache` controls TTL seconds. Cache entries are a linked list of map/key/value copies. Expired entries may be reused by `ypmatch_add()`.

## Dependencies
Depends on `_yp_dobind()`, `_yp_domain`, `__yp_unbind()`, RPC/XDR helpers, `ypprot_err()`, `time()`, and malloc/free.

## Risks And Notes
The cache is global and not independently locked in this file. Cache add failure after a successful network lookup changes the result to `YPERR_RESRC` and frees the just-returned output.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/yp_match.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/yp_order.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/yp_order.c

## Purpose
Implements `yp_order()`, returning a YP map’s order number.

## Behavior
Validates domain, map, and output pointer. Binds, calls `YPPROC_ORDER`, retries after RPC failures, handles `RPC_PROCUNAVAIL` as a YP server error for NIS+ compatibility mode, writes the returned order number, frees XDR response memory, unbinds, and returns protocol status through `ypprot_err()`.

## Dependencies
Depends on `_yp_dobind()`, `__yp_unbind()`, `xdr_ypreq_nokey`, `xdr_ypresp_order`, and YP retry globals.

## Risks And Notes
`*outorder` is assigned before converting the protocol status, so callers should trust it only when the return code is zero.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/yp_order.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/yperr_string.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/yperr_string.c

## Purpose
Implements `yperr_string()`, converting YP client error codes to human-readable strings.

## Behavior
Returns constant strings for all known `YPERR_*` values and formats unknown values into a static 80-byte buffer.

## Dependencies
Depends on `rpcsvc/ypclnt.h`, `snprintf()`, libc namespace support, and weak aliasing.

## Risks And Notes
The unknown-error path is not thread-safe because it uses a shared static buffer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/yperr_string.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/yplib.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/yplib.c

## Purpose
Implements shared YP client binding, unbinding, default-domain, and domain validation logic.

## Main Entry Points
- `_yp_dobind()` obtains or refreshes a domain binding and RPC client.
- `yp_bind()` binds a domain.
- `yp_unbind()` removes a cached binding.
- `__yp_unbind()` destroys a binding’s active client without removing the binding object.
- `yp_get_default_domain()` caches and returns the process domain name.
- `yp_setbindtries()` updates the retry limit.
- `_yp_check()` validates default-domain availability and binding.
- `_yp_invalid_domain()` rejects null, empty, too-long, or slash-containing domains.

## Control Flow
`_yp_dobind()` first checks `/var/run/ypbind.lock` to determine whether ypbind is running. It resets cached bindings across fork by tracking PID. It tries to read `/var/yp/binding/<domain>.2` while locked by ypbind; if unavailable, it contacts local `ypbind` over TCP. Once a YP server address is known, it creates a UDP client for `YPPROG/YPVERS`, sets close-on-exec on the socket, and caches the binding.

## Dependencies
Depends on file locks, binding files, local ypbind RPC service, RPC TCP/UDP client APIs, socket structures, `getdomainname()`, and reentrant mutex wrappers.

## Risks And Notes
Binding state is global per process. Fork detection clears inherited clients. Some error paths print to stderr via RPC helper functions. The reentrant lock is used by `_yp_check()` but not every public operation in other files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/yplib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/ypprot_err.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/ypprot_err.c

## Purpose
Implements `ypprot_err()`, translating YP protocol status codes to YP client error codes.

## Behavior
Maps `YP_TRUE` to success and known protocol failures to corresponding `YPERR_*` values, falling back to `YPERR_YPERR`.

## Dependencies
Depends on `rpcsvc/yp_prot.h`, `rpcsvc/ypclnt.h`, and weak aliasing.

## Risks And Notes
The mapping is intentionally lossy because client APIs expose a smaller error taxonomy than the protocol.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/yp/ypprot_err.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_aligned/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libc_aligned/Makefile

## Purpose
Builds `libc_aligned`, a support library containing libc routines that avoid unaligned memory access.

## Build Behavior
Selects an architecture include file from `arch/${LIBC_MACHINE_CPU}`, `arch/${MACHINE_ARCH}`, or `arch/${MACHINE}` if present, adds the matching path, and builds `LIB=c_aligned` only when `SRCS` is non-empty.

## Dependencies
Depends on NetBSD make variables, architecture-specific `Makefile.inc` files, and `bsd.lib.mk`.

## Risks And Notes
The library silently does not build if no matching architecture source list exists.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_aligned/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_aligned/arch/powerpc/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc_aligned/arch/powerpc/Makefile.inc

## Purpose
Selects aligned-safe string/memory routines for PowerPC `libc_aligned`.

## Build Behavior
Adds common libc string source path and compiles C implementations of `memcmp`, `bcopy`, `memcpy`, and `memmove`, explicitly avoiding assembly versions that use unaligned memory access.

## Dependencies
Depends on `${NETBSDSRCDIR}/common/lib/libc/string`.

## Risks And Notes
This is architecture-specific build selection; correctness depends on the referenced C routines preserving strict alignment assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_aligned/arch/powerpc/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_fp/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libc_fp/Makefile

## Purpose
Builds `libc_fp`, an architecture-selected floating-point support library.

## Build Behavior
Includes the first matching architecture `Makefile.inc` from CPU, architecture, or machine directories and builds `LIB=c_fp` only when sources are selected.

## Dependencies
Depends on NetBSD make architecture variables and `bsd.lib.mk`.

## Risks And Notes
This generic makefile contains no FP code itself; source selection is entirely architecture-driven.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_fp/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_fp/arch/mips/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc_fp/arch/mips/Makefile.inc

## Purpose
Configures MIPS `libc_fp` to build hard-float implementations of soft-float ABI helper routines.

## Build Behavior
Adds `-mhard-float`, disables `MKSOFTFLOAT`, and selects `fpsf.S` and `fpdf.S` with hard-float assembler flags.

## Dependencies
Depends on MIPS assembler/compiler support for hard-float instructions.

## Risks And Notes
These objects are intended to be ABI-compatible with soft-float callers while executing on hardware with floating-point support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_fp/arch/mips/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_fp/arch/mips/fpdf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc_fp/arch/mips/fpdf.S

## Purpose
Implements double-precision GCC soft-float helper symbols using MIPS floating-point hardware instructions.

## Main Entry Points
Provides arithmetic helpers `__adddf3`, `__subdf3`, `__muldf3`, `__divdf3`, negation, single-to-double extension, double-to-int conversions, unsigned conversions, int-to-double conversions, and comparison/unordered helpers with strong aliases for GCC comparison entry points.

## Control Flow
Arguments are moved from integer registers to FP registers with `dmtc1`/`mtc1`, operations execute using `.d` FP instructions, and results are moved back to integer return registers. Unsigned conversions use subtract/add bias constants for the high signed range.

## Dependencies
Depends on MIPS assembler macros from `<mips/asm.h>`, COP1 FP instructions, MIPS ABI register conventions, and optional `MIPS3` synchronization nops.

## Risks And Notes
Correctness is ABI- and endianness-sensitive. Comparison helpers must return the exact values GCC expects for soft-float runtime calls, including unordered cases.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_fp/arch/mips/fpdf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_fp/arch/mips/fpsf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc_fp/arch/mips/fpsf.S

## Purpose
Implements single-precision GCC soft-float helper symbols using MIPS floating-point hardware instructions.

## Main Entry Points
Provides `__addsf3`, `__subsf3`, `__mulsf3`, `__divsf3`, `__negsf2`, double-to-single truncation, single-to-int conversions, unsigned conversions, int-to-single conversions, and comparison/unordered helpers.

## Control Flow
Integer-register float bit patterns are moved into FP registers, computed with `.s` FP instructions, and returned via integer registers. Unsigned conversion helpers use large FP constants and integer biasing.

## Dependencies
Depends on MIPS COP1, `<mips/asm.h>`, GCC soft-float helper symbol conventions, and MIPS ABI register conventions.

## Risks And Notes
Some strong aliases appear to point at double-named comparison helpers, so symbol naming must be checked against the assembler macro/ABI expectations when modifying this file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_fp/arch/mips/fpsf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_fp/gcc-softfloat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc_fp/gcc-softfloat.c

## Purpose
Provides C reference/witness functions for GCC soft-float primitive operations.

## Contents
Defines `x*` wrapper functions that perform C casts, arithmetic comparisons, and conversions for double and float operations. These help identify or verify which compiler runtime helper operations GCC emits.

## Dependencies
Depends only on C floating-point and integer conversion semantics.

## Risks And Notes
This is not the optimized runtime implementation; it is a diagnostic/reference source for architecture authors implementing soft-float-compatible helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_fp/gcc-softfloat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_vfp/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libc_vfp/Makefile

## Purpose
Builds ARM VFP-backed libc floating-point helper library `libc_vfp`.

## Build Behavior
Sets `LIB=c_vfp`, enables shared-library directory placement, selects `vfpsf.S` and `vfpdf.S`, and includes `bsd.lib.mk`.

## Dependencies
Depends on ARM/VFP assembler support and NetBSD library make infrastructure.

## Risks And Notes
This library assumes a target context where VFP instructions are valid.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_vfp/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_vfp/vfpdf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc_vfp/vfpdf.S

## Purpose
Implements double-precision soft-float ABI helpers using ARM VFP instructions.

## Main Entry Points
Provides double add/subtract/multiply/divide/negate, float-to-double, double-to-signed/unsigned int, int-to-double, unsigned-int-to-double, ARM EABI reverse subtraction, EABI compare helpers, and non-EABI GCC comparison helpers.

## Control Flow
Macros move double arguments between ARM integer registers and VFP `d` registers, accounting for ARM endian order. Arithmetic and conversions use VFP instructions, and results are moved back to integer registers. EABI symbol names are mapped to GCC helper names when `__ARM_EABI__` is defined.

## Dependencies
Depends on `<arm/asm.h>`, VFP hardware, ARM EABI/non-EABI calling conventions, and APSR/FPSCR condition flag transfer.

## Risks And Notes
Comparison helpers depend on exact interpretation of VFP condition flags, especially unordered NaN cases. Endian-specific argument movement is critical.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_vfp/vfpdf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_vfp/vfpsf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc_vfp/vfpsf.S

## Purpose
Implements single-precision soft-float ABI helpers using ARM VFP instructions.

## Main Entry Points
Provides single add/subtract/multiply/divide/negate, double-to-single truncation, single-to-signed/unsigned int, int-to-single, unsigned-int-to-single, EABI reverse subtraction, EABI compare helpers, and non-EABI GCC comparison helpers.

## Control Flow
Moves raw float arguments from integer registers into VFP `s` registers, performs VFP `.f32` operations, returns raw bits in integer registers, and transfers VFP comparison flags to APSR for conditional returns.

## Dependencies
Depends on `<arm/asm.h>`, `<arm/vfpreg.h>`, VFP hardware, and ARM EABI/non-EABI helper naming conventions.

## Risks And Notes
Like `vfpdf.S`, correctness is tightly coupled to ABI register layout and NaN/unordered comparison semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc_vfp/vfpsf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/4.1/ftime.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcompat/4.1/ftime.c

## Purpose
Implements historical `ftime()` compatibility API.

## Behavior
Calls `gettimeofday()` with a `struct timezone`, fills `struct timeb` seconds, milliseconds, minutes west of UTC, and DST flag, and returns `0` or `-1`.

## Dependencies
Depends on `sys/time.h`, `sys/timeb.h`, and `_DIAGASSERT`.

## Risks And Notes
This preserves obsolete timezone fields from `gettimeofday()`. The caller must pass a valid `struct timeb *`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/4.1/ftime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/4.1/gtty.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcompat/4.1/gtty.c

## Purpose
Implements historical `gtty()` compatibility API.

## Behavior
Calls `ioctl(fd, TIOCGETP, tty)` to fetch old `sgttyb` terminal modes.

## Dependencies
Depends on `<sgtty.h>`, ioctl definitions, and `_DIAGASSERT`.

## Risks And Notes
This is a thin wrapper around legacy terminal ioctls.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/4.1/gtty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/4.1/stty.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcompat/4.1/stty.c

## Purpose
Implements historical `stty()` compatibility API.

## Behavior
Calls `ioctl(fd, TIOCSETP, tty)` to set old `sgttyb` terminal modes.

## Dependencies
Depends on `<sgtty.h>`, ioctl definitions, and `_DIAGASSERT`.

## Risks And Notes
This is a thin wrapper around legacy terminal ioctls and inherits their behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/4.1/stty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/4.3/cfree.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcompat/4.3/cfree.c

## Purpose
Implements historical `cfree()` compatibility API.

## Behavior
Calls `free(p)`.

## Dependencies
Depends on `<stdlib.h>`.

## Risks And Notes
This exists only for source/binary compatibility with older interfaces.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/4.3/cfree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/4.3/regex.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcompat/4.3/regex.c

## Purpose
Implements old `re_comp()`/`re_exec()` compatibility APIs in terms of the historical `regexp` interface.

## Behavior
`re_comp()` frees any previous compiled expression and error string, compiles a new expression with `regcomp()`, and returns an error string on failure. `re_exec()` runs `regexec()` against the stored expression and returns `-1` if compilation/execution signaled an error. `regerror()` records the error string for these wrappers.

## Dependencies
Depends on `<regexp.h>`, `<re_comp.h>`, `regcomp()`, `regexec()`, and global compatibility state.

## Risks And Notes
The implementation is not thread-safe because compiled regexp and error state are static globals. `re_exec()` assumes a prior successful `re_comp()` initialized `re_regexp`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/4.3/regex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/4.3/rexec.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcompat/4.3/rexec.c

## Purpose
Implements historical `rexec()`, connecting to a remote exec server and sending credentials/command.

## Behavior
Resolves the host, optionally fills username/password via `ruserpass()`, connects to the requested TCP port with exponential retry on refused connections, optionally opens a secondary listening socket for stderr, writes secondary port, username, password, and command as NUL-terminated strings, reads the server status byte, prints server error text to stderr on failure, and returns the connected socket on success.

## Dependencies
Depends on DNS (`gethostbyname()`), sockets, `ruserpass()`, `err/warn`, and classic rexec protocol behavior.

## Risks And Notes
This sends the password in cleartext, as noted in the source. The API is legacy and network-security-sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/4.3/rexec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/4.3/ruserpass.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcompat/4.3/ruserpass.c

## Purpose
Parses `~/.netrc` to supply login/password information for legacy remote access clients such as `rexec()`.

## Behavior
Opens `$HOME/.netrc`, tokenizes keywords and values, matches `machine` or `default` entries against the requested host, handles local-domain short-name matching, fills missing login/password strings, enforces restrictive permissions for password/account entries, and parses/stores `macdef` macro definitions in static buffers.

## Dependencies
Depends on environment `HOME`, hostname/domain detection, `stat` permission checks, token parsing, fixed macro arrays, and libc warning/error helpers.

## Risks And Notes
Global parser state and macro storage are not thread-safe. Password/account entries in group/world-readable `.netrc` files are rejected. Token buffers and macro buffers are fixed-size historical limits.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/4.3/ruserpass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/4.4/cuserid.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libcompat/4.4/cuserid.c

## Purpose
Implements historical `cuserid()` compatibility API.

## Behavior
Looks up the effective UID with `getpwuid_r()`. If lookup fails, clears the caller buffer when provided and returns it. If no caller buffer is supplied, uses a static `L_cuserid` buffer. Copies the username with `strncpy()`.

## Dependencies
Depends on password database APIs, `geteuid()`, and `L_cuserid`.

## Risks And Notes
The static buffer path is not thread-safe. `strncpy()` may not NUL-terminate if the username length reaches `L_cuserid`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/4.4/cuserid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libcompat/Makefile

## Purpose
Builds NetBSD `libcompat`, a library of older BSD/libc compatibility APIs.

## Build Behavior
Sets `LIB=compat`, compatibility CPP flags, assembler include paths, and `.PATH` for 4.1, 4.3, 4.4, machine-specific, and regexp sources. Builds 4.1 APIs (`gtty`, `ftime`, `stty`), 4.3 APIs (`cfree`, `regex`, `rexec`, `ruserpass`), 4.4 `cuserid`, and regexp sources (`regexp.c`, `regsub.c`). Installs related manpages and links.

## Dependencies
Depends on NetBSD make infrastructure, libc architecture include directories, optional `DESTDIR`, and source files under compatibility version subdirectories.

## Risks And Notes
This library deliberately preserves obsolete interfaces. The makefile documents several missing historical sources, so compatibility coverage is selective rather than complete.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libcompat/Makefile -->