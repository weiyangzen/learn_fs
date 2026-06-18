# subset-b-007745 research

Grouped research for OpenAFS Windows NetIDMgr, wshelper, license conversion, and AFS credential plugin sources. Each file section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/mstring.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/mstring.h

## Purpose

`mstring.h` declares NetIDMgr utility APIs for Windows wide-character multi-strings and CSV conversion. A multi-string is a sequence of null-terminated strings terminated by an extra null, which this API uses for configuration values such as cell lists, recent realms, and status strings.

## Important APIs, types, and functions

The public constants are `KHM_PREFIX`, `KHM_CASE_SENSITIVE`, `KHM_MAXCCH_STRING`, and `KHM_MAXCB_STRING`. Core mutation APIs are `multi_string_init`, `multi_string_prepend`, `multi_string_append`, and `multi_string_delete`. Search and traversal are handled by `multi_string_find` and `multi_string_next`. Serialization APIs are `multi_string_to_csv` and `csv_to_multi_string`. Size and copy helpers include `multi_string_length_cb`, `multi_string_length_cch`, `multi_string_length_n`, `multi_string_copy_cb`, and `multi_string_copy_cch`.

## Control flow

This header only declares APIs, but the documented contract is two-pass friendly: callers pass a buffer size, and append/prepend/conversion APIs report `KHM_ERROR_TOO_LONG` plus the required byte count when the destination is too small or null. Search/delete behavior is controlled by exact versus prefix matching and case-sensitive versus default case-insensitive matching. Traversal starts at the first element and repeatedly calls `multi_string_next` until null.

## State and persistence behavior

The API operates on caller-owned buffers. It does not allocate persistent state in the header contract. Persistence enters through callers that store the multi-string in NetIDMgr configuration spaces or convert it to/from CSV resource strings.

## Dependencies and integration points

The header depends on `khdefs.h` for `KHMEXP`, `KHMAPI`, `khm_int32`, and `khm_size`. It is included by `utils.h` and by NetIDMgr configuration code. In this work item, `afsconfigdlg.c` uses `csv_to_multi_string` and `multi_string_next` to turn a localized service-status CSV resource into display strings.

## Risks and edge cases

The maximum size is fixed at 16,384 wide characters. Callers must distinguish byte counts from character counts and preserve the double-null terminator. Empty strings are invalid for append. Prefix matching can delete the first partial match, which is useful but risky for ambiguous cell or realm names. CSV conversion must preserve quoting and embedded quotes to avoid lossy configuration round trips.

## Test signals

Useful tests cover empty initialized strings, append/prepend buffer-too-small reporting, delete exact/prefix and case-sensitive/insensitive behavior, traversal across the final double-null, CSV quoting for commas and quotes, malformed CSV handling, and byte-versus-character copy limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/mstring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/netidmgr.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/netidmgr.h

## Purpose

`netidmgr.h` is the umbrella include for the NetIDMgr SDK subset carried in the OpenAFS Windows tree. It gives plugins one stable include that pulls together definitions for utilities, UI, message queues, credential database access, configuration, modules, and plugin declarations.

## Important APIs, types, and functions

This file declares no functions of its own. It includes `khdefs.h`, `utils.h`, `khuidefs.h`, `kmq.h`, `khmsgtypes.h`, `kcreddb.h`, `kherr.h`, `kherror.h`, `kconfig.h`, `kmm.h`, and `kplugin.h`.

## Control flow

There is no runtime control flow. Compile-time control is the include guard `__NETIDMGR_H`, which prevents duplicate inclusion.

## State and persistence behavior

The header owns no state. It exposes APIs whose implementations manage credential state, configuration state, module state, and UI state elsewhere.

## Dependencies and integration points

The AFS credential plugin includes this through `afscred.h`, making NetIDMgr message queues, credential attributes, configuration spaces, plugin callbacks, error reporting, and UI configuration APIs available throughout the plugin.

## Risks and edge cases

As an umbrella header, the main risk is accidental dependency expansion and include-order coupling. The included headers expose Windows and NetIDMgr types broadly, so consumers may compile only in the expected NetIDMgr/KfW environment.

## Test signals

Build validation is the primary signal: plugin sources should compile when including only `netidmgr.h` through `afscred.h`, and duplicate inclusion should not redefine symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/netidmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/netidmgr_version.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/netidmgr_version.h

## Purpose

`netidmgr_version.h` centralizes NetIDMgr version constants and Windows version-resource macros. It lets modules and resource scripts agree on product version, API version, compatibility floor, file type, and special NetIDMgr string-resource keys.

## Important APIs, types, and functions

The key macros are `KH_VERSION_MAJOR`, `KH_VERSION_MINOR`, `KH_VERSION_PATCH`, `KH_VERSION_AUX`, `KH_VERSION_API`, `KH_VERSION_API_MINCOMPAT`, `KH_VERSION_LIST`, and string forms such as `KH_VERSION_STRING` and `KH_VERSION_STRINGW`. Windows resource fields include `KH_VER_FILEFLAGMASK`, `KH_VER_FILEFLAGS`, `KH_VER_FILEOS`, `KH_VER_FILETYPEDLL`, and `KH_VER_FILETYPEAPP`. NetIDMgr metadata keys are `NIMV_MODULE`, `NIMV_PLUGINS`, `NIMV_APIVER`, and `NIMV_SUPPORT`.

## Control flow

The file has only preprocessor control flow via `__NETIDMGR_VERSION_H`. Version values are compile-time constants.

## State and persistence behavior

No runtime state is created. The constants become persistent only when embedded into binaries or resources, where they govern plugin/API compatibility checks and version display.

## Dependencies and integration points

It includes `windows.h` for version-resource constants such as `VOS_NT_WINDOWS32`, `VFT_DLL`, and `VFT_APP`. The AFS plugin uses NetIDMgr API compatibility in `afscred.h`; when `KH_VERSION_API < 7`, it loads older UI APIs dynamically.

## Risks and edge cases

Incorrect version constants can break plugin loading or cause resource metadata to advertise the wrong compatibility. The API minimum equals the API version here, which means consumers requiring older compatibility must update these constants deliberately.

## Test signals

Inspect built resource metadata, plugin load logs, and compatibility paths. Builds against API versions below 7 should exercise the dynamic function-pointer fallback declared in `afscred.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/netidmgr_version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/perfstat.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/perfstat.h

## Purpose

`perfstat.h` declares debug allocation wrappers for NetIDMgr utility code. In debug builds, allocation calls are routed through tracking functions that record source file and line; in non-debug builds, the macros map directly to CRT allocation and string-duplication functions.

## Important APIs, types, and functions

Macros include `PMALLOC`, `PCALLOC`, `PREALLOC`, `PFREE`, `PDUMP`, `PWCSDUP`, and `PSTRDUP`. Debug implementations declared here are `perf_malloc`, `perf_realloc`, `perf_free`, `perf_dump`, `perf_wcsdup`, `perf_strdup`, and `perf_calloc`.

## Control flow

Preprocessor branching on `DEBUG` selects tracked versus direct allocation. Debug macros pass `__FILE__` and `__LINE__` to the allocator. Release builds compile away dump behavior with `PDUMP(f) ((void) 0)`.

## State and persistence behavior

The header does not define storage, but debug implementations likely maintain an in-process allocation ledger. `perf_dump` can persist that ledger to a named file.

## Dependencies and integration points

It depends on `khdefs.h` for export/calling convention macros and on CRT allocation APIs. The AFS plugin uses `PMALLOC`/`PFREE` for dialog state and extension strings, so debug builds can trace leaks across plugin configuration and extension registration paths.

## Risks and edge cases

Because release macros map to CRT `wcsdup` and `strdup`, portability depends on those functions being available. Mixing `PMALLOC` allocations with nonmatching frees outside `PFREE` would undermine debug tracking. Debug source-location tracking can also reveal memory leaks caused by early return paths in plugin dialogs or extension setup.

## Test signals

Debug test signals include no residual entries after dialogs are destroyed and extensions are freed, correct dump output, and clean behavior for zero-size or failed allocations. Release builds should compile without unresolved perf symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/perfstat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/sync.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/sync.h

## Purpose

`sync.h` declares a Windows read/write lock abstraction for NetIDMgr utilities. It provides multiple-reader/single-writer coordination using a `CRITICAL_SECTION`, event handles, lock counters, status, and a writer thread id.

## Important APIs, types, and functions

The central type is `rw_lock_t`, also exposed as `RWLOCK` and `PRWLOCK`. It stores `locks`, `status`, `cs`, `readwx`, `writewx`, and `writer`. Lifecycle APIs are `InitializeRwLock` and `DeleteRwLock`. Locking APIs are `LockObtainRead`, `LockReleaseRead`, `LockObtainWrite`, and `LockReleaseWrite`.

## Control flow

The documented behavior is classic reader/writer arbitration. Readers can share access unless a writer owns or is pending on the lock. Writers wait until readers drain, and recursive write locks by the same thread are supported if every obtain has a matching release. Wakeups are issued to waiting readers or writers after release.

## State and persistence behavior

All state is in the caller-owned `RWLOCK` object and Windows kernel synchronization primitives created during initialization. The state is process-lifetime only and must be deleted to close handles.

## Dependencies and integration points

The header depends on `khdefs.h` and Windows types. It is included by `utils.h`, making it part of the common NetIDMgr utility surface. Shared credential/configuration code can use it where concurrent readers and exclusive writers are needed.

## Risks and edge cases

The implementation contract requires strict acquire/release pairing. Failing to call `DeleteRwLock` can leak handles. Recursive write support is documented, but recursive read behavior and upgrade/downgrade semantics are not defined here. Writer fairness depends on implementation details outside this header.

## Test signals

Tests should exercise concurrent readers, writer exclusion, release wakeups, recursive write acquire/release by one thread, deletion after use, and stress for writer starvation or missed wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/sync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/utils.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/utils.h

## Purpose

`utils.h` is a convenience include that groups NetIDMgr utility modules under the Doxygen `util` group. It pulls in hash tables, synchronization, multi-strings, and performance allocation tracking.

## Important APIs, types, and functions

The file declares no direct APIs. It includes `hashtable.h`, `sync.h`, `mstring.h`, and `perfstat.h`.

## Control flow

There is no runtime control flow. The include guard is `__KHIMAIRA_UTIL_H`.

## State and persistence behavior

The header owns no state. It exposes utility modules that may manage caller-owned buffers, synchronization objects, or debug allocation ledgers.

## Dependencies and integration points

`netidmgr.h` includes this file, so plugin code receiving the umbrella header also receives multi-string helpers, allocation wrappers, read/write locks, and hash-table declarations. In this work item, the AFS plugin relies indirectly on `PMALLOC`, `PFREE`, and multi-string conversion through that include chain.

## Risks and edge cases

The main risk is broad coupling: a consumer that includes `utils.h` must have all subordinate headers available and compatible. It also increases the chance of naming collisions from older Windows/C runtime headers.

## Test signals

Compile-only tests are appropriate. A source including `utils.h` should see all four utility families and should not require ordering hacks around Windows headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/arpa/nameser.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/arpa/nameser.h

## Purpose

`nameser.h` is a bundled BSD/BIND-compatible DNS protocol header for the Windows wshelper library. It defines DNS packet sizes, classes, types, opcodes, response codes, the DNS `HEADER` bitfield layout, resource-record structure, and network-byte-order helper macros.

## Important APIs, types, and functions

Important constants include `PACKETSZ`, `MAXDNAME`, `MAXCDNAME`, `MAXLABEL`, `QFIXEDSZ`, `RRFIXEDSZ`, `NAMESERVER_PORT`, `QUERY`, `NOERROR`, `NXDOMAIN`, DNS types such as `T_A`, `T_NS`, `T_CNAME`, `T_MX`, `T_TXT`, query types `T_AXFR` and `T_ANY`, and classes `C_IN`, `C_CHAOS`, `C_HS`, and `C_ANY`. Types include `HEADER` and `struct rrec`. It declares `_getshort` and `_getlong` and defines `GETSHORT`, `GETLONG`, `PUTSHORT`, and `PUTLONG`.

## Control flow

Compile-time byte-order detection selects the bitfield layout inside `HEADER`; if no platform is matched, the header defaults to little-endian for Intel x86. The GET/PUT macros advance caller-provided byte pointers while composing or consuming DNS wire-format integers.

## State and persistence behavior

No runtime state is stored. The macros and structures shape transient DNS request and response buffers generated by resolver code.

## Dependencies and integration points

For Win32 builds it includes `winsock.h` to obtain `u_short`, `u_char`, and related network types. `resolv.h` includes this header when `MAXDNAME` is not already defined. The wshelper resolver APIs use these constants to emulate BIND resolver behavior over Windows DNS APIs.

## Risks and edge cases

The `HEADER` bitfields are compiler- and byte-order-sensitive. The fallback to little-endian is appropriate for the intended Windows x86 history but risky for unusual targets. `PUTLONG` intentionally modifies its first argument. Pointer-advancing macros trust buffer size and can overrun if callers do not prevalidate DNS packet bounds.

## Test signals

DNS packet tests should validate header bit layout, integer encode/decode round trips, compressed-name offset handling with `INDIR_MASK`, and cross-compiler structure packing. Fuzzing DNS buffers should focus on macro callers, because this header itself has no bounds checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/arpa/nameser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/hesiod.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/hesiod.h

## Purpose

`hesiod.h` declares the Windows wshelper Hesiod API. Hesiod maps names and types to DNS TXT-style records, historically used at MIT for user, mail, service, and password data.

## Important APIs, types, and functions

Configuration constants are `HESIOD_CONF`, `DEF_RHS`, and `DEF_LHS`. Error codes are `HES_ER_UNINIT`, `HES_ER_OK`, `HES_ER_NOTFOUND`, `HES_ER_CONFIG`, and `HES_ER_NET`. Query APIs are `hes_to_bind`, `hes_resolve`, `hes_error`, and `hes_free`. Higher-level accessors are `hes_getmailhost`, `hes_getservbyname`, `hes_getpwnam`, and `hes_getpwuid`. `struct hes_postoffice` stores `po_type`, `po_host`, and `po_name`.

## Control flow

The documented flow is `hes_to_bind` combines the caller's name/type with LHS/RHS suffixes, `hes_resolve` performs the DNS lookup and returns a null-terminated vector, callers inspect errors through `hes_error`, and `hes_free` releases vector results. Higher-level APIs perform specific Hesiod lookups and return thread-local/static structures that callers must copy before the next call.

## State and persistence behavior

The library can read `c:\net\tcp\hesiod.cfg` for site-specific LHS/RHS suffixes, falling back to `.ns` and `.Athena.MIT.EDU`. Returned structures are owned by the library and reused per call per thread, making them transient state rather than caller-owned allocations except for `hes_resolve` vectors.

## Dependencies and integration points

The header includes `windows.h` and uses `LPSTR` plus `WINAPI`. It integrates with `resolv.h` DNS search behavior and with wshelper's Unix-compatible network lookup surface.

## Risks and edge cases

The hard-coded default file path and MIT defaults are site-specific. Callers can accidentally keep stale pointers returned by thread-local/static APIs. Error state is likely global or thread-local, so mixed concurrent calls need implementation review. Returned strings are narrow `LPSTR`, so code-page assumptions matter.

## Test signals

Tests should cover config-file parsing versus default suffixes, DNS not-found and network errors, freeing `hes_resolve` vectors, repeated calls overwriting static structures, and integration with service/passwd/mailhost record formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/hesiod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/mitwhich.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/mitwhich.h

## Purpose

`mitwhich.h` defines legacy Windows operating-system, Winsock stack, DNS server, default domain, resolver configuration path, and TCP/IP registry-key constants used by wshelper to discover network configuration.

## Important APIs, types, and functions

OS/stack strings and identifiers include `NT_32`, `NT_16`, `W95_32`, `W95_16`, `LWP_16`, `MS_NT_32`, `MS_95_32`, `NOVELL_LWP_16`, `MS_OS_NT`, `MS_OS_2000`, `MS_OS_XP`, and related unknown codes. DNS fallback constants are `DNS1`, `DNS2`, `DNS3`, and `DEFAULT_DOMAIN`. Resolver and registry constants include `_PATH_RESCONF`, `NT_TCP_PATH`, `NT_TCP_PATH_TRANS`, `W95_TCP_PATH`, `NT_DOMAIN_KEY`, `NT_NS_KEY`, `W95_DOMAIN_KEY`, and `W95_NS_KEY`.

## Control flow

There is no runtime logic. Preprocessor branching sets `_PATH_RESCONF` to `/etc/resolv.conf` for non-Windows targets and `c:/net/tcp/resolv.cfg` for Windows targets.

## State and persistence behavior

The file creates no state, but it points resolver code at persistent registry paths and optional resolver configuration files. The DNS server defaults are compiled into binaries as last-resort configuration.

## Dependencies and integration points

`wshelper.h` includes this header, and resolver initialization code uses these registry keys and defaults to locate domain names and name servers on older Microsoft TCP/IP stacks.

## Risks and edge cases

The values are historically MIT-specific and include hard-coded DNS server IPs. Modern Windows networking may not use the old registry paths or stack names. Site administrators were expected to rebuild or edit resources for non-MIT defaults, so unmodified binaries can resolve through inappropriate fallback servers if discovery fails.

## Test signals

Resolver initialization tests should simulate registry-present, config-file-present, and fallback-only cases. Non-MIT packaging should verify these defaults are overridden where appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/mitwhich.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/resolv.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/resolv.h

## Purpose

`resolv.h` declares a BIND-style resolver interface implemented on Windows. It exposes resolver state, DNS search options, query/compression functions, and compatibility stubs for unsupported resolver APIs.

## Important APIs, types, and functions

Constants include `MAXNS`, `MAXDFLSRCH`, `MAXDNSRCH`, `LOCALDOMAINPARTS`, `RES_TIMEOUT`, and `MAXMXRECS`. `struct mxent` stores MX preferences and hostnames. `struct state` stores retry timing, option flags, name server addresses, packet id, default domain, and search list. Resolver option flags include `RES_INIT`, `RES_DEBUG`, `RES_USEVC`, `RES_RECURSE`, `RES_DEFNAMES`, `RES_DNSRCH`, and `RES_DEFAULT`. Public APIs are `res_init`, `res_search`, `dn_comp`, `rdn_expand`, `res_setopts`, `res_getopts`, `res_mkquery`, `res_send`, and `res_querydomain`. The macro `dn_expand` is redirected to `rdn_expand`.

## Control flow

The intended runtime flow is to call `res_init` to populate global `_res`, then call `res_search` with a DNS name, class, and type. Compression helpers encode and expand DNS names while maintaining pointer tables. Unsupported functions are declared for compatibility but documented as unsupported.

## State and persistence behavior

The global `extern struct state _res` holds resolver process state: retry settings, options, name servers, default domain, and search domains. `res_init` reads environment, local host/domain, registry, or resolver files to populate this state. Query buffers are caller-owned.

## Dependencies and integration points

The header includes `windows.h`, `arpa/nameser.h`, and `stdio.h`. It is included by `wshelper.h`, which layers host, service, and Hesiod helpers over these resolver primitives. The `dn_expand` redirection avoids conflict with Microsoft library implementations.

## Risks and edge cases

Global `_res` state is mutable and potentially non-thread-safe. The answer buffer contract requires callers to compare returned response size with `anslen` to detect truncation. Legacy option flags include virtual-circuit and stay-open semantics that may not be implemented when backed by Windows DNS APIs. Macro remapping of `dn_expand` can surprise consumers expecting the Winsock symbol.

## Test signals

Tests should cover `res_init` with environment, registry, and fallback inputs; `res_search` response sizing; name compression/decompression including loops and bounds; `dn_expand` macro behavior; and unsupported function return behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/resolv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/wshelper.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/wshelper.h

## Purpose

`wshelper.h` is the top-level public header for the Windows WSHelper DNS/Hesiod compatibility library. It exposes resolver-backed replacements for host, service, address parsing, hostname, and domain-name lookup APIs.

## Important APIs, types, and functions

Supported APIs are `rgethostbyname`, `rgethostbyaddr`, `rgetservbyname`, `inet_aton`, `wsh_gethostname`, and `wsh_getdomainname`. Declared unsupported placeholders are `gethinfobyname`, `getmxbyname`, `getrecordbyname`, and `rrhost`.

## Control flow

Callers use `rgethostbyname` or `rgethostbyaddr` to obtain library-owned `hostent` structures, `rgetservbyname` for service data, `inet_aton` to parse IPv4 dotted strings, and `wsh_gethostname`/`wsh_getdomainname` to discover local naming. Simple hostnames are documented as expanded using the default domain search behavior.

## State and persistence behavior

Returned `hostent` and `servent` structures are library-owned and only one copy is allocated per call per thread, so callers must copy data they need to retain. Resolver configuration state is inherited from `resolv.h` and `mitwhich.h`.

## Dependencies and integration points

The header includes `winsock.h`, `mitwhich.h`, `resolv.h`, and `hesiod.h`. It provides a Unix-like lookup surface for Windows components that expect BIND/Hesiod semantics.

## Risks and edge cases

The API mixes supported and unsupported functions in one header. Static/thread-local result ownership can cause use-after-next-call bugs. It is IPv4-centric through `inet_aton` and older Winsock structures. Name expansion depends on resolver defaults that may be MIT-specific unless configured.

## Test signals

Tests should verify host lookup with simple and fully qualified names, reverse lookup, service lookup including protocol filtering, `inet_aton` acceptance/rejection cases, buffer sizing for hostname/domain functions, and repeated-call ownership behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/wshelper/wshelper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/license/main.cpp -->
# sources/distributed-fs/openafs/src/WINNT/license/main.cpp

## Purpose

`main.cpp` implements a standalone Windows command-line converter named in usage as `sgml2rtf`. It reads SGML-like license/source text files, converts a small set of markup tags into RTF paragraph/header formatting, escapes RTF-special characters, and writes `.rtf` files next to the input names.

## Important APIs, types, and functions

Global state is `g::CodePage`, defaulting to `CP_ACP` and overrideable by numeric command-line switches. `EscapeSpecialCharacters` escapes `\`, `{`, and `}` for RTF. `FormatFile` maps input text to RTF output. `TranslateFile` reads the source file, converts wide input text to a multibyte target with `WideCharToMultiByte`, and calls `FormatFile`. `FindFullPath` combines a wildcard path prefix with a found filename. `main` parses arguments, expands wildcards with `FindFirstFile`/`FindNextFile`, accumulates file names with `mstrcat`, and invokes conversion.

## Control flow

`main` scans command-line arguments. Switches beginning with `-` or `/` set the code page. Other arguments are treated as wildcard file specs. For each matching non-directory file, it appends the full path to a null-separated multistring. It then walks that multistring and calls `TranslateFile`.

`TranslateFile` opens the file, reads the entire content into a zero-padded buffer, allocates a target buffer four times the source size, converts from wide characters with the selected code page, and passes the text to `FormatFile`. `FormatFile` replaces the extension with `.rtf`, creates a new output file, writes an RTF prolog with the code page, tokenizes the input by whitespace, newlines, and `<...>` tags, maps `<?>` and `<p>` to paragraph breaks, maps `<d>` to bold section headings, writes escaped text runs, and finishes with an RTF trailer.

## State and persistence behavior

Persistent output is the generated `.rtf` file. The converter overwrites existing output with `CREATE_ALWAYS`. `EscapeSpecialCharacters` uses a static heap buffer reused across calls, and `FindFullPath` uses a static `MAX_PATH` buffer, so both are single-threaded helpers. Input file lists are stored in the license utility's custom multistring allocation and freed after processing.

## Dependencies and integration points

The file depends on Win32 file APIs, wildcard enumeration, `WideCharToMultiByte`, RTF syntax, and `license/multistring.h`. It is independent of NetIDMgr and the AFS plugin.

## Risks and edge cases

The converter assumes the source buffer can be interpreted as `LPCWSTR`, which is risky for byte-oriented SGML inputs. `EscapeSpecialCharacters` computes `cchReq = cchIn * 2 + 1`, but a `}` expands to four characters (`\\'7D`), so the static output buffer can be too small for many right braces. `FormatFile` uses `lstrcpy`/`lstrcat` into `MAX_PATH` buffers with no length checks. File-size based allocations have little overflow/error handling. The parsing only understands a tiny tag subset and skips leading whitespace/newlines aggressively.

## Test signals

Tests should convert files containing backslashes, braces, `<?>`, `<p>`, and multiple `<d>` headings; verify code-page values in the RTF prolog; exercise wildcard expansion; check extension replacement for names with and without dots; and stress right-brace-heavy input to catch the escaping buffer bug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/license/main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/license/multistring.cpp -->
# sources/distributed-fs/openafs/src/WINNT/license/multistring.cpp

## Purpose

`multistring.cpp` implements a small TCHAR multistring helper used by the license converter. It supports allocation, freeing, walking, length/count calculation, case-insensitive search, append, and delete over strings separated by an arbitrary separator character, including `'\0'` for conventional double-null multistrings.

## Important APIs, types, and functions

`lstrncmpi` is a local case-insensitive bounded comparison using `CharNext` and `toupper`. Public functions are `mstralloc`, `mstrfree`, `mstrwalk`, `mstrlen`, `mstrcount`, `mstrstr`, `mstrcat`, and `mstrdel`.

## Control flow

`mstrwalk` is the iterator primitive. On first call, when `*ppSegment` is null, it returns the first segment; on later calls it advances by the previous segment length, consumes the separator, and returns the next segment until it reaches an empty segment. `mstrlen`, `mstrcount`, and `mstrstr` are simple loops over `mstrwalk`.

`mstrcat` computes the old multistring length, the appended string length, and how many characters to retain before the terminal separator. It allocates a new buffer, copies retained content, inserts a separator when needed, copies the appended string, double-terminates when `chSep` is null, frees the old buffer, and updates the caller's pointer. `mstrdel` allocates a replacement buffer and copies all segments except case-insensitive exact matches for the removal string.

## State and persistence behavior

All multistring memory is allocated with `GlobalAlloc(GMEM_FIXED)` and must be released with `mstrfree`. The functions mutate the caller's pointer on append/delete and do not persist state elsewhere.

## Dependencies and integration points

The implementation depends on `windows.h`, TCHAR APIs, `GlobalAlloc`, `GlobalFree`, `lstrlen`, `lstrcpy`, `CharNext`, and CRT `toupper`. `main.cpp` uses `mstrcat` to collect wildcard-expanded filenames and `mstrfree` after translation.

## Risks and edge cases

`lstrncmpi` calls `toupper` on `TCHAR`, which is not correct for Unicode builds with wide characters. `mstrcat` does not validate `pszAppend` before `lstrcpy`; null append computes zero length but can still dereference null. The helpers repeatedly allocate and copy on every append, so large file lists scale poorly. Separator handling is subtle when `chSep` is null versus non-null, and callers must initialize the pointer to null.

## Test signals

Tests should cover appending to null and non-empty multistrings, walking null-separated and comma-separated variants, deleting first/middle/last/all entries, case-insensitive matching, Unicode/TCHAR build behavior, null append handling, and length/count consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/license/multistring.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/license/multistring.h -->
# sources/distributed-fs/openafs/src/WINNT/license/multistring.h

## Purpose

`multistring.h` declares the custom multistring helper used by the Windows license conversion tool. It is separate from NetIDMgr's `mstring.h` and uses `TCHAR`/`LPTSTR` plus an explicit separator character.

## Important APIs, types, and functions

Declared APIs are `mstralloc`, `mstrfree`, `mstrwalk`, `mstrlen`, `mstrcount`, `mstrstr`, `mstrcat`, and `mstrdel`.

## Control flow

The header has no runtime flow. Its comments document the expected operations: allocate/free, iterative progression, length including separators/nulls, entry count, substring membership, append without duplicate checking, and removal.

## State and persistence behavior

The caller owns the multistring pointer and passes it to the implementation for mutation. There is no global state declared here.

## Dependencies and integration points

This header assumes Windows/TCHAR types are already available; `main.cpp` includes `windows.h` before it. It is used only by the license converter in this work item.

## Risks and edge cases

Because the header does not include `windows.h` itself, include ordering matters. The API names are generic and can collide with other multistring utilities if included broadly. Allocation/free pairing with the implementation's `GlobalAlloc`/`GlobalFree` must be respected.

## Test signals

Compile tests should include it after `windows.h`. Behavioral tests belong to `multistring.cpp` and should verify caller-visible pointer mutation and separator semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/license/multistring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsconfig.c -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsconfig.c

## Purpose

`afsconfig.c` is generated configuration schema data for the OpenAFS NetIDMgr credential provider. It declares the tree of plugin configuration spaces and default values consumed by the plugin at registration and runtime.

## Important APIs, types, and functions

The only exported object is `kconf_schema schema_afsconfig[]`. It defines the root `AfsCred` space, metadata keys `Module`, `Description`, `Dependencies`, `Type`, and `Flags`, plugin options such as `Cells` and `Disableafscreds`, the nested `Parameters` space with `AFSEnabled`, `LRUCells`, `LRURealms`, and `DefaultCells`, plus a `Cells` space for per-identity cell mappings and per-cell `_Schema` values `MethodName`, deprecated `Method`, and `Realm`.

## Control flow

There is no runtime code. NetIDMgr configuration registration walks the schema array until `KC_ENDSPACE` entries close nested spaces.

## State and persistence behavior

Defaults become persistent configuration values when NetIDMgr creates or opens plugin spaces. User changes are later written through `khc_write_*` calls in dialog and credential code. The schema stores multi-string-like options as `KC_STRING` values.

## Dependencies and integration points

The file includes `kconfig.h` and is declared in `afscred.h`. Plugin initialization registers it so `csp_afscred` and `csp_params` can be opened and read by `afsconfigdlg.c`, `afsfuncs.c`, and new-credential UI code.

## Risks and edge cases

The file is generated and warns not to edit directly. Duplicate space names (`Parameters` under `AfsCred`, and `Cells` used both as a string and a nested space name) require consumers to open the correct path. `Method` is marked deprecated but retained for compatibility; code must prefer `MethodName` where supported.

## Test signals

Configuration tests should verify schema registration, default `AFSEnabled=1`, default `Disableafscreds=0`, default empty LRU/default cell lists, and migration behavior for deprecated numeric method values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsconfigdlg.c -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsconfigdlg.c

## Purpose

`afsconfigdlg.c` implements NetIDMgr configuration dialog procedures for AFS settings. It handles global AFS enablement, per-identity token configuration via the new-credentials dialog logic, OpenAFS service status/start/stop controls, version/company display, startup shortcut suppression, and context help.

## Important APIs, types, and functions

`afs_cfg_ids_proc` manages the global "obtain AFS tokens" option backed by `csp_params/AFSEnabled`. `afs_cfg_id_proc` wraps `afs_dlg_proc` for identity-specific configuration and writes identity data on apply. `set_service_status` queries `TransarcAFSDaemon`, maps service status through localized CSV strings, updates buttons and progress bar, and schedules polling during pending transitions. `afs_cfg_show_last_error` formats Windows errors for UI display. `afs_cfg_get_afscreds_shortcut` checks the common Startup folder for `AFS Credentials.lnk`. `afs_cfg_main_proc` drives the main service/config page.

## Control flow

`afs_cfg_ids_proc` allocates dialog state on `WM_INITDIALOG`, reads `AFSEnabled`, updates a checkbox, marks the config node modified on click, writes the value on `WMCFG_APPLY`, and frees state on destroy.

`afs_cfg_id_proc` delegates initialization to `afs_dlg_proc`, creates an identity from the selected config node name, populates `afs_dlg_data` with existing credentials and AFS enablement, marks the dialog as configuration mode, and on apply writes per-identity cell data. Destroy releases the identity and delegates cleanup.

`afs_cfg_main_proc` initializes by reading `Disableafscreds`, reading the OpenAFS service `ImagePath` from HKLM, extracting version/company fields from file version resources, and calling `set_service_status`. Button commands call `ServiceControl` to start/stop the daemon, shell out to `AFS_CONFIG.EXE`, or mark shortcut settings modified. Apply writes `Disableafscreds` and deletes the common-startup shortcut if requested. Timer messages refresh service status, and `WM_HELP` routes control-specific help through `afs_html_help`.

## State and persistence behavior

State is stored in per-dialog heap allocations, `DWLP_USER`, NetIDMgr configuration spaces, the Windows service control manager, HKLM service registry metadata, file version resources, and the common Startup folder shortcut. The global enable flag and `Disableafscreds` setting persist in NetIDMgr plugin config.

## Dependencies and integration points

The code depends on `afscred.h`, NetIDMgr configuration UI APIs, `afs_dlg_proc` and credential data helpers from the new-credentials code, `mstring.h` CSV conversion, Windows common controls, Shell APIs, registry APIs, service helpers from `afsfuncs.c`, localized resources, and HTML help.

## Risks and edge cases

`set_service_status` indexes localized CSV strings by raw Windows service status numeric value; malformed resource strings fall back to the first "unknown" entry. Progress calculation uses `GetTickCount` and can behave oddly across wraparound. `RegCloseKey(service_key)` is called only after successful open, but early jumps require careful maintenance. `kmm_get_plugin_config` return values are not always checked before writes. Deleting the startup shortcut is one-way and does not recreate it when the box is unchecked.

## Test signals

UI tests should verify checkbox persistence, per-identity apply behavior, service stopped/running/pending button enablement, timer progress updates, version/company extraction from the service binary, error dialogs for service-control failures, `AFS_CONFIG.EXE` launch failure, startup shortcut deletion, and context help routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsconfigdlg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afscred.h -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afscred.h

## Purpose

`afscred.h` is the central private/public include for the OpenAFS NetIDMgr credential provider. It gathers Windows, OpenAFS, Kerberos, NetIDMgr, resource, extension, token-acquisition, configuration, help, notification-icon, and compatibility declarations used by the plugin implementation.

## Important APIs, types, and functions

It defines plugin and credential names (`AFS_PLUGIN_NAME`, `AFS_CREDTYPE_NAME`, `KRB5_CREDTYPE_NAME`, `KRB4_CREDTYPE_NAME`), attribute/type names (`AFS_ATTRNAME_*`, `AFS_TYPENAME_*`), configuration node names, valid cell/realm character sets, and help file name. It declares lifecycle functions `init_afs`, `exit_afs`, `init_module`, `exit_module`, the plugin callback `afs_plugin_cb`, configuration dialog procs, `afs_html_help`, extension lookup/method APIs, `afs_ext_resolve_token`, `afs_ext_klog`, shortcut lookup, notification icon APIs, and global handles/attribute ids.

## Control flow

This header declares the plugin's main control surfaces but contains no executable code. It also conditionally declares dynamic NetIDMgr UI function pointers when `KH_VERSION_API < 7`, mapping older decorated DLL exports into modern-looking macros.

## State and persistence behavior

Extern globals include module/resource instances, credential type ids, attribute ids, message type ids, credential set, configuration space handles, and subscription handles. These are process-lifetime plugin state initialized and released by module/plugin code outside this work item. Persistent configuration is accessed through schema names declared here.

## Dependencies and integration points

The header bridges `netidmgr.h`, OpenAFS auth/cache manager headers, `afspext.h`, `afsfuncs.h`, `afsnewcreds.h`, string safety APIs, language resources, and Windows. It is included by every plugin implementation file in this work item.

## Risks and edge cases

Because it is broad, include-order and macro side effects matter: `_WINSOCKAPI_`, `_USE_32BIT_TIME_T`, `NOSTRSAFE`, and compatibility macros can affect consumers. Most extension APIs are explicitly "not thread safe" and must be called only from the plugin thread. Global handles must be initialized before use by dialogs and token functions.

## Test signals

Build tests should cover 32-bit, 64-bit, `KH_VERSION_API < 7`, and newer API cases. Runtime tests should verify global id registration, extension method enumeration, valid method lookup/name conversion, and compatibility function-pointer loading on older NetIDMgr builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afscred.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsext.c -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsext.c

## Purpose

`afsext.c` implements the AFS plugin extension registry and dispatch layer. It allows extension plugins to announce themselves, optionally provide token acquisition methods, resolve existing AFS tokens to NetIDMgr identities, and perform token acquisition when built-in Kerberos methods fail or are explicitly selected.

## Important APIs, types, and functions

Static state includes `extensions[MAX_EXTENSIONS]`, `n_extensions`, and `next_method_id` starting at `AFS_TOKEN_USER`. Registration/lifetime functions are `afs_add_extension`, `afs_free_extension`, and `afs_remove_extension`. Lookup/enumeration functions are `afs_find_extension`, `afs_get_extension`, `afs_get_next_token_acq`, `afs_is_valid_method_id`, `afs_get_next_method_id`, `afs_get_method_id`, `afs_get_method_name`, `afs_get_method_ext`, and `afs_method_describe`. Dispatch functions are `afs_ext_resolve_token`, `afs_ext_klog`, and `afs_msg_ext`.

## Control flow

`afs_add_extension` validates the announcement size, name length, subscription handle, optional token-acquisition descriptions, and supported API version. It rejects invalid announcements and a full registry, copies the announcement into the next array slot, duplicates mutable strings with `PMALLOC`, assigns a new method id for token-acquisition providers, and increments `n_extensions`.

Method enumeration returns built-in methods first (`AUTO`, `KRB5`, `KRB524`, `KRB4`), then extension-provided methods in registry order. Name/id conversion maps built-ins through stable token-name constants and extension methods through extension names.

`afs_ext_resolve_token` builds an `afs_msg_resolve_token` request and sends it to each token-acquisition extension subscription until one succeeds and fills an identity/method. `afs_ext_klog` builds an `afs_msg_klog`, copies the cell configuration to a correctly sized local structure, and sends it to all matching providers or all providers for automatic mode until one succeeds. `afs_msg_ext` currently handles only `AFS_MSG_ANNOUNCE`.

## State and persistence behavior

Extension state is in-process and not persisted. Method ids for extension providers are assigned sequentially during runtime announcement and are therefore not stable across process starts. Announced subscriptions are deleted when an extension is freed.

## Dependencies and integration points

The file depends on `afscred.h`, NetIDMgr message queues (`kmq_send_sub_msg`, `kmq_delete_subscription`), resource strings for method descriptions, and the `afspext.h` message structures. `afsfuncs.c` calls `afs_ext_resolve_token` while listing existing tokens and `afs_ext_klog` as a fallback/acquisition path.

## Risks and edge cases

The extension registry is fixed at eight entries and explicitly not thread-safe. `afs_remove_extension` checks `idx > n_extensions` instead of `idx >= n_extensions`, so an index equal to the count passes the early check and can hit debug assertions or invalid access. Allocation failures are asserted but not fully handled in release builds before string copies. Extension method ids are volatile, so persisted numeric method ids are fragile; method names are safer.

## Test signals

Tests should cover valid/invalid announcements, max-extension rejection, duplicate/long names, built-in and extension method enumeration order, short/long descriptions, removal from middle/end, resolve dispatch success/failure, klog dispatch with explicit versus automatic method selection, and non-thread-safe access discipline on the plugin thread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsfuncs.c -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsfuncs.c

## Purpose

`afsfuncs.c` contains the AFS token and service helper logic for the NetIDMgr AFS credential provider. It detects the OpenAFS client service, lists and deletes tokens, maps AFS tokens into NetIDMgr credentials, obtains new tokens through Kerberos 5, krb524, Kerberos 4, or extension providers, resolves cell configuration, maps cells to realms, reports AFS errors, controls the Windows service, and checks identity realm compatibility.

## Important APIs, types, and functions

Public functions are `afs_is_running`, `afs_unlog`, `afs_unlog_cred`, `afs_princ_to_string`, `afs_list_tokens`, `afs_find_token`, `afs_list_tokens_internal`, `afs_klog`, `GetServiceStatus`, `ServiceControl`, `afs_report_error`, and `afs_check_for_cell_realm_match`. Important static helpers include `afs_filter_by_cell`, `afs_filter_for_token`, `afs_filter_krb5_tkt`, `afs_filter_krb4_tkt`, `ViceIDToUsername`, `copy_realm_of_ticket`, `afs_realm_of_cell`, `afs_get_cellconfig`, and `afs_get_cellconfig_callback`.

## Control flow

Service checks begin with `AfsAvailable` and `GetServiceStatus` against `TRANSARCAFSDAEMON`. `afs_unlog` forgets all tokens when the service is running. `afs_unlog_cred` extracts the token server principal from a NetIDMgr credential, logs a human-readable name, and calls `ktc_ForgetToken`.

`afs_list_tokens` flushes the plugin credential set, calls `afs_list_tokens_internal`, collects the resulting AFS credentials into the root NetIDMgr set, and updates the tray icon as token list, service stopped, or service error. `afs_list_tokens_internal` loops through `ktc_ListTokens`/`ktc_GetToken`, converts client and server principals to display strings, derives the AFS cell from the server principal, and associates each token with a NetIDMgr identity using layered heuristics: an existing root AFS token for the same cell, a matching Kerberos 5 `afs/<cell>` or `afs@<cell>` ticket, a matching Kerberos 4 `afs.<cell>` or `afs@<cell>` ticket, extension resolver callbacks, a persisted cell-to-identity mapping under `csp_afscred/Cells`, and finally a newly created identity based on the token principal. It then creates an AFS credential, sets method, issue/expire times, client/server principals, cell, and location attributes, and adds it to `afs_credset`.

`afs_klog` is the token-acquisition path. It verifies the service, normalizes null/empty service/cell/realm strings, resolves cell configuration from registry, cell file, or DNS, computes default service/cell/realm names, and attempts built-in Kerberos methods unless a specific method excludes them. The Kerberos 5 path initializes a context and cache for the identity, gets the client realm, tries service principals in several forms (`service/cell@realm`, `service@realm`, client realm, cell realm, and referral fallback), removes expired matching credentials and retries, embeds a Kerberos 5 ticket directly into an AFS token when possible, compares against an existing identical token, builds the AFS client principal, optionally maps/registers the user through the protection server with `ViceIDToUsername`, and calls `ktc_SetToken`. When built with Kerberos 4 support, failure or explicit krb524/krb4 selection can convert credentials through krb524d or obtain Kerberos 4 service tickets and set a v4-style token. If built-in methods do not obtain credentials and automatic or extension method mode is allowed, it dispatches to `afs_ext_klog`.

Cell and realm support flows through `afs_get_cellconfig`, which gets the root cell, fills a caller-supplied empty cell with the local cell, searches registry, cell file, and DNS for servers, and records linked-cell information. `afs_realm_of_cell` asks Kerberos 5 for the host realm of the first cell server or falls back to uppercasing the server DNS suffix or cell name.

## State and persistence behavior

The file mutates the global NetIDMgr AFS credential set, token state inside the OpenAFS cache manager through `ktc_SetToken`/forget APIs, service state through the Service Control Manager, and optional protection-server registration state via `pr_CreateUser`. It reads persistent cell data from OpenAFS registry/cellservdb/DNS sources and reads persisted NetIDMgr cell-to-identity mappings from `csp_afscred`. `afs_realm_of_cell` returns a pointer to a static realm buffer, so each call overwrites prior results.

## Dependencies and integration points

Dependencies include OpenAFS client/token APIs (`ktc_*`, `cm_*`, protection server functions), Kerberos 5 APIs and Heimdal ticket decoding, optional Kerberos 4 and krb524 dynamic imports, NetIDMgr credential and identity APIs, NetIDMgr error reporting, Windows service APIs, Winsock address structures, and extension dispatch from `afsext.c`. `afsconfigdlg.c` calls the service helpers; new-credential code calls `afs_klog`; notification icon code reflects `afs_list_tokens` results.

## Risks and edge cases

The identity-association logic is heuristic and can attach externally acquired tokens to the wrong identity when multiple identities have tickets for the same cell. `afs_get_cellconfig_callback` increments `numServers` without checking the destination array capacity visible in this file. `afs_realm_of_cell` uses static storage and is not thread-safe. Some assignments use `if (rc = ...)`, intentionally but easy to misread. `ViceIDToUsername` can create users in foreign cells when `ALLOW_REGISTER` is enabled. Kerberos acquisition has many fallback paths and can silently move from stronger/specific methods to legacy or extension behavior depending on build flags and method selection. Service-handle cleanup calls `CloseServiceHandle` on possibly null handles, which Windows tolerates poorly depending on API expectations.

## Test signals

Important tests include service stopped/running paths, list-token behavior with no tokens and multiple cells, identity association through each heuristic tier, expired ticket removal/retry, direct Kerberos 5 token setting, krb524/krb4 fallback builds, extension fallback success/failure, linked-cell output, cell config from registry/file/DNS, realm fallback with referrals, token deletion, service start/stop error handling, and realm-match checks for identities. Integration tests should confirm NetIDMgr attributes, expiration times, icon state, and no credential handle leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsfuncs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsfuncs.h -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsfuncs.h

## Purpose

`afsfuncs.h` declares the AFS service, token listing, token acquisition, token deletion, error reporting, and cell/realm compatibility helpers implemented in `afsfuncs.c`.

## Important APIs, types, and functions

Declared functions are `afs_is_running`, `afs_princ_to_string`, `afs_list_tokens`, `afs_find_token`, `afs_list_tokens_internal`, `afs_klog`, `afs_unlog`, `afs_unlog_cred`, `GetServiceStatus`, `ServiceControl`, `afs_report_error`, and `afs_check_for_cell_realm_match`. The `afs_klog` signature takes identity, service, cell, realm, lifetime, token method, output expiration, and output linked-cell buffer.

## Control flow

The header has no runtime flow, but its API shape exposes the main lifecycle: check service, obtain/list tokens, find/delete tokens, and report/control service state.

## State and persistence behavior

Callers should expect these functions to interact with OpenAFS token state, NetIDMgr credential sets, and the Windows Service Control Manager. `afs_klog` can return token expiration and linked cell through caller-provided outputs.

## Dependencies and integration points

The header assumes `afscred.h` has already provided `khm_handle`, `afs_tk_method`, and OpenAFS principal/token types. It is included back into `afscred.h` and used by dialogs and new-credential code.

## Risks and edge cases

Because it declares `GetServiceStatus` and `ServiceControl` with generic names, there is collision risk with other utility layers. Buffer-size expectations for `afs_princ_to_string` and `linkedCell` are implicit in the implementation rather than encoded in the prototype.

## Test signals

Compile tests should ensure the header is included through `afscred.h`. Runtime tests are the `afsfuncs.c` service/token scenarios, with special attention to output buffer sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsfuncs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afshelp.c -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afshelp.c

## Purpose

`afshelp.c` resolves and launches the OpenAFS NetIDMgr plugin HTML help file. It builds the full path to `afsplhlp.chm` relative to the plugin module and appends optional topic/postfix strings for callers.

## Important APIs, types, and functions

The file defines static `helpfile[MAX_PATH]` and public `afs_html_help(HWND caller, wchar_t * postfix, UINT cmd, DWORD_PTR data)`.

## Control flow

On first call, `afs_html_help` uses `GetModuleFileNameEx` with `hInstance` to locate the plugin module, strips the file name with `PathRemoveFileSpec`, appends `AFS_HELPFILE`, and caches that base path. On every call it copies the cached base to a larger stack buffer, appends any postfix such as a topic path, and calls `HtmlHelp` with the requested command and data.

## State and persistence behavior

The cached `helpfile` path is process-lifetime mutable state and is not protected by a lock. It does not persist to disk. HTML Help may open external UI state managed by the Windows help subsystem.

## Dependencies and integration points

It depends on `afscred.h`, `shlwapi.h`, `htmlhelp.h`, `psapi.h`, and string-safe APIs. `afsconfigdlg.c` and `afsicon.c` call it for configuration help and notification-menu help topics.

## Risks and edge cases

The comment says it can only be called from the UI thread. The static cache is not thread-safe. In debug builds it asserts that module-path lookup succeeds; in release builds a failure can leave an empty base and still call `HtmlHelp` with a relative/postfix-only path. The combined buffer is `MAX_PATH + MAX_PATH`, so very long postfixes can fail copy/cat silently via `StringCb*` return values that are ignored.

## Test signals

Tests should verify first-call path resolution, repeated-call cache reuse, topic postfix append, missing help file behavior, UI-thread invocation, and help commands used by configuration popups and welcome topics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afshelp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsicon.c -->
# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsicon.c

## Purpose

`afsicon.c` implements the OpenAFS token-state notification icon for NetIDMgr. It creates a hidden message-only window, adds/removes a shell notification icon, handles click/context-menu commands, opens help/release notes, and updates icon/tooltip state based on service or token status.

## Important APIs, types, and functions

Static state includes `message_window_class`, `notifier_window`, and `notification_icon_added`. Helper functions are `get_default_notifier_action`, `get_release_notes`, `handle_select`, `prepare_context_menu`, `handle_context_menu`, `notifier_wnd_proc`, `initialize_if_necessary`, `set_tooltip_and_icon`, `collect_cell_names`, and `set_state_from_ui_thread`. Public functions are `afs_remove_icon` and `afs_icon_set_state`.

## Control flow

`afs_icon_set_state` packages the desired `notification_icon_state` and optional credential set. If the icon already exists, it updates directly; otherwise it requests a NetIDMgr UI-thread callback. The callback initializes the window class/window/icon if necessary, then switches on state. For token reporting, it collects non-expired AFS cell names from the provided credential set and shows either a no-token icon or an OK icon with the cell list. Service-stopped and service-error states use separate icons and localized tooltips.

The hidden window receives `TOKEN_MESSAGE_ID` from the shell. Select/key-select triggers the configured default NetIDMgr action (`KHUI_ACTION_OPEN_APP` or new credentials). Context menu loads `IDR_CTXMENU`, adjusts the default item caption, hides Release Notes if not found, and tracks the popup. Command handling triggers the default action, opens plugin help, or opens `ReleaseNotes.chm` from the OpenAFS client installation path. `afs_remove_icon` deletes the shell icon.

## State and persistence behavior

State is in-process: registered window class atom, message window handle, and whether the shell icon was added. It reads persistent NetIDMgr config `CredWindow\NotificationAction` and HKLM OpenAFS client `CurrentVersion\PathName` for release notes. Tooltip content is generated from live credential expiration and cell attributes, not persisted.

## Dependencies and integration points

The file depends on shell notification APIs, NetIDMgr UI actions and callback scheduling, credential set traversal, AFS credential attributes, localized resources/icons/menus, `afs_html_help`, HTML Help, Shlwapi path helpers, and version resource macro `AFS_VERINFO_BUILD`.

## Risks and edge cases

`afs_icon_set_state` passes a pointer to a stack `state_data` into `khui_request_UI_callback`; correctness depends on that callback being synchronous or copying the data, which is not obvious from this file. `collect_cell_names` concatenates into a fixed 256-character buffer and ignores truncation failures. The release-notes registry string termination uses `cpath[min(cb_data, MAX_PATH - 1)]`, where `cb_data` is bytes for `RegQueryValueEx`, not a wide-character index. `Shell_NotifyIcon(NIM_SETFOCUS)` calls use a mostly empty `NOTIFYICONDATA`, which may not identify the icon on all shell versions.

## Test signals

Tests should verify icon creation/removal, click and keyboard selection, context menu default caption, release-notes discovery, help launch, tooltip content for no tokens and multiple non-expired cells, expired-token filtering, service stopped/error icons, callback behavior before icon creation, and long cell-list truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsicon.c -->
