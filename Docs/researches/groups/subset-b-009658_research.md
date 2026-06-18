# Research Group subset-b-009658

This grouped report covers selected libsmb2 examples, build metadata, platform configuration headers, public/private SMB2/DCERPC interfaces, and AES wrapper files under `sources/user-network-fs/libsmb2`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-stat-sync.c -->
# sources/user-network-fs/libsmb2/examples/smb2-stat-sync.c

## Purpose
`smb2-stat-sync.c` is a synchronous command-line example that connects to an SMB share and prints POSIX-like metadata for one SMB URL path. It demonstrates the high-level `libsmb2.h` synchronous connection, URL parsing, and `smb2_stat()` API.

## Important APIs, Types, and Functions
`usage()` prints the expected `smb://[domain;][user@]host[:port]/share/path` form and exits. `main()` uses `smb2_init_context()`, `smb2_parse_url()`, `smb2_set_security_mode(SMB2_NEGOTIATE_SIGNING_ENABLED)`, `smb2_connect_share()`, `smb2_stat()`, `smb2_disconnect_share()`, `smb2_destroy_url()`, and `smb2_destroy_context()`. The result is read from `struct smb2_stat_64`, including `smb2_type`, `smb2_size`, `smb2_ino`, link count, and four timestamp fields.

## Control Flow
The program validates that a URL argument was supplied, initializes a context, parses the URL into server/share/user/path fields, enables signing capability, connects to the share, calls `smb2_stat()` for `url->path`, switches over the returned SMB2 file type, prints scalar metadata and formatted local-time timestamps, then disconnects and destroys allocated URL/context state.

## State and Persistence Behavior
All state is transient process memory inside the libsmb2 context, parsed URL, and stack `smb2_stat_64`. It does not persist files or modify the share. On several error paths it exits without destroying the URL/context, which is acceptable for a short-lived example but not a pattern for long-running tools.

## Dependencies and Integration Points
It depends on libc formatting/time APIs, `smb2.h`, `libsmb2.h`, and `libsmb2-raw.h`. The operational integration point is any reachable SMB2/SMB3 server with credentials encoded in the URL or resolved by libsmb2 defaults.

## Risks and Edge Cases
The usage string has an extra `>` after host in the URL example. `asctime(localtime())` can return NULL on invalid timestamps and is locale/timezone dependent. Exit code `0` is used for init/parse failures, while connection/stat failures use `10`. The program enables signing as supported but does not require signing.

## Test Signals
Run against files, directories, missing paths, permission-denied paths, and servers with unusual timestamps. Check printed type mapping, 64-bit size/inode formatting, cleanup under success, and failure messages from `smb2_get_error()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-stat-sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-statvfs-sync.c -->
# sources/user-network-fs/libsmb2/examples/smb2-statvfs-sync.c

## Purpose
`smb2-statvfs-sync.c` is a synchronous example that reports filesystem capacity for an SMB URL path. It demonstrates `smb2_statvfs()` after URL parsing and share connection.

## Important APIs, Types, and Functions
The file uses `usage()`, `smb2_init_context()`, `smb2_parse_url()`, `smb2_set_security_mode()`, `smb2_connect_share()`, `smb2_statvfs()`, `smb2_disconnect_share()`, `smb2_destroy_url()`, and `smb2_destroy_context()`. Output comes from `struct smb2_statvfs`, especially `f_bsize`, `f_blocks`, `f_bfree`, and `f_bavail`.

## Control Flow
After argument validation, the program builds an SMB2 context and URL, enables signing capability, connects to the target share, calls `smb2_statvfs(smb2, url->path, &vfs)`, prints block size and allocation counts, then disconnects and frees resources.

## State and Persistence Behavior
State is limited to the connection context, parsed URL, and stack statvfs structure. The remote share is queried but not modified. Error exits before the final cleanup leak the context and URL for process lifetime.

## Dependencies and Integration Points
The example depends on libsmb2 high-level APIs and standard integer formatting. It conditionally excludes `<poll.h>` on Amiga-like targets, showing that examples are expected to compile on some non-POSIX platforms.

## Risks and Edge Cases
Only a subset of `struct smb2_statvfs` is printed, so file count/name-length fields are not demonstrated. `f_bsize` is printed with `%d` despite being `uint32_t`. The signing setting is enabled, not required, and URL parse/init failures exit with status `0`.

## Test Signals
Exercise root paths and subpaths on shares with quotas, full volumes, permission restrictions, and servers with large allocation-unit counts. Verify `PRIu64` output and behavior on unsupported filesystem-info classes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-statvfs-sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-truncate-sync.c -->
# sources/user-network-fs/libsmb2/examples/smb2-truncate-sync.c

## Purpose
`smb2-truncate-sync.c` is a synchronous mutation example that resizes a remote SMB file to a user-supplied length. It demonstrates `smb2_truncate()` with the high-level connection flow.

## Important APIs, Types, and Functions
`main()` uses `smb2_init_context()`, `smb2_parse_url()`, `smb2_set_security_mode()`, `smb2_connect_share()`, `smb2_truncate()`, `smb2_disconnect_share()`, `smb2_destroy_url()`, and `smb2_destroy_context()`. The length is parsed with `strtoll(argv[2], NULL, 10)` and passed to the `uint64_t` length parameter.

## Control Flow
The program requires URL and length arguments, initializes and parses the SMB URL, enables signing capability, connects, calls `smb2_truncate(smb2, url->path, parsed_length)`, and then disconnects/free resources on success.

## State and Persistence Behavior
The only durable effect is remote file size modification. Local state is transient. Failed initialization, URL parsing, connection, or truncation exits leave process-local resources unfreed; truncation failure may still have remote-side partial effects depending on server semantics.

## Dependencies and Integration Points
It integrates with SMB `SET_INFO`/end-of-file behavior through the high-level libsmb2 API. It depends on server permissions that allow write attributes or file resize.

## Risks and Edge Cases
`strtoll()` errors are not checked; negative values are converted to a large unsigned length when passed to `smb2_truncate()`. Directory paths, read-only files, missing files, and share modes fail through libsmb2. The usage URL has the same extra `>` typo as the stat example.

## Test Signals
Test shrinking, extending, zero length, nonnumeric length, negative length, read-only files, directories, and locked files. Verify remote size with `smb2-stat-sync` or another client after each successful operation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/examples/smb2-truncate-sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/idf_component.yml -->
# sources/user-network-fs/libsmb2/idf_component.yml

## Purpose
`idf_component.yml` declares libsmb2 as an ESP-IDF component. It provides metadata for Espressif builds rather than C code.

## Important APIs, Types, and Functions
The YAML keys are `version: "3.0.1"`, `description`, `url`, and `dependencies`. The only dependency constraint is `idf: ">=4.2"`.

## Control Flow
There is no runtime control flow. ESP-IDF tooling reads this file during component resolution to enforce minimum IDF version and expose package metadata.

## State and Persistence Behavior
No runtime state is created. The file influences dependency lockfiles or build metadata generated by ESP-IDF outside this source file.

## Dependencies and Integration Points
It integrates with the ESP-IDF component registry/build system and points to the upstream GitHub URL. It is paired with `lib/CMakeLists.txt`, which has an `ESP_PLATFORM` branch registering source files as a component.

## Risks and Edge Cases
The component version `3.0.1` differs from the generated config headers and public version macros that say libsmb2 `4.0.0`, which can confuse package consumers. The dependency only constrains IDF, not lwIP/mbedTLS or optional Kerberos support.

## Test Signals
Run ESP-IDF component resolution and build with IDF 4.2+ and a current IDF release. Check that the reported package version matches release expectations and that `ESP_PLATFORM` CMake sources compile.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/idf_component.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/Makefile.am -->
# sources/user-network-fs/libsmb2/include/Makefile.am

## Purpose
`include/Makefile.am` defines which headers are installed or distributed by the autotools build for libsmb2.

## Important APIs, Types, and Functions
`smb2dir = $(includedir)/smb2` sets the installation subdirectory. `dist_smb2_HEADERS` installs public headers: `libsmb2.h`, DCERPC headers, `libsmb2-raw.h`, `smb2.h`, and `smb2-errors.h`. `dist_noinst_HEADERS` distributes but does not install private/portability headers such as `asprintf.h`, `libsmb2-private.h`, `portable-endian.h`, and `slist.h`.

## Control Flow
Autotools expands these variables during `make dist`, `make install`, and library builds. No runtime code executes from this file.

## State and Persistence Behavior
The file affects installed filesystem layout and release tarball content. It does not create runtime state.

## Dependencies and Integration Points
It integrates with automake and must stay aligned with public CMake install headers and the library source includes. Public API additions need updates here to be installed by autotools.

## Risks and Edge Cases
`smb2-ioctl.h` is not listed in `dist_smb2_HEADERS`, so autotools installs may omit that public-looking header. Header list drift between CMake and automake can create build-system-specific API availability.

## Test Signals
Run `make distcheck` and inspect `make install DESTDIR=...` output. Confirm all headers included by public headers are available to downstream consumers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/amiga_os/config.h -->
# sources/user-network-fs/libsmb2/include/amiga_os/config.h

## Purpose
This generated-style `config.h` snapshot configures libsmb2 for Amiga OS targets.

## Important APIs, Types, and Functions
It defines feature macros such as `CONFIGURE_OPTION_TCP_LINGER`, header availability, `HAVE_SOCKADDR_LEN`, package identity, and version strings. GSSAPI/Kerberos, `HAVE_LINGER`, `HAVE_POLL_H`, `HAVE_SYS_POLL_H`, and `HAVE_SOCKADDR_STORAGE` are disabled in this variant.

## Control Flow
There is no direct control flow. The macros steer conditional compilation in socket, auth, endian, and compatibility code.

## State and Persistence Behavior
No state is persisted. Compile-time state is fixed by macros and affects binary capabilities.

## Dependencies and Integration Points
It integrates with code guarded by `HAVE_*` macros, especially network address handling, polling support, and auth provider selection. Package macros report libsmb2 `4.0.0`.

## Risks and Edge Cases
Disabling poll and sockaddr storage forces alternate code paths that need platform coverage. GSSAPI is unavailable, so authentication falls back to non-Kerberos mechanisms. Generated comments may not match a current configure run if platform headers change.

## Test Signals
Cross-compile on the Amiga target, run connection tests without poll support, and verify address iteration, linger behavior, and NTLM authentication.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/amiga_os/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/apple/config.h -->
# sources/user-network-fs/libsmb2/include/apple/config.h

## Purpose
This `config.h` snapshot configures libsmb2 for Apple platforms.

## Important APIs, Types, and Functions
It enables common POSIX headers, `HAVE_GSSAPI_GSSAPI_H`, linger, poll, sockaddr length/storage, and many system headers. `HAVE_LIBKRB5` remains undefined even though GSSAPI headers are present.

## Control Flow
Compilation uses these macros to include Apple socket, poll, GSSAPI, and platform byte-order paths. No runtime code lives here.

## State and Persistence Behavior
No runtime persistence. The header fixes feature detection for Apple builds and package strings report `libsmb2 4.0.0`.

## Dependencies and Integration Points
It integrates with Apple-specific GSS imports in `libsmb2-private.h`, Apple byte swapping in `portable-endian.h`, and the AES wrapper selecting `aes_apple.h` from `aes.c`.

## Risks and Edge Cases
GSSAPI headers are enabled but `HAVE_LIBKRB5` is not, so Kerberos code guarded by `HAVE_LIBKRB5` may be absent. Static generated macros can go stale across macOS SDK versions.

## Test Signals
Build on macOS with and without Kerberos library detection, run signed/encrypted SMB sessions, and confirm Apple AES and endian branches compile.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/apple/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/asprintf.h -->
# sources/user-network-fs/libsmb2/include/asprintf.h

## Purpose
`asprintf.h` provides inline fallback implementations of `_vscprintf`, `vasprintf`, and `asprintf` for platforms lacking those libc functions.

## Important APIs, Types, and Functions
`_vscprintf_so()` computes formatted length with `vsnprintf(NULL, 0, ...)` using `va_copy`. `vasprintf()` allocates a buffer of computed length plus terminator and formats into it. `asprintf()` wraps `vasprintf()` with varargs. Xbox maps `inline` to `__inline` and uses `_vscprintf`/`_vsnprintf`.

## Control Flow
Callers invoke `asprintf()`, which starts a `va_list`, delegates to `vasprintf()`, then ends the list. `vasprintf()` computes required length, allocates, formats, stores the output pointer, and returns the formatted byte count or `-1`.

## State and Persistence Behavior
The only persistent state is heap memory returned through `*strp`; callers must free it. On format failure after allocation, the function frees the buffer before returning `-1`.

## Dependencies and Integration Points
It depends on `<stdio.h>`, `<stdlib.h>`, `<stdarg.h>`, and usually `<malloc.h>`. It is distributed as a non-installed portability header used internally where `asprintf` is not available.

## Risks and Edge Cases
If `vsnprintf(NULL, 0, ...)` is not supported by a target, length calculation fails. The fallback is guarded with `#ifndef asprintf`/`vasprintf`, which detects macros but not necessarily external functions. Allocation size can overflow if `len` is near `INT_MAX`.

## Test Signals
Compile on MSVC/Xbox/MinGW and POSIX targets, format empty and long strings, force allocation failure where possible, and verify callers free returned buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/asprintf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/esp/config.h -->
# sources/user-network-fs/libsmb2/include/esp/config.h

## Purpose
This generated-style `config.h` snapshot configures libsmb2 for ESP-IDF/ESP platforms.

## Important APIs, Types, and Functions
It enables many libc headers plus `HAVE_LINGER`, `HAVE_SOCKADDR_STORAGE`, `HAVE_SYS_POLL_H`, and basic POSIX socket/stat/uio support. It disables GSSAPI, Kerberos, `HAVE_NETINET_TCP_H`, sockaddr `sa_len`, `sys/time.h`, and some Unix-specific header paths.

## Control Flow
No code executes here. Conditional compilation uses these feature macros in socket, auth, and portability layers.

## State and Persistence Behavior
The header has no runtime state. It determines compiled-in transport/auth behavior for ESP builds.

## Dependencies and Integration Points
It pairs with `idf_component.yml` and the `ESP_PLATFORM` branch in `lib/CMakeLists.txt`. Kerberos is excluded, so authentication depends on NTLMSSP and local credential configuration.

## Risks and Edge Cases
ESP lwIP/socket behavior differs from POSIX despite some POSIX macros being enabled. Generated package version macros say `4.0.0`, while ESP component metadata says `3.0.1`.

## Test Signals
Build under ESP-IDF 4.2+ and run socket connection, DNS, timeout, signing, and NTLM authentication tests on device or emulator.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/esp/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/libsmb2-private.h -->
# sources/user-network-fs/libsmb2/include/libsmb2-private.h

## Purpose
`libsmb2-private.h` is the central internal header for libsmb2. It defines the private context/PDU structures, receive-state machine, queue and vector bookkeeping, crypto/session fields, and internal packer/unpacker function contracts.

## Important APIs, Types, and Functions
Core types include `struct smb2_context`, `struct smb2_pdu`, `struct smb2_header`, `struct smb2_io_vectors`, `struct smb2dir`, `struct smb2_dirent_internal`, and `struct sync_cb_data`. Constants cover SMB2 header sizes, signature/key sizes, vector limits, tree nesting, credits, salts, and padding. Internal functions include allocation helpers, iovec management, tree-id stack management, PDU allocation/queue lookup/free, header decode, signature calculation, scalar endian get/set helpers, command-specific fixed/variable payload processors, file/filesystem/security descriptor encode/decode helpers, socket read/write helpers, timeout handling, and DCERPC alignment/scalar helpers.

## Control Flow
Incoming data advances through `enum smb2_recv_state`: SPL length, SMB2 or transform header, fixed payload, variable payload, padding, encrypted transform payload, or unknown cancelled-PDU data. Outgoing commands are built as `smb2_pdu` objects with header/iovec arrays and moved through `outqueue` and `waitqueue`. Each received header is matched to a waiting PDU by message id, decoded through command-specific fixed and variable processors, and completed through the PDU callback.

## State and Persistence Behavior
`struct smb2_context` owns socket descriptors, connection attempts, authentication settings, credentials, credits, tree/session/message ids, session/signing/sealing keys, encryption buffers, queues, receive buffers, last file id for related compounds, server capability values, error state, event callbacks, DCERPC settings, and server-list linkage. This is in-memory session state only; sensitive key material persists in the context until close/destroy.

## Dependencies and Integration Points
It includes Kerberos/GSSAPI headers only when `HAVE_LIBKRB5` is defined, and depends on public SMB2/DCERPC types from other headers. It is consumed by almost every implementation file under `lib/` and bridges public APIs, raw command packers, socket I/O, signing/encryption, and optional server mode.

## Risks and Edge Cases
The context is large and highly stateful; queue ownership, callback destruction, timeout processing, and encrypted/cancelled PDU handling are correctness-critical. `SMB2_MAX_PDU_SIZE` is 16 MiB and `SMB2_MAX_VECTORS` is fixed at 256, so compound or passthrough use must respect bounds. Sensitive keys require reliable cleanup paths.

## Test Signals
Exercise async request cancellation, compound requests, SMB3 encryption, signing verification, tree-id nesting, timeout expiry, partial socket reads/writes, out-of-order replies, server-side request decoding, and error string/NT status propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/libsmb2-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/picow/FreeRTOSConfig.h -->
# sources/user-network-fs/libsmb2/include/picow/FreeRTOSConfig.h

## Purpose
`FreeRTOSConfig.h` configures the FreeRTOS kernel for Pico W libsmb2 examples or builds.

## Important APIs, Types, and Functions
It enables preemption, mutexes, recursive mutexes, counting semaphores, queue sets, software timers, dynamic allocation, trace facility, and common task APIs. It sets a 1 kHz tick rate, 32 priorities, 2048 minimal stack units, 128 KiB heap, and `configASSERT(x)` to `assert(x)`. SMP-specific macros are enabled when `FREE_RTOS_KERNEL_SMP` is set.

## Control Flow
No libsmb2 control flow exists here. FreeRTOS uses the macros at compile time to include/exclude scheduler, timer, allocation, and task APIs.

## State and Persistence Behavior
Runtime state is FreeRTOS-managed heap, tasks, queues, semaphores, and timers sized according to this header. No filesystem persistence occurs.

## Dependencies and Integration Points
It integrates with Pico SDK/FreeRTOS and lwIP socket support used by libsmb2 on Pico W. `configENABLE_BACKWARD_COMPATIBILITY` is explicitly enabled for lwIP `sys_arch` compilation.

## Risks and Edge Cases
The 128 KiB heap and 1024 timer/thread stack sizes can be tight for SMB sessions with signing/encryption buffers. `configUSE_NEWLIB_REENTRANT` is disabled, which can matter for libc calls in multi-tasking examples. Stack overflow and malloc failed hooks are disabled.

## Test Signals
Build Pico W examples, run concurrent SMB operations under FreeRTOS, monitor heap and stack high-water marks, and test lwIP integration in both SMP and non-SMP configurations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/picow/FreeRTOSConfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/picow/config.h -->
# sources/user-network-fs/libsmb2/include/picow/config.h

## Purpose
This `config.h` snapshot configures libsmb2 for Raspberry Pi Pico W builds.

## Important APIs, Types, and Functions
It defines package metadata and selected feature macros. Most POSIX networking headers are disabled, while `HAVE_FCNTL_H`, `HAVE_DLFCN_H`, `HAVE_STDINT_H`, `HAVE_STDIO_H`, `HAVE_STDLIB_H`, `HAVE_SYS_STAT_H`, `HAVE_SYS_TYPES_H`, `HAVE_TIME_H`, `HAVE_UNISTD_H`, and `HAVE_SOCKADDR_STORAGE` are enabled.

## Control Flow
No direct control flow exists. The macros select embedded/lwIP-compatible code paths during compilation.

## State and Persistence Behavior
No runtime persistence. Compile-time feature choices affect socket/address and authentication behavior.

## Dependencies and Integration Points
It integrates with Pico SDK, lwIP, `portable-endian.h`'s `PICO_PLATFORM` path, and the Pico W FreeRTOS/lwIP option headers.

## Risks and Edge Cases
Many normal POSIX headers and string macros are disabled, so portability shims are required. Kerberos/GSSAPI is unavailable. The generated package version is `4.0.0`, which should be checked against the build/package metadata used for Pico.

## Test Signals
Cross-compile for Pico W and run DNS, TCP connect, stat/read/write, signing, and timeout behavior over lwIP.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/picow/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/picow/lwipopts.h -->
# sources/user-network-fs/libsmb2/include/picow/lwipopts.h

## Purpose
`lwipopts.h` provides Pico W lwIP configuration overlays for libsmb2 examples.

## Important APIs, Types, and Functions
It includes `lwipopts_examples_common.h`, enables `LWIP_SO_RCVBUF`, and sets `LWIP_TIMEVAL_PRIVATE` to `0`. When `NO_SYS` is false, it defines TCP/IP and default thread stack sizes, mailbox sizes, and `LWIP_TCPIP_CORE_LOCKING_INPUT`.

## Control Flow
There is no runtime control flow in this header. lwIP compiles socket, mailbox, and thread behavior based on these macros.

## State and Persistence Behavior
Runtime lwIP state sizes are affected through receive buffers, mailboxes, and TCP/IP thread stack settings. No persistent storage is used.

## Dependencies and Integration Points
It depends on the common Pico lwIP options header and integrates with FreeRTOS or bare-metal Pico W network builds. `LWIP_TIMEVAL_PRIVATE 0` avoids conflicts with system timeval definitions expected by libsmb2.

## Risks and Edge Cases
Small 1024-byte thread stacks and mailbox sizes of 8 can limit heavy SMB transfers. Option behavior changes depending on `NO_SYS`, so builds must ensure intended socket/thread mode.

## Test Signals
Build with both polling and non-polling Pico networking modes, run sustained SMB reads/writes, and observe receive buffer/mailbox exhaustion or stack growth.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/picow/lwipopts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/picow/lwipopts_examples_common.h -->
# sources/user-network-fs/libsmb2/include/picow/lwipopts_examples_common.h

## Purpose
This header supplies common lwIP settings for Pico W examples.

## Important APIs, Types, and Functions
It defaults `NO_SYS` to `1` and `LWIP_SOCKET` to `1`, sets memory and pbuf sizes, enables ARP/Ethernet/ICMP/raw/DHCP/IPv4/TCP/UDP/DNS/keepalive, configures TCP window/send buffer/queue lengths, and turns most lwIP debug categories off. In non-`NDEBUG` builds it enables lwIP debug/statistics.

## Control Flow
No direct code flow. lwIP uses these macros to include protocol features, memory pools, checksums, DHCP behavior, and debug support.

## State and Persistence Behavior
It controls lwIP heap/pool sizing (`MEM_SIZE`, `MEMP_NUM_TCP_SEG`, `PBUF_POOL_SIZE`) and statistics state. No filesystem persistence.

## Dependencies and Integration Points
It integrates with Pico W network examples and `lwipopts.h`. The memory sizing directly affects libsmb2 socket throughput and ability to handle SMB packet bursts.

## Risks and Edge Cases
`MEM_SIZE` of 4000 and `PBUF_POOL_SIZE` of 24 are small relative to SMB workloads, especially large reads/writes or signing/encryption. `MEM_LIBC_MALLOC` depends on `PICO_CYW43_ARCH_POLL`, so allocator behavior differs by architecture mode.

## Test Signals
Run long directory listings and read/write workloads, track lwIP stats in debug builds, and check DHCP/DNS/connect reliability after repeated reconnects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/picow/lwipopts_examples_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/portable-endian.h -->
# sources/user-network-fs/libsmb2/include/portable-endian.h

## Purpose
`portable-endian.h` normalizes host-to/from big/little endian conversion macros across many operating systems, consoles, and embedded targets used by libsmb2.

## Important APIs, Types, and Functions
It defines or maps `htobe16`, `htole16`, `be16toh`, `le16toh`, and 32/64-bit variants. Platform branches cover PS2/Pico, Dreamcast, Linux/Cygwin/ESP/BSD/GNU, Apple, PS3/Wii/GameCube, Switch/3DS/NDS, Windows/Xbox, Amiga, AROS, and generic GCC/Clang. Some branches define `__BYTE_ORDER`, `__BIG_ENDIAN`, and related aliases.

## Control Flow
Preprocessor conditionals select exactly one platform branch at compile time. There is no runtime branch; conversions are macros wrapping system functions, builtin byte swaps, or identity operations depending on host endian.

## State and Persistence Behavior
No state is stored. The header determines binary wire-format correctness for all SMB2/DCERPC scalar encoding.

## Dependencies and Integration Points
It integrates with packers/unpackers that read/write SMB2's little-endian fields and with network byte-order helpers for some embedded targets. It includes platform headers such as `<endian.h>`, `<sys/endian.h>`, `<libkern/OSByteOrder.h>`, `<windows.h>`, `<xtl.h>`, or `<machine/endian.h>`.

## Risks and Edge Cases
The PS2/Pico branch maps 64-bit big-endian conversion as `htobe64(x) be64toh(x)` but does not visibly define `be64toh` in that branch, relying on included platform support. Generic GCC/Clang assumes little-endian identity for `htole*`; unusual big-endian GCC targets must hit an earlier branch. Macro redefinitions can conflict with system headers.

## Test Signals
Compile on each supported platform branch when possible and run encode/decode round trips for 16/32/64-bit values, including SMB headers and DCERPC NDR scalars.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/portable-endian.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/ps3/config.h -->
# sources/user-network-fs/libsmb2/include/ps3/config.h

## Purpose
This generated-style `config.h` snapshot configures libsmb2 for PS3 builds.

## Important APIs, Types, and Functions
It enables `HAVE_ERRNO_H`, `HAVE_FCNTL_H`, `HAVE_LINGER`, `HAVE_NETINET_IN_H`, `HAVE_STDINT_H`, `HAVE_STDIO_H`, `HAVE_STDLIB_H`, `HAVE_STRING_H`, `HAVE_SYS_TYPES_H`, `HAVE_TIME_H`, and `HAVE_UNISTD_H`. It disables GSSAPI/Kerberos, poll, most socket/stat/uio sys headers, sockaddr length/storage, and netdb.

## Control Flow
No runtime control flow. Compile-time branches use these feature flags.

## State and Persistence Behavior
No persisted state. The generated macros define platform capabilities for the resulting binary.

## Dependencies and Integration Points
It integrates with PS3 platform networking and `portable-endian.h`'s big-endian PS3 branch. Kerberos is unavailable.

## Risks and Edge Cases
Several socket/sys headers are disabled while networking is still required, so PS3-specific compatibility code must cover all needed types and calls. Big-endian conversion paths require explicit testing.

## Test Signals
Cross-compile for PS3, run basic connect/share/stat tests, and verify endian-correct SMB header and payload fields on the wire.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/ps3/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/slist.h -->
# sources/user-network-fs/libsmb2/include/slist.h

## Purpose
`slist.h` defines lightweight singly linked list macros used internally by libsmb2.

## Important APIs, Types, and Functions
`SMB2_LIST_ADD(list, item)` prepends an item. `SMB2_LIST_ADD_END(list, item)` appends by walking the list. `SMB2_LIST_REMOVE(list, item)` unlinks a matching item. `SMB2_LIST_LENGTH(list, length)` counts elements. Each macro assumes list elements have a `next` member.

## Control Flow
The append, remove, and length macros temporarily advance `*list` while walking and restore the original head from a local `void *head`. `SMB2_LIST_ADD` updates the item's `next` and then updates the head.

## State and Persistence Behavior
The macros mutate caller-owned in-memory list links only. They allocate and free nothing.

## Dependencies and Integration Points
It is a non-installed internal helper used by list-managing implementation code such as context, queue, or directory-entry tracking. It has no external library dependencies.

## Risks and Edge Cases
Macros evaluate arguments multiple times and are not type-safe. The `void *head` restoration relies on compatible pointer assignment. `SMB2_LIST_REMOVE` does not clear the removed item's `next`, which can surprise callers that reuse removed nodes.

## Test Signals
Unit-test prepend, append to empty/non-empty lists, remove head/middle/tail/missing items, length on empty and populated lists, and repeated remove/reinsert behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/slist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/smb2/libsmb2-dcerpc-lsa.h -->
# sources/user-network-fs/libsmb2/include/smb2/libsmb2-dcerpc-lsa.h

## Purpose
`libsmb2-dcerpc-lsa.h` defines DCERPC Local Security Authority structures and coders used by libsmb2 for policy handles and SID lookup operations.

## Important APIs, Types, and Functions
It declares LSA opnums `LSA_CLOSE`, `LSA_OPENPOLICY2`, and `LSA_LOOKUPSIDS2`, policy access-mask flags, `RPC_SID`, translated-name/domain-list structures, `LSAPR_OBJECT_ATTRIBUTES`, request/reply structs for close/open-policy/lookup-SIDs, and coder functions such as `lsa_OpenPolicy2_req_coder()`, `lsa_LookupSids2_rep_coder()`, and `lsa_RPC_SID_coder()`.

## Control Flow
Runtime code builds request structs, encodes them with the declared coder for a DCERPC call, decodes reply structs, checks embedded NT status fields, and eventually closes context handles with `LSA_CLOSE`.

## State and Persistence Behavior
The header represents transient RPC data: policy context handles, SID arrays, translated names, referenced domains, and mapped counts. Memory ownership is managed by DCERPC/libsmb2 allocation and freeing routines.

## Dependencies and Integration Points
It depends on `libsmb2-dcerpc.h` types such as `ndr_context_handle`, `dcerpc_context`, `dcerpc_pdu`, and `smb2_iovec`. It integrates with LSA pipes over IPC$ and SID/name translation helpers.

## Risks and Edge Cases
NDR pointer and array counts must match server responses exactly. `MaxEntries` is documented as ignored. SID subauthority arrays and referenced-domain indexes are variable-length and require careful decode/free handling.

## Test Signals
Test opening policy with different desired access masks, resolving valid and unknown SIDs, multi-domain responses, zero-entry buffers, partial mapping status, and close-handle cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/smb2/libsmb2-dcerpc-lsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/smb2/libsmb2-dcerpc-srvsvc.h -->
# sources/user-network-fs/libsmb2/include/smb2/libsmb2-dcerpc-srvsvc.h

## Purpose
`libsmb2-dcerpc-srvsvc.h` defines SRVSVC DCERPC share enumeration and share-info structures, plus high-level share enumeration helpers.

## Important APIs, Types, and Functions
It declares SRVSVC opnums `SRVSVC_NETRSHAREENUM` and `SRVSVC_NETRSHAREGETINFO`, share type flags, `enum SHARE_INFO_enum`, share info levels 0/1/2 and containers, request/reply structs for `NetrShareEnum` and `NetrShareGetInfo`, coder functions for each structure, and `smb2_share_enum_async()`/`smb2_share_enum_sync()`.

## Control Flow
The async helper requires an IPC$ connection, encodes a `NetrShareEnum` request at the chosen info level, calls SRVSVC over DCERPC, and reports a decoded `srvsvc_NetrShareEnum_rep` through the callback. The sync helper wraps the async flow and returns the reply pointer or NULL.

## State and Persistence Behavior
Share enumeration results are transient decoded arrays of UTF-16-backed share names, remarks, paths, and counters. Callers must free successful results using `smb2_free_data()`.

## Dependencies and Integration Points
It includes `libsmb2-dcerpc.h` and integrates with IPC$ tree connections and DCERPC transport setup. `libsmb2.h` includes this header for compatibility.

## Risks and Edge Cases
The API only works on IPC$ and requires suitable server permissions. Level-specific unions must be decoded according to `Level`; misuse can read the wrong union member. Large share lists may require resume handling.

## Test Signals
Run level 0, 1, and 2 enumeration against servers with normal, hidden, IPC, printer, and administrative shares. Test permission-denied, empty list, resume handle, and proper `smb2_free_data()` cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/smb2/libsmb2-dcerpc-srvsvc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/smb2/libsmb2-dcerpc.h -->
# sources/user-network-fs/libsmb2/include/smb2/libsmb2-dcerpc.h

## Purpose
`libsmb2-dcerpc.h` defines the generic DCERPC/NDR API layered on top of libsmb2.

## Important APIs, Types, and Functions
It defines data-representation constants, `dcerpc_coder`, `enum dcerpc_encoding`, pointer kinds, UUID/syntax/context-handle types, `struct dcerpc_utf16`, global interface IDs for LSA and SRVSVC, callback type `dcerpc_cb`, context lifecycle functions, async connect/open/call functions, PDU allocation/free helpers, request/size/switch metadata accessors, and NDR/DCERPC scalar/string/array/union/struct coder helpers.

## Control Flow
A caller creates a DCERPC context from an SMB2 context, connects to a named pipe with an interface syntax, opens/binds, then issues `dcerpc_call_async()` with request and reply coders. Coders advance an iovec offset while encoding or decoding data according to NDR rules and pointer metadata.

## State and Persistence Behavior
`struct dcerpc_context` and `struct dcerpc_pdu` are opaque. They retain transport binding, encoding mode, request metadata, and allocated decoded data until freed. No on-disk persistence occurs.

## Dependencies and Integration Points
It integrates with SMB named-pipe I/O and higher-level LSA/SRVSVC headers. It uses `struct smb2_iovec` and `struct smb2_context` from the libsmb2 API surface.

## Risks and Edge Cases
NDR alignment, endianness, conformant/varying array sizes, and pointer referent handling are easy to break. Async callbacks must respect context lifetime and free decoded data with the correct context.

## Test Signals
Test bind/open/call flows for LSA and SRVSVC, little and big endian NDR if supported, null/unique/full pointer handling, UTF-16 strings, arrays, unions, decode failures, and callback lifetime.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/smb2/libsmb2-dcerpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/smb2/libsmb2-raw.h -->
# sources/user-network-fs/libsmb2/include/smb2/libsmb2-raw.h

## Purpose
`libsmb2-raw.h` exposes the low-level asynchronous SMB2 command interface. It lets applications build raw SMB2 PDUs directly and also provides reply helpers for server/proxy use.

## Important APIs, Types, and Functions
The header declares `compound_file_id`, `smb2_free_data()`, and one or more async functions for negotiate, session setup, tree connect/disconnect, create, close, read, write, query directory, change notify, query info, set info, ioctl, echo, lock, logoff, flush, oplock/lease break, and error replies. Many commands have both request and reply creation helpers, such as `smb2_cmd_create_async()` and `smb2_cmd_create_reply_async()`.

## Control Flow
Callers allocate command PDUs with raw async functions, optionally compound them through the public PDU helpers, queue them, and drive socket progress with `smb2_service()`. Completion arrives through `smb2_command_cb`, with command-specific decoded payloads or NT status errors.

## State and Persistence Behavior
Raw calls create `struct smb2_pdu` objects and decoded output buffers. PDU lifetime is explicit: callers must free PDUs as documented, and query/ioctl output buffers are freed through `smb2_free_data()`. No disk persistence.

## Dependencies and Integration Points
It depends on protocol structs from `smb2.h` and callbacks/context from `libsmb2.h`. High-level POSIX-like APIs in `libsmb2.c` build on this layer, while server/proxy code uses reply helpers.

## Risks and Edge Cases
The raw layer exposes wire-level sizes, ownership, and callback semantics; callers can create invalid request combinations. Some comments are copy-pasted with inaccurate command names, so behavior should be verified against signatures and implementation.

## Test Signals
Build raw compound stat/open/read/write flows, cancel PDUs before callbacks, test server reply helpers, validate output-buffer freeing, and fuzz malformed request structs where internal validation should reject them.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/smb2/libsmb2-raw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/smb2/libsmb2.h -->
# sources/user-network-fs/libsmb2/include/smb2/libsmb2.h

## Purpose
`libsmb2.h` is the main public API header for libsmb2. It exposes context lifecycle, event-loop integration, authentication/session configuration, POSIX-like file/directory operations, share enumeration compatibility, UTF conversion helpers, compound PDU helpers, and server-side request handler interfaces.

## Important APIs, Types, and Functions
Important types include `struct smb2_context`, `struct smb2_iovec`, `smb2_command_cb`, `smb2_error_cb`, `struct smb2_stat_64`, `struct smb2_statvfs`, `struct smb2dirent`, `struct smb2_url`, opaque `struct smb2fh`/`struct smb2dir`, `enum smb2_negotiate_version`, `enum smb2_sec`, `struct smb2_server_request_handlers`, and `struct smb2_server`. Functions cover `smb2_init_context()`, close/destroy/active checks, fd/event callbacks, `smb2_service()`/`smb2_service_fd()`, timeout/passthrough/version/security/sign/seal/auth/user/password/domain/workstation setters, URL parsing, connect/disconnect, tree/session/PDU helpers, opendir/readdir/open/close/fsync/read/write/lseek/unlink/rmdir/mkdir/stat/statvfs/rename/truncate/readlink/echo/notify-change sync and async variants, UTF-8/UTF-16 conversion, and server bind/accept/serve.

## Control Flow
Client flow is: create a context, configure security/auth/user options, parse or provide server/share/path, connect asynchronously or synchronously, issue high-level or raw operations, drive async progress with fd readiness, then disconnect and destroy. Sync APIs wrap async operations with internal completion state. Server flow binds/listens, accepts connections into contexts, and dispatches decoded SMB2 commands to function pointers in `smb2_server_request_handlers`.

## State and Persistence Behavior
The context holds connection/session/tree/auth/crypto/queue state internally. File handles and directory handles are owned by the context and become invalid when the context is destroyed. Remote operations persist only when they modify the SMB share, such as write, unlink, mkdir, rename, truncate, and set-info-backed calls.

## Dependencies and Integration Points
It integrates with standard event loops via fd/event polling or callback registration, with Kerberos/NTLM authentication through configuration, with raw SMB2 structs from `smb2.h`, and with SRVSVC DCERPC share enumeration via the included compatibility header.

## Risks and Edge Cases
Async lifetime rules are central: callbacks can destroy contexts, PDUs can be cancelled by freeing them, and returned command data has command-specific ownership. `smb2_lseek(SEEK_END)` uses the original open EOF and does not refresh size. Some APIs require IPC$ or directory handles. Signing/sealing configuration must match server policy.

## Test Signals
Cover sync and async variants for connection, directory, file I/O, stat/statvfs, truncate, notify, and error cases. Test event-loop fd changes, Happy Eyeballs `smb2_get_fds()`, timeout servicing, context destruction from callbacks, server handler dispatch, and signing/encryption negotiation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/smb2/libsmb2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/smb2/smb2-errors.h -->
# sources/user-network-fs/libsmb2/include/smb2/smb2-errors.h

## Purpose
`smb2-errors.h` defines NTSTATUS severity masks and a large set of SMB2/Windows status constants used by libsmb2.

## Important APIs, Types, and Functions
The header defines severity/customer/facility/code masks and constants such as `SMB2_STATUS_SUCCESS`, `SMB2_STATUS_PENDING`, `SMB2_STATUS_NO_MORE_FILES`, `SMB2_STATUS_ACCESS_DENIED`, `SMB2_STATUS_OBJECT_NAME_NOT_FOUND`, `SMB2_STATUS_LOGON_FAILURE`, `SMB2_STATUS_IO_TIMEOUT`, `SMB2_STATUS_NOT_SUPPORTED`, `SMB2_STATUS_CANCELLED`, `SMB2_STATUS_BUFFER_OVERFLOW`, and many others.

## Control Flow
There is no executable control flow. Runtime code compares SMB response status values against these macros and maps them through `nterror_to_str()` or `nterror_to_errno()` declared in `libsmb2.h`.

## State and Persistence Behavior
No state or persistence. The constants are compile-time protocol definitions.

## Dependencies and Integration Points
`smb2.h` includes this header, making the constants available to public protocol structs and callers. Error handling in raw and high-level APIs depends on these values.

## Risks and Edge Cases
Coverage is broad but static; missing newer NTSTATUS values may map poorly. The custom `SMB2_STATUS_SHUTDOWN` value is `0xffffffff`, outside normal NTSTATUS success/error classes. Macro-only definitions provide no type safety.

## Test Signals
Verify NTSTATUS-to-errno/string mappings for common authentication, path, sharing, timeout, EOF, and no-more-files statuses. Test unknown status handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/smb2/smb2-errors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/smb2/smb2-ioctl.h -->
# sources/user-network-fs/libsmb2/include/smb2/smb2-ioctl.h

## Purpose
`smb2-ioctl.h` defines additional Windows/SMB filesystem control codes for use with SMB2 IOCTL requests.

## Important APIs, Types, and Functions
It defines `FSCTL_*` constants for object IDs, reparse points, duplicate extents, filesystem statistics, trim, compression, NTFS/ReFS volume data, retrieval pointers, sparse/zero data, pipe operations, allocated ranges, offload read/write, integrity, encryption, USN, and snapshot enumeration. It aliases `FSCTL_GET_SHADOW_COPY_DATA` to `FSCTL_SRV_ENUMERATE_SNAPSHOTS`.

## Control Flow
No runtime code exists. Callers place these constants in `struct smb2_ioctl_request.ctl_code` and submit through raw IOCTL APIs.

## State and Persistence Behavior
The header has no state. Specific IOCTLs can query or mutate remote filesystem metadata when used by callers.

## Dependencies and Integration Points
It complements `smb2.h`, which defines core SMB2 IOCTL structs and a smaller set of `SMB2_FSCTL_*` constants. It is not listed in the autotools install header list in `include/Makefile.am`.

## Risks and Edge Cases
The license comment uses curly quotes and the author email appears misspelled. Constant names omit the `SMB2_` prefix used in `smb2.h`, so collision with platform headers is possible. Install/build metadata may not expose this header consistently.

## Test Signals
Compile downstream code including this header alone and with Windows headers. Exercise harmless query IOCTLs and validate server status for unsupported control codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/smb2/smb2-ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/smb2/smb2.h -->
# sources/user-network-fs/libsmb2/include/smb2/smb2.h

## Purpose
`smb2.h` defines the public SMB2/SMB3 wire protocol constants and C structures used by the raw and high-level libsmb2 APIs.

## Important APIs, Types, and Functions
The header includes command ids, SMB2 header flags, negotiate/session/tree/create/read/write/query/set/ioctl/change-notify/oplock/lease/lock/logoff/echo constants, file access masks, attributes, share flags, create disposition/options, file and filesystem information classes, security descriptor/SID/ACE/ACL structures, reparse/symlink structures, IOCTL structs, notify structs, and request/reply structs for all major SMB2 commands. It declares helpers such as `smb2_get_file_id()`, `smb2_fh_from_file_id()`, `smb2_decode_fileidfulldirectoryinformation()`, and `smb2_decode_filenotifychangeinformation()`.

## Control Flow
There is no executable flow in the header. Runtime packers fill request structs, encode them to SMB2 wire format, receive replies, and decode bytes into reply/info structures according to the constants and fixed-size definitions here.

## State and Persistence Behavior
Most structures represent transient wire messages. Some fields refer to caller-owned or decoder-allocated buffers such as names, security descriptors, reparse data, read/write buffers, create contexts, query outputs, and notify linked lists. Remote persistence depends on commands using these structs, such as create, write, set-info, lock, and ioctl.

## Dependencies and Integration Points
It includes `smb2-errors.h` and conditionally includes `<stdint.h>`/`<time.h>` based on config macros. `libsmb2.h`, `libsmb2-raw.h`, and implementation packers/unpackers depend on this file for ABI and wire layout.

## Risks and Edge Cases
Because this is a wire-layout contract, size constants and structure fields must match SMB2 specs exactly. Duplicate macro names appear for some file information classes and oplock constants. Variable-length buffers require careful ownership and bounds checks in implementation code.

## Test Signals
Round-trip encode/decode every command struct, validate fixed-size constants against protocol examples, test security descriptor and directory info parsing, and interoperate with Windows/Samba servers for negotiate, create, read/write, query-info, ioctl, notify, oplock/lease break, and lock flows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/smb2/smb2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/xbox 360/config.h -->
# sources/user-network-fs/libsmb2/include/xbox 360/config.h

## Purpose
This generated-style `config.h` snapshot configures libsmb2 for Xbox 360 builds.

## Important APIs, Types, and Functions
It enables `HAVE_ERRNO_H`, `HAVE_FCNTL_H`, `HAVE_LINGER`, `HAVE_STDINT_H`, `HAVE_STDIO_H`, `HAVE_STDLIB_H`, `HAVE_STRING_H`, `HAVE_SYS_STAT_H`, `HAVE_SYS_TYPES_H`, and `HAVE_TIME_H`. It disables POSIX socket, poll, uio, unistd, netdb, GSSAPI/Kerberos, sockaddr length, and sockaddr storage macros.

## Control Flow
No runtime control flow exists. The macros steer compilation into Xbox-specific compatibility paths.

## State and Persistence Behavior
No state is persisted. Compile-time feature state controls the resulting binary.

## Dependencies and Integration Points
It integrates with Xbox headers and `portable-endian.h`'s Windows/Xbox branch, plus `asprintf.h`'s `_XBOX` handling.

## Risks and Edge Cases
The directory path contains a space, which can break scripts that do not quote paths. Disabled socket/storage macros require Xbox-specific socket typedefs and APIs to be used correctly.

## Test Signals
Cross-compile with path quoting, run basic URL parse/connect/stat/read/write tests, and verify `_XBOX` formatting and endian branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/xbox 360/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/xbox/config.h -->
# sources/user-network-fs/libsmb2/include/xbox/config.h

## Purpose
This generated-style `config.h` snapshot configures libsmb2 for original Xbox builds.

## Important APIs, Types, and Functions
It enables stdio/stdlib/string/sys types/stat/time, `HAVE_ERRNO_H`, `HAVE_FCNTL_H`, `HAVE_LINGER`, and `HAVE_SOCKADDR_STORAGE`, but disables `HAVE_STDINT_H`, POSIX socket/poll/uio/unistd/netdb, GSSAPI, and Kerberos.

## Control Flow
No runtime logic exists. Macros control compile-time portability branches for Xbox.

## State and Persistence Behavior
No runtime persistence. Feature state is fixed at compile time.

## Dependencies and Integration Points
It integrates with Xbox socket headers from `libsmb2.h`, `_XBOX` support in `portable-endian.h`, and `asprintf.h`.

## Risks and Edge Cases
`HAVE_STDINT_H` is disabled while much of the public API uses fixed-width integer types; compatibility headers must provide them. GSSAPI/Kerberos is unavailable. Differences from the Xbox 360 config need target-specific testing.

## Test Signals
Compile public headers in a downstream Xbox sample, run endian/formatting smoke tests, and exercise basic SMB connect and file metadata operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/include/xbox/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/CMakeLists.txt -->
# sources/user-network-fs/libsmb2/lib/CMakeLists.txt

## Purpose
`lib/CMakeLists.txt` assembles the libsmb2 library or platform-specific targets for CMake and ESP-IDF builds.

## Important APIs, Types, and Functions
It conditionally sets `KRB5_SOURCE`, defines source lists for `ESP_PLATFORM`, PS2 IOP/IRX, and normal builds, calls `register_component()` for ESP, creates `smb2_rpc`, `smb2man.irx`, `libsmb2` static Pico library, or normal `smb2` library targets, configures include directories, version/SOVERSION properties, Dreamcast VFS sources/install, `_U_` definitions, WindowsStore `_MSC_UWP`, and install rules.

## Control Flow
CMake evaluates platform variables, selects a source list, creates exactly the relevant target branch, adds definitions, and emits install rules unless excluded by platform conditions.

## State and Persistence Behavior
The file creates build-system state: targets, source membership, include paths, link libraries, install destinations, and post-build commands. No runtime persistence.

## Dependencies and Integration Points
It integrates with top-level CMake variables such as `GSSAPI_FOUND`, `LIBKRB5_FOUND`, `core_DEPENDS`, `CORE_LIBRARIES`, `PROJECT_VERSION`, `SOVERSION`, `INSTALL_INC_DIR`, `PICO_BOARD`, `ESP_PLATFORM`, `EE`, `IOP`, and `BUILD_IRX`.

## Risks and Edge Cases
The condition `if(NOT PICO_BOARD OR NOT ESP_PLATFORM)` is true for most combinations and may not express the intended "not Pico and not ESP" install gating. Header install lists omit `smb2-ioctl.h`. Source lists are duplicated across branches, so adding/removing a `.c` file requires multiple updates.

## Test Signals
Configure/build normal, ESP, Pico, PS2 IOP/IRX, Dreamcast, MSVC, and Kerberos-enabled builds. Inspect target source lists, install manifests, exported library names, and `_U_` definitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/Makefile.am -->
# sources/user-network-fs/libsmb2/lib/Makefile.am

## Purpose
`lib/Makefile.am` defines the autotools/libtool build for the `libsmb2.la` library.

## Important APIs, Types, and Functions
It sets `AM_CFLAGS`, `lib_LTLIBRARIES`, include CPPFLAGS, the full `libsmb2_la_SOURCES` list, libtool version components `SOCURRENT=6`, `SOREVISION=1`, `SOAGE=0`, linker flags using `-version-info`, `-no-undefined`, exported symbols from `libsmb2.syms`, optional Kerberos libraries, and distribution of `libsmb2.syms`.

## Control Flow
Automake expands variables into compile/link rules. Libtool links the listed sources into `libsmb2.la` and applies symbol export and versioning rules.

## State and Persistence Behavior
The file affects build artifacts, shared-library ABI version metadata, and install outputs. It has no runtime state.

## Dependencies and Integration Points
It integrates with autotools variables from `configure.ac`, public/private headers under `include/`, crypto/auth/protocol implementation files, and optional Kerberos link flags.

## Risks and Edge Cases
Source list drift against CMake is a maintenance risk. The indentation for `smb2-cmd-oplock-break.c` differs but is syntactically harmless. ABI version numbers must be advanced deliberately when exported symbols change.

## Test Signals
Run `autoreconf`, `./configure` with and without Kerberos, `make`, `make check` if available, `make distcheck`, and inspect exported symbols and libtool soname.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/aes.c -->
# sources/user-network-fs/libsmb2/lib/aes.c

## Purpose
`aes.c` provides the common `AES128_ECB_encrypt()` wrapper used by libsmb2 crypto code.

## Important APIs, Types, and Functions
It includes `aes.h` and then selects `aes_apple.h` on Apple platforms or `aes_reference.h` otherwise. The only function, `AES128_ECB_encrypt(uint8_t *input, const uint8_t *key, uint8_t *output)`, delegates to `AES128_ECB_encrypt_apple()` or `AES128_ECB_encrypt_reference()`.

## Control Flow
At compile time, `#ifdef __APPLE__` selects the backend include and delegate call. Runtime control flow is a single direct call to the selected backend.

## State and Persistence Behavior
No state is retained. The function reads a 16-byte block and key according to backend expectations and writes the encrypted block to `output`.

## Dependencies and Integration Points
It integrates with SMB signing/sealing or related crypto helpers that need AES-128 ECB. It depends on backend headers/sources being present in the build lists; CMake includes both Apple and reference sources in normal builds but ESP/PS2 branches omit `aes_apple.c`.

## Risks and Edge Cases
There is no argument validation for NULL pointers or overlapping buffers. ECB is only a primitive here; higher-level code must use it safely within correct modes. Apple backend availability must match build branch.

## Test Signals
Run AES-128 ECB known-answer tests on Apple and non-Apple builds, test repeated calls, and verify higher-level SMB3 signing/sealing tests that depend on AES.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/aes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/aes.h -->
# sources/user-network-fs/libsmb2/lib/aes.h

## Purpose
`aes.h` declares the AES wrapper API used internally by libsmb2.

## Important APIs, Types, and Functions
It conditionally includes `config.h` when `HAVE_CONFIG_H` is defined, includes `compat.h`, and declares `void AES128_ECB_encrypt(uint8_t *input, const uint8_t *key, uint8_t *output);`.

## Control Flow
There is no runtime control flow. Include guards prevent duplicate declarations and configuration headers prepare fixed-width integer definitions before the prototype.

## State and Persistence Behavior
No state or persistence. The function declared here writes to caller-provided output.

## Dependencies and Integration Points
It depends on `compat.h` for portable integer types and is included by `aes.c` and crypto callers. It is listed in autotools sources and normal CMake source lists.

## Risks and Edge Cases
The API exposes raw pointers without size annotations, so all callers must provide 16-byte input, key, and output buffers. It is internal but not namespace-hidden beyond the function name.

## Test Signals
Compile all crypto users with `HAVE_CONFIG_H` on/off and run AES known-answer tests through the public wrapper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/aes.h -->
