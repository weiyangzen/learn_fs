# Group Research: group_294_dragonflybsd_sources_os_bsd_dragonflybsd_sys_kern_kern_conf_c_source_8b60b4f0d32a

Scope: `Docs/research_subset_a.md`, DragonFlyBSD kernel sources under `sources/os/bsd/dragonflybsd`.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_conf.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_conf.c

## Purpose

Implements DragonFlyBSD character-device identity, creation, destruction, aliasing, autocloning, reference, and name helper APIs. This file is the compatibility-facing layer above `devfs` and `dev_ops`, while lower-level operation dispatch lives in `kern_device.c`.

## Key Responsibilities

- Converts between `cdev_t`, old-style `dev_t`, user major/minor encodings, and display names.
- Creates device nodes through `make_dev*()` and `devfs_create_dev()`.
- Creates internal-only or devfs-only device objects with the `make_only_*()` family.
- Destroys devices and aliases through `devfs_destroy_dev()` / alias helpers.
- Supports autocloning device entries using devfs clone handlers.
- Wraps device lifetime around `sysref` via `reference_dev()` and `release_dev()`.

## Main Entry Points

- `major()`, `minor()`, `lminor()` return device major/minor values from `cdev_t`; `major()` deliberately reads `si_umajor` instead of `si_ops` because destroyed devices may have their ops replaced with `dead_dev_ops`.
- `devid_from_dev()` and `dev_from_devid()` bridge `cdev_t` and devfs inode/device IDs.
- `uminor()`, `umajor()`, `makeudev()` preserve old userland device-number packing.
- `makedev_unit_b32()` formats a unit suffix in base 32.
- `make_dev()`, `make_dev_covering()`, `make_only_devfs_dev()`, `make_only_dev()`, `make_only_dev_covering()` allocate/initialize `cdev_t` instances and optionally create devfs-visible nodes.
- `destroy_dev()`, `destroy_only_dev()`, `sync_devs()` clean up devices and drain disk/devfs configuration work.
- `make_dev_alias()` / `destroy_dev_alias()` create/remove devfs aliases.
- `make_autoclone_dev()` / `destroy_autoclone_dev()` manage clone-handler-backed device names.
- `reference_dev()` / `release_dev()` operate on `dev->si_sysref`.
- `devtoname()` lazily synthesizes `#driver/minor` names when `si_name` is empty or internal.

## Important Implementation Details

- `compile_dev_ops()` is called before device creation, ensuring missing device operation slots are populated from defaults.
- `make_dev()` returns an ad-hoc, unreferenced device pointer; callers storing it long-term must call `reference_dev()`.
- `destroy_dev()` assumes the caller owns a real reference; the comments warn against `destroy_dev(make_dev(...))`.
- `destroy_only_dev()` releases three references, reflecting the specific reference arrangement created by `make_only_dev()`/devfs internals.
- `make_autoclone_dev()` installs a clone handler and creates a covering device using `default_dev_ops` over the real backing ops.
- `sync_devs()` calls `disk_config()` and `devfs_config()` twice to flush asynchronous disk/devfs operations before mountroot or module unload.

## Dependencies and Coupling

- Strongly coupled to `devfs` APIs: `devfs_new_cdev`, `devfs_create_dev`, `devfs_destroy_dev`, `devfs_make_alias`, `devfs_clone_handler_add`, clone bitmap helpers.
- Depends on `struct dev_ops`, `dead_dev_ops`, and `default_dev_ops` from the device-operation layer.
- Used by driver attach/detach paths, disk code, clone devices, and `/dev` namespace management.

## Filesystem/Storage Relevance

This file is central to exposing kernel devices as `/dev` nodes. Filesystems and block layers reach storage through device vnodes, so correct lifetime and devfs naming here directly affect mountable disks, pseudo devices, and driver teardown safety.

## Research Notes

- The API distinguishes ad-hoc returned pointers from caller-owned references; misuse can create lifetime bugs.
- Major/minor compatibility helpers preserve legacy encodings and can return `NOUDEV` when values cannot be represented.
- Autoclone setup bridges devfs name lookup and runtime device instance creation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_cputimer.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_cputimer.c

## Purpose

Provides DragonFlyBSD’s generic CPU timer, interrupt timer, and CPU counter registration/selection infrastructure. It abstracts free-running counters used by systimers and per-CPU timer interrupts.

## Key Responsibilities

- Maintains the selected `sys_cputimer`, starting with a monotonic dummy timer.
- Registers and deregisters candidate `struct cputimer` implementations.
- Computes frequency conversion helpers for microseconds/nanoseconds.
- Registers, selects, configures, restarts, and power-save-switches interrupt cputimers.
- Dispatches per-CPU timer interrupts into `systimer_intr()`.
- Registers and selects `struct cpucounter` implementations for MP-safe or per-CPU counter use.
- Exposes timer state through `kern.cputimer.*` sysctls.

## Main Entry Points

- `cputimer_select()` switches the active timer if priority allows, preserving continuity by constructing the new timer from the old count and warning if it jumps backward.
- `cputimer_register()` / `cputimer_deregister()` maintain the timer list and fall back to the dummy timer when needed.
- `cputimer_set_frequency()`, `cputimer_default_fromhz()`, `cputimer_default_fromus()` handle tick conversion.
- `cputimer_intr_register()`, `cputimer_intr_deregister()`, `cputimer_intr_select()` maintain interrupt timer providers.
- `cputimer_intr_select_caps()` selects the best interrupt timer matching required capability bits.
- `cputimer_intr_powersave_addreq()` / `cputimer_intr_powersave_remreq()` switch interrupt timer capabilities around power-saving requirements.
- `pcpu_timer_process()` and `pcpu_timer_process_frame()` process per-CPU timer events.
- `cpucounter_find_pcpu()`, `cpucounter_find()`, `cpucounter_register()` manage CPU counter backends.

## Important State

- `dummy_cputimer` and `dummy_cpucounter` provide always-available fallbacks.
- `sys_cputimer` points at the active free-running counter.
- `cputimerhead` stores registered cputimers.
- `sys_cputimer_intr`, `cputimer_intr_caps`, and `cputimer_intr_head` track selected and available interrupt timers.
- `cputimer_intr_ps_reqs` counts active power-save requests, protected by `cputimer_intr_ps_slize`.
- `cpucounterhead` stores registered CPU counters.

## Control Flow

- Timer selection updates conversion fields, calls the new timer’s `construct()`, reconfigures interrupt timers, updates `sys_cputimer`, destructs the old timer, and notifies `systimer_changed()`.
- Interrupt cputimer initialization is deferred via `SYSINIT(cputimer_intr, SI_BOOT2_CLOCKREG, SI_ORDER_SECOND, ...)`.
- Per-CPU timer interrupt handling calls optional provider-specific `pcpuhand`, clears `gd_timer_running`, then dispatches pending `gd_systimerq` work.
- Power-save add/remove paths reselect interrupt timers by capability and restart the timer if selection changed.

## Sysctl Surface

- `kern.cputimer.select`, `name`, `clock`, `freq`.
- `kern.cputimer.intr.reglist`, `freq`, `select`.

## Filesystem/Storage Relevance

Not filesystem-specific, but storage and VFS subsystems depend on kernel timers for timeouts, delayed work, buffer scheduling, and periodic cleanup. Timer monotonicity and interrupt-timer reliability matter for I/O scheduling correctness.

## Research Notes

- `cpucounter_find()` requires `CPUCOUNTER_FLAG_MPSYNC` and asserts that the selected counter is MP-safe.
- Power-save switching uses `ERESTART` internally to signal that the interrupt timer changed and must be restarted.
- The dummy counter uses `microuptime()` and is lower priority than hardware backends.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_cputimer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_debug.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_debug.c

## Purpose

Small kernel debug support file. It provides test sysctl bitfields and a fallback `print_backtrace()` implementation when DDB is not compiled in.

## Key Responsibilities

- Defines writable debug bit sysctls for 32-bit and 64-bit variables.
- Supplies a non-DDB `print_backtrace()` stub that reports DDB is required.

## Main Entry Points

- `SYSCTL_BIT32(_debug, b32_0, ...)` and `SYSCTL_BIT32(_debug, b32_31, ...)`.
- `SYSCTL_BIT64(_debug, b64_0, ...)` and `SYSCTL_BIT64(_debug, b64_63, ...)`.
- `print_backtrace(int count)` under `#ifndef DDB`.

## Dependencies

- Includes `opt_ddb.h`, `sys/systm.h`, `sys/sysctl.h`, and `ddb/ddb.h`.
- Actual stack tracing is provided elsewhere when DDB is present.

## Filesystem/Storage Relevance

No direct filesystem logic. Its relevance is diagnostic: kernel storage/VFS debugging can use backtraces when DDB is enabled, and this file defines the fallback behavior otherwise.

## Research Notes

- The sysctls appear to be generic bit-manipulation/debug validation hooks.
- The fallback `print_backtrace()` intentionally does not attempt architecture-specific unwinding.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_descrip.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_descrip.c

## Purpose

Implements DragonFlyBSD file descriptor tables, open file object lifetime, descriptor duplication/close/fcntl syscalls, descriptor caching, revocation, `/dev/fd`, file-table sysctls, and fallback file operations.

This is one of the core VFS-facing process I/O files: it maps integer file descriptors to `struct file`, dispatches file operations, and controls close semantics that release vnode/socket/pipe resources.

## Key Responsibilities

- Manages `struct filedesc` tables and `struct file` references.
- Allocates descriptor numbers efficiently using an in-place binary-tree allocation count in `fd_files[].allocated`.
- Maintains per-thread descriptor caches (`td_fdcache`) to speed up repeated fd-to-file lookups.
- Implements syscalls and kernel helpers for `dup`, `dup2`, `fcntl`, `close`, `closefrom`, `shutdown`, `fstat`, `fpathconf`, and `flock`.
- Implements POSIX/BSD advisory-lock cleanup during close, exec, fork, and descriptor-table release.
- Tracks global open files through hashed file lists.
- Handles file pointer revocation for revoked vnodes/devices.
- Initializes `/dev/fd/N`, `/dev/stdin`, `/dev/stdout`, and `/dev/stderr`.
- Exposes file-table information and tunables via sysctls.

## Major Data Structures and State

- `filelist_heads[NFILELIST_HEADS]`: hashed global lists of all live `struct file` objects, each protected by a spinlock.
- `nfiles`: global open file count.
- `revoke_token`: serializes revocation against descriptor externalization paths.
- `struct filedesc`: per-process descriptor table with spinlock, current/root/jail dirs, descriptor nodes, allocation counters, and close counters.
- `struct fdnode`: descriptor slot containing file pointer, flags, reservation state, cache links, and allocation metadata.
- `struct fdcache`: per-thread cache entries that can temporarily lend or hold `struct file` references.
- `fildesc_ops`: device ops for `/dev/fd`.
- `badfileops`: file operation table that returns errors for invalid/revoked/uninitialized file objects.

## Descriptor Lookup and Cache Flow

- `holdfp_fdp()` and `holdfp_fdp_locked()` acquire a referenced file pointer from an arbitrary descriptor table.
- `_holdfp_cache()` first searches the current thread’s fd cache; on miss it locks the descriptor table, holds the file, and may install a cache entry.
- `dropfp()` tries to return a borrowed cache reference; if it cannot, it drops the file normally.
- `fexitcache()` clears all cached descriptors for a thread, used before descriptor table destruction/replacement.
- `fclearcache()` removes descriptor cache entries when a descriptor is cleared or replaced.

## Descriptor Allocation

- `fdgrow_locked()` grows the descriptor table to `2^n - 1` size, preserving the allocation tree layout.
- `right_subtree_size()`, `right_ancestor()`, and `left_ancestor()` implement navigation for the in-place allocation tree.
- `fdreserve_locked()` increments/decrements allocation counts up the tree.
- `fdalloc_locked()` enforces `RLIMIT_NOFILE`, `maxfilesperproc`, `minfilesperproc`, and per-user limits, then finds/reserves a free descriptor.
- `fdalloc()` wraps allocation with descriptor table locking.
- `fdavail()` tests whether a process has enough free descriptors.

## Syscall and Helper Entry Points

- `sys_getdtablesize()` returns the effective descriptor-table size cap.
- `sys_dup2()`, `sys_dup()`, and `kern_dup()` implement descriptor duplication, including fixed/variable allocation and `CLOEXEC`/`CLOFORK` variants.
- `sys_fcntl()` and `kern_fcntl()` implement descriptor flags, file status flags, owner ioctls, advisory record locks, `F_GETPATH`, and multiple dup commands.
- `sys_close()`, `kern_close()`, `sys_closefrom()`, `kern_closefrom()` remove descriptor table entries and close underlying files.
- `sys_shutdown()` / `kern_shutdown()` dispatch `fo_shutdown()`.
- `sys_fstat()` / `kern_fstat()` dispatch `fo_stat()`.
- `sys_fpathconf()` dispatches pathconf for vnode/fifo and pipe/socket cases.
- `sys_flock()` implements BSD whole-file advisory locks.

## File Object Lifetime

- `falloc()` creates a `struct file`, initializes `f_count`, `f_ops`, credentials, kqueue list, global file-list insertion, and optionally reserves a descriptor.
- `fsetfd_locked()` installs or clears a reserved descriptor.
- `funsetfd_locked()` removes a file pointer from a descriptor, clears cache entries, updates allocation counters, and returns the file reference previously owned by the descriptor table.
- `fhold()` increments `f_count`.
- `fdrop()` safely performs the last-reference transition by removing the file from the global file list under the list spinlock before calling `fo_close()` and `ffree()`.
- `ffree()` releases credentials, namecache handle, and memory.
- `fsetcred()` synchronizes `uidinfo` open-file counts, including per-CPU batching.

## Descriptor Table Lifecycle

- `fdinit_bootstrap()` initializes proc0’s file descriptor table.
- `fdinit()` creates a new descriptor table inheriting cwd/root/jail dirs.
- `fdshare()` increments table refcount for shared descriptor tables.
- `fdcopy()` clones descriptor tables across fork-like operations, dropping reserved slots and not copying kqueue descriptors or `UF_FOCLOSE` descriptors.
- `fdfree()` releases descriptor tables, closes files, handles POSIX lock leader structures, waits for soft references from process scans, and releases directory/namecache references.
- `filedesc_to_leader_alloc()` manages process-leader lock-cleanup topology for shared descriptor tables.

## Revocation

- `fdrevoke()` allocates a replacement dummy file, marks matching file pointers `FREVOKED` via `allfiles_scan_exclusive()`, then scans processes to replace matching descriptors and close old files.
- `fdrevoke_check_callback()` filters by prison and file data/type.
- `fdrevoke_proc_callback()` handles process descriptor replacement and controlling-terminal cleanup.

## `/dev/fd` Handling

- `fildesc_drvinit()` creates `fd/0` through `fd/63`, plus `stdin`, `stdout`, and `stderr`.
- `fdopen()` implements `/dev/fd/N` open semantics:
  - Looks up the source descriptor.
  - Rejects incompatible access modes.
  - For vnode-backed descriptors, creates a new file pointer so seek offset is not shared.
  - For non-vnode descriptors, shares the existing file pointer.
  - Handles revoked descriptors by substituting a dummy file.

## Exec and Setuid Safety

- `setugidsafety()` closes unsafe procfs descriptors in fd 0..2 for setuid/setgid exec safety.
- `fdcloseexec()` closes `UF_EXCLOSE` descriptors and clears `UF_FOCLOSE` across exec.
- `fdcheckstd()` opens `/dev/null` for missing standard descriptors 0, 1, and 2.

## Sysctl Surface

- `kern.file` returns `struct kinfo_file` snapshots through `sysctl_kern_file()`.
- `kern.minfilesperproc`, `kern.maxfilesperproc`, `kern.maxfilesperuser`, `kern.maxfiles`, `kern.maxfilesrootres`, `kern.openfiles`.

## Filesystem/Storage Relevance

This file is directly VFS-critical. Every open vnode, device vnode, pipe, socket, and kqueue descriptor flows through this layer. Close paths invoke vnode advisory lock cleanup and file operations; `/dev/fd` can reopen vnode-backed descriptors; revocation supports forced invalidation of descriptors referencing revoked vnodes/devices.

## Research Notes

- Descriptor cache correctness depends on careful interaction between `fclearcache()`, borrowed references, and descriptor-table spinlocks.
- The allocation tree in `fd_files[].allocated` avoids linear scans for large descriptor tables.
- `closef()` implements POSIX record-lock behavior: a close by a process can release all process-owned POSIX locks on a vnode.
- `fdrop()` avoids last-reference races with global file-list scanners by removing the file from the list while holding the list spinlock.
- Several functions are marked not fully MPSAFE in comments, especially paths that scan descriptor tables while operations can block.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_descrip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_device.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_device.c

## Purpose

Implements the DragonFlyBSD device-operation dispatch layer. It wraps `struct dev_ops` calls, supplies default/dead operations, handles Giant/MPLock compatibility for non-MPSAFE drivers, and provides helpers for operation interception and compilation.

## Key Responsibilities

- Defines `syslink_desc` descriptors for each device operation offset.
- Provides `default_dev_ops` and `dead_dev_ops`.
- Wraps device open/close/read/write/ioctl/mmap/strategy/dump/psize/kqfilter/clone/revoke calls.
- Applies MPLock around non-`D_MPSAFE` device operations.
- Handles KVABIO synchronization for device strategies when drivers lack `D_KVABIO`.
- Tracks per-device read/write I/O via `bio_track`.
- Fills missing `dev_ops` function pointers with default handlers.
- Supports temporary dev_ops interception/restoration.
- Exposes simple device metadata helpers.

## Main Entry Points

- `dev_dopen()`, `dev_dclose()`, `dev_dread()`, `dev_dwrite()`, `dev_dioctl()`.
- `dev_dmmap()`, `dev_dmmap_single()`.
- `dev_dclone()`, `dev_drevoke()`.
- `dev_dstrategy()` and `dev_dstrategy_chain()` submit block I/O strategies.
- `dev_ddump()` and `dev_dpsize()` support dump and size queries.
- `dev_dkqfilter()` forwards kqueue filter registration.
- `dev_drefs()`, `dev_dname()`, `dev_dflags()`, `dev_dmaj()` expose device metadata.
- `dev_doperate()` dispatches an operation by descriptor offset.
- `dev_doperate_ops()` dispatches through a foreign ops structure, used by console interception.
- `compile_dev_ops()` fills NULL operation slots.
- `dev_ops_remove_all()` and `dev_ops_remove_minor()` destroy devfs devices associated with ops.
- `dev_ops_intercept()` / `dev_ops_restore()` swap per-device ops for interception.

## Important Implementation Details

- `dev_needmplock()` checks `D_MPSAFE`; wrappers acquire/release `get_mplock()` around non-MPSAFE driver calls.
- `dev_nokvabio()` checks `D_KVABIO`; strategy wrappers call `bkvasync_all()` for KVABIO buffers if the driver cannot handle them.
- `dev_dstrategy()` asserts no existing `bio_track`, selects read/write tracking, enters disk scheduler accounting via `dsched_buf_enter()`, and dispatches.
- `dev_dstrategy_chain()` assumes `bio_track` was already set by an upstream chained strategy path.
- `compile_dev_ops()` iterates from `dev_ops_first_field` through `dev_ops_last_field`, assigning either `d_default` or the `default_dev_ops` slot.
- Default unsupported ops generally return `ENODEV`; default strategy marks the buffer `B_ERROR`, sets `EOPNOTSUPP`, and calls `biodone()`.

## Data and Registration

- `DEVOP_DESC_INIT()` creates operation descriptors such as `dev_open_desc`, `dev_strategy_desc`, and `dev_ioctl_desc`.
- `default_dev_ops` supplies fallback implementations.
- `dev_ops_rbhead` is declared with RB-tree generation for major-number tracking, though this file’s visible add/remove paths are delegated to devfs helpers.
- `dead_dev_ops` exists for destroyed devices and is referenced by other device code.

## Filesystem/Storage Relevance

This file is the call path between VFS/device vnodes and block/character drivers. Storage I/O reaches device drivers through `dev_dstrategy()` and related wrappers, so this layer mediates locking, buffer mapping constraints, disk scheduler entry, and error fallback behavior.

## Research Notes

- Strategy path comments distinguish normal and chained BIO submission; chained submission intentionally does not push a new tracking structure.
- Operation interception copies major/data/flags from old ops to interceptor ops, sets `SI_INTERCEPTED`, then restores and clears those fields later.
- Default `noclone()` returns success, allowing clone unless a driver overrides it.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_device.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_dmsg.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_dmsg.c

## Purpose

Implements the kernel DMSG messaging layer used for stateful message transactions over a file-backed communication endpoint such as a socket or pipe. It manages IO threads, message framing, transaction state trees, parent/child circuit topology, automatic link messages, abort/failure simulation, and message allocation/freeing.

## Key Responsibilities

- Initializes and reconnects `kdmsg_iocom_t` communication sessions.
- Runs one read thread and one write thread per iocom.
- Reads/writes DMSG headers and aligned auxiliary payloads through `fp_read()` / `fp_write()`.
- Tracks persistent message transactions in red-black trees by message ID.
- Tracks nested/circuit transactions through parent `subq` queues.
- Handles CREATE/DELETE/REPLY/ABORT protocol state transitions.
- Provides automatic handling for link-level `LNK_CONN`, `LNK_SPAN`, and `LNK_PING` messages.
- Simulates transaction failures on link loss so upper layers get cleanup callbacks.
- Computes header and auxiliary CRCs before transmit.
- Exposes `kdmsg.debug` sysctl.

## Main Data Structures and State

- `kdmsg_iocom_t`: owns locks, file pointer, message queue, state trees, IO threads, auto link fields, sequence number, flags, and callbacks.
- `kdmsg_state_t`: represents a persistent transaction, with `rxcmd`, `txcmd`, `icmd`, `msgid`, parent/subq topology, refs, flags, callback, and private data.
- `kdmsg_msg_t`: carries a DMSG header union, optional aux data, transaction state pointer, and queue linkage.
- `staterd_tree`: received command transactions.
- `statewr_tree`: locally initiated outbound transactions.
- `state0`: root state for one-off messages and top-level transactions.
- `freerd_state` / `freewr_state`: cached state objects used by receive/transmit paths.

## Initialization and Connection Flow

- `kdmsg_iocom_init()` zeroes and initializes an iocom, message lock, queue, state trees, root state, allocator type, callback, and flags.
- `kdmsg_iocom_reconnect()` stops existing IO threads, drops the old file, installs a new file pointer, resets sequencing/control flags, and creates read/write threads.
- `kdmsg_iocom_autoinitiate()` sends an automatic `DMSG_LNK_CONN | DMSGF_CREATE` and optionally stores the resulting connection state.

## IO Threads

- `kdmsg_iocom_thread_rd()`:
  - Reads fixed header, validates magic and header size.
  - Allocates a message based on base command.
  - Reads extended header and aligned auxiliary data.
  - Checks payload size against `DMSG_AUX_MAX`.
  - Passes the message to `kdmsg_msg_receive_handling()`.
  - On error/shutdown, shuts down the file and signals TX termination.

- `kdmsg_iocom_thread_wr()`:
  - Sleeps while the transmit queue is empty.
  - Dequeues messages and runs `kdmsg_state_msgtx()`.
  - Writes header and optional aux payload.
  - Calls `kdmsg_state_cleanuptx()` even on write failure after state transition.
  - On termination, waits for RX to exit, drains queued messages, simulates failures, and waits for all states to disappear before exit.

## Receive State Machine

- `kdmsg_msg_receive_handling()` runs state lookup/update via `kdmsg_state_msgrx()`, then dispatches to:
  - `msg->state->func` if the state has a callback.
  - `kdmsg_autorxmsg()` when automatic link handling is enabled.
  - `iocom->rcvmsg()` otherwise.
- `kdmsg_state_msgrx()`:
  - Looks up state by message ID in read or write tree depending on `DMSGF_REVTRANS`.
  - Handles one-off messages without CREATE/DELETE/ABORT.
  - Creates new state for received transaction CREATE messages.
  - Validates DELETE, REPLY|CREATE, REPLY|DELETE, and ABORT races.
  - Removes fully closed states from RB trees after both RX and TX sides are deleted.
  - Computes `msg->tcmd` for higher-level switch dispatch.

## Transmit State Machine

- `kdmsg_state_msgtx()`:
  - Validates CREATE/DELETE/REPLY/ABORT combinations before transmit.
  - Initializes outbound transaction state on CREATE.
  - Detects already-closed or reused states and returns `EALREADY` for harmless raced abort/delete cases.
  - Sets `KDMSG_STATE_INTERLOCK` while a send may block, preventing receive-side races.
- `kdmsg_state_cleanuptx()`:
  - Clears interlock and wakes any waiters.
  - Marks TX DELETE.
  - Removes fully closed states from the appropriate RB tree.
  - Removes leaf subq topology when possible.
  - Executes deferred aborts if a state became dying/aborting during send.

## Failure and Abort Handling

- `kdmsg_drain_msgq()` drains queued TX messages during shutdown.
- `kdmsg_drain_msg()` simulates send-side processing and link failure for a message’s state.
- `kdmsg_simulate_failure()` recursively walks a state’s subtransactions and calls `kdmsg_state_abort()`.
- `kdmsg_state_abort()` marks a state aborting/dying and synthesizes a received `DMSG_LNK_ERROR` DELETE message if RX is not already closed.
- `kdmsg_state_dying()` recursively prevents new transmissions on a state and its children.
- `kdmsg_subq_delete()` unlinks a state from its parent queue and drops parent/subq references.

## Message API

- `kdmsg_msg_alloc()` allocates messages and, for outbound CREATE commands, allocates/inserts a new transaction state with a msgid derived from the state pointer.
- `kdmsg_msg_free()` releases aux data, drops state reference, and frees message memory.
- `kdmsg_detach_aux_data()` transfers aux buffer ownership to `kdmsg_data_t`.
- `kdmsg_free_aux_data()` frees detached aux buffers.
- `kdmsg_msg_write()` / `kdmsg_msg_write_locked()` compute CRCs, assign sequence salt, set msgid/circuit fields, and queue or drain messages.
- `kdmsg_msg_reply()` / `kdmsg_msg_result()` reply to a message with a `DMSG_LNK_ERROR` result, either terminating or continuing the transaction.
- `kdmsg_state_reply()` / `kdmsg_state_result()` do the same from a held state.

## Automatic Link Handling

- `kdmsg_lnk_conn_reply()` reacts to `LNK_CONN` acknowledgements and can automatically start `LNK_SPAN`.
- `kdmsg_lnk_span_reply()` handles span callbacks and termination.
- `kdmsg_autorxmsg()` automatically replies to pings, acknowledges/maintains/terminates auto connection and span transactions, and delegates unhandled messages to `iocom->rcvmsg()`.

## Filesystem/Storage Relevance

DMSG is not a local filesystem implementation itself, but it is relevant to DragonFlyBSD storage/filesystem infrastructure because it provides a stateful kernel messaging substrate used by higher-level distributed/block/filesystem components. Its transaction/circuit semantics are suitable for asynchronous storage protocol operations that need explicit create/delete lifecycle and link-loss cleanup.

## Research Notes

- State lifetime is reference-counted and constrained by RB-tree insertion, parent subq insertion, message ownership, and cached free-state references.
- Link-loss handling is intentionally callback-driven: upper layers receive synthetic transaction termination messages to clean up asynchronous operations.
- The code has a visible typo/bug-like diagnostic path in `kdmsg_state_abort()` using `kdio_printf(iocom, ...)` where no local `iocom` variable is declared in that function body; macro expansion depends on a valid symbol and this would be suspicious in isolation.
- Protocol race handling treats many ABORT+DELETE races as `EALREADY` and discards them without failing the connection.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_dmsg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_dsched.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_dsched.c

## Purpose

Stub implementation for disk scheduler lifecycle hooks. The file declares the expected disk scheduler integration points but leaves them empty.

## Key Responsibilities

- Provides callable hooks for disk creation, disk info update, and disk destruction.
- Preserves build/link compatibility for callers expecting dsched integration.

## Main Entry Points

- `dsched_disk_create(struct disk *dp, const char *head_name, int unit)`: intended to choose/read a scheduler policy when a disk is created.
- `dsched_disk_update(struct disk *dp, struct disk_info *info)`: intended to associate policies with disk serial/device info.
- `dsched_disk_destroy(struct disk *dp)`: intended to shut down scheduler state and cancel remaining BIOs.

## Current Behavior

All three functions are empty. Comments describe intended responsibilities, but no scheduler state, policy lookup, or BIO cancellation is implemented in this file.

## Dependencies

Includes disk, buffer, device, msgport, dsched, and fcntl headers, implying this file is a placeholder for a larger disk scheduling subsystem.

## Filesystem/Storage Relevance

Directly storage-facing, but currently inert. Device strategy dispatch in `kern_device.c` calls `dsched_buf_enter()`, while this file would be the disk lifecycle side of scheduler integration if implemented.

## Research Notes

- This file should be treated as a compatibility or disabled-feature shim.
- Any analysis of actual disk scheduling behavior must look outside this file, especially `sys/dsched.h` and any enabled scheduler implementation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_dsched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_environment.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_environment.c

## Purpose

Implements DragonFlyBSD kernel environment variable storage, syscalls, tunable fetching helpers, boot-time static environment sysctl traversal, and conversion from bootloader-provided static environment strings to a dynamic kernel-managed array.

## Key Responsibilities

- Maintains `kern_envp`, the bootloader-provided static environment pointer.
- Converts static environment strings into dynamic kernel storage during boot.
- Implements `sys_kenv()` for userland get/set/unset/dump operations.
- Provides in-kernel `kgetenv`, `ksetenv`, `kunsetenv`, `ktestenv`, `kfreeenv`, and typed fetch helpers.
- Supports tunable initialization wrappers for int, long, ulong, quad, and string tunables.
- Exposes static boot environment via `kern.environment` sysctl node.

## Main State

- `kern_envp`: exported static boot environment.
- `kenv_dynp`: dynamic NULL-terminated array of `name=value` strings.
- `kenv_isdynamic`: indicates dynamic environment availability.
- `kenv_dynlock`: spinlock protecting dynamic environment access.
- `M_KENV`: malloc type for dynamic environment storage.
- `KENV_DYNMAXNUM`: maximum dynamic environment entries, 512.

## Syscall Behavior

`sys_kenv()` handles:

- `KENV_DUMP`:
  - Computes needed bytes for all dynamic environment strings.
  - Optionally copies bounded data into a temporary kernel buffer and then out to userland.
  - Returns 0 if full dump fit, or required size if truncated.

- `KENV_GET`:
  - Copies in the name.
  - Uses `kgetenv()`.
  - Copies out up to the user-supplied length.
  - Returns copied length.

- `KENV_SET` and `KENV_UNSET`:
  - Require `caps_priv_check_self(SYSCAP_NOKENV_WR)`.
  - Set or remove dynamic variables.

## Environment Helpers

- `kenv_getstring_dynamic()` searches the dynamic array under lock and optionally returns the index.
- `kenv_getstring_static()` walks the bootloader string block.
- `kernenv_next()` advances through the static NUL-separated environment block.
- `kgetenv()` returns a dynamic malloc copy once dynamic storage exists; before that, it returns a pointer into static storage.
- `ksetenv()` replaces or appends a `name=value` string, enforcing `KENV_MNAMELEN` and `KENV_MVALLEN`.
- `kunsetenv()` removes an entry and compacts the array.
- `kfreeenv()` frees only dynamic copies.
- `ktestenv()` checks for variable existence.
- `kgetenv_string()`, `kgetenv_int()`, `kgetenv_long()`, `kgetenv_ulong()`, `kgetenv_quad()` parse typed values. `kgetenv_quad()` supports `k/m/g/t` suffixes as powers of 1024.

## Boot and Sysctl Integration

- `sysctl_kenv_boot()` exposes indexed static boot environment strings under `kern.environment`.
- `kenv_init()` allocates `kenv_dynp`, copies static environment entries, initializes the spinlock, and sets `kenv_isdynamic`.
- `SYSINIT(kenv, SI_BOOT1_POST, SI_ORDER_ANY, kenv_init, NULL)` performs dynamic setup early after boot stage 1.
- `tunable_*_init()` wrappers fetch tunable values into registered variables.

## Filesystem/Storage Relevance

Kernel environment and tunables influence storage/VFS boot behavior, such as root device selection, driver tunables, debug flags, and filesystem module configuration. This file is the core source of those boot-time and runtime tunable values.

## Research Notes

- Dynamic environment access is spinlock-protected and copies values out before allocating/freeing outside the lock where needed.
- Static-mode `kgetenv()` returns non-owned static memory; dynamic-mode returns owned memory that must be released with `kfreeenv()`.
- `KENV_DUMP` caps buffer size to the maximum possible dynamic environment payload.
- Set/unset are blocked until the dynamic array exists; early boot code must rely on static lookup.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/kern_environment.c -->