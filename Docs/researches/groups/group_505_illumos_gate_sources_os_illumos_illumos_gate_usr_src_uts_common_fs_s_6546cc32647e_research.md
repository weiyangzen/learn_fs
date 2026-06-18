# Group Research: group_505_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_s_6546cc32647e

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included. All 8 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socktpi.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socktpi.c

## Purpose
Implements the TPI/STREAMS-backed sockfs socket backend for illumos. It creates and initializes TPI socket sonodes, maps BSD socket operations onto TPI primitives and STREAMS operations, handles AF_UNIX pathname sockets, supports direct TCP/UDP fast paths, and provides fallback conversion between non-STREAMS sockets and TPI sockets.

## Key Responsibilities
- Creates and destroys TPI `sonode` instances through `sotpi_create`, `sotpi_destroy`, `socktpi_init`, and the `sotpi_smod_create` socket-module entry.
- Opens the transport stream in `sotpi_init`, detects clone opens, configures socket-aware stream flags, discovers provider information, negotiates direct-call support, initializes stream state, and applies wildcard protocol selection.
- Implements bind/listen/unbind through `sotpi_bindlisten`, `sotpi_bind`, `sotpi_unbind`, and `sotpi_listen`, including implicit binds, AF_INET/AF_INET6 port/address handling, AF_UNIX filesystem vnode creation, rebinding for listen backlog changes, and cached local-address invalidation.
- Implements connection lifecycle through `sotpi_connect`, `sodisconnect`, `sotpi_accept`, `sotpi_shutdown`, and `so_unix_close`.
- Implements `recvmsg` translation in `sotpi_recvmsg`, converting `T_DATA_IND`, `T_UNITDATA_IND`, `T_OPTDATA_IND`, and `T_EXDATA_IND` into socket receive semantics, ancillary data, source addresses, `MSG_TRUNC`, `MSG_EOR`, `MSG_WAITALL`, `MSG_PEEK`, and urgent-data behavior.
- Implements send paths through `sotpi_sendmsg`, `sosend_dgram`, `sosend_dgramcmsg`, `sosend_svc`, `sosend_svccmsg`, `sotpi_sendmblk`, and `kstrwritemp`, including datagram destination selection, connected datagram errors, ancillary data, file-descriptor passing, out-of-band data, `MSG_DONTROUTE`, sendfile mblk writes, and stream/datagram TPI primitive construction.
- Provides direct fast paths in `sodgram_direct` and `sostream_direct` that call UDP/TCP write-side functions directly when flow control and stream state allow, falling back to normal STREAMS writes when needed.
- Implements `sotpi_getpeername`, `sotpi_getsockname`, `sotpi_getsockopt`, and `sotpi_setsockopt`, mixing sockfs-cached values with TPI option/name ioctls.
- Handles socket and STREAMS ioctls in `sotpi_ioctl` and `socktpi_plumbioctl`, including the virtual `sockmod` view, `I_PUSH`/`I_POP` transitions, async/pgrp controls, `SIOCATMARK`, and peer credential retrieval.
- Implements socket poll semantics in `sotpi_poll` on top of stream-head polling while accounting for connection state, queued connection indications, shutdown, socket errors, and urgent-data state.
- Supports fallback conversion with `sotpi_convert_sonode`, `sotpi_revert_sonode`, and `sotpi_update_state`.

## Concurrency and Lifetime
The main socket lock `so_lock` protects `so_state`, cached addresses, urgent-data counters, delayed errors, and many TPI state transitions. `SOLOCKED` serializes whole-socket control operations; `SOREADLOCKED` serializes receive paths, especially urgent-data and mark handling. `sti_plumb_lock` serializes stream plumbing ioctls so the virtual `sockmod` state and actual module stack do not diverge.

The file carefully drops `so_lock` around blocking STREAMS operations such as `kstrputmsg`, `strioctl`, `strclose`, and memory allocation, then revalidates or restores state afterward. AF_UNIX bound pathname sockets maintain a cross-link between the filesystem vnode and socket stream via `sti_ux_bound_vp` and `v_stream`; close/unbind paths must tear that down before the stream head disappears.

## Filesystem Relevance
AF_UNIX bind creates an underlying filesystem `VSOCK` vnode for pathname sockets and stores it in `sti_ux_bound_vp`. The file also maintains sockfs vnode stream state, exposes socket-specific `stat` timestamps through `sotpi_info_t`, and supports sendfile through kernel mblk writes. It is the main bridge between the VFS-visible socket vnode and TPI/STREAMS transport providers.

## Edge Cases and Risks
The code is state-machine heavy. Small changes can break socket compatibility around implicit bind, listen rebinding, nonblocking connect, datagram reconnect/unconnect, shutdown half-close behavior, `SO_DGRAM_ERRIND`, `MSG_WAITALL`, and urgent-data marks. AF_UNIX address translation is particularly subtle because external pathname addresses and internal transport vnode-addresses coexist, with `sti_faddr_noxlate` changing behavior across connect, accept, close, send, and getpeername. Direct TCP/UDP fast paths must preserve STREAMS error, flow-control, auditing, and partial-write semantics when falling back.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socktpi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socktpi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socktpi.h

## Purpose
Defines the TPI-specific private state stored behind `sonode.so_priv` and declares the public-internal TPI socket entry points used by sockfs and related modules.

## Key Elements
`struct soaddr` wraps cached socket addresses with allocated length metadata. `sotpi_info_t` stores the TPI socket state: transport device, original sockparams for fallback, plumbing lock, ack CV, cached local/foreign addresses, TPI provider capabilities, preallocated unbind message, pending ack and disconnect messages, connection indication queue, delayed datagram errors, timestamps, urgent-data counters, direct-call state, and AF_UNIX pathname/internal address state.

The header documents AF_UNIX pathname socket binding: sockfs creates a `VSOCK` vnode in the underlying filesystem while using `v_stream` linkage to find the bound socket. It also documents urgent-data handling through `sti_oobcnt`, `sti_oobsigcnt`, `T_EXDATA_IND`, `MSGMARK`, `MSGMARKNEXT`, `MSGNOTMARKNEXT`, and stream-head mark flags.

## Dependencies
Depends on socket, TPI, STREAMS, and sockfs types such as `sonode`, `sockparams`, `mblk_t`, `t_uscalar_t`, `T_capability_ack`, and `so_ux_addr`.

## Behavior/Risks
This header is the internal contract for TPI sockets. Field validity bits drive `getsockname`/`getpeername` caching, AF_UNIX translation, fallback conversion, and direct transport calls. The urgent-data comments describe behavior that must remain consistent with `strsock_proto`, stream-head mark handling, `sotpi_recvmsg`, `SIOCATMARK`, and poll/select behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socktpi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socktpi_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socktpi_impl.h

## Purpose
Provides private implementation declarations for TPI sockfs code and defines the combined allocation object used by normal TPI sockets.

## Key Elements
Defines `sotpi_sonode_t`, embedding a generic `sonode` plus a `sotpi_info_t`; its `so_priv` always points to the embedded `st_info`. Declares internal helpers for TPI capability processing, stream initialization, address allocation and validation, AF_UNIX address translation, stream/socket conversion, ack and connection indication queuing, disconnect indication flushing, protocol mblk allocation, async signal ownership, hook installation, direct send paths, and datagram/service send helpers.

## Dependencies
Includes `sys/socketvar.h` and `fs/sockfs/socktpi.h`, then exposes functions implemented across `socktpi.c` and other sockfs support files.

## Behavior/Risks
This is private linkage glue. The declarations encode locking and ownership assumptions that are visible only in implementations: ack/connection queues are mblk-owned, stream/socket conversion changes observable ioctl behavior, and direct send helpers assume socket state checks were already performed by callers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socktpi_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockvfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockvfsops.c

## Purpose
Provides the loadable filesystem module wrapper and minimal VFS operation support for `sockfs`.

## Key Elements
Registers `sockfs` through a `vfsdef_t` whose init function is `sockinit` and whose flags include `VSW_ZMOUNT`. `_init` creates a zone key so sockfs per-zone kstats are initialized and finalized for every zone, then installs the filesystem module. If module installation fails, the zone key is deleted. `_info` delegates to `mod_info`. `_fini` always returns `EBUSY`; sockfs is not unloadable.

`sockfs_statvfs` fills a token `statvfs64` response: zeroes the structure, sets `f_bsize` to `PAGESIZE`, derives `f_fsid` from `vfs_dev`, and sets `f_basetype` to `sockfs`.

## Dependencies
Uses illumos module, VFS, vnode, STREAMS, socket, zone, and kstat hooks. The real sockfs initialization is supplied by `sockinit` elsewhere.

## Behavior/Risks
This file intentionally exposes little filesystem capacity information. Module unload is disabled, so any future unload support would need to add real cleanup for the zone key and sockfs global state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockvfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sodirect.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sodirect.c

## Purpose
Implements sockfs receive-side support for asynchronous direct copyout using `uioa_t`, intended for DMA-assisted copy hardware such as Intel I/OAT.

## Key Elements
`sod_rcv_init` is called at the start of `recvmsg`. It enables `uioa_t` use only for sufficiently large receives, enabled sodirect sockets, global `uioasync` enablement, non-`MSG_PEEK`, non-loopback, no active socket filters, and non-EOF receive state. On success it replaces the caller's `uio_t` with the embedded `sod_uioa`.

`sod_rcv_done` finalizes async copyout with `uioafini`, restores the original `uio_t`, and frees any mblk chains accumulated on the sodirect pending-free list.

`sod_uioa_mblk_init` schedules async copyout for newly enqueued `M_DATA` mblk chains while `UIOA_ENABLED` is set, marks data blocks with `DBLK_UIOA`, and switches to `UIOA_FINI` if the chain no longer fits or scheduling fails. `sod_uioa_so_init` scans already queued socket receive data and the dump area when transitioning into enabled state, scheduling eligible data and splitting mblk chains when async processing must stop.

`sod_uioa_mblk_done` moves already-copied `DBLK_UIOA` chains to the pending-free list, advances their read pointers to write pointers, and flips the uioa state to finalization. `sod_uioa_mblk` removes eligible queued copied data from socket receive queues, completes it, verifies no copied blocks remain queued in debug builds, and returns copied byte count.

`sod_sock_init`, `sod_sock_fini`, and `sod_init` manage per-socket `sodirect_t` allocation from the `sock_sod_cache`.

## Concurrency and Lifetime
Most queue manipulation requires `so_lock`. The async state lives in `so->so_direct` and must not be freed while copied mblk chains remain on `sod_uioafh`. The code relies on `DBLK_UIOA` marking to distinguish data already copied to user buffers from data still requiring normal socket receive processing.

## Edge Cases and Risks
The mblk chain splitting and receive-queue relinking are fragile: incorrect `b_next`, `b_prev`, or `b_cont` updates would corrupt socket receive queues. Async copyout is deliberately disabled for peeks, loopback, filters, EOF, insufficient receive size, out-of-band mark crossings, and overflow of the target uio. The code must preserve the invariant that `DBLK_UIOA` data is not later delivered through normal receive copy paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sodirect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sodirect.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sodirect.h

## Purpose
Defines the per-socket sodirect state and declares the async direct-copy receive helpers used by sockfs.

## Key Elements
`sodirect_t` contains an enable flag, a pending-free mblk chain head and tail, and an embedded `uioa_t` for active async copyout state. Macros include `SOD_DISABLE`, `SOD_SOTOSODP`, and `SOD_UIOAFINI`, which flips an enabled uioa state to finalization.

The header declares setup/teardown (`sod_init`, `sod_sock_init`, `sod_sock_fini`), receive lifecycle (`sod_rcv_init`, `sod_rcv_done`), and mblk scheduling/completion helpers (`sod_uioa_mblk_init`, `sod_uioa_so_init`, `sod_uioa_mblk`, `sod_uioa_mblk_done`).

## Dependencies
Depends on `sonode`, `mblk_t`, `uio_t`, and `uioa_t` definitions from the socket/STREAMS/uio layers.

## Behavior/Risks
The macros directly mutate state and assume callers already hold the right socket locks or are in a safe receive path. Misuse can leave async copyout enabled after the receive path has decided to finalize, causing copied mblks to be handled twice or leaked.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sodirect.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/specfs/specsubr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/specfs/specsubr.c

## Purpose
Implements core specfs special-vnode support: snode creation, common vnode lookup, device vnode association, snode hash management, device fencing, initialization, and special-device close helpers.

## Key Responsibilities
- `specvp` returns a shadow special vnode for a real device vnode, reusing an existing snode keyed by device/type/real vnode or creating a new one. FIFOs are redirected to `fifovp`.
- `specvp_devfs` wraps `specvp` and associates the common snode with a devinfo node.
- `makespecvp` creates a special vnode without a real vnode, commonly for device-oriented synthetic opens.
- `commonvp` and `get_cvp` return the common vnode shared by all snodes for the same block/character device.
- `sfind`, `sinsert`, and `sdelete` maintain the global `stable` hash table protected by `stable_lock`.
- `spec_assoc_vp_with_devi`, `spec_hold_devi_by_vp`, `devi_stillreferenced`, and `spec_devi_open_count` manage devinfo association, holds, and open/reference accounting.
- `spec_assoc_fence`, `spec_fence_snode`, and `spec_unfence_snode` set or clear `SFENCED` on common snodes when device instances are retired or restored.
- `common_specvp`, `specfind`, `spec_snode_walk`, `spec_is_clone`, `spec_is_selfclone`, and `spec_size_invalidate` provide lookup, iteration, clone-state, and cached-size invalidation helpers.
- `smark` updates snode access/modify/change timestamps and flags.
- `spec_maxoffset` computes maximum allowed offsets based on stream state and device 64-bit capability flags.
- `specinit` installs VFS/vnode ops, initializes locks, creates the snode kmem cache, initializes `spec_vfs`, and allocates a synthetic filesystem device id.
- `device_close` closes character or block devices, including stream close for character streams and block-cache invalidation on last close.
- `makectty` creates a character special vnode for a controlling terminal and increments the common snode open count.

## Concurrency and Lifetime
The global `stable_lock` protects the snode hash table. Each snode has `s_lock` and `s_cv` for per-snode state. Snode constructors allocate embedded vnodes and install specfs vnode ops. Shadow snodes hold their real vnode and VFS; common snodes are self-referential through `s_commonvp`. `spec_assoc_vp_with_devi` transfers devinfo holds from old to new associations and invalidates cached size when the associated device changes.

## Filesystem Relevance
Specfs is the VFS layer that represents character and block devices as vnodes. It bridges real filesystem device nodes, devfs-attached instances, common device identity, stream state, buffer-cache invalidation, page writeback, vnode path copying, and visibility checks for zones.

## Edge Cases and Risks
The common-vnode model is central: confusing shadow snodes with common snodes can corrupt open counts, device association, stream pointers, or cached size. `specvp` preallocates snodes before locking to avoid blocking under `stable_lock`; that pattern must be preserved. Devinfo fencing depends on retirement flags and common snode association. `spec_size_invalidate` obtains a held common snode through `sfind` and releases it asynchronously after clearing `SSIZEVALID`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/specfs/specsubr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/specfs/specvfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/specfs/specvfsops.c

## Purpose
Provides the loadable filesystem module wrapper and VFS sync operation for `specfs`.

## Key Elements
Registers `specfs` through a `vfsdef_t` whose init function is `specinit` and whose flags include `VSW_ZMOUNT`. `_init` installs the filesystem module, `_info` delegates to `mod_info`, and there is no unload path.

`spec_sync` serializes sync work with `spec_syncbusy`, ignores `SYNC_ATTR`, scans all snodes in the global `stable` table, skips virtual swap vnodes, and collects block-device vnodes with cached data. It holds each vnode before dropping `stable_lock`, then asynchronously writes pages with `VOP_PUTPAGE(..., B_ASYNC, ...)` and releases the hold.

## Dependencies
Depends on specfs globals from `specsubr.c`, including `stable`, `STABLESIZE`, `stable_lock`, `specinit`, and snode/vnode helpers. Uses VFS module registration, vnode cached-data checks, swap-vnode checks, and `VOP_PUTPAGE`.

## Behavior/Risks
The sync path avoids holding `stable_lock` during page writeback by first building a held temporary list through `s_list`. It is intentionally best-effort and returns immediately if another specfs sync is already active. Correct vnode holds are required so snodes do not disappear between the hash scan and asynchronous putpage calls.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/specfs/specvfsops.c -->