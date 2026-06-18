# Group Research: group_315_dragonflybsd_sources_os_bsd_dragonflybsd_sys_sys_mouse_h_sources_os__82cbf42fe454

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/dragonflybsd`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mouse.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/mouse.h

Public mouse ioctl and packet-format interface for DragonFlyBSD mouse, sysmouse, PS/2, serial, USB, and touchpad consumers.

Key responsibilities:
- Defines userland-visible mouse ioctls: `MOUSE_GETSTATUS`, `MOUSE_GETHWINFO`, `MOUSE_GETMODE`, `MOUSE_SETMODE`, `MOUSE_GETLEVEL`, `MOUSE_SETLEVEL`, `MOUSE_READSTATE`, `MOUSE_READDATA`, and Synaptics hardware info query.
- Defines status, hardware, Synaptics capability, mode, and data-buffer structures.
- Enumerates button bitmasks through 31 buttons and state-change flags.
- Defines interface, device type, model, protocol, resolution, packet size, sync mask, and button-bit constants for many legacy and modern mouse protocols.
- Documents `/dev/sysmouse` level-0 and level-1 packet layout and remote socket path `_PATH_MOUSEREMOTE`.

Important behavior:
- This header is ABI material: ioctl numbers and structure layouts are consumed by drivers and userland tools.
- `mousestatus_t` reports deltas and button transitions; `mousemode_t` describes report protocol framing.
- Protocol definitions cover Microsoft serial, Mouse Systems, MM series, PS/2, IntelliMouse, Explorer, VersaPad, A4 Tech 4D, Synaptics, Elantech, and sysmouse.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.
- Used by mouse drivers, console/sysmouse layers, and userland programs that inspect or configure pointer devices.

Notable risks:
- Many constants encode hardware packet bits directly; mistakes break driver decoding or userland compatibility.
- `synapticshw_t` is a large flat capability ABI with no explicit version field.
- Several legacy protocols have inverted button semantics, especially Mouse Systems/sysmouse `UP` bits.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mouse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mpipe.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/mpipe.h

Kernel-only pipelined fixed-size allocation facility with optional persistent cached object state.

Key responsibilities:
- Defines `struct malloc_pipe`, which manages a bounded cache/array of fixed-size allocations with an LWKT token and callback queue.
- Exposes `mpipe_init`, `mpipe_done`, waitable/non-waitable allocation, callback allocation, wait, and free APIs.
- Supports constructor and deconstructor hooks plus caller-private data.
- Defines flags controlling zeroing, cached data lifetime, interrupt reserve use, queue waiting, callback mode, and teardown.

Important behavior:
- Intended to allow blocking allocations while avoiding allocation deadlocks by maintaining a preallocated nominal pool.
- New buffers are zeroed by default.
- `MPF_CACHEDATA` preserves reused buffer contents and delays deconstruction until physical free.
- `MPF_NOZERO` disables zeroing for newly allocated buffers and cache reuses.

Dependencies:
- Kernel-only; rejects userland inclusion.
- Includes `_malloc.h`, `thread.h`, and `queue.h`.
- Uses `malloc_type_t`, `struct lwkt_token`, `struct thread`, and `STAILQ`.

Notable risks:
- Cached-data mode requires callers to tolerate stale contents.
- Callback allocations imply asynchronous control flow and valid callback arguments until completion.
- Pool sizing fields (`ary_count`, `max_count`, `free_count`, `total_count`) are correctness-critical for deadlock avoidance.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mpipe.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mplock2.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/mplock2.h

Inline macro wrapper for DragonFlyBSD's legacy MP lock, implemented as an LWKT token.

Key responsibilities:
- Maps MP lock operations to `mp_token` token operations:
  - `get_mplock()`
  - `try_mplock()`
  - `rel_mplock()`
  - `get_mplock_count(td)`
- Declares `cpu_get_initial_mplock()`.
- Provides `MP_LOCK_HELD()` and `ASSERT_MP_LOCK_HELD()` helpers.

Important behavior:
- `try_mplock()` returns non-zero on success, matching `lwkt_trytoken()`.
- The lock is represented as exclusive ownership of `mp_token`.

Dependencies:
- Includes machine atomic operations, `thread.h`, and `globaldata.h`.
- Depends on LWKT token APIs/macros and global `mp_token`.

Notable risks:
- This is a compatibility synchronization boundary; callers must understand whether their subsystem is still MP-lock protected or independently MPSAFE.
- Misinterpreting the success convention of `try_mplock()` can invert lock handling.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mplock2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mpt_ioctl.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/mpt_ioctl.h

Userland ioctl ABI for LSI MPT-Fusion host adapter configuration and RAID actions.

Key responsibilities:
- Defines configuration page request structures for normal and extended MPI config pages.
- Defines `struct mpt_raid_action` for RAID action commands and returned status/data.
- Defines ioctl numbers for reading config headers/pages, reading extended config headers/pages, writing config pages, and issuing RAID actions.
- Provides 32-bit compatibility request structures and ioctl aliases on `__x86_64__`.

Important behavior:
- Header requests use the `header` fields to specify page type/version/number; buffer and length are unused.
- Page read/write requests expect `buf` and `len` to describe the whole page including header.
- All requests carry `page_address` and return IOC status.

Dependencies:
- Includes `sys/ioccom.h`.
- Depends on MPT MPI headers under `dev/disk/mpt/mpilib/`.

Notable risks:
- User pointers are embedded directly in ABI structures; compat structures are required for 32-bit callers on 64-bit kernels.
- ioctl command numbers are shared between native and compat variants, so dispatch code must select the correct layout by caller ABI.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mpt_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mqueue.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/mqueue.h

POSIX message queue public and kernel-internal definitions.

Key responsibilities:
- Defines `MQ_OPEN_MAX`, `MQ_PRIO_MAX`, `mqd_t`, and public `struct mq_attr`.
- Defines kernel-only internal queue flags, name length, default message size, priority queue sizing, and reserved queue index.
- Defines `struct mqueue` with name, lock, sleep channels, attributes, kqueue notification state, signal notification, permissions, refcount, priority queue heads, bitmap, global list entry, and timestamps.
- Defines variable-length `struct mq_msg`.
- Declares kernel initialization and send/receive helper APIs.

Important behavior:
- Internal flags use high bits in `mq_flags`, which the comment notes is POSIX-appropriate.
- Queues use 32 fixed priority queues plus a reserved linear-insertion queue if the priority maximum is expanded.
- Kqueue and signal notification state is embedded directly in each queue.

Dependencies:
- Kernel structures depend on `types.h`, `lock.h`, `queue.h`, `event.h`, and `signal.h`.
- Kernel APIs use `struct lwp`, `mqd_t`, `timespec`, and message buffers.

Notable risks:
- `mq_msg` uses a one-byte flexible tail idiom, so allocation sizing must include payload length.
- Priority bitmap and queue indexing must stay in sync with `MQ_PQSIZE` and `MQ_PRIO_MAX`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mqueue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/msg.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/msg.h

System V message queue ABI header.

Key responsibilities:
- Defines `MSG_NOERROR`, `msglen_t`, `msgqnum_t`, and required scalar typedef guards.
- Defines public `struct msqid_ds` for queue permissions, first/last message links, byte/message counts, limits, sender/receiver PIDs, and timestamps.
- Defines BSD-visible example `struct mymsg` with message type and one-byte body placeholder.
- Defines kernel-visible `struct msginfo` tunables.
- Declares userland `msgctl`, `msgget`, `msgsnd`, and `msgrcv`, or kernel `msginfo`.

Important behavior:
- Comments note kernel and userland implementations historically differ in how message links are interpreted.
- `msgrcv` is declared as returning `int` with an XXX note that it should return `ssize_t`.

Dependencies:
- Includes `sys/cdefs.h`, `sys/ipc.h`, and `machine/stdint.h`.

Notable risks:
- `struct msqid_ds` layout is ABI-sensitive for SysV IPC tools and libc.
- The historical `msgrcv` return type mismatch is compatibility-sensitive.
- Pointer fields in `msqid_ds` are not meaningful as stable userland object references.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/msg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/msgbuf.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/msgbuf.h

Kernel message buffer ring metadata for console/log output.

Key responsibilities:
- Defines `struct msgbuf` with magic, buffer size, write/base/read indices, backing pointer, and reserved field.
- Defines current and old magic constants: `MSG_MAGIC` and `MSG_OMAGIC`.
- Declares kernel globals `msgbuftrigger` and `msgbufp`.
- Declares `msgbufinit()`.
- Provides default `MSGBUF_SIZE` of 1 MiB if not configured.

Important behavior:
- Indices are not masked when stored; accessors must mask against `msg_size` to get physical buffer offsets.
- Unsigned arithmetic allows relative distance calculation by subtraction.

Dependencies:
- Includes `sys/types.h`.
- Kernel consumers are console/logging and message-buffer initialization code.

Notable risks:
- Any accessor that forgets to mask indices can address outside the ring.
- Ring index wraparound assumptions depend on unsigned integer behavior.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/msgbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/msgport.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/msgport.h

Core LWKT message and port interface for intra-kernel thread communication.

Key responsibilities:
- Defines opaque pointer typedefs `lwkt_msg_t` and `lwkt_port_t`.
- Defines `lwkt_msg_queue` as a TAILQ of messages.
- Defines `struct lwkt_msg` with queue linkage, target/reply ports, abort handler, flags, error, result union, and receipt callback.
- Defines message state flags: done, reply, queued, sync, in-transit, waiting, droppable, abortable, priority, receipt, and user command bits.
- Defines `struct lwkt_port` with normal/priority queues, flags, CPU id, synchronization union, owning thread, and port operation callbacks.
- Declares kernel port initialization and message send/forward/abort APIs.

Important behavior:
- Message ownership is explicit: only the current owner should manipulate a message.
- Synchronous messages may wake waiters directly instead of being queued on reply.
- Thread ports and spin/descriptor ports use different fields in the port union and have different ownership expectations.
- High 16 message-flag bits are available to handlers and also define CDEV/VFS/SYSCALL command namespaces.

Dependencies:
- Includes `queue.h`, `spinlock.h`, and machine integer types.
- Kernel section depends on `boolean_t`, `struct thread`, `struct spinlock`, and `struct lwkt_serialize`.

Notable risks:
- Port callbacks define the semantics; incorrect `mp_putport`, `mp_replyport`, or `mp_dropmsg` implementations can break sync/async completion.
- Message flags are manipulated by owners only; cross-owner mutation is a race.
- Dropping is only supported by certain embedded/thread ports and must be done in the port owner thread.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/msgport.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/msgport2.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/msgport2.h

Kernel inline helpers for LWKT message and port operations.

Key responsibilities:
- Declares `M_LWKTMSG` malloc type when `MALLOC_DECLARE` is available.
- Provides inline message initialization helpers:
  - `lwkt_initmsg`
  - `lwkt_initmsg_abortable`
- Provides inline wrappers for reply, get, wait, check, drop, and receipt setup operations.
- Routes operations through the target/reply port callback table.

Important behavior:
- `lwkt_initmsg()` does not zero the whole message; it only initializes flags and reply port.
- Initialized messages are marked `MSGF_DONE` until sent.
- `lwkt_dropmsg()` asserts `MSGF_DROPABLE`, then calls the current target port's drop hook if present.
- `lwkt_setmsg_receipt()` sets `MSGF_RECEIPT` and stores a callback.

Dependencies:
- Kernel-only; rejects userland inclusion.
- Includes `sys/systm.h`.
- Requires `msgport.h` definitions and error constants such as `ENOENT`.

Notable risks:
- Because initialization is partial, stale fields must be initialized by callers before use.
- Replying assumes `ms_reply_port` is valid and has a correct `mp_replyport` method.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/msgport2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mtio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/mtio.h

Magnetic tape ioctl ABI and status definitions.

Key responsibilities:
- Defines `struct mtop` for tape operation commands and repeat counts.
- Enumerates tape operations such as write EOF, file/record spacing, rewind, offline, cache control, block size, density, erase, EOD, compression, retension, and setmark operations.
- Defines DragonFly-specific compression status constants and drive-state `mt_dsreg` values.
- Defines `struct mtget` for tape status, position, density, block size, compression, and mode-specific settings.
- Defines SCSI tape error status structures and reserved union padding.
- Enumerates legacy tape controller/device type constants.
- Defines tape ioctls for operations, status, logical/hardware position, locate, error stats, and EOT model control.
- Defines default tape path for userland and kernel minor-device bit masks.

Important behavior:
- `MTIOCERRSTAT` returns latched SCSI sense data and clears it.
- `mt_resid` is noted as potentially nonsensical for large residuals; detailed residuals are available through error status.
- DragonFly extends the historical BSD tape ABI with block size, density, compression, and state fields.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

Notable risks:
- Structure layout and ioctl numbers are userland ABI.
- Some fields are reserved or explicitly not implemented but preserved for compatibility.
- Older 32-bit residual fields are inadequate for large tape I/O.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mtio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mutex.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/mutex.h

Core DragonFlyBSD mutex structure and non-inline backend declarations.

Key responsibilities:
- Defines `struct mtx_link` for linked/asynchronous mutex acquisition requests with owner, state, callback, and argument.
- Defines cache-aligned `struct mtx` with lock word, flags, exclusive/shared wait links, owner, and identifier.
- Defines initializer macro and lock-state bit layout:
  - `MTX_EXCLUSIVE`
  - shared/exclusive wanted bits
  - link spin bit
  - recursive/shared count mask
- Defines owner sentinel values and link state constants.
- Declares backend functions used by inline wrappers in `mutex2.h`.

Important behavior:
- The mutex supports recursive shared and exclusive locking, downgrade, non-blocking upgrade, blocking and spin forms, and asynchronous link-based acquisition.
- The lock word combines ownership mode, waiter bits, internal spin state, and reference count.
- `MTXF_NOCOLLSTATS` disables collision statistics where not applicable.

Dependencies:
- Kernel/kernel-structures only for structure definitions.
- Includes `types.h`, machine atomics, and CPU functions.
- Backend declarations are kernel-only.

Notable risks:
- Lock word bit layout is tightly coupled to `mutex2.h` fast paths and implementation functions.
- Link state and callback lifetime must be correct for asynchronous/abortable use.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mutex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mutex2.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/mutex2.h

Inline fast paths and utility functions for DragonFlyBSD mutexes.

Key responsibilities:
- Provides initialization and deinitialization helpers for mutexes and mutex links.
- Provides exclusive/shared lock operations with optional link, timeout, quick, try, and recursion support.
- Provides exclusive spinlock/spinunlock helpers that enter and exit hard critical sections and update per-CPU spinlock counts.
- Provides downgrade and upgrade-try helpers.
- Provides unlock variants for generic, exclusive, and shared releases.
- Provides lock-state predicates, owner predicates, lock reference count, and temporary release/restore helpers.

Important behavior:
- Fast paths use `atomic_cmpset_int()` for uncontended acquisition and release.
- Exclusive locks set `mtx_owner` to `curthread`; shared locks do not.
- Spinlocking enters a critical section before attempting acquisition and must be paired with `mtx_spinunlock()`.
- Unlock handles exclusive, shared, blocking, and spin-acquired mutexes via the same lock word and slow-path fallback.
- `mtx_lock_temp_release()` records only whether the prior state was exclusive, then unlocks and later restores exclusive or shared mode.

Dependencies:
- Includes `mutex.h`, `thread2.h`, `globaldata.h`, and machine atomics.
- Depends on `curthread`, `mycpu`, critical-section helpers, CPU fences, `KKASSERT`, and slow-path `_mtx_*` functions.

Notable risks:
- Correct pairing of spinlock/spinunlock is required to balance critical sections and `gd_spinlocks`.
- `mtx_notlocked_ex()` returns `(mtx_lock & MTX_EXCLUSIVE) != 0`, which contradicts its comment saying it returns true if not exclusively locked.
- Temporary release/restore only restores mode, not recursion depth.
- Atomic fast paths and owner updates must remain ordered with backend slow paths.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/mutex2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/namecache.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/namecache.h

DragonFlyBSD namecache and namecache-handle interface for filesystem namespace management.

Key responsibilities:
- Defines `struct namecache` for cached namespace entries, child/parent topology, vnode association, hash linkage, mount generation, generation tracking, references, timeout, flags, and lock.
- Defines `struct nchandle`, pairing a namecache pointer with a mount reference for overlay-aware path topology.
- Defines namecache flags for unresolved, whiteout, mount point, cache/no-cache chflags, symlink, directory, destroyed, deferred zap, world-searchable shortcut, and dummy nodes.
- Defines cache invalidation flags.
- Declares kernel APIs for locking, lookup, mount-point handling, invalidation, resolution, reference/copy/drop, rename/unlink, vnode conversion, full path construction, root setup, and per-CPU rollup.

Important behavior:
- DragonFly maintains namecache topology from active nodes to root except for NFS server and removed-file cases.
- Multiple namecache entries may pass through one vnode due to mount overlays, nullfs, union mounts, and mount crossings.
- Namespace locking must be performed on the cache record whose parent represents the physical directory for the operation.
- Generation changes are bracketed so unlocked accessors can detect concurrent changes and retry.

Dependencies:
- Includes `types.h`, `lock.h`, `queue.h`, and `spinlock.h`.
- Kernel APIs depend on vnodes, mounts, credentials, component/nlookup data, processes, and globaldata.

Notable risks:
- Namecache/vnode/mount topology is subtle; using the wrong `nchandle` across overlays can lock or operate on the wrong namespace.
- Generation and reference protocols must be followed to avoid stale unlocked lookups.
- Negative entries, whiteouts, destroyed entries, and unresolved entries have distinct semantics.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/namecache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/namei.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/namei.h

Legacy namei component lookup definitions retained for VOP lookup compatibility.

Key responsibilities:
- Defines `struct componentname`, carrying operation, flags, thread, credentials, component pointer/length, consumed characters, cache timeout, and NFS collision vnode.
- Defines kernel namei operation constants for lookup, create, delete, and rename.
- Defines selected component-name flags for parent locking, following symlinks, read-only semantics, NFS `notvp` check, dot-dot, whiteouts, parent unlock, and cache timeout.
- Defines modifier and parameter masks.
- Declares `varsym_enable` and `relookup()`.

Important behavior:
- Many historical flags are commented out, suggesting DragonFly has shifted much path walking into `nlookup`/namecache while preserving selected VOP-facing bits.
- `componentname` is shared between lookup and commit routines.

Dependencies:
- Includes `queue.h`.
- Kernel includes `thread.h`, `proc.h`, and `nchstats.h`.

Notable risks:
- This header is an interop layer with legacy VFS lookup contracts; flag compatibility matters.
- Comments and masks include holes for removed/unused flags, so adding new bits requires care.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/namei.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/nata.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/nata.h

ATA/ATAPI parameter, command, sense, ioctl, and RAID control ABI.

Key responsibilities:
- Defines packed `struct ata_params`, matching the ATA IDENTIFY DEVICE word layout through word 255.
- Defines ATA protocol, ATAPI type, DRQ, capability, validity, SATA, command support/enabled, UDMA, cable, acoustic, queue, and size-related bit constants.
- Defines ATA transfer mode constants for PIO, WDMA, UDMA, SATA, and USB modes.
- Defines ATA and ATAPI command opcodes and subfeature constants.
- Defines channel/device ioctl structures and ioctls.
- Defines packed ATAPI request sense structure and sense-key constants.
- Defines `struct ata_ioc_request` for raw ATA/ATAPI requests.
- Defines device ioctls for raw request, parameter retrieval, mode get/set, and spindown get/set.
- Defines ATA RAID config/status structures, RAID type/status/disk flags, and RAID management ioctls.

Important behavior:
- The identify structure is packed and laid out by ATA word numbers; comments annotate word offsets.
- Raw requests support both ATA register-style command fields and ATAPI CCB/sense data.
- RAID ioctl structures use fixed arrays of 16 disks.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

Notable risks:
- `struct ata_params` is hardware/ABI layout; alignment or packing changes would break parsing.
- Userland raw ATA ioctls pass data pointers and command flags, so kernel validation is critical.
- Several sense bit macros include trailing semicolons in their definitions, which can surprise expression-style macro use.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/nata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/nchstats.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/nchstats.h

Per-CPU namecache statistics structure.

Key responsibilities:
- Defines cache-aligned `struct nchstats`.
- Tracks good hits, negative hits, bad hits, false hits, misses, long path hits/misses, and unused attempts.

Important behavior:
- Intended to be allocated in per-CPU arrays, hence explicit cache alignment.
- Separates useful positive/negative hits from stale/bad/false hits.

Dependencies:
- Consumed by namecache/namei implementation and sysctl/stat reporting paths.

Notable risks:
- Counters are unsigned long and per-CPU; aggregation code must handle CPU-local arrays.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/nchstats.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/nlookup.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/nlookup.h

DragonFlyBSD namecache-based path lookup state and API.

Key responsibilities:
- Defines `struct nlcomponent` for a path component pointer and length.
- Defines `struct nlookupdata`, which encapsulates lookup result, base/root/jail namecache handles, path buffer, thread, credentials, directory vnode, flags, symlink loop count, directory error, iteration number, and `vn_open()` result state.
- Defines nlookup flags controlling symlink following, mount crossing, buffer ownership, whiteout/directory state, locks, open/create/delete/rename/truncate/hardlink checks, NFS behavior, shared locking, access bits, credential borrowing, sticky/append-only/immutable/writable indicators, and vnode return behavior.
- Defines masks for all permission checks and modifying operations.
- Declares kernel nlookup initialization, cleanup, path walk, simple lookup, mount lookup, symlink read, zeroing, and access-check APIs.

Important behavior:
- `nl_op`-style operation semantics are replaced by flags; operation bits are used for access checks and do not themselves modify the returned namecache.
- `vn_open()` may populate `nl_open_vp`, and `nlookup_done()` will close it unless the caller extracts and nulls it.
- `NLC_HASBUF` marks path buffer ownership.
- `NLC_BORROWCRED` marks borrowed credential references.

Dependencies:
- Includes `namecache.h` and `file.h`.
- Kernel section includes `_uio.h` and uses vnodes, mounts, credentials, threads, and attributes.

Notable risks:
- Cleanup ownership is easy to get wrong, especially for `nl_path`, `nl_cred`, `nl_dvp`, and `nl_open_vp`.
- Access-check flags and modifying-operation flags are separate from actual mutation; callers must use `vn_open()`/VOPs for changes.
- Symlink loop handling depends on `nl_loopcnt`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/nlookup.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/objcache.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/objcache.h

Kernel object cache allocator interface with pluggable backing allocator and statistics ABI.

Key responsibilities:
- Defines object constructor, destructor, allocation, and free function pointer types.
- Declares object cache creation helpers for generic, simple malloc-backed, and configurable malloc-backed caches.
- Declares APIs to set cluster limits, get/put objects, run destructor, prepopulate from a linear object area, reclaim cache lists, and destroy caches.
- Defines common malloc-backed allocator argument structure.
- Declares malloc, zeroing malloc, and no-op backing alloc/free helpers.
- Defines stats constants and public `struct objcache_stats`.

Important behavior:
- `OC_MFLAGS` reserves low bits for malloc-style flags.
- Constructors return `bool`, allowing acquisition failure or rejection.
- `OBJCACHE_UNLIMITED` is represented as a high sentinel in stats limits.

Dependencies:
- Includes `sys/types.h`; kernel structures include `_malloc.h`.
- Kernel APIs depend on `malloc_type_t` and object-cache implementation.

Notable risks:
- Constructor/destructor semantics differ from backing allocator semantics; callers must know when object state is initialized or torn down.
- Stats structure is public/user-visible and includes reserved zero fields for future expansion.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/objcache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/param.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/param.h

Central machine-independent DragonFlyBSD system parameter header.

Key responsibilities:
- Defines historical BSD version macros and `__DragonFly_version` with an extensive version-change log, currently `600519`.
- Includes core type, limit, machine alignment, and machine parameter headers.
- Defines common limits: command name, interpreter, login name, process/file/group limits, hostname, device-name, block/path/symlink sizes, and allocation constants.
- Defines sleep/wakeup flags and wakeup domain/cpu encoding macros.
- Defines bitset, rounding, alignment, min/max, array-size, page rounding, fixed-point, device-block/page conversion, mbuf sizing, byte-order aliases, and variable-length array accessor macros.
- Declares `panic()` for kernel consumers.

Important behavior:
- `MAXBSIZE` is 64 KiB and must be a power of two.
- `MAXPATHLEN` maps to `PATH_MAX`; `MAXSYMLINKS` is 32.
- `PWAKEUP_CPUMASK` limits encoded wakeup CPU IDs and notes a maximum supported CPU count of 16384.
- `MINBUCKET` and `MAXALLOCSAVE` parameterize kernel allocator behavior.
- `MSIZE`, `MCLSHIFT`, and related constants describe mbuf and cluster sizing.

Dependencies:
- Public and kernel consumers include it widely.
- Pulls in `sys/_null.h`, `sys/types.h`, `sys/syslimits.h`, machine headers, and kernel-only `cdefs`, `errno`, and `time`.

Notable risks:
- This is extremely high blast-radius configuration; changing constants affects ABI, VFS, VM, networking, allocator, and userland build assumptions.
- Rounding macros may evaluate arguments multiple times.
- Version macro values gate ports and conditional compatibility code.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/param.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/paths.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/paths.h

Kernel/system internal path constant definitions.

Key responsibilities:
- Defines canonical system device paths for console, default tape, null, zero, drum, kmem, mem, tty, and `/dev/`.
- Provides `__SYS_PATH_DEV` with a trailing slash for pathname construction.

Important behavior:
- These are internal `__SYS_PATH_*` names, distinct from userland `_PATH_*` constants.

Dependencies:
- No includes beyond guard.

Notable risks:
- Constants are embedded string ABI assumptions for low-level system components.
- `__SYS_PATH_DEV` intentionally includes a trailing slash, unlike individual device paths.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/paths.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/pciio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/pciio.h

Userland ioctl ABI for PCI configuration enumeration and access.

Key responsibilities:
- Defines maximum PCI device name length.
- Defines `pci_getconf_status` and `pci_getconf_flags`.
- Defines `struct pcisel` for domain/bus/device/function selection.
- Defines `struct pci_conf` for PCI device identity, class, revision, driver name, and unit.
- Defines `struct pci_match_conf` and `struct pci_conf_io` for filtered enumeration.
- Defines `struct pci_io` for config register read/write and `struct pci_bar_io` for BAR info.
- Defines ioctl commands for getconf, config read/write, attached query, and BAR query.

Important behavior:
- PCI matching can filter by domain, bus, device, function, driver name/unit, vendor/device, and class.
- `pci_conf_io` supports generation and offset tracking for iterative enumeration and list-change detection.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

Notable risks:
- User pointers in enumeration structures require careful kernel copyin/copyout.
- PCI domain support is included in selectors and must be preserved for multi-domain systems.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/pciio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/pioctl.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/pioctl.h

procfs ioctl definitions for process stop/event control.

Key responsibilities:
- Defines `struct procfs_status` for process state, flags, event mask, stop reason, and extra value.
- Defines ioctls to set/clear event flags, set/get flags, wait for stop, continue process, and get status.
- Defines stop-event bits for exec, signal, syscall entry/exit, coredump, and exit.
- Defines procfs flags `PF_LINGER` and `PF_ISUGID`.

Important behavior:
- `PF_LINGER` keeps stop state around after the last close of `/proc/<pid>/mem`.
- Event stop flags are used by procfs tracing/debugging control paths.

Dependencies:
- Includes `sys/ioccom.h`.

Notable risks:
- Comments include historical typo-level text, but ioctl values and bit masks are ABI.
- Event-mask semantics overlap with process tracing behavior and must be coordinated with signal/ptrace/procfs code.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/pioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/pipe.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/pipe.h

Kernel pipe buffer and pipe endpoint structure definitions.

Key responsibilities:
- Defines `struct pipebuf`, with cache-aligned read and write substructures, locks, FIFO indices, blocking request markers, access/modify times, buffer size/pointer, VM object, kqueue info, async I/O state, state flags, and timestamp optimization field.
- Defines pipe state flags for async I/O, reader/writer wait, read EOF, write EOF, and closed.
- Defines `struct pipe`, containing two `pipebuf` endpoints, status-change time, list linkage, open count, inode number, and padding.

Important behavior:
- A pipe object encompasses two pipe buffers; bit 0 in `fp->f_data` identifies which side.
- Read and write metadata are cache-aligned separately to reduce contention.
- Pipe buffers are backed by VM objects and integrate with kqueue/select/poll and signal-driven I/O.

Dependencies:
- Kernel/kernel-structures only.
- Includes `types.h`, `time.h`, `event.h`, `xio.h`, `thread.h`, and machine `param.h`.

Notable risks:
- Endpoint selection by pointer low bit requires careful masking and alignment assumptions.
- Reader/writer locks and wait flags must be coordinated to avoid missed wakeups.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/pipe.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/poll.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/poll.h

Public `poll(2)` and BSD `ppoll(2)` interface definitions.

Key responsibilities:
- Defines `nfds_t`.
- Defines `struct pollfd`.
- Defines requestable poll event bits and always-returned event bits.
- Defines BSD-visible `POLLSTANDARD` and `INFTIM`.
- Declares userland `poll()` and BSD `ppoll()` when visibility macros allow.

Important behavior:
- `POLLWRNORM` aliases `POLLOUT`.
- Comments note limited traditional distinction between priority/band events.
- Kernel inclusion avoids userland function declarations.

Dependencies:
- Userland declarations include `sys/cdefs.h`, and BSD-visible declarations include `signal.h` and `time.h`.

Notable risks:
- Event bit values are cross-platform ABI.
- Visibility macros determine which prototypes/constants userland sees.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/poll.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/posix4.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/posix4.h

Kernel-only POSIX.1b/POSIX.4 scheduling support declarations.

Key responsibilities:
- Rejects userland inclusion.
- Includes `opt_posix.h` and `sys/sched.h`.
- Declares `M_P31B` malloc type and `p31b_setcfg()`.
- Under `_KPOSIX_PRIORITY_SCHEDULING`, defines scheduler operation enum and read/write access vector.
- Declares `struct ksched` lifecycle and operation functions for POSIX scheduling parameter, scheduler policy, yield, priority min/max, and round-robin interval operations.

Important behavior:
- `KSCHED_OP_RW` encodes which operations need write access.
- Scheduler APIs operate on `struct lwp` and return through `register_t *` where needed.

Dependencies:
- Kernel config option `_KPOSIX_PRIORITY_SCHEDULING`.
- Uses `struct proc`, `struct lwp`, `struct sched_param`, `timespec`, and `register_t`.

Notable risks:
- Behavior is compile-option dependent.
- Access-mode vector must remain synchronized with `enum ksched_op` order.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/posix4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/power.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/power.h

Power management type, command, sleep-state, and power-profile kernel API definitions.

Key responsibilities:
- Defines power management system types: APM, ACPI, and none.
- Defines suspend command and standby/suspend/hibernate sleep-state constants.
- Defines `power_pm_fn_t` callback type and kernel APIs to register a power manager, get type, and suspend.
- Defines performance/economy power profile constants and get/set APIs.
- Declares `power_profile_change` eventhandler hook.
- Provides inline `powerstate_to_str()` mapping numeric D-states to strings.

Important behavior:
- Kernel APIs are available only under `_KERNEL`, but `powerstate_to_str()` is outside that guard.
- `powerstate_to_str()` assumes `state` is a valid index 0-4.

Dependencies:
- Kernel section includes `types.h` and `eventhandler.h`.

Notable risks:
- `powerstate_to_str()` has no bounds check, so invalid states can read past the static string table.
- PM callback signature is variadic, requiring strict convention between caller and provider.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/power.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/proc.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/proc.h

Kernel process, LWP, process group, session, and process-management interface definitions.

Key responsibilities:
- Rejects direct userland inclusion; userland must include `sys/user.h`.
- Includes process dependencies for callouts, CPU masks, file descriptors, queues, trees, priorities, signals, locks, credentials, events, sysent, threads, scheduler, resources, machine proc state, and signal vars.
- Defines list and RB tree heads for processes, process groups, sessions, and LWPs.
- Defines `struct session`, `struct pgrp`, `struct pargs`, `struct lwp`, `struct proc`, and `struct procglob`.
- Defines process, LWP, and LWP MP-state flags.
- Defines macros for LWP iteration, single-LWP assertion, session leader, jail credential check, stop events, process/LWP holds, and process stall.
- Declares global process/thread roots and many kernel process lifecycle, lookup, group/session, scheduling, fork/exit, hold/release, user mapping, and reaper APIs.

Important behavior:
- `struct proc` contains shared process-wide state; `struct lwp` contains schedulable lightweight-process/thread-specific state.
- `p_startcopy`/`p_endcopy` and `lwp_startcopy`/`lwp_endcopy` mark fork-copy regions.
- Process lists are protected by `proc_token` inside `struct procglob`.
- `ONLY_LWP_IN_PROC()` panics if used on a multi-threaded process.
- `PHOLD/PRELE` and `LWPHOLD/LWPRELE` prevent destruction while other subsystems operate on objects.
- Reaper support is integrated through `p_reaper`, `p_deathsig`, and reaper APIs.

Dependencies:
- Kernel-only and kernel-structures consumers.
- Tightly coupled to scheduler, signal, VM, VFS/namecache, procfs, ptrace, jail, kqueue, sysent, and machine-dependent process code.

Notable risks:
- This is high-blast-radius kernel ABI/internal structure layout.
- Several fields are compatibility placeholders or deprecated markers; removing or reusing them affects kernel modules/crash tools.
- Process and LWP hold/lock/reference protocols are critical for ptrace, procfs, signals, and exit races.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/proc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/proc_common.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/proc_common.h

Shared process and LWP state enum definitions.

Key responsibilities:
- Defines `enum lwpstat` values:
  - `LSRUN`
  - `LSSTOP`
  - `LSSLEEP`
- Defines `enum procstat` values:
  - `SIDL`
  - `SACTIVE`
  - `SSTOP`
  - `SZOMB`
  - `SCORE`

Important behavior:
- Kept separate so process-state enums can be shared by process-related headers without pulling in full `proc.h`.

Dependencies:
- No includes beyond guard.

Notable risks:
- Numeric enum values are visible through kernel structure consumers and diagnostic tools.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/proc_common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/procctl.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/procctl.h

Process-control ABI for reapers, parent-death signals, and Solaris-compatible id types.

Key responsibilities:
- Defines `idtype_t` enum synchronized with Solaris values for process, parent PID, process group, session, class, UID, GID, all, LWP, task, project, pool, jail/zone, contract, CPU, and processor set identifiers.
- Defines reaper status, kill, and union information structures.
- Defines procctl command constants for acquiring/releasing reaper status, parent death signal control/status, and descendant kill.
- Defines reaper status and kill flags.
- Defines kernel `struct sysreaper` with lock, parent topology, owning process, flags, and references.
- Declares userland `procctl()`.

Important behavior:
- `_PROCCTL_PRESENT` advertises the interface.
- Reaper kill can target direct children only via `REAPER_KILL_CHILDREN`.
- Kernel structure exists only for kernel/kernel-structures builds.

Dependencies:
- Includes `sys/cdefs.h`.
- Kernel includes `sys/lock.h`; userland includes `sys/types.h`.

Notable risks:
- `idtype_t` numerical compatibility with Solaris/FreeBSD-style consumers is intentional.
- Reaper topology and refs must be maintained across process exit/reparenting.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/procctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/procfs.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/procfs.h

ELF core/procfs debugger structure definitions.

Key responsibilities:
- Includes `param.h` and machine-independent register wrapper `reg.h`.
- Typedefs general and floating-point register sets for procfs/core consumers.
- Defines versioned `prstatus_t` with sizes, OS release, current signal, PID, and general register set.
- Defines register-set aliases `prgregset_t` and `prfpregset_t`.
- Defines `prpsinfo_t` with version, size, command name, and saved argument bytes.
- Defines `psaddr_t`.

Important behavior:
- Comments explicitly state these structures must not remove/reorder fields; additions go at the end with version increments.
- Current versions are both 1.
- Provides the minimum needed for GDB ELF core dump support.

Dependencies:
- Depends on `MAXCOMLEN` from `param.h` and `struct reg`/`struct fpreg` from machine register headers.

Notable risks:
- This is debugger/core-file ABI; structure changes affect old core dump readability.
- Saved argument bytes are capped at `PRARGSZ` 80.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/procfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/protosw.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/protosw.h

Network protocol switch and protocol user-request interface definitions.

Key responsibilities:
- Defines `struct pr_output_info`.
- Defines kernel `netmsg_t` and `struct protosw`, containing protocol type/domain/number/flags, port selection, input/output/control hooks, initialization/drain hooks, and user-request table.
- Defines protocol timer constants and protocol flags for atomic/addressed messages, connection requirement, rights passing, implied open/close, MPSAFE state, sync port, and async send/receive/connect behavior.
- Defines `PRU_*` user-request operation numbers and optional debug name arrays.
- Defines `struct pru_attach_info` and `struct pr_usrreqs`, including netmsg-based protocol operations and synchronous send/receive/preconnect/preattach callbacks.
- Declares not-supported helpers, CPU0 port helpers, protocol-control command constants, ctloutput constants, and protocol lookup/control APIs.
- Defines `PR_GET_MPLOCK` and `PR_REL_MPLOCK` wrappers for non-MPSAFE protocols.

Important behavior:
- DragonFly routes many protocol operations through LWKT message ports and protocol threads.
- Some operations remain synchronous in user context, notably generic send/receive paths and preconnect/preattach.
- Non-MPSAFE protocol calls are wrapped in the MP lock.
- `pr_ctlport` and Toeplitz/netisr selection control protocol-thread placement.

Dependencies:
- Includes `sys/types.h`.
- Kernel structures depend on sockets, mbufs, sockopts, sockbufs, ucred, uio, ifnet, stat, rlimit, vnodes, LWKT ports, and netmsg definitions.

Notable risks:
- Protocol callback contracts mix synchronous and asynchronous paths; ownership of mbufs/control data must follow the specific hook.
- `PRU_NREQ`, debug request arrays, and enum values must remain synchronized.
- MP-lock wrappers require correct `PR_MPSAFE` flagging.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/protosw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ptio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/ptio.h

Pass-through device timeout ioctl definitions.

Key responsibilities:
- Includes `sys/ioccom.h`.
- Defines `PTIOCGETTIMEOUT` and `PTIOCSETTIMEOUT` ioctls for integer timeout control.

Important behavior:
- Very small ABI header for consumers that need to read or update pass-through timeout behavior.

Dependencies:
- Depends on ioctl encoding macros.

Notable risks:
- ioctl command letter `'T'` and numbers are ABI.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ptio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ptrace.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/ptrace.h

ptrace request constants, I/O descriptor, and kernel/userland declarations.

Key responsibilities:
- Defines traditional ptrace request constants for trace-me, read/write instruction/data space, continue, kill, step, attach, detach, and I/O.
- Reserves `PT_FIRSTMACH` for machine-specific requests and includes `machine/ptrace.h`.
- Defines `struct ptrace_io_desc` for bulk I/O between parent and traced process.
- Defines `PIOD_*` operation constants.
- Declares kernel helpers for reparenting, setting PC, single-step, and `kern_ptrace()`.
- Declares userland `ptrace()`.

Important behavior:
- Historical read/write user-area requests are commented as removed/reserved.
- `PT_IO` uses `ptrace_io_desc` to read/write instruction or data space.

Dependencies:
- Includes `sys/types.h` and machine ptrace definitions.
- Kernel APIs use `struct proc` and `struct lwp`.

Notable risks:
- ptrace request numbers are ABI and debugger-facing.
- Machine-specific request range must not collide with common requests.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ptrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/queue.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/queue.h

BSD intrusive linked-list and queue macro library.

Key responsibilities:
- Defines declarations and operations for:
  - `SLIST`: singly linked lists
  - `STAILQ`: singly linked tail queues
  - `LIST`: doubly linked forward lists
  - `TAILQ`: doubly linked tail queues
- Provides head/entry declarations, initializers, empty/first/next/prev/last accessors, foreach variants, mutable traversal variants, insertion, removal, concatenation, and swap macros.
- Provides optional `QUEUE_MACRO_DEBUG` trace storage and update macros.
- Provides kernel invariant checks for LIST and TAILQ link consistency.
- Trashes removed links under debug mode.

Important behavior:
- `SLIST`/`STAILQ` arbitrary removal is O(n); `LIST`/`TAILQ` arbitrary removal is O(1).
- `TAILQ` supports reverse traversal; `STAILQ` supports tail insertion with a last-next pointer.
- Debug and invariant macros add trace/check behavior without changing normal API names.

Dependencies:
- Includes `sys/cdefs.h` for helpers such as `__containerof`.

Notable risks:
- These macros evaluate arguments directly and require exact field names and initialized heads.
- Removing an element not in the expected list can corrupt memory; invariant checks help only when enabled.
- Intrusive list membership fields cannot safely be shared by multiple lists at once.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/queue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/random.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/random.h

Randomness device/getrandom flags and kernel entropy API declarations.

Key responsibilities:
- Defines legacy `/dev/random` memory interrupt ioctls.
- Defines `getrandom()` flags: `GRND_RANDOM`, `GRND_NONBLOCK`, and `GRND_INSECURE`.
- Defines kernel entropy source IDs and per-CPU source flag.
- Defines `struct random_softc` for interrupt-source tracking.
- Declares kernel RNG initialization, entropy input, random read, and kqueue filter APIs.
- Declares userland `getrandom()`.

Important behavior:
- Kernel entropy sources distinguish seeding, timing, interrupts, CPU RNGs, crypto hardware, virtio, threads, and TPM.
- `read_random()` takes an `unlimited` flag.
- `add_buffer_randomness_src()` accepts explicit source IDs.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.
- Kernel section uses `struct knote`.

Notable risks:
- Source ID space is fixed by constants; new sources must avoid collisions.
- `GRND_INSECURE` is visible API and must be handled intentionally by implementation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/random.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/reboot.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/reboot.h

Reboot system call and boot flag definitions.

Key responsibilities:
- Defines reboot flags for autoboot, ask name, single-user, no sync, halt, init name, default root, debugger, read-only root, dump, miniroot, verbose, serial, CD-ROM root, poweroff, GDB, mute, selftest, pause, video, and bootinfo.
- Documents console-selection behavior: if mute, serial, and video are all unset, multi-console mode is assumed.

Important behavior:
- Flags are passed to boot code and init-related startup paths.
- `RB_AUTOBOOT` is zero.

Dependencies:
- No includes beyond guard.

Notable risks:
- Bit assignments are bootloader/kernel ABI.
- Some flags are obsolete or unused but must remain reserved for compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/reboot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/refcount.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/refcount.h

Atomic reference-count helper API with optional waiter wakeup support.

Key responsibilities:
- Defines `REFCNTF_WAITING` high-bit flag.
- Declares `_refcount_wait()`.
- Provides inline helpers to initialize, acquire one or many refs, release one or many refs, release with wakeup handling, and wait for refs to drain.
- Uses acquire atomic increments and fetch-add decrements.

Important behavior:
- Release helpers return true when the release drops the count to zero, ignoring the waiting flag.
- Wakeup releases clear `REFCNTF_WAITING` and wake waiters when the last ref is released with waiters present.
- `refcount_wait()` delegates only if the count is non-zero.

Dependencies:
- Includes `sys/systm.h` for `wakeup()` and machine atomics.

Notable risks:
- If `refcount_wait()` is used, all releases on that count must use wakeup-capable release helpers; the header warns this explicitly.
- The waiting flag shares the count word, so maximum practical refcount excludes that bit.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/refcount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/reg.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/reg.h

Machine-independent wrapper for process register access interfaces.

Key responsibilities:
- Includes machine-specific register structure definitions from `machine/reg.h`.
- Declares kernel APIs to fill and set general registers, floating-point registers, and debug registers for an LWP.
- Declares `exec_setregs()` for setting initial register state on exec.

Important behavior:
- Provides a stable MI include path for code that manipulates architecture-specific `struct reg`, `struct fpreg`, and `struct dbreg`.

Dependencies:
- Kernel declarations use `struct lwp` and `struct proc`.

Notable risks:
- Actual structure layouts are machine-dependent; callers must not assume cross-architecture register layouts from this header alone.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/reg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/resident.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/resident.h

Resident executable support syscall declarations and sysctl export structure.

Key responsibilities:
- Declares userland `exec_sys_register()` and `exec_sys_unregister()` when not building the kernel.
- Defines `struct xresident`, exported via sysctl `vm.resident`, containing resident entry address, resident id, file path, and file stat data.

Important behavior:
- `res_file` is sized to `MAXPATHLEN`.
- The structure embeds `struct stat`, preserving file metadata for userland inspection.

Dependencies:
- Includes `sys/types.h`, `sys/param.h`, and `sys/stat.h`.

Notable risks:
- `xresident` is a sysctl ABI structure; field layout and embedded `struct stat` compatibility matter.
- Entry address is exposed as `intptr_t`, so consumers should treat it as address-sized data.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/resident.h -->