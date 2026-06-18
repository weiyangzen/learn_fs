# Group Research: group_538_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_fb857bda9aca

Scope confirmed against `Docs/research_subset_a.md`: all files are under `sources/os/illumos/illumos-gate`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zthr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zthr.c

This file implements the ZFS zthr infrastructure: a small managed kernel-thread abstraction for SPA-scoped background work that may span multiple transaction groups. It is intended for operations with a durable or in-memory “work needed/running/stopped” indicator, where external threads start work and the zthr itself is responsible for deciding when the work is complete.

The central state is `struct zthr`, containing the current `kthread_t`, state and request mutexes, a condition variable, a cancellation flag, an optional maximum sleep interval, and consumer-provided `checkfunc`, `func`, and argument pointer. `zthr_create()` delegates to `zthr_create_timer()`, which initializes this state and starts `zthr_procedure()` at system priority.

`zthr_procedure()` holds `zthr_state_lock` while checking cancellation and invoking the checker. If the checker returns true, it drops the state lock while running the worker callback so cancellation can be observed between callback invocations or explicitly via `zthr_iscancelled()`. If no work is needed, it sleeps either indefinitely on `zthr_cv` or with `cv_timedwait_hires()` according to `zthr_wait_time`. On cancellation, it clears the thread pointer and cancellation flag, broadcasts to wake the canceling requester, and exits.

External operations are serialized by `zthr_request_lock` and then use `zthr_state_lock` for state transitions. `zthr_wakeup()` broadcasts without changing state. `zthr_cancel()` sets `zthr_cancel`, wakes a sleeping thread, and waits until `zthr_thread` becomes `NULL`. `zthr_resume()` recreates the kernel thread if it is currently canceled/stopped. `zthr_destroy()` asserts the thread has already stopped, destroys synchronization primitives, and frees the object.

The main correctness contract is lock ordering and cancellation visibility. Normal request paths take request lock before state lock, while `zthr_iscancelled()` intentionally takes only the state lock because it is called by the zthr callback itself and must not deadlock with a concurrent cancel request.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zthr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zvol.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zvol.c

This file implements the illumos ZFS volume emulation driver. It exposes a ZFS DMU object as block and character device minor nodes under `/dev/zvol/dsk/...` and `/dev/zvol/rdsk/...`, handles ordinary raw I/O, volume property changes, ZIL logging/replay, device ioctls, EFI label emulation, unmap/free requests, and crash-dump preparation.

The per-volume in-core state is `zvol_state_t`. It stores the dataset name, advertised volume size, block size, minor number, minimum logical block shift, flags such as read-only/exclusive/dumpified/write-cache-enable, objset and dnode handles, open counts, ZIL handle, dump extents, and a rangelock. Global `zfsdev_state_lock` protects soft-state lookup, minor creation/removal, and temporary objset ownership that must not race normal opens.

Creation and lifecycle are split between dataset initialization and device-minor management. `zvol_create_cb()` claims `ZVOL_OBJ`, creates `ZVOL_ZAP_OBJ`, records the `size` property, and removes zvol-specific properties from the generic property nvlist. `zvol_create_minor()` owns the dataset read-only, allocates soft state and block/raw minor nodes, records the device property, initializes `zvol_state_t`, caches the object block size, and replays or destroys the ZIL as appropriate. `zvol_remove_zv()` and `zvol_remove_minor()` remove minor nodes only when there are no opens, and `zvol_remove_minors()` removes descendants by dataset-name prefix.

Open/close management is centered on `zvol_first_open()` and `zvol_last_close()`. First open owns the objset, reads the zvol size ZAP entry, holds the dnode, updates specfs-visible `Size` and `Nblocks`, opens the ZIL, and refreshes read-only status from dataset properties and pool state. Last close closes the ZIL, releases the dnode, syncs dirty writable data before evicting dbufs, and disowns the objset. `zvol_open()` enforces write permissions, snapshots/read-only pools, and exclusive opens; `zvol_close()` decrements type-specific and total open counts.

The core I/O path is `zvol_strategy()` for block-device buffers and `zvol_read()`/`zvol_write()` for character-device uio access. Both paths reject out-of-range offsets, use the per-volume rangelock for reader/writer serialization, split transfers by `zvol_maxphys` or DMU limits, convert checksum errors to EIO, and wrap unsafe sections with SMT mitigation hooks. Reads call `dmu_read()`/`dmu_read_uio()`. Writes create DMU transactions, hold/write the zvol object, call `zvol_log_write()` to enqueue TX_WRITE intent records, and optionally commit the ZIL depending on write-cache-enable and `sync=always`.

ZIL integration includes replay and get-data callbacks. `zvol_replay_write()` replays TX_WRITE records, including dmu_sync-style block-pointer records, while `zvol_replay_truncate()` replays TX_TRUNCATE as `dmu_free_long_range()`. `zvol_get_data()` supplies immediate or indirect write data to ZIL commit, locking the relevant range and using `dmu_read_by_dnode()` or `dmu_buf_hold_by_dnode()` plus `dmu_sync()`. `zvol_log_write()` chooses copied, need-copy, or indirect write records based on logbias, SLOG presence, block size, and synchronous commit needs. `zvol_log_truncate()` records DKIOCFREE/free-long-range operations as TX_TRUNCATE.

The ioctl surface emulates disk behavior. It returns device/media information, fabricates an EFI GPT and partition entry via `zvol_getefi()`, flushes write cache by committing the ZIL, gets/sets write-cache-enable, rejects legacy VTOC geometry queries with ENOTSUP, handles dump initialization/finalization, answers `DKIOC_CANFREE`, and implements `DKIOCFREE` by validating/freeing requested extents under the rangelock with optional synchronous ZIL commit. External helpers expose stable handles and volume parameters to other kernel consumers.

Crash dump support is the most specialized path. `zvol_dumpify()` rejects read-only and encrypted zvols, ensures dump properties and block size are suitable, preallocates the entire volume, traverses the dataset with `zvol_get_lbas()` to build physical extent mappings, marks the zvol dumpified, and records `dumpsize`. `zvol_dumpio()` bypasses normal DMU I/O and calls vdev dumpio directly through mapped extents, with strict sector/block-boundary checks. `zvol_dump_fini()` best-effort restores saved checksum, compression, refreservation, dedup, and block-size properties, frees extents and blocks, and clears the dumpified flag.

Important dependencies include DMU object/ZAP APIs, DSL properties, ZIL, rangelocks, DDI soft state and minor nodes, specfs size invalidation, DKIO interfaces, EFI structures, vdev dump I/O, pool feature activation, and ZFS property setting. Correctness risks concentrate around `zfsdev_state_lock` scope, objset ownership lifetime, ZIL commit ordering, rangelock coverage during dmu_sync, live resizing while dumpified, and the dump path’s assumption that all blocks are allocated and physically mappable.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zvol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zut/zut.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zut/zut.c

This file implements the ZFS unit-test pseudo driver `/dev/zut`. The driver exposes ioctl helpers used to exercise vnode lookup, extended attribute lookup, readdir, case-insensitive lookup behavior, directory-entry flags, access filtering, and extended stat attributes from kernel context.

`zut_open_dir()` resolves a directory path from either root or the caller’s current directory, using the process root/current directory under `p_lock`, `lookuppnvp()`, and a final directory read-access check. It handles ACE-aware filesystems with `ACE_LIST_DIRECTORY` and falls back to `VREAD` otherwise.

`zut_readdir()` copies in a `zut_readdir_t`, opens the requested directory, optionally switches to a named-attribute directory by looking up a file and then `LOOKUP_XATTR`, builds a kernel `uio`, maps request flags to `V_RDDIR_ENTFLAGS` and `V_RDDIR_ACCFILTER`, calls `VOP_READDIR()` under a vnode read lock, copies directory data and updated metadata back to userland, and releases all vnodes. `zut_lookup()` similarly resolves a directory, optionally enables `FIGNORECASE`, looks up a file or named attribute file, optionally fills a stat buffer via `zut_stat64()`, and returns the resolved path and directory-entry flags.

`zut_stat64()` requests normal stat attributes plus a set of ZFS/system extended attributes through `xvattr_t`. It fills a `stat64` and translates returned xoptattr bits into `F_ARCHIVE`, `F_SYSTEM`, `F_READONLY`, `F_HIDDEN`, `F_NOUNLINK`, `F_IMMUTABLE`, `F_APPENDONLY`, `F_NODUMP`, `F_OPAQUE`, AV flags, reparse, offline, and sparse bits.

The driver shell is a single minor pseudo device. `zut_ioctl()` accepts `ZUT_IOC_LOOKUP` and `ZUT_IOC_READDIR` after command-range and minor checks. `zut_attach()` creates the `"zut"` character minor node, `zut_detach()` removes properties and minors, and `zut_info()`, `zut_open()`, and `zut_close()` implement standard pseudo-driver plumbing. `_init()` installs the module and obtains an LDI identifier; `_fini()` removes it and releases that identifier.

The main dependencies are vnode lookup/read/stat operations, pathname handling, ACE/VREAD access checks, DDI pseudo-device registration, and structures from `sys/fs/zut.h`. The ioctl path is intentionally narrow but must carefully release vnodes on all lookup branches and preserve user/kernel copyout semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zut/zut.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zut/zut.conf -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zut/zut.conf

This is the driver configuration file for the ZFS unit-test pseudo device. Its only active configuration line is:

`name="zut" parent="pseudo";`

That binds the `zut` driver to the pseudo nexus so the module can attach as a pseudo-device and create `/dev/zut`. The rest of the file is the CDDL/license and copyright header.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zut/zut.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/acct.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/acct.c

This file implements the `acct(2)` process-accounting system call and the weak-stub `acct()` hook called from process exit. Accounting is virtualized per zone: each zone has an `acct_globals` containing the reusable accounting record buffer, a lock, and the held vnode for the accounting file. A global list of all zone accounting states allows the kernel to reject reuse of an accounting file or filesystem already used by another zone.

Module initialization creates the global list and lock, registers a zone key with init/shutdown/fini callbacks, and installs the `acct(2)` syscall. The module refuses unload in `_fini()` because unloading after accounting is enabled would silently stop process-exit accounting.

`sysacct()` checks `secpolicy_acct()`, then either disables accounting for the caller’s zone when `fname == NULL`, or opens a new regular file for writing. It prevents accounting to non-regular files, maps `EISDIR` to `EACCES` for SVID compatibility, and uses `acct_find()` under `acct_list_lock` to detect vnode or filesystem reuse. Switching files swaps the new vnode into the zone state while closing and releasing the old one outside the per-zone lock as needed.

`acct_find()` performs deep vnode comparison through `VOP_REALVP()` so loopback/shadow vnodes compare to the same underlying file. With `compare_vfs` true it detects whether a mounted filesystem contains any active accounting file; `acct_fs_in_use()` exposes that check to other kernel code.

`acct()` runs during process exit. It copies command name, start time, compressed user/system/elapsed time, memory, I/O counts, uid/gid, controlling tty, status, and accounting flags into the zone’s `acctbuf`. It appends the record to the accounting vnode with `vn_rdwr()` under the per-zone lock, bounded by `MAXOFF32_T` because traditional accounting tools are not large-file aware. If the append fails or is short, it restores the previous file size to avoid leaving a corrupt partial record.

The important dependencies are zone-specific storage, vnode open/close/read-write operations, process resource accounting fields, credentials, and the legacy `comp_t` pseudo-floating format. Correctness concerns are lock ordering between global and per-zone accounting locks, avoiding held vnodes during zone shutdown, and preventing partial record corruption.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/acct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/aio.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/aio.c

This file implements the kernel asynchronous I/O syscall module for raw character devices. It dispatches legacy Solaris AIO operations, POSIX `aio_read`/`aio_write`, list I/O, wait/suspend/error/cancel calls, 32-bit compatibility, large-file variants, and event-port notification setup. Actual physical I/O completion and cleanup helpers live mainly in `aio_subr.c`.

The syscall entry points are `kaioc()` on LP64 and `kaio()` for the syscall table path. They decode operation numbers such as `AIOREAD`, `AIOWRITE`, `AIOWAIT`, `AIOWAITN`, `AIOLIO`, `AIOSUSPEND`, `AIOERROR`, `AIOAREAD`, `AIOAWRITE`, `AIOCANCEL`, and the 32-bit large-file variants. `aioinit()` lazily allocates the per-process `aio_t`, while `aiostart()` starts the per-process cleanup thread that exists to release physical page locks when unmap, exit, fork holds, or DR memory delete need progress.

Waiting paths manage done queues and timeouts. `aiowait()` waits for any completed request or user-level notification and reaps one request. `aiowaitn()` serializes concurrent waitn calls with `AIO_WAITN`, collects up to the requested number of done requests, handles zero-time polling and timed waits, copies completed aiocb pointers back, unlocks pages, copies results, and frees request structures. `aiosuspend()` copies in an aiocb pointer list, looks for any matching completed request, optionally waits, and then reaps matching completions.

List I/O is implemented in three shape variants: native LP64 `alio()`, 32-bit large-file `alioLF()`, and 32-bit non-largefile `alio32()`. Each copies the aiocb pointer array, optionally allocates an `aio_lio_t` head for `LIO_WAIT` or notification, prepares signal or event-port completion metadata, skips invalid or `LIO_NOP` entries, validates file descriptors and read/write permissions, caches repeated vnode/mode checks, creates individual `aio_req_t` objects, marks user `aio_errno` as `EINPROGRESS` before driver submission, and submits requests to the driver callback returned by `check_vp()`. `aliowait()` later finds the list head from any member request and waits for the list reference count to drain before cleaning up.

Single-request submission is handled by `arw()` for old Solaris AIO and `aiorw()` for POSIX-style aiocb requests. These functions copy in aiocb data as needed, validate the descriptor and mode, call `check_vp()` to ensure the target is a supported raw character device or PXFS vnode, allocate and initialize an `aio_req_t`, optionally enable poll mode, associate event-port notification, handle zero-length requests with `aio_zerolen()`, and call the device/PXFS async read or write entry point. On immediate submission failure, they release the descriptor reference, remove pending queue state, free the request, decrement pending counts, and wake cleanup waiters if needed.

The request-management helpers keep a per-process hash keyed by user `aio_result_t *`. `aio_hash_insert()` rejects duplicate result pointers. `aio_req_done()`, `aio_req_find()`, and `aio_req_remove()` locate and remove completed requests from the done queue. `aioerror()` maps an aiocb to in-progress, invalid, or completed-and-reaped status. `aio_cancel()` does not issue true device cancellation; it reports `AIO_NOTCANCELED` if matching pending requests exist and `AIO_ALLDONE` otherwise.

`check_vp()` deliberately restricts kernel AIO to non-STREAMS character devices with suitable driver async entries and a usable strategy routine; regular files and STREAMS return NULL so userland/libaio fallback can handle them. PXFS vnodes route to cluster PXFS async functions. Regular devices are wrapped by `driver_aio_read()` and `driver_aio_write()`, which call `cb_aread`/`cb_awrite` through the device’s `cb_ops`.

The cleanup thread `aio_cleanup_thread()` responds to address-space unmap waits, DR cleanup requests, process exit/kill, and fork/watch holds. It moves completed done-queue entries needing physical resource cleanup onto cleanup queues, calls `aio_cleanup()`, waits on the address-space or cleanup condition variable, blocks new requests with `AIO_REQ_BLOCK` during exit, and exits through post-syscall AST once pending I/O has drained.

The file’s key dependencies are per-process `aio_t` state, file descriptor reference management, vnode/snode/device tables, event ports, signals, 32-bit data-model conversion, process contracts for signal metadata, address-space unmap coordination, and helper functions from `aio_subr.c`. Main risks are request/result pointer uniqueness, race-free transition among pending/done/poll/cleanup/port queues, list-I/O reference counts, event-port lifecycle, and not holding locks across driver calls or page-unlock paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/aio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/aio_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/aio_subr.c

This file provides lower-level support for kernel AIO: asynchronous physical I/O setup, `biodone()` completion routing, page unlock and result copyout, queue manipulation, cleanup of completed requests, event-port close/callback support, and process-exit teardown.

`aphysio()` is the async counterpart to `physio()`. It validates offsets, initializes the embedded `buf_t`, applies `mincnt`, page-locks the user buffer with `as_pagelock()`, records the page list in the buf shadow fields, installs `aio_done()` as the default completion callback, and calls the driver strategy routine. It rejects drivers that try to use cancellation other than `anocancel()`. `aphysio_unlock()` later releases the page locks, clears physical/busy/shadow flags, and marks the buf done; zero-length requests bypass page unlock.

`aio_done()` is the central completion path called from `biodone()`. It maps out remapped buffers, releases the held file descriptor reference, decrements process pending counts, and moves the request to the correct queue depending on whether it uses event ports, cleanup mode, poll mode, per-request signals, list-I/O heads, or ordinary done-queue completion. It handles port-close waiters, cleanup-thread queues, AST-based poll cleanup, waitn wakeups, SIGIO compatibility for old Solaris AIO, per-request queued signals, list-I/O final notification, and event-port delivery.

Queue utilities implement circular doubly-linked queues for request lists. `aio_enq()` and `aio_deq()` add/remove requests with optional flag bits, `aio_cleanupq_concat()` moves a full queue to the cleanup queue while rewriting queue flags, and DEBUG builds verify queue integrity. `aio_hash_delete()`, `aio_req_free()`, and `aio_req_free_port()` return requests and list heads to freelists while clearing signal and port resources and maintaining outstanding counts.

`aio_cleanup()` drains cleanup, notify, poll, and selected port cleanup queues. It calls specialized helpers: `aio_cleanup_cleanupq()` unlocks physical pages and moves or frees requests; `aio_cleanup_notifyq()` additionally sends per-request or list signals; `aio_cleanup_pollq()` copies results for poll requests; and `aio_cleanup_portq()` carefully disconnects the port queue while unlocking pages so interrupt completion cannot deadlock on AIO locks. Cleanup may run from AST context, the cleanup thread, or process exit.

`aio_cleanup_exit()` runs when a process exits. It marks `AIO_CLEANUP`, waits for pending I/O and in-progress completion handling to drain, processes cleanup queues in exit mode, frees done-queue requests and freelists, frees cached waitn aiocb storage, destroys mutexes, clears `p_aio`, and frees the per-process AIO state.

Result copyout is handled by `aio_copyout_result()` and `aio_copyout_result_port()`, which translate buf error/resid state into `aio_return` and `aio_errno` in native or 32-bit result layouts. `aio_zerolen()` short-circuits zero-length requests through the normal completion path with zero residual and no physical I/O.

Event-port support includes `aio_req_remove_portq()`, `aio_close_port()`, and port queue cleanup interactions. `aio_close_port()` marks pending requests for a closing port, waits for them to complete, removes matching done events from the port queue, discards the port events, unlocks resources, and frees request state. `aio_cleanup_dr_delete_memory()` lets dynamic memory delete wake the cleanup machinery so locked AIO pages can be released.

The main dependencies are VM address-space page locking, buf/biodone semantics, file descriptor reference release, signal queues, event ports, per-process AIO locks and condition variables, and process/AST wakeups. Correctness depends on not unlocking pages while holding locks that completion paths need, preserving queue flags during movement, and coordinating cleanup with exit, unmap, DR, and port close races.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/aio_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/audit_core.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/audit_core.c

This file initializes and manages core per-process, per-thread, and per-file audit data used by the C2 audit subsystem. It also handles audit context updates after policy changes and provides fork/exit/thread/file allocation hooks.

`audit_init()` checks whether the `c2audit` module is explicitly excluded. If excluded, auditing is permanently disabled; otherwise it marks audit unloaded-loadable, initializes the process audit data cache, initializes per-zone audit contexts, allocates initial thread and process audit data for `curthread` and `curproc`, patches existing kernel threads to use the initial thread audit data, initializes `kcred` audit info with `AU_NOAUDITID`, and creates initial root/current-directory audit paths.

`audit_update_context()` applies pending per-process audit mask updates. If `PAD_SETMASK` is set, it obtains or uses a preallocated credential, locks the process audit data, copies the current credential to the new one under `p_crlock`, updates the audit mask, clears the pending flag, and either installs it for `curproc` with `crset()` or frees the extra reference for other processes.

`audit_newproc()` allocates child process audit data during fork, copies the parent’s audit path/data under the parent pad lock, holds root and cwd paths, and, when full auditing is active, completes the parent fork audit record before the child runs. `audit_pfree()` releases audit paths and frees per-process audit data on exit or fork failure, except for the immortal initial `pad0`.

Thread and file hooks are straightforward. `audit_thread_create()` allocates zeroed `t_audit_data` for new threads. `audit_thread_free()` skips the initial shared `tad0`, asserts no residual audit record/path state, releases deferred at-path state, frees deferred records if auditing is loaded, and frees the thread audit data. `audit_falloc()` attaches `f_audit_data` to new file structures, and `audit_unfalloc()` releases saved audit paths and frees file audit data. `audit_getstate()` reports whether auditing is loaded and enabled for the current thread.

Important dependencies include audit caches from `audit_memory.c`, zone setup from `audit_zone.c`, credentials, process/thread/file lifecycle hooks, audit record/token helpers, and path reference management. Risks are primarily lifecycle and locking: audit path references must be held/released correctly across fork and exit, credential replacement must use the right locks, and initial kernel threads share bootstrap audit data.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/audit_core.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/audit_memory.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/audit_memory.c

This file contains small memory-management helpers for audit process data and audit path strings. It defines the global `au_pad_cache` kmem cache used for `p_audit_data_t` allocations.

`au_pathhold()` and `au_pathrele()` maintain an atomic reference count on `struct audit_path`; the release path frees the variable-sized allocation when the count reaches zero. `au_pathdup()` creates a resized copy of an existing audit path, optionally adding one path section and/or extra string storage. It preserves section offsets by computing new pointers relative to the copied string base, updates the new end pointer, copies existing strings, and initializes the new reference count and allocation size.

The kmem cache constructor/destructor initialize and destroy the `pad_lock` mutex embedded in `p_audit_data_t`. `au_pad_init()` creates the `"audit_proc"` cache with those callbacks.

The main dependencies are atomic reference operations, kmem variable-size allocation, and the audit path layout where section pointers and string storage are packed into a single allocation. Correctness depends on preserving pointer offsets during duplication and matching `audp_size` on free.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/audit_memory.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/audit_zone.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/audit_zone.c

This file manages per-zone audit kernel contexts through a zone key. Each zone receives an `au_kcontext_t` with audit identity, policy, queue configuration, statistics, service locks, condition variables, and door-buffer storage.

`au_zone_init()` allocates and initializes a context. For zone 0 it records the global context and attaches it to `global_zone`; for non-global zones it inherits policy from the global context and attaches the context to the current process zone. It sets validity, zone id, default IPv4 terminal id, `AU_NOAUDITID`, initial audit state, queue high/low watermarks, buffer sizes, delay, statistics version/event count, door buffer, and all queue/service locks and condition variables.

`au_zone_shutdown()` sends a shutdown door message when auditing is loaded and the context has an active audit output target, marks the context invalid, forces audit state to no-audit, wakes the output thread, and destroys the per-zone taskq if output was active. `au_zone_destroy()` asserts no-audit state, destroys locks and condition variables, frees any queued audit record, releases the door buffer, and frees the context. `au_zone_setup()` registers these callbacks with `zone_key_create()`, and `au_zone_getstate()` returns either the supplied context state or the current zone context state.

Key dependencies are zone lifecycle callbacks, audit queues and records, audit door messaging, taskqs, and global audit policy/state. Correctness depends on orderly shutdown of active output before destroying queue state and on inheriting global policy for zones created after the global audit context exists.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/audit_zone.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/autoconf.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/autoconf.c

This file contains early boot and dynamic-reconfiguration DDI autoconfiguration helpers. It sets up DDI subsystems, creates the initial devinfo tree from firmware/platform data, attaches the root nexus, and attaches core pseudo devices needed by the kernel.

`setup_ddi()` initializes node IDs, binds the root class, creates the devinfo tree, initializes instance assignment, callbacks, event logging, fault management, resource management, UFM, kernel sensors, driver configuration loading, layered driver interfaces, and device files. `setup_ddi_poststartup()` starts the DDI flush daemon, runs post-startup interrupt resource management, and redistributes interrupts on platforms supporting weighted distribution.

`impl_create_root_class()` finds the `rootnex` major, reads the firmware manufacturer/root name, normalizes slashes to underscores, binds that name to the root nexus driver, records the platform implementation architecture, and on x86 imports optional bootpath and fstype boot properties. It warns and overrides conflicting root-name bindings because the root nexus must own the firmware root name.

PROM/devinfo traversal is handled by `getlongprop_buf()`, `get_neighbors()`, `di_dfs()`, and `i_ddi_create_branch()`. These helpers read `name` properties, work around non-null-terminated OBP strings, skip nodes failing `check_status()`, add the first valid sibling/child, and recursively expand children. `create_devinfo_tree()` initializes the node cache, allocates and permanently holds `top_devinfo`, binds it to `rootnex`, walks firmware to add descendants, and on x86 calls platform PCI discovery because there is no PROM tree.

`i_ddi_init_root()` initializes and attaches the root nexus by hand: it runs rootnex child initialization, holds the root driver, assigns an instance, loads driver configuration, sets attaching state, calls `devi_attach()`, initializes `global_vhci_lock`, marks root ready, expands `.conf` children, initializes power-management locks, attaches `options`, `pseudo`, `clone`, records major numbers for clone/mm/nulldriver, and attaches `scsi_vhci` for MPXIO class registration.

Important dependencies are bootops/PROM property access, driver name-to-major bindings, devinfo node state, root nexus operations, pseudo nexus creation, fault-management and resource subsystems, LDI, and interrupt management. Correctness risks are early-boot ordering, permanent root devinfo holds, firmware property quirks, and binding conflicts that could prevent the root nexus from attaching.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/autoconf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bdev_dsort.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bdev_dsort.c

This file implements the classic `disksort()` seek-sort helper for block-device driver queues. It assumes the caller stores the request cylinder number in `b_resid` via the local `b_cylin` macro and maintains a `struct diskhd` activity queue through `b_actf` and `b_actl`.

The algorithm is a one-way elevator scan. The queue is treated as two ascending-cylinder lists joined together: the first contains requests at or after the current cylinder, and the second contains requests that arrived after their cylinder had already been passed. An inversion in cylinder order marks the transition from the first list to the second.

If the queue is empty, the new buffer becomes both head and tail. If the new request is before the current request, `disksort()` searches for the inversion and inserts into the second list in ascending order, or appends if no larger second-list request exists. If the new request is at or after the current request, it inserts into the first list before the first larger cylinder or just before an inversion. Tail bookkeeping updates `b_actl` when insertion occurs after the old tail.

This helper depends only on legacy buf queue fields and driver-provided cylinder numbers. Its correctness depends on callers maintaining the activity queue invariant and interpreting `b_resid` as a sortable seek position.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bdev_dsort.c -->