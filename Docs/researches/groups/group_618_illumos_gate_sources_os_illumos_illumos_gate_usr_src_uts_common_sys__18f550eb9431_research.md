# Group Research: group_618_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__18f550eb9431

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/smbios_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/smbios_impl.h

## Role

Private implementation header for illumos SMBIOS parsing in libsmbios and the kernel SMBIOS provider. Public clients are explicitly directed to use `<smbios.h>` or `<sys/smbios.h>` instead.

## Key Contents

Defines packed SMBIOS wire-format structures for many DMTF structure types: BIOS, system, baseboard, chassis, processor, cache, port, slot, onboard devices, string tables, event log, memory arrays/devices/maps, pointer devices, battery, hardware security, probes, cooling devices, boot info, management/IPMI/power supply, additional information, TPM, processor-specific info, firmware inventory, string properties, and Sun OEM extensions.

Includes decode macros for BIOS extended ROM fields, chassis element types, cache size/configuration, hardware security bitfields, probe type/status, IPMI fields, and PSU characteristics.

Defines the internal `smb_struct_t` descriptor and `struct smbios_hdl`, including entry-point type, table buffer, parsed structure array, hash buckets, error state, ABI/library version, SMBIOS version, and flags.

## Interfaces

Declares internal lookup, string, version, error, allocation, free, and debug helpers such as `smb_lookup_type`, `smb_lookup_id`, `smb_strptr`, `smb_gteq`, `smb_set_errno`, `smb_open_error`, `smb_alloc`, and `smb_dprintf`.

## Design Notes

The file centralizes raw SMBIOS layout knowledge, including variable-length records and versioned structure continuations. It also defines base public-structure snapshots used to preserve ABI compatibility when public SMBIOS structures grow.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/smbios_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sobject.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sobject.h

## Role

Defines synchronization object type numbers and the operation vector used by the scheduler/sleep-queue code to reason about owners and priority inheritance.

## Key Contents

Enumerates `SOBJ_NONE`, `SOBJ_MUTEX`, `SOBJ_RWLOCK`, `SOBJ_CV`, `SOBJ_SEMA`, `SOBJ_USER`, `SOBJ_USER_PI`, and `SOBJ_SHUTTLE`. The numeric ordering starts at zero because the synchronization-object mapping array depends on these values.

Defines `sobj_ops_t` with object type, owner lookup, unsleep, and priority-change callbacks.

## Kernel Macros

Under `_KERNEL`, provides dispatch macros for reading object type, finding owner, waking sleepers, and changing inherited/effective priority through the registered operations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sobject.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/socket.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/socket.h

## Role

Primary public socket API header. It defines socket types, flags, options, address/protocol families, message structures, ancillary-data macros, shutdown constants, and user-visible socket function prototypes.

## Key Contents

Defines `socklen_t`, socket types, `SOCK_CLOEXEC`, `SOCK_NONBLOCK`, `SOCK_NDELAY`, and `SOCK_CLOFORK`. Socket options include traditional bit flags, newer large-number options for attach/detach filters, buffer/time/error/protocol/domain options, credential/timestamp controls, zone/security options, and kernel-only internal options.

Defines socket filter control values, `struct fil_info`, address family constants through `AF_PACKET`, matching `PF_*` aliases, `SOMAXCONN`, `struct msghdr`, compatibility `omsghdr`, 32-bit syscall structures, `MSG_*` flags, `struct cmsghdr`, and `CMSG_*` macros.

## Interfaces

Declares `accept`, `accept4`, `bind`, `connect`, `getpeername`, `getsockname`, `getsockopt`, `listen`, `socketpair`, `recv*`, `send*`, `setsockopt`, `shutdown`, `socket`, and `sockatmark` where namespace rules permit.

## Design Notes

The header contains substantial standards/ABI gating for XPG, POSIX, boot, kernel, and 32-bit syscall views. Several constants are compatibility-bound and must remain synchronized with external consumers such as DTrace IP provider definitions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/socket.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/socket_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/socket_impl.h

## Role

Implementation support header included by `<sys/socket.h>` for basic socket address structure definitions.

## Key Contents

Defines `sa_family_t`, `struct sockaddr`, and, when standards namespace permits, pulls in UNIX-domain and link-layer address support.

Defines `struct sockaddr_storage` with a 256-byte implementation-specific maximum size and alignment padding based on `double`, providing room for common address families such as IPv4, IPv6, and link-layer addresses.

Also defines Linux-compatible `struct sockaddr_ll` and packet type constants for `PF_PACKET` sockets.

## Design Notes

This is the ABI substrate for socket address storage. It deliberately keeps Linux packet socket compatibility visible through normal `<sys/socket.h>` inclusion.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/socket_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/socket_proto.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/socket_proto.h

## Role

Kernel-facing protocol interface between sockfs and socket protocol providers.

## Key Contents

Defines `sock_connid_t` generation counters and comparison helpers. Defines `struct sock_proto_props`, which transports protocol properties such as write offset, watermarks, max/min packet size, zero-copy flags, OOB behavior, receive timer/threshold, maximum address length, and loopback status.

## Kernel Interfaces

Defines opaque upper/lower handles, `sock_downcalls_t` for sockfs-to-protocol operations, and `sock_upcalls_t` for protocol-to-sockfs notifications. Downcalls cover activate, accept, bind, listen, connect, names, options, send/receive, poll, shutdown, ioctl, and close. Upcalls cover new connections, connected/disconnected state, receive delivery, protocol property changes, flow control, OOB notification, zero-copy completion, errors, close, and vnode lookup.

Also declares standard `*_notsupp` helpers returning unsupported-operation behavior.

## Design Notes

The version macros are `sizeof` the upcall/downcall structures, making ABI compatibility sensitive to structure layout.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/socket_proto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/socketvar.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/socketvar.h

## Role

Private sockfs kernel header defining the internal socket object, socket module registry, socket parameter table, fallback support, sendfile queues, operation vectors, and sockconfig data structures.

## Key Contents

Defines AF_UNIX transport-level address structures used to avoid pathname ambiguity. Defines `struct sonode`, the core in-kernel socket object associated with a vnode, including locks, state flags, socket identity, accept queues, options, OOB state, credentials, zone, poll state, receive queues, protocol handles/downcalls, kernel socket callbacks, direct receive support, filters, and callback hooks.

Defines state flags such as connection state, shutdown state, async/listen/OOB/filter/fallback status, socket modes, socket version constants, socket module registration structures, `sockparams`, reference-count macros, sendfile request/queue structures, and `sonodeops`.

## Interfaces

Declares sockparams and socket module registry functions, sockfs lifecycle and data conversion helpers, file-descriptor passing helpers, state transition helpers, wrapper operations such as `sobind`, `soconnect`, `sorecvmsg`, `sosendmsg`, and kernel direct receive callback functions.

## Design Notes

Locking is central: `so_lock`, single/read locks, accept queue lock, fallback rwlock, and filter state all coordinate access. The file also defines public-ish kstat export structures and `sockconfig()` command data for socket/filter administration.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/socketvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sockfilter.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sockfilter.h

## Role

Defines the kernel socket filter API used to intercept and manipulate socket lifecycle, control, and data paths.

## Key Contents

Defines opaque `sof_handle_t`, filter callback return codes, notification events, and function pointer types for active/passive attach, detach, inbound/outbound data, bind, listen, accept, connect, shutdown, name lookup, socket options, ioctl, mblk property adjustment, and notification.

Groups callbacks in `sof_ops_t` and defines `SOF_VERSION`.

## Interfaces

Exports registration and control helpers: `sof_register`, `sof_unregister`, `sof_newconn_ready`, `sof_bypass`, cookie get/CAS, data injection in both directions, receive/send flow control toggles, and moving a new connection between filter handles.

## Design Notes

The API supports both automatic and programmatic filter attachment and permits filters to defer, detach, continue, stop successfully, or stop with selected errors.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sockfilter.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sockio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sockio.h

## Role

Defines socket, routing, ARP, interface, logical-interface, multicast, SCTP, PF_PACKET, and private networking ioctl command numbers.

## Key Contents

Includes classic socket ioctls for watermarks, OOB mark, and process group. Defines route ioctls, multicast routing counters, obsolete `struct ifreq` interface controls, newer `struct lifreq` IPv4/IPv6 logical-interface controls, address query ioctls, IPMP controls, IPv6 address policy controls, extended ARP controls, sockfs fallback ioctl, zone-interface association controls, SCTP option/peeloff ioctls, source address controls, RFC 3678 source-filter controls, PF_PACKET hardware-address/timestamp controls, ILB ioctl, module property ioctls, DAD state, IPv6 prefix generation, and logical-interface hardware address query.

## Design Notes

Many commands use `_IOWRN` or `_IOWN` to remain data-model independent. The file preserves extensive historical ioctl numbering and marks reusable gaps left by removed private interfaces.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sockio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/softmac.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/softmac.h

## Role

Public softmac interface header for creating, destroying, holding, releasing, and recreating softmac devices.

## Interfaces

Declares `softmac_create`, `softmac_destroy`, `softmac_hold_device`, `softmac_rele_device`, and `softmac_recreate`.

## Dependencies

Pulls in DDI, MAC, and DLS types. The hold/release API exposes `dls_dev_handle_t`, indicating this header bridges softmac lifecycle with the data-link services device layer.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/softmac.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/softmac_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/softmac_impl.h

## Role

Private implementation header for softmac, the compatibility layer that registers legacy DLPI network devices with the GLDv3/MAC framework.

## Key Contents

Defines lower-stream receive callback types, `softmac_lower_t`, softmac attachment state, per-minor `softmac_dev_t`, softmac flags, and the central `softmac_t` object. `softmac_t` tracks device identity, attach/detach state, hold counts, minor nodes, MAC handle, DLPI media/style/address/SDU properties, notification capabilities, checksum/capability flags, active/fastpath state, notify thread queues, lower stream, and upper stream list.

Defines ioctl start control structures and datapath mode constants for unknown, slowpath, and fastpath. Defines `softmac_upper_t` for upper STREAMS instances, including task queue linkage, associated lower stream, pending DLPI messages, fastpath state, flow control, direct RX callbacks, and MAC TX notify callback.

## Interfaces

Declares DLPI request helpers, init/fini, fastpath init/fini, capability enable/fill, receive processing, output, MAC provider entry points, hold/release, lower setup, active/fastpath controls, datapath switching, and upper stream write/close routines.

## Design Notes

The header documents several locking domains: per-softmac mutexes, active mutex, fastpath mutex, upper dispatch mutex, and upper fastpath mutex. Fastpath/slowpath switching is a major design concern.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/softmac_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/soundcard.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/soundcard.h

## Role

Compatibility shim for OSS-style soundcard interfaces.

## Key Contents

Includes `<sys/audio/audio_oss.h>` and defines no additional symbols.

## Design Notes

This header exists so consumers including `<sys/soundcard.h>` receive the illumos OSS audio compatibility definitions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/soundcard.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/squeue.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/squeue.h

## Role

Public kernel header for serialized queue processing used heavily by networking.

## Key Contents

Declares opaque `squeue_t`, queue-entry setup macros, entry flags `SQ_FILL`, `SQ_NODRAIN`, and `SQ_PROCESS`, and helper macros for entering single or chained mblks into an squeue.

Defines `SQUEUE_SWITCH` for moving a connection to another squeue while executing inside one. Defines private data slots through `sqprivate_t`.

## Interfaces

Declares `squeue_init`, `squeue_create`, bind/unbind, `squeue_enter`, private data lookup, and synchronous enter/exit helpers for connections.

## Design Notes

The API stores callback procedure and argument in `mblk_t` linkage fields, so callers must pass clean mblks with null `b_next`/`b_prev`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/squeue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/squeue_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/squeue_impl.h

## Role

Private implementation header for squeue internals.

## Key Contents

Defines debug/profile compilation controls, default priority, statistics structure, squeue set structure, callback function types, and the full `struct squeue_s`.

The structure contains entry/drain function pointers, lock, state, queue count/head/tail, current running thread, receive ring/ILL association, worker timing and condition variables, CPU binding, worker/poll threads, private storage, set linkage, priority, and debug-only current packet/procedure/connection/tag fields.

## State Flags

Defines processing, worker, enter, fast, user, bound, reenter, polling capability, ILL binding, packet retrieval, default queue, polling, interrupt blanking, forced timer, poll cleanup/quiesce/restart, thread-control, and pause flags.

## Design Notes

The MDB IP module depends on the numeric values of state flags, so flag layout is externally significant to debugging tooling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/squeue_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/srn.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/srn.h

## Role

Defines suspend/resume notification event codes and ioctl commands.

## Key Contents

Provides event constants for standby, suspend, resume, battery low, power change, time update, critical suspend, user/system requests, next event, resume/suspend/standby ioctls, and autosx behavior changes.

Defines `srn_event_info_t` with event type `ae_type`.

## Kernel Contents

Under `_KERNEL`, defines clone limit and notification source types for APM and autosx.

## Design Notes

The header warns that these commands and structures may change or disappear, so this is not a stable public contract.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/srn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sservice.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sservice.h

## Role

PCMCIA Socket Services/Card Services interface definitions for adapters, sockets, windows, events, and resource allocation.

## Key Contents

Defines Socket Services function identifiers, Card Services helper identifiers, return codes, card/socket events, event masks, and registration structure `csregister_t`.

Provides data structures for getting and setting adapter, page, socket, status, and window state. Defines IRQ, page, socket, interface, DMA, power, resource, window, and voltage flags. Includes inquiry structures for adapter/socket/window capabilities, memory and I/O window characteristics, IRQ handler registration, device-node creation, adapter info, cookies/DIP retrieval, and reset modes.

Defines the `sservice_t` union over exported request structures and event-manager `pcm_make_dev`.

## Kernel Interfaces

Under `_KERNEL`, declares PCMCIA nexus attach/control/property/intr/open/close/ioctl/power/resume/wait functions and resource allocation, free, map, and bus-map helpers.

## Design Notes

This is a legacy but broad hardware-management ABI. It combines service dispatch IDs, event callbacks, device-node operations, and resource allocation contracts in one header.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sservice.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stat.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stat.h

## Role

Defines `stat`/`stat64` ABI structures, mode bits, file-type predicates, timestamp aliases, large-file symbol mapping, 32-bit syscall views, and file mode-related function prototypes.

## Key Contents

Selects namespace-safe time definitions depending on standards mode. Defines kernel and user variants of `struct stat` and `struct stat64` for LP64 and ILP32. Handles `_FILE_OFFSET_BITS=64` remapping and LP64 large-file aliases through pragma or macro redirection.

Defines 32-bit kernel views `stat32` and `stat64_32`, including packing for alignment differences. Provides file type bits, permission bits, special bits, POSIX permission macros, `S_IS*` predicates, POSIX.4 type macros, x86 SVR4 version constants, and `UTIME_NOW`/`UTIME_OMIT`.

## Interfaces

Declares `chmod`, `fchmod`, `mkdir`, `mkfifo`, `umask`, large-file `stat64` family, and `*at`/timestamp functions when enabled. Includes `<sys/stat_impl.h>` for additional non-kernel declarations.

## Design Notes

This header is dominated by ABI preservation across standards modes, LP64/ILP32, large-file transition, and old x86 compatibility.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/statfs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/statfs.h

## Role

Legacy `statfs(2)`/`fstatfs(2)` ABI header, superseded by `statvfs`.

## Key Contents

Defines `struct statfs` with filesystem type, block size, fragment size, block counts, inode counts, volume name, and pack name. Defines `struct statfs32` for 32-bit syscall compatibility.

## Interfaces

For non-kernel code, declares `statfs` and `fstatfs`.

## Design Notes

The header states this interface has been replaced by `statvfs`/`fstatvfs` and may be removed in a future release.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/statfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/statvfs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/statvfs.h

## Role

Defines the modern filesystem statistics ABI for `statvfs(2)` and `fstatvfs(2)`.

## Key Contents

Defines `_FSTYPSZ`/`FSTYPSZ`, `statvfs_t`, 32-bit `statvfs32_t`, large-file `statvfs64_t`, and 32-bit large-file `statvfs64_32_t`. Structures report block sizes, block counts, file counts, filesystem ID, base type, mount flags, maximum filename length, and filesystem-specific string.

Defines mount flags `ST_RDONLY`, `ST_NOSUID`, and `ST_NOTRUNC`.

## Interfaces

Handles `_FILE_OFFSET_BITS=64` and LP64 large-file remapping, then declares `statvfs`, `fstatvfs`, and transitional `statvfs64`/`fstatvfs64` where enabled.

## Design Notes

Like `stat.h`, this file is ABI-sensitive and preserves data-model-specific layout, including packed 32-bit large-file structures when required by alignment rules.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/statvfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stdalign.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stdalign.h

## Role

Implements ISO C11 `<stdalign.h>` support for illumos system headers.

## Key Contents

For C, maps `alignas` to `_Alignas` and `alignof` to `_Alignof`. For C++, it avoids redefining keywords but still defines `__alignas_is_defined` and `__alignof_is_defined`.

## Design Notes

The header intentionally does not add compiler feature guards beyond C++ handling. It assumes C11 or newer use and lets missing compiler support surface as a compiler error.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stdalign.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stdbit.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stdbit.h

## Role

Implements C23 `<stdbit.h>` functionality for illumos, with usable non-generic functions across C versions and type-generic macros when C11 `_Generic` is available.

## Key Contents

Defines `__STDC_VERSION_STDBIT_H__`, endian constants, native endian selection, and `size_t` if needed. Declares extern functions for leading/trailing zeros and ones, first leading/trailing zero/one, zero/one counts, single-bit test, bit width, bit floor, and bit ceiling for unsigned char, unsigned short, unsigned int, unsigned long, and conditionally unsigned long long.

## Generic Macros

When `_STDC_C11` is defined, maps generic `stdc_*` macros by `sizeof(val)` to 1-, 2-, 4-, or 8-byte implementations using `_Generic` on a fixed-length array pointer expression.

## Design Notes

The implementation deliberately uses extern functions provided by libc and the kernel rather than relying on compiler builtins or inline expansion, avoiding runtime support mismatches.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stdbit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stdbool.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stdbool.h

## Role

Implements ISO C99 `<stdbool.h>` compatibility.

## Key Contents

Includes feature-test definitions and, outside C++, defines `bool` as `_Bool`, `true` as `1`, `false` as `0`, and `__bool_true_false_are_defined` when C99 features or compatible compiler support are available.

## Design Notes

The header notes that undefining/redefining `bool`, `true`, and `false` is obsolescent but preserved for standards compatibility.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stdbool.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stddef.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stddef.h

## Role

Provides common `<stddef.h>`-style support for `offsetof`.

## Key Contents

Defines `offsetof(s, m)` if not already defined. Uses `__builtin_offsetof` for GCC 4.1 and newer. Falls back to address-of-null-member expressions, casting to `std::size_t` in C++98-or-newer or `size_t` in C.

## Design Notes

This is a compact compatibility header with no type definitions beyond the macro.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stddef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stdint.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stdint.h

## Role

System implementation backing for ISO C99 `<stdint.h>`.

## Key Contents

Includes integer type, limit, and constant headers: `<sys/int_types.h>`, `<sys/int_limits.h>`, and `<sys/int_const.h>`.

## Design Notes

The header is intentionally only a composition layer over illumos integer definitions and does not define integer types directly.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stdint.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stermio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stermio.h

## Role

Legacy synchronous terminal/printer channel ioctl definitions and associated structures.

## Key Contents

Defines control-channel commands such as protocol start/halt, printer assignment, polling enable/disable/rate, status reports, and trace channel selection. Defines terminal/printer commands for getting/setting line options, throwing away queued input, getting synchronous line number, and getting all line information.

Defines `struct stio`, mode bits `STFLUSH`, `STWRAP`, and `STAPPL`, status structures `sttsv` and `stcntrs`, and trace message `LOC`.

## Design Notes

This is a legacy terminal compatibility header with fixed ioctl numeric encodings and compact packed-style structures.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stermio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stmf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stmf.h

## Role

Core SCSI Target Mode Framework API header for LU providers, port providers, SCSI sessions, tasks, data buffers, state changes, task control, and SCSI helper routines.

## Key Contents

Defines STMF structure IDs, provider callback commands/flags, `data_seg_handle_t`, constants, scatter/gather entries, `stmf_data_buf_t`, data-buffer flags, and the central `scsi_task_t` structure. Task fields include provider/private handles, session/lport/LU pointers, LUN, task flags, priority, task management function, buffer counts, command sequence info, expected transfer length, CDB, transfer accounting, status/sense data, and extension pointer.

Defines task flags, task-management codes, additional flags, buffer limits, status controls, I/O flow flags, allocation flags, state-change structures, reason flags, abort commands, control commands for LU/LPORT state changes, info command classifiers, event constants, DDI node type strings, VPD bits, and a seconds-to-ticks helper.

## Interfaces

Declares STMF allocation/free, task allocation/posting, dbuf allocation/setup/xfer/free, status send/completion callbacks, task done/abort/poll, control, ITL handle registration, event registration, SCSI VPD/devid/status helpers, transport ID validation/comparison, remote port allocation/free, LU hold/release, and abort-state query.

## Design Notes

This header is the in-kernel contract between STMF core, logical-unit providers, and port providers. The structures encode both SCSI protocol state and provider-private extension points.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stmf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stmf_defines.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stmf_defines.h

## Role

Common STMF constants, status encoding, SCSI field helpers, sense/ASC/ASCQ constants, and forward declarations.

## Key Contents

Defines `BIT_0` through `BIT_31`. Defines `stmf_status_t` as `uint64_t` and status encoding constants for success, generic failure, target failure, LU failure, function-specific codes, retry bit, busy, not found, invalid argument, LUN taken, aborted, allocation failure, already, timeout, not supported, and bad state.

Provides byte-offset and aligned-structure-size macros plus big-endian SCSI integer readers for 16-, 21-, 32-, and 64-bit fields. Defines pointer/integer conversion macros, a synchronize-cache command not present elsewhere, and common packed SCSI sense/action codes used by STMF SCSI library status helpers.

## Design Notes

The status format reserves high bits for broad failure class and middle bits for framework-specific codes, allowing providers and core code to share compact status values.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stmf_defines.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stmf_ioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stmf_ioctl.h

## Role

User/kernel ioctl ABI for administering STMF logical units, target ports, sessions, groups, views, provider data, trace buffers, ALUA state, and default properties.

## Key Contents

Defines ioctl command numbers under the STMF namespace and version `STMF_VERSION_1`. Defines `stmf_iocdata_t`, which carries input/output buffer sizes, entry counts, errors, and 64-bit buffer addresses.

Defines list entries for LUs, target ports, and SCSI sessions; LU/LPORT/STMF states; config states; LU and target-port property structures; state descriptors; ALUA state descriptor; ioctl-specific error codes; group names and group-entry identifiers; group operation data; view-entry operation data; provider private data ioctl payload; and default property setting structure.

Also defines SCSI device identifier descriptors and protocol/code-set/association/identifier type constants.

## Interfaces

Declares `stmf_copyin_iocdata` and `stmf_copyout_iocdata`.

## Design Notes

The ABI uses fixed-size identifiers and flexible trailing data conventions. Many structures carry validity bits so ioctl payloads can represent partial updates.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stmf_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stmf_sbd_ioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stmf_sbd_ioctl.h

## Role

Ioctl ABI for the STMF SBD logical-unit provider, covering creation, import, deletion, modification, property lookup, LU listing, standby/global LU controls, and unmap properties.

## Key Contents

Defines provider-specific return codes for metadata creation, block size, separate metadata requirements, duplicate file/GUID, invalid paths, lookup/open/getattr failures, type mismatch, file size/alignment/range/support errors, missing metadata, version unsupported, busy/not found, insufficient buffer, write-cache failure, and access-state failure.

Defines SBD ioctl numbers and payload structures: `sbd_create_and_reg_lu_t`, `sbd_global_props_t`, `sbd_set_lu_standby_t`, `sbd_import_lu_t`, `sbd_modify_lu_t`, `sbd_delete_lu_t`, `sbd_lu_props_t`, and `sbd_unmap_props_t`.

## Design Notes

Most request structures include structure size, validity bitfields, offset fields into trailing buffers, fixed VPD strings, GUIDs, and “likely more than 8” trailing arrays. The ABI is designed for variable-length path, alias, URL, and serial data while keeping the fixed header stable.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stmf_sbd_ioctl.h -->