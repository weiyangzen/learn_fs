# Group Research: group_504_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_s_37ca008d22b8

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockstr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockstr.c

## Overview
`sockstr.c` is the STREAMS/TPI-facing half of illumos sockfs. It installs stream-head hooks, initializes TPI provider capabilities, translates incoming TPI primitives into socket state changes, manages urgent/OOB data state, queues connection indications and acknowledgements, and supports temporarily exposing a socket as a plain stream when the illusory `sockmod` is popped.

## Main Responsibilities
- Convert between socket and stream modes with `so_sock2stream()` and `so_stream2sock()`.
- Install/remove stream-head protocol hooks through `so_installhooks()` and `so_removehooks()`.
- Initialize TPI metadata with `so_basic_strinit()`, `so_strinit()`, `do_tcapability()`, and `do_tinfo()`.
- Maintain socket state transitions for connect, disconnect, half-close, read/write errors, and OOB data.
- Queue and wait for TPI acknowledgement primitives and pending connection indications.
- Process inbound STREAMS messages in `strsock_proto()` and `strsock_misc()`.
- Manage async signal ownership and compatibility `getmsg`/`putmsg` wrappers.

## Key Control Flow
- `so_strinit()` installs hooks, requests `T_CAPABILITY_ACK` first, falls back to `T_INFO_REQ` when needed, copies transport limits into `sotpi_info_t`, derives `so_mode`, and allocates address buffers.
- `sowaitprim()` waits for a matching ack or `T_ERROR_ACK`, validating primitive type and minimum length before returning the message to callers.
- `strsock_proto()` is the central dispatcher for TPI primitives. It validates message type, size, and alignment, then handles data, unitdata, optdata, exdata, connect confirmation, connection indication, orderly release, disconnect, datagram errors, and ack primitives.
- `strsock_misc()` handles non-protocol STREAMS messages, notably `M_PCSIG/SIGURG`, selected flush behavior, and ignoring hangup/error messages that sockfs tracks itself.

## State and Locking
- `so_lock_single()` serialization is assumed for operations that generate TPI acks.
- `so_lock_read()` prevents concurrent receive-side processing paths from interfering, especially around STREAMS conversion and OOB handling.
- `SOASYNC_UNBIND` protects asynchronous unbind processing after disconnect; `so_save_discon_ind()` defers `T_DISCON_IND` work when another serialized operation is active.
- Connection indications are stored on `sti_conn_ind_head/tail`, while TPI acks are stored in `sti_ack_mp` and signaled through condition variables.

## Notable Behaviors
- `so_sock2stream()` strips TCP accept fast-path options from queued `T_CONN_IND` messages before moving them to the stream head.
- `so_stream2sock()` forces sleeping reads to leave, installs hooks again, flushes queued STREAMS data, and resumes socket tracking from an initial-like state.
- Connected datagram sockets filter inbound `T_UNITDATA_IND` sources for AF_INET/AF_INET6 but deliberately do not filter AF_UNIX source addresses.
- AF_UNIX close indications are encoded as options and can turn into `ECONNRESET`, `SS_CANTSENDMORE`, or discarded no-data messages depending on socket state.
- OOB handling keeps separate signal and data counters, marks `T_EXDATA_IND` messages with `MSGMARK`, stores out-of-line urgent data in `so_oobmsg`, and compresses adjacent out-of-line OOB marks to avoid stream-head flow-control buildup.

## Error Handling and Validation
- The file aggressively rejects too-short or unaligned TPI messages with warnings and frees the offending message.
- Provider capability timeouts mark the provider as not supporting `T_CAPABILITY_REQ` and retry through `T_INFO_REQ`.
- Disconnect and datagram error reasons are treated as errno values, with zero reasons normalized to compatibility errors such as `ECONNRESET` where needed.
- `sogetrderr()` and `sogetwrerr()` provide stream-head callbacks that clear or preserve socket errors depending on peek behavior.

## Dependencies
- Uses STREAMS APIs such as `strsetrputhooks`, `kstrputmsg`, `strseteof`, `strsetrerror`, `strsetwerror`, `strgetmsg`, and `strputmsg`.
- Shares socket structures and helpers from `socktpi_impl.h`, including `sotpi_info_t`, `SOTOTPI()`, and socket state flags.
- Relies on helpers from `socksubr.c` for option parsing, OOB verification, address formatting in debug builds, and lock helpers.

## Research Notes
This file is the main compatibility bridge between BSD-style socket semantics and TPI/STREAMS transport providers. Its highest-risk areas are deferred disconnect/unbind sequencing, OOB counter invariants, datagram source filtering, and the distinction between ordinary socket mode and stream-exposed mode.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socksubr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socksubr.c

## Overview
`socksubr.c` contains common sockfs support routines: initialization, vnode/device lookup, socket serialization locks, AF_UNIX address translation, ancillary data conversion, file descriptor passing, debug formatting, OOB invariant checks, sockfs kstats, file-read helpers for sendfile, and kernel/user copy helpers.

## Main Responsibilities
- Initialize sockfs global state in `sockinit()`, including vnode/vfs ops, socket cache, TPI support, direct socket support, socket parameter tables, filters, sendfile state, and the global sockfs VFS.
- Resolve transport device paths with `sogetvp()`.
- Maintain socket timestamps for stream-backed sockets via `so_update_attrs()`.
- Provide per-socket serialization helpers: `so_lock_single()`, `so_unlock_single()`, `so_lock_read()`, `so_lock_read_intr()`, and `so_unlock_read()`.
- Validate TPI offsets with `sogetoff()`.
- Translate AF_UNIX pathname addresses to internal vnode-based transport addresses.
- Convert between socket control messages and TPI options, including SCM_RIGHTS/SO_FILEP fd passing.
- Produce zone-specific AF_UNIX socket kstats.

## AF_UNIX and Address Handling
- `so_ux_lookup()` resolves a pathname, follows real vnodes through lofs, verifies `VSOCK`, checks access when requested, and finds the active sockfs vnode through the stream head.
- `so_addr_verify()` enforces family-specific sockaddr lengths for AF_INET/AF_INET6, validates AF_UNIX lengths and family, and allows opaque address forms for other families.
- `so_ux_addr_xlate()` converts an AF_UNIX pathname into a `sockaddr_ux`-style internal address based on the peer vnode pointer.

## Ancillary Data and File Descriptor Passing
- `fdbuf_create()` converts user fd integers into held `file_t *` references and audits sends.
- `fdbuf_allocmsg()` creates an external-buffer STREAMS message whose free callback closes file references.
- `fdbuf_extract()` allocates new user fds on receive, increments file reference counts, honors `MSG_CMSG_CLOEXEC` and `MSG_CMSG_CLOFORK`, and audits receives.
- `fdbuf_verify()` ensures an incoming `SO_FILEP` option matches the esballoc free-argument metadata before trusting it.
- `so_getfdopt()`, `so_optlen()`, `so_cmsg2opt()`, `so_cmsglen()`, and `so_opt2cmsg()` bridge old `msg_accrights`, modern `cmsghdr`, and internal TPI option formats.
- `so_closefds()` and `so_truncatecmsg()` clean up descriptors and adjust headers when control data is truncated or copyout fails.

## Message Allocation Helpers
- `soallocproto()`, `soallocproto1()`, `soallocproto2()`, and `soallocproto3()` allocate and populate `M_PROTO` messages with selectable sleep behavior.
- `soappendmsg()` appends zeroed or copied data into preallocated mblks.

## Debug and Invariants
- In debug builds, `pr_state()` and `pr_addr()` format socket state and addresses.
- `so_verify_oobstate()` validates legal combinations of OOB flags, mark counters, and `so_oobmsg` ownership.

## Kstats and Utility I/O
- `sock_kstat_init()` creates a per-zone raw `sock_unix_list` kstat.
- `sockfs_update()` counts active AF_UNIX sockets in the current zone.
- `sockfs_snapshot()` copies sonode state, AF_UNIX local/foreign names, vnode pointer strings, inode numbers, and zone metadata into `struct sockinfo`.
- `soreadfile()` performs cached kernel-space file reads for sendfile support.
- `so_copyin()` and `so_copyout()` switch between direct kernel copies and `xcopyin`/`xcopyout`.

## Research Notes
This file is the shared substrate that keeps sockfs syscall and STREAMS code from duplicating tricky policy. The most important correctness areas are fd-passing lifetime rules, cmsghdr/TPI length alignment, AF_UNIX vnode lifetime, and the lock ordering around sonode state and vnode/stream references.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socksubr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socksyscalls.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socksyscalls.c

## Overview
`socksyscalls.c` implements the kernel side of socket-related system calls and sendfile support. It maps user file descriptors to sonodes, copies user arguments safely, delegates protocol behavior to the socket operation layer, handles legacy ABI differences, manages socket configuration/filter registration, and implements sendfile through direct I/O or page-cache-backed transmission.

## Main Responsibilities
- Implement `socket`, `socketpair`, `bind`, `listen`, `accept`, `connect`, `shutdown`, `recv`, `recvfrom`, `recvmsg`, `send`, `sendmsg`, `sendto`, `getpeername`, `getsockname`, `getsockopt`, and `setsockopt`.
- Provide `getsonode()` fd-to-sonode lookup with namefs/stream-head awareness.
- Copy in and normalize sockaddr arguments with `copyin_name()`, including AF_UNIX NUL termination.
- Copy out addresses/options with XNET-compatible truncation semantics.
- Register/remove socket transports and filters through `sockconfig()`.
- Implement `sendfile` backing paths: asynchronous direct I/O, zero-copy segmap/vpm, and cached read/send loops.
- Provide 32-bit syscall wrappers and legacy compatibility wrappers around the sonode operation switch.

## Syscall Path Details
- `so_socket()` validates type flags, optionally copies a transport device path, creates the socket, allocates a file descriptor, sets nonblocking/ndelay state, and applies close-on-exec/close-on-fork flags.
- `so_socketpair()` builds AF_UNIX datagram pairs by binding and cross-connecting both endpoints; stream pairs are made with a listener, nonblocking connect, accept, and fd replacement.
- `accept()` preallocates a user fd before consuming a connection, optionally copies out peer address, creates a file structure, applies accept flags, and propagates listener nonblocking state.
- `recvit()` and `sendit()` are the common receive/send workers. They set `uio` flags from the file, handle address/control copyin or copyout, and delegate to `socket_recvmsg()`/`socket_sendmsg()`.
- `recvmsg()` and `sendmsg()` translate native and ILP32 structures, bound iovec counts, reject negative or overflowing lengths, and preserve legacy non-XPG behavior.

## Compatibility Semantics
- Non-XPG send paths force `MSG_EOR` to match older libsocket/sockmod behavior.
- Old `msg_accrights` style control data is supported separately from modern `cmsghdr` control data.
- 32-bit callers get iovec widening and timeval/timespec-compatible ancillary handling through the shared subroutines.
- `copyout_name()` reports the full kernel length even when the user buffer truncates, matching XNET semantics.

## Sockconfig and Filters
- `sockconf_add_sock()` installs socket parameter mappings either for `/dev/...` transports or named socket modules.
- `sockconfig_add_filter()` copies filter properties, validates hints and socket tuples, supports ILP32 property translation, and adds auto or programmatic socket filters.
- Removal marks filters condemned if still referenced, otherwise frees them immediately.
- `sockconfig()` requires network configuration privilege and dispatches add/remove/get-table commands.

## Sendfile Implementation
- `sendfile_init()` initializes the sendfile request queue, service-thread limits, timeout, and default cache policy.
- Direct I/O uses `create_thread()` and `snf_async_thread()` to run `snf_async_read()` as a producer, queueing mblks with high/low water flow control. `snf_direct_io()` consumes queued mblks and sends them with `socket_sendmblk()`.
- `snf_segmap()` uses vpm mappings when available, otherwise segmap soft locks, builds zero-copy esballoc mblks, marks `STRUIO_ZC`, and optionally waits for zero-copy completion unless `SFV_NOWAIT` is set.
- `snf_cache()` reads file data into allocated mblks and sends them, adjusting chunk sizes for stream/socket max packet sizes and active socket filters.
- `sosendfile64()` chooses direct I/O when the transfer exceeds `sendfile_max_size`; otherwise it validates file size, decides if zero-copy is worthwhile and safe, and falls back to cached copying.

## Error Handling and Lifetime
- All syscall entry points release held file descriptors on each exit path.
- Copyin/copyout failures return `EFAULT`; excessive user-controlled sizes return `EINVAL` or `EMSGSIZE`.
- Sendfile direct I/O coordinates read/write errors so write errors win when both sides fail, drains queued mblks on failure, and always waits for the reader to finish.
- Zero-copy sendfile callbacks release vpm/segmap mappings and held vnodes only after the mblk data block’s last reference is dropped.

## Research Notes
This file is the user/kernel ABI surface for sockfs. Its highest-risk areas are argument translation across ABI versions, fd lifetime during socketpair/accept/sendmsg/recvmsg, privilege-checked dynamic configuration, and sendfile’s interaction with vnode locking, zero-copy completion, active socket filters, and partial-transfer accounting.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socksyscalls.c -->