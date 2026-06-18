# Group Research: group_1183_netbsd_src_sources_os_bsd_netbsd_src_lib_libarch_alpha_alpha_pci_me_9b197a09c082

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/alpha/alpha_pci_mem.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/alpha/alpha_pci_mem.c

This file implements Alpha userland support for mapping PCI/EISA/ISA memory windows through `/dev/mem`.

Key behavior:
- Lazily discovers PCI memory bus windows with `alpha_bus_getwindows(ALPHA_BUS_TYPE_PCI_MEM, ...)`.
- Rejects linear mappings unless they are also prefetchable.
- Finds a bus window covering the requested address range and chooses dense space for prefetchable mappings, sparse space otherwise.
- Opens `_PATH_MEM`, computes the shifted system address, maps it with `mmap(PROT_READ|PROT_WRITE, MAP_FILE|MAP_SHARED)`, and closes the fd.
- Copies the selected `alpha_bus_space_translation` to the caller and unmaps by shifting the original size with `abst_addr_shift`.

Filesystem relevance: indirect only. It uses the `/dev/mem` character device but is architecture/device-memory support, not filesystem logic.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/alpha/alpha_pci_mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/arm/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/arm/Makefile.inc

This make fragment selects ARM libarch sources and manual pages.

Key behavior:
- Includes `<bsd.own.mk>` and defaults `LIBC_MACHINE_CPU` to `${MACHINE_CPU}`.
- Adds `arm_sync_icache.c` and `arm_drain_writebuf.c` when building for ARM.
- Installs man pages for the ARM cache/write-buffer helpers.

Filesystem relevance: none. It is architecture-specific userland library build glue.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/arm/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/arm/arm_drain_writebuf.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/arm/arm_drain_writebuf.c

This file provides the `arm_drain_writebuf()` wrapper.

Key behavior:
- Includes `machine/sysarch.h`.
- Calls `sysarch(ARM_DRAIN_WRITEBUF, NULL)` and returns the kernel result.

Filesystem relevance: none. It is CPU/cache ordering support.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/arm/arm_drain_writebuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/arm/arm_sync_icache.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/arm/arm_sync_icache.c

This file provides the `arm_sync_icache()` wrapper.

Key behavior:
- Accepts an address and length.
- Fills `struct arm_sync_icache_args`.
- Calls `sysarch(ARM_SYNC_ICACHE, &p)`.

Filesystem relevance: none. It is architecture-specific instruction-cache maintenance.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/arm/arm_sync_icache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/i386/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/i386/Makefile.inc

This make fragment selects i386 libarch wrappers.

Key behavior:
- For native i386 or i386 multilib builds, adds LDT, I/O privilege, I/O permission, and MTRR wrappers.
- Adds manual pages and aliases for LDT and MTRR APIs.

Filesystem relevance: none. It is build configuration for architecture sysarch wrappers.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/i386/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_get_ioperm.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_get_ioperm.c

This file implements `i386_get_ioperm()`.

Key behavior:
- Stores the caller's I/O bitmap pointer in `struct i386_get_ioperm_args`.
- Calls `sysarch(I386_GET_IOPERM, &p)`.

Filesystem relevance: none. It exposes architecture I/O-port permission state.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_get_ioperm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_get_ldt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_get_ldt.c

This file implements `i386_get_ldt()`.

Key behavior:
- Accepts a start selector, descriptor buffer, and descriptor count.
- Passes them through `struct i386_get_ldt_args`.
- Calls `sysarch(I386_GET_LDT, &p)`.

Filesystem relevance: none. It is i386 descriptor-table access support.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_get_ldt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_iopl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_iopl.c

This file implements `i386_iopl()`.

Key behavior:
- Stores the requested I/O privilege level in `struct i386_iopl_args`.
- Calls `sysarch(I386_IOPL, &p)`.

Filesystem relevance: none. It controls CPU privilege state for port I/O.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_iopl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_mtrr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_mtrr.c

This file implements i386 MTRR wrappers.

Key behavior:
- `i386_get_mtrr()` passes an MTRR array and count pointer to `sysarch(I386_GET_MTRR, ...)`.
- `i386_set_mtrr()` passes the same style of arguments to `sysarch(I386_SET_MTRR, ...)`.

Filesystem relevance: none. It manages CPU memory type range registers.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_mtrr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_set_ioperm.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_set_ioperm.c

This file implements `i386_set_ioperm()`.

Key behavior:
- Stores the caller's I/O permission bitmap pointer in `struct i386_set_ioperm_args`.
- Calls `sysarch(I386_SET_IOPERM, &p)`.

Filesystem relevance: none. It changes architecture I/O-port permission state.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_set_ioperm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_set_ldt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_set_ldt.c

This file implements `i386_set_ldt()`.

Key behavior:
- Accepts a start selector, descriptor buffer, and descriptor count.
- Calls `sysarch(I386_SET_LDT, &p)` with those fields.

Filesystem relevance: none. It is i386 local descriptor table support.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/i386/i386_set_ldt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/m68k/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/m68k/Makefile.inc

This make fragment selects m68k libarch support.

Key behavior:
- For `MACHINE_CPU == "m68k"`, disables lint and builds `m68k_sync_icache.S`.
- Adds the `m68k_sync_icache.2` man page.

Filesystem relevance: none. It is architecture helper build glue.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/m68k/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/m68k/m68k_sync_icache.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/m68k/m68k_sync_icache.S

This assembly file implements `m68k_sync_icache`.

Key behavior:
- Loads length and address from the stack into `%d1` and `%a1`.
- Places operation code `0x80000004` in `%d0`.
- Enters kernel service via `trap #12`, then returns.

Filesystem relevance: none. It is m68k instruction-cache synchronization.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/m68k/m68k_sync_icache.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/powerpc/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/powerpc/Makefile.inc

This make fragment conditionally adds a PowerPC sublibrary.

Key behavior:
- Includes `<bsd.own.mk>`.
- For `evbppc` with `MACHINE_ARCH == powerpc`, descends into `powerpc/espresso`.

Filesystem relevance: none. It is platform-specific build dispatch.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/powerpc/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/powerpc/espresso/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/powerpc/espresso/Makefile

This makefile builds the `powerpc_espresso` libarch shared library.

Key behavior:
- Disables normal link library/profile/lint handling and avoids libc linkage with `DPLIBC=` and `LDLIBC=-nodefaultlibs`.
- Uses `AFLAGS+= -mcpu=750 -DPPC_IBMESPRESSO`.
- Pulls atomic assembly sources from `common/lib/libc/arch/powerpc/atomic`.

Filesystem relevance: none. It builds PowerPC Espresso atomic support.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/powerpc/espresso/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/sparc/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/sparc/Makefile.inc

This make fragment selects the SPARC v8 subdirectory.

Key behavior:
- For `MACHINE_ARCH == sparc`, sets `SUBDIR=sparc/v8`.

Filesystem relevance: none. It is architecture build routing.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/sparc/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/sparc/v8/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/sparc/v8/Makefile

This makefile builds the `sparc_v8` shared library.

Key behavior:
- Builds `sparc_v8.S` without linking against libc.
- Uses assembler flag `-Wa,-Av8`.
- Installs via shared-library directory rules.

Filesystem relevance: none. It packages SPARC v8 arithmetic helper routines.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/sparc/v8/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/sparc/v8/sparc_v8.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/sparc/v8/sparc_v8.S

This assembly file provides SPARC v8 integer arithmetic entry points.

Key behavior:
- Defines `.umul`, `.mul`, `.udiv`, `.div`, `.urem`, and `.rem`.
- Uses SPARC v8 multiply/divide instructions and `%y` setup/readback.
- Returns quotient/remainder or high product words according to compiler helper ABI expectations.

Filesystem relevance: none. It is CPU arithmetic runtime support.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/sparc/v8/sparc_v8.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/x86_64/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/x86_64/Makefile.inc

This make fragment selects x86_64 libarch wrappers.

Key behavior:
- For native x86_64 non-i386 multilib builds, adds `x86_64_mtrr.c` and `x86_64_iopl.c`.
- Adds man pages and MTRR manual aliases.

Filesystem relevance: none. It is architecture wrapper build glue.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/x86_64/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/x86_64/x86_64_iopl.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/x86_64/x86_64_iopl.c

This file implements `x86_64_iopl()`.

Key behavior:
- Stores the requested privilege level in `struct x86_64_iopl_args`.
- Calls `sysarch(X86_64_IOPL, &p)`.

Filesystem relevance: none. It exposes x86_64 I/O privilege control.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/x86_64/x86_64_iopl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/x86_64/x86_64_mtrr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libarch/x86_64/x86_64_mtrr.c

This file implements x86_64 MTRR wrappers.

Key behavior:
- `x86_64_get_mtrr()` calls `sysarch(X86_64_GET_MTRR, ...)`.
- `x86_64_set_mtrr()` calls `sysarch(X86_64_SET_MTRR, ...)`.
- Both pass an MTRR pointer and count pointer.

Filesystem relevance: none. It manages CPU memory type range registers.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libarch/x86_64/x86_64_mtrr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/Makefile

This makefile builds NetBSD's Bluetooth userland library.

Key behavior:
- Builds `libbluetooth` from Bluetooth address/protocol helpers, HCI device helpers, and SDP data/session/service files.
- Optionally includes `sdp_compat.c` unless `SDP_COMPAT=no`.
- Installs `bluetooth.h` and `sdp.h`.
- Defines extensive manual page links for Bluetooth host/protocol lookup, device APIs, and SDP get/put/set helpers.

Filesystem relevance: minimal. It builds network protocol library code, not filesystem code.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/bluetooth.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/bluetooth.c

This file implements Bluetooth host/protocol database lookups and Bluetooth address parsing/formatting.

Key behavior:
- Reads `/etc/bluetooth/hosts` for `bt_gethostent()`, `bt_gethostbyname()`, and `bt_gethostbyaddr()`.
- Reads `/etc/bluetooth/protocols` for `bt_getprotoent()`, `bt_getprotobyname()`, and `bt_getprotobynumber()`.
- Maintains static parser state and optional stay-open behavior similar to libc network database APIs.
- Converts Bluetooth addresses between binary `bdaddr_t` and colon-separated hexadecimal text with `bt_ntoa()` and `bt_aton()`.

Filesystem relevance: limited to reading Bluetooth configuration text files under `/etc/bluetooth`.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/bluetooth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/bluetooth.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/bluetooth.h

This public header declares libbluetooth APIs and data structures.

Key behavior:
- Includes NetBSD Bluetooth, HCI, and L2CAP protocol headers.
- Declares host/protocol lookup APIs, address conversion APIs, HCI device access APIs, filter helpers, inquiry APIs, and device enumeration callbacks.
- Defines `bt_devinfo`, `bt_devreq`, `bt_devfilter`, and `bt_devinquiry`.
- Defines bthcid PIN request/response packet layouts and `/var/run/bthcid`.
- Optionally provides BlueZ compatibility macros.

Filesystem relevance: only path constants for Bluetooth daemon sockets/config consumers; no filesystem implementation.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/bluetooth.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/bt_dev.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/bt_dev.c

This file implements Bluetooth HCI device access helpers over NetBSD Bluetooth sockets and ioctls.

Key behavior:
- Resolves device names and addresses with `SIOCGBTINFO` and `SIOCGBTINFOA`.
- Opens bound raw HCI sockets with optional direction and timestamp options.
- Sends HCI commands with `writev()` and receives complete HCI packets with optional `kqueue()` timeout handling.
- Implements `bt_devreq()` by temporarily installing packet/event filters, sending a command, and waiting for command status/completion or a requested event.
- Provides packet/event filter get/set/test wrappers around HCI socket options.
- Performs inquiries, normalizing limits/timeouts, collecting classic/RSSI/extended inquiry results, and deduplicating by Bluetooth address.
- Reports device info and enumerates HCI devices via `SIOCNBTINFO`.

Filesystem relevance: none. It is socket/ioctl device-control code.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/bt_dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp-int.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp-int.h

This private header defines internal SDP session state and helper prototypes.

Key behavior:
- Defines `struct sdp_session` with transaction ID, incoming MTU, input/response buffers, continuation state, and socket fd.
- Declares internal open/close, PDU send/receive, SDP errno translation, and data-print helpers.

Filesystem relevance: none. It supports Bluetooth SDP sessions.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp-int.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp.h

This public header defines Bluetooth SDP constants, PDU formats, APIs, and compatibility types.

Key behavior:
- Defines SDP data element type/size tags, protocol UUIDs, service class IDs, and universal/profile attribute IDs.
- Defines `sdp_pdu_t`, standard PDU IDs, SDP error codes, and local `sdpd(8)` control PDU IDs.
- Declares modern service discovery, record management, data get/put/set, matching, validation, and printing APIs.
- Under `SDP_COMPAT`, declares legacy APIs, endian get/put macros, 128-bit compatibility structs, and profile-specific structures.

Filesystem relevance: includes the local SDP daemon socket path `/var/run/sdp`; otherwise protocol definitions only.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_compat.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_compat.c

This file implements the deprecated source-level SDP compatibility API on top of the newer libbluetooth SDP internals.

Key behavior:
- Wraps `sdp_session_t` in `struct sdp_compat` with stored error and scratch buffer.
- Provides legacy `sdp_open`, `sdp_open_local`, `sdp_close`, and `sdp_error`.
- Converts legacy `sdp_search()` arguments into ServiceSearchAttribute patterns/lists, then parses returned attribute/value sequences into caller-provided `sdp_attr_t` entries.
- Implements legacy register/change/unregister requests using old private PDU IDs and validates success via Error Response code 0.
- Provides UUID/attribute description lookup tables and `sdp_print()` forwarding to `_sdp_data_print()`.

Filesystem relevance: none beyond opening local SDP sessions through lower layers.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_data.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_data.c

This file implements SDP data element inspection, validation, and pretty-printing.

Key behavior:
- `sdp_data_type()` returns the first element type byte.
- `sdp_data_size()` computes the complete byte length of one data element, including extended length fields.
- Recursively validates strings, URLs, sequences, and alternatives without allowing length overruns.
- Pretty-prints scalar values, UUIDs, strings/URLs with `vis()`, and nested sequences/alternatives with indentation.
- Reports malformed print input as `SDP data error`.

Filesystem relevance: none. It parses and displays in-memory Bluetooth SDP data.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_get.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_get.c

This file implements typed readers for SDP data streams.

Key behavior:
- Readers validate type and bounds before advancing `sdp_data_t.next`.
- Extracts raw elements, attribute/value pairs, UUIDs, booleans, unsigned/signed integers, sequences, alternatives, strings, and URLs.
- Converts 16-bit and 32-bit Bluetooth UUID aliases into the Bluetooth base UUID.
- Rejects 128-bit integers that cannot fit in `uintmax_t` or `intmax_t`.

Filesystem relevance: none. It is in-memory protocol parsing.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_get.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_match.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_match.c

This file implements SDP matching helpers.

Key behavior:
- `sdp_match_uuid16()` builds a Bluetooth-base UUID with the supplied 16-bit value.
- Attempts to read a UUID from the data stream and advances only if it matches.

Filesystem relevance: none. It is protocol data matching.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_match.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_put.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_put.c

This file implements typed writers for SDP data streams.

Key behavior:
- Copies raw elements and writes attribute/value pairs with validation.
- Encodes UUIDs as 16-bit, 32-bit, or 128-bit depending on Bluetooth base UUID compatibility.
- Encodes booleans, signed/unsigned integers using the smallest suitable width, strings, URLs, sequences, and alternatives.
- Selects 8/16/32-bit extended length headers and refuses writes that exceed the destination buffer.

Filesystem relevance: none. It is in-memory SDP encoding.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_put.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_record.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_record.c

This file implements local `sdpd(8)` record-management transactions.

Key behavior:
- `sdp_record_insert()` sends Bluetooth device address plus a sequence-wrapped service record and optionally returns the assigned handle.
- `sdp_record_update()` sends a handle plus a sequence-wrapped replacement record.
- `sdp_record_remove()` sends a handle for deletion.
- All three use private control PDU IDs and expect `SDP_PDU_ERROR_RESPONSE` with success error code 0.

Filesystem relevance: none directly. It talks to SDP daemon sessions opened elsewhere, commonly via a local socket.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_record.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_service.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_service.c

This file implements SDP service search and attribute transactions.

Key behavior:
- Uses a default AttributeIDList requesting all attributes when the caller passes `NULL`.
- Reads `SDP_RESPONSE_MAX` once to cap accumulated response buffers, defaulting to `UINT16_MAX`.
- `sdp_service_search()` sends search requests, follows continuation state, and fills service record handles.
- `sdp_service_attribute()` retrieves attributes for one service handle, appending continuation chunks into `ss->rbuf`.
- `sdp_service_search_attribute()` combines service search and attribute retrieval with the same continuation and validation logic.
- Validates response lengths, continuation-state shape, outer SDP sequence size, and recursive SDP data validity.

Filesystem relevance: none. It is Bluetooth SDP network/local protocol transaction code.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_service.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_session.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_session.c

This file implements SDP session setup and PDU transport.

Key behavior:
- `_sdp_open()` opens a Bluetooth L2CAP `SOCK_SEQPACKET` socket, binds local address, connects remote SDP PSM, obtains incoming MTU, and allocates input buffer.
- `_sdp_open_local()` opens a local stream socket to the SDP control path, defaulting to `/var/run/sdp`.
- `_sdp_close()` closes the socket and frees input/response buffers.
- `_sdp_send_pdu()` increments transaction ID, prepends an SDP PDU header, and writes the full iovec.
- `_sdp_recv_pdu()` reads header plus payload, checks PDU ID, transaction ID, and length, and maps SDP Error Response codes to `errno`.

Filesystem relevance: limited to local UNIX-domain socket connection for the SDP daemon.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_session.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_set.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_set.c

This file updates existing SDP data elements in place.

Key behavior:
- `sdp_set_bool()`, `sdp_set_uint()`, and `sdp_set_int()` verify existing element type/width and update payload bytes without changing the element type.
- Handles 8/16/32/64/128-bit integer encodings with bounds checks.
- `sdp_set_seq()` and `sdp_set_alt()` update extended sequence/alternative length fields, optionally deriving length from the buffer.

Filesystem relevance: none. It mutates in-memory SDP records.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_set.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_uuid.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_uuid.c

This file defines the Bluetooth base UUID constant.

Key behavior:
- Exports `BLUETOOTH_BASE_UUID` as `00000000-0000-1000-8000-00805f9b34fb`.

Filesystem relevance: none. It is a protocol constant.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_uuid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbpfjit/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libbpfjit/Makefile

This makefile builds the private BPF JIT library.

Key behavior:
- Builds `libbpfjit` from `sys/net/bpfjit.c`.
- Marks the library private because it depends on private sljit.
- Adds sljit include path from `sys/external/bsd/sljit/dist`.
- Disables manual page installation.

Filesystem relevance: indirect at most. BPF can observe network traffic; this makefile is not filesystem logic.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbpfjit/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbsdmalloc/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libbsdmalloc/Makefile

This makefile builds the historical BSD malloc library.

Key behavior:
- Builds `libbsdmalloc` from `malloc.c`.
- Disables compiler builtins for malloc-family functions so this library can override libc allocation symbols.
- Defines reentrant flags and includes libc internal headers.
- Installs `bsdmalloc.3`.

Filesystem relevance: none directly. It is memory allocator build configuration.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbsdmalloc/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbsdmalloc/malloc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libbsdmalloc/malloc.c

This file implements the historical BSD bucket allocator plus modern front ends.

Key behavior:
- Uses power-of-two bucket free lists with `union overhead` before returned user memory.
- Initializes page size on first allocation and page-aligns the program break with `sbrk()`.
- `malloc()` rounds requests to a bucket, pulls from `nextf[]`, and calls `morecore()` to extend heap storage.
- `free()` validates magic when available and pushes blocks back to the appropriate bucket.
- `realloc()` preserves old BSD behavior for reallocating recently freed blocks by searching free lists; otherwise allocates, copies, and frees.
- Optional `RCHECK`, `DEBUG`, and `MSTATS` code provide range checking, assertions, and allocator statistics.
- Adds `aligned_alloc`, `calloc`, and `posix_memalign` wrappers.
- Provides libc fork hooks to lock/unlock or reinitialize the allocator mutex across fork.

Filesystem relevance: none. It uses process heap growth via `sbrk()`/`break`, not filesystem storage.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbsdmalloc/malloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbz2/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libbz2/Makefile

This makefile builds NetBSD's bzip2 library.

Key behavior:
- Builds `libbz2` from vendored bzip2 distribution sources.
- Installs `bzlib.h`.
- Applies warning suppression for implicit fallthrough.
- Adds a sh3 GCC workaround for `blocksort.c`.
- Installs reference manual HTML when share files are enabled.

Filesystem relevance: indirect. Compression libraries may be used by filesystem tools, but this is not filesystem logic.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libbz2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/Makefile

This is the main NetBSD libc build makefile.

Key behavior:
- Includes `Makefile.inc`, sets `LIB=c`, and adds libc include paths.
- Includes architecture-specific makefiles and optional generated `assym.h`.
- Builds compatibility code either as a separate library or directly into libc with `__BUILD_LEGACY`.
- Includes many libc subsystem make fragments: common, atomic, db, citrus, compat, gdtoa, gen, gmon, inet, locale, net, nls, resolver, stdio, stdlib, string, sys, uuid, yp, and more.
- Removes C source duplicates when assembly versions provide the same entry points and keeps lint-source fallbacks.
- Generates libc tags for non-multilib non-rumprun builds.
- Sets shared libc-specific flags and linker behavior, including init-first dynamic linker ordering.

Filesystem relevance: broad libc build orchestration. It includes syscall and stdio sources that user filesystem code depends on, but this makefile is not a filesystem implementation.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/Makefile.inc

This make fragment defines shared libc build defaults.

Key behavior:
- Disables sanitizer instrumentation and enables fortified build defaults.
- Sets shared-library install behavior and `RUMPRUN` default.
- Adds libc-wide CPP flags: `_LIBC`, SCCS markers, `_REENTRANT`, `_LIBC_INTERNAL`, and `_DIAGNOSTIC`.
- Enables optional Hesiod, IPv6, NLS, and YP flags.
- Configures strict lint flags.
- Includes libc public include rules and sets `ARCHDIR`.
- Clears `LLIBS` to avoid linting libc against itself.

Filesystem relevance: none directly. It is libc build configuration.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/Makefile.inc

This make fragment selects aarch64 libc architecture sources.

Key behavior:
- Adds `__sigtramp2.S`.
- Adds aarch64 softfloat support via `qp.c` and `softfloat-wrapper.c`.
- Defines softfloat-related CPP flags and include paths.
- Notes that `softfloat.c` is pulled through a wrapper due to `.PATH` issues.

Filesystem relevance: none. It is architecture runtime build glue.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/SYS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/SYS.h

This header defines aarch64 assembly syscall wrapper macros.

Key behavior:
- Defines `SYSTRAP(x)` as `svc #(SYS_x)`.
- Provides syscall and pseudo-syscall macros with and without error handling.
- Error handling branches to hidden global `__cerror` when the carry condition indicates failure.
- Defines weak syscall alias support with `WSYSCALL`.

Filesystem relevance: indirect. It underlies all aarch64 libc syscalls, including filesystem syscalls.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/SYS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/gdtoa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/gdtoa/Makefile.inc

This make fragment selects aarch64 gdtoa conversion sources.

Key behavior:
- Adds `strtof.c`, `strtold_pQ.c`, and `strtopQ.c`.

Filesystem relevance: none. It is floating-point string conversion build glue.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/gdtoa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/gdtoa/arith.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/gdtoa/arith.h

This gdtoa architecture header declares aarch64 floating-point byte order.

Key behavior:
- Defines `IEEE_BIG_ENDIAN` when `__AARCH64EB__` is set.
- Otherwise defines `IEEE_LITTLE_ENDIAN`.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/gdtoa/arith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/gdtoa/gd_qnan.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/gdtoa/gd_qnan.h

This header defines quiet-NaN bit patterns for aarch64 gdtoa.

Key behavior:
- Defines single-precision `f_QNAN`.
- Defines double and long-double quiet NaN words differently for big-endian and little-endian aarch64.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/gdtoa/gd_qnan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/net/Makefile.inc

This make fragment documents aarch64 network byte-order handling.

Key behavior:
- Notes that `hton*` and `nto*` functions are supplied by `../gen/byte_swap_*.S`.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/aarch64-gcc.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/aarch64-gcc.h

This SoftFloat configuration header defines aarch64/GCC integer and endian types.

Key behavior:
- Maps NetBSD machine endian macros to `BIGENDIAN` or `LITTLEENDIAN`.
- Enables `BITS64`.
- Defines SoftFloat convenience integer typedefs and exact-width bit typedefs.
- Defines `LIT64`, `INLINE`, and float64 mangle/demangle identity macros.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/aarch64-gcc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/milieu.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/milieu.h

This SoftFloat milieu header imports platform types and boolean constants.

Key behavior:
- Includes `aarch64-gcc.h`.
- Defines `FALSE` and `TRUE`.
- Retains SoftFloat Release 2a licensing/provenance text.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/milieu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/qp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/qp.c

This file provides a remaining aarch64 long-double softfloat ABI wrapper.

Key behavior:
- Defines unions bridging C `float`, `double`, and `long double` with SoftFloat `float32`, `float64`, and `float128`.
- Implements `__negtf2(long double)` using SoftFloat `float128_div()` on zero and the input value.
- Exists because aarch64 ABI passes/returns `long double` in FP/SIMD registers while SoftFloat `float128` uses normal registers.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/qp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/softfloat-qp.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/softfloat-qp.h

This header renames SoftFloat symbols for aarch64 quad-precision support.

Key behavior:
- When `SOFTFLOATAARCH64_FOR_GCC` is defined, maps SoftFloat global names to `_softfloat_*` internal names.
- Renames both single/double helpers and quad-precision helpers that would otherwise enter the user namespace.
- Defines `SOFTFLOAT_FOR_GCC` after renaming to compile out unneeded code paths.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/softfloat-qp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/softfloat-wrapper.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/softfloat-wrapper.c

This wrapper source includes the shared SoftFloat implementation.

Key behavior:
- Contains only `#include <softfloat.c>`.
- Used so the build can pull in the common file despite `.PATH` constraints.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/softfloat-wrapper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/softfloat.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/softfloat.h

This header declares SoftFloat types, flags, and operations used for aarch64 quad precision.

Key behavior:
- Enables `FLOAT128` and leaves `FLOATX80` disabled.
- Includes `softfloat-qp.h`, endian, and floating-point environment headers.
- Defines `float32`, `float64`, and endian-dependent `float128`.
- Declares rounding mode, exception flags/masks, `float_raise()`, integer conversion routines, single/double operations, and quad-precision operations.
- Maps SoftFloat rounding/exception constants onto NetBSD `ieeefp.h` constants.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/softfloat/softfloat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/stdlib/Makefile.inc

This architecture stdlib make fragment is currently empty except for its NetBSD ID.

Key behavior:
- Adds no aarch64-specific stdlib sources.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/string/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/string/Makefile.inc

This architecture string make fragment is currently empty except for its NetBSD ID.

Key behavior:
- Adds no aarch64-specific string sources.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/string/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/__clone.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/__clone.S

This assembly file implements aarch64 `__clone`/`clone`.

Key behavior:
- Validates non-null function and stack arguments, returning `EINVAL` through `__cerror` otherwise.
- Pushes function and argument onto the child stack.
- Calls the `__clone` syscall with `(flags, stack)`.
- Parent returns the child pid; child pops function/argument, calls the function, and exits with its return value.

Filesystem relevance: none directly. It is process/thread creation syscall glue.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/__clone.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/__sigtramp2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/__sigtramp2.S

This file implements the aarch64 signal trampoline return path.

Key behavior:
- Defines DWARF CFI for signal-frame unwinding, including a pseudo return-address register.
- Entry `__sigtramp_siginfo_2` moves the ucontext pointer from `x28` to `x0`.
- Calls `setcontext`; if that fails, calls `exit` with the error code.

Filesystem relevance: none. It is signal/unwind runtime support.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/__sigtramp2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/__syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/__syscall.S

This file implements the generic aarch64 `__syscall` entry.

Key behavior:
- Moves the syscall number out of `x0` into `x17`.
- Shifts syscall arguments down from `x1..x7` to `x0..x6`.
- Loads the eighth syscall argument from the stack into `x7`.
- Executes the syscall trap and invokes `__cerror` on failure.

Filesystem relevance: indirect. This is generic syscall dispatch, including filesystem syscalls.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/__syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/__vfork14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/__vfork14.S

This file implements aarch64 `__vfork14`.

Key behavior:
- Saves link register in `x8`.
- Calls the `__vfork14` syscall.
- Uses the second return register to return pid in the parent and zero in the child.
- Returns through the saved link register.

Filesystem relevance: none directly. It is process creation syscall glue.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/__vfork14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/brk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/brk.S

This file implements aarch64 `brk`/`_brk`.

Key behavior:
- Defines `__minbrk` initialized to `_end`.
- Clamps requested break below `__minbrk` up to the minimum.
- Calls the `break` syscall.
- Stores the new break in `__curbrk` and returns 0 on success.

Filesystem relevance: none. It manages process heap end.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/brk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/cerror.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/cerror.S

This file implements aarch64 syscall error handling.

Key behavior:
- Saves `x19` and link register.
- Preserves errno value, calls `__errno()`, stores the error number.
- Returns `-1` in `x0`.

Filesystem relevance: indirect. It is shared error handling for all libc syscalls.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/cerror.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/fork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/fork.S

This file implements aarch64 `__fork`.

Key behavior:
- Calls the `fork` syscall via `_SYSCALL(__fork,fork)`.
- Uses the second return register to produce parent child-pid and child zero return semantics.

Filesystem relevance: none directly. It is process creation syscall glue.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/fork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/getcontext.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/getcontext.S

This file implements aarch64 `getcontext`.

Key behavior:
- Weak-aliases `getcontext` to `_getcontext`.
- Saves the ucontext pointer before the syscall.
- Calls `getcontext`, then adjusts saved PC to the caller return address.
- Stores zero in saved `x0` so restored context returns 0.

Filesystem relevance: none. It is user context/signal runtime support.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/getcontext.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/pipe.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/pipe.S

This file implements aarch64 `pipe`.

Key behavior:
- Saves the caller's fd array pointer.
- Calls the `pipe` syscall.
- Stores returned fd values into the array and returns 0.

Filesystem relevance: indirect. Pipes are file descriptors, but this is syscall ABI glue.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/pipe.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/ptrace.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/ptrace.S

This file implements aarch64 `ptrace`.

Key behavior:
- Saves arguments and frame registers.
- Clears `errno` before issuing the syscall, preserving arguments across the `__errno()` call.
- Calls `ptrace` and uses normal syscall error handling.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/ptrace.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/sbrk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/sbrk.S

This file implements aarch64 `sbrk`.

Key behavior:
- Defines `__curbrk` initialized to `_end`.
- Adds the requested increment to current break and calls `break`.
- Updates `__curbrk`.
- Returns the old break value.

Filesystem relevance: none. It manages process heap growth.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/sbrk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/shmat.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/shmat.S

This file defines the aarch64 `shmat` syscall wrapper.

Key behavior:
- Includes `SYS.h`.
- Uses `RSYSCALL(shmat)`.

Filesystem relevance: none directly. It attaches System V shared memory.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/shmat.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/syscall.S

This file builds the public aarch64 `syscall` wrapper from `__syscall.S`.

Key behavior:
- Sets `FUNCNAME` to `_syscall`.
- Sets trap macro to `SYSTRAP(syscall)`.
- Includes `__syscall.S`.
- Weak-aliases `syscall` to `_syscall`.

Filesystem relevance: indirect. It is generic syscall ABI support.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/Makefile.inc

This make fragment selects Alpha libc architecture sources.

Key behavior:
- Adds `__longjmp14.c` and `__sigtramp2.S`.
- Generates division and remainder assembly files from `arch/alpha/gen/divrem.m4` with m4 parameters for signedness, operation, and word size.
- Marks generated assembly files for cleanup.
- Adds `CPPFLAGS+= -I.`.

Filesystem relevance: none. It is architecture runtime build glue.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/SYS.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/SYS.h

This header defines Alpha assembly syscall wrapper macros.

Key behavior:
- Provides syscall macros using `CALLSYS_NOERROR` plus error branching through `__cerror` when `a3` indicates failure.
- Defines normal, no-error, pseudo, restartable, and weak-alias syscall wrapper forms.
- Handles GP setup after syscall branch stubs.

Filesystem relevance: indirect. It underlies all Alpha libc syscalls, including filesystem calls.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/SYS.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/gdtoa/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/gdtoa/Makefile.inc

This make fragment selects Alpha gdtoa conversion sources.

Key behavior:
- Adds `strtof.c`.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/gdtoa/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/gdtoa/arith.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/gdtoa/arith.h

This gdtoa architecture header declares Alpha floating-point behavior.

Key behavior:
- Defines `IEEE_LITTLE_ENDIAN`.
- Defines `Sudden_Underflow` when `_IEEE_FP` is not defined.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/gdtoa/arith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/gdtoa/gd_qnan.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/gdtoa/gd_qnan.h

This header defines Alpha gdtoa quiet-NaN bit patterns.

Key behavior:
- Defines `f_QNAN`, `d_QNAN0`, and `d_QNAN1` for little-endian Alpha layouts.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/gdtoa/gd_qnan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/gmon/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/gmon/Makefile.inc

This make fragment adds Alpha gmon profiling support.

Key behavior:
- Adds `_mcount.S`.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/gmon/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/net/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/net/Makefile.inc

This make fragment handles Alpha network byte-order lint stubs.

Key behavior:
- Notes that `hton*` and `nto*` functions come from `../gen/byte_swap_*.S`.
- Adds lint source names for `htonl`, `htons`, `ntohl`, and `ntohs` to `LSRCS`, `DPSRCS`, and `CLEANFILES`.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/net/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/stdlib/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/stdlib/Makefile.inc

This Alpha stdlib make fragment is currently empty except for its NetBSD ID.

Key behavior:
- Adds no Alpha-specific stdlib sources.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/stdlib/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/string/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/string/Makefile.inc

This make fragment selects Alpha assembly string routines.

Key behavior:
- Adds `bcopy.S`, `bzero.S`, `ffs.S`, `memcpy.S`, and `memmove.S`.

Filesystem relevance: indirect only through libc memory primitives used by all code.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/string/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/__clone.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/__clone.S

This assembly file implements Alpha `__clone`/`clone`.

Key behavior:
- Validates function and stack pointers, returning `EINVAL` through `__cerror` if invalid.
- Stores the function and argument on the child stack.
- Calls the `__clone` syscall with flags and stack.
- Parent returns child pid; child retrieves function/argument, calls the function, and exits with its return value.

Filesystem relevance: none directly. It is process/thread creation syscall glue.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/__clone.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/__sigtramp2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/__sigtramp2.S

This file implements the Alpha signal trampoline return path.

Key behavior:
- Defines CFI for signal-frame unwinding, including the Alpha signal-return pseudo register.
- Entry `__sigtramp_siginfo_2` passes the ucontext pointer from the stack to `setcontext`.
- Calls `exit(-1)` if `setcontext` unexpectedly fails.

Filesystem relevance: none. It is signal/unwind runtime support.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/__sigtramp2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/__syscall.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/__syscall.S

This file defines the Alpha `__syscall` wrapper.

Key behavior:
- Includes `SYS.h`.
- Expands `RSYSCALL(__syscall)`.

Filesystem relevance: indirect. It is generic syscall ABI support.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/__syscall.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/__vfork14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/__vfork14.S

This file implements Alpha `__vfork14`.

Key behavior:
- Calls the `__vfork14` syscall.
- Uses `a4` second return value to return zero in the child and pid in the parent.

Filesystem relevance: none directly. It is process creation syscall glue.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/__vfork14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/brk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/brk.S

This file implements Alpha `brk`/`_brk`.

Key behavior:
- Exports `__minbrk` initialized to `_end`.
- Clamps requested break below `__minbrk`.
- Calls the `break` syscall, stores the new value in `__curbrk`, and returns 0.

Filesystem relevance: none. It manages process heap end.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/brk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/cerror.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/cerror.S

This file implements Alpha syscall error handling.

Key behavior:
- In reentrant builds, saves return address and syscall error value, calls `__errno()`, and stores the error.
- In non-reentrant builds, stores directly to `errno`.
- Returns `-1` in `v0`.

Filesystem relevance: indirect. It is shared error handling for libc syscalls.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/cerror.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/fork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/fork.S

This file implements Alpha `__fork`.

Key behavior:
- Calls the `fork` syscall through `CALLSYS_ERROR`.
- Uses `a4` second return value to return zero in the child and child pid in the parent.

Filesystem relevance: none directly. It is process creation syscall glue.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/fork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/getcontext.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/getcontext.S

This file implements Alpha `getcontext`.

Key behavior:
- Weak-aliases `getcontext` to `_getcontext`.
- Calls the `getcontext` syscall.
- Adjusts the saved PC to the caller return address.
- Stores zero into saved `v0` so restored context returns 0.

Filesystem relevance: none. It is user context runtime support.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/getcontext.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/pipe.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/pipe.S

This file implements Alpha `pipe`.

Key behavior:
- Calls the `pipe` syscall.
- Stores returned descriptors from `v0` and `a4` into the caller's fd array.
- Returns 0 on success.

Filesystem relevance: indirect. Pipes are file descriptors, but this is syscall ABI glue.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/pipe.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/ptrace.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/ptrace.S

This file implements Alpha `ptrace`.

Key behavior:
- Loads GP and clears `errno` before the syscall.
- Calls `ptrace` with normal syscall error handling.

Filesystem relevance: none.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/ptrace.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/sbrk.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/sbrk.S

This file implements Alpha `sbrk`.

Key behavior:
- Exports `__curbrk` initialized to `_end`.
- Adds the requested increment to current break and calls `break`.
- Stores the new break in `__curbrk`.
- Returns the old break.

Filesystem relevance: none. It manages process heap growth.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/sbrk.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/shmat.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/shmat.S

This file defines the Alpha `shmat` syscall wrapper.

Key behavior:
- Includes `SYS.h`.
- Expands `RSYSCALL(shmat)`.

Filesystem relevance: none directly. It attaches System V shared memory.

<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/shmat.S -->