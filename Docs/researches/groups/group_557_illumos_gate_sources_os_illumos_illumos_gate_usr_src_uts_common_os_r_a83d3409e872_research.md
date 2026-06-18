# Group Research: group_557_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_r_a83d3409e872

Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`. All source files listed for this group were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rctl.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rctl.c

## Purpose

Core kernel implementation of illumos resource controls (`rctl`). It lets subsystems register named controls, attach ordered control-value lists to process-model entities, enforce limits, translate legacy `rlimit` state, trigger actions, and maintain resource accounting for zone/project memory, swap, and lofi limits.

## Main Concepts

- Global dictionaries map resource-control handles and names to `rctl_dict_entry_t` definitions.
- Each controlled entity owns an `rctl_set_t` hash table of `rctl_t` instances keyed by handle.
- Each `rctl_t` has an ordered doubly linked list of `rctl_val_t` values plus an active `rc_cursor`.
- Ordering is by maximal flag, numeric value, deny action, privilege, and optionally action recipient.
- Controls apply to process, task, project, or zone entities.
- Project database values are cached separately in `rc_projdb` and synchronized with active `rc_values`.

## Key Entry Points

- `rctl_init()` creates caches, dictionaries, ID space, entity lists, and calls `rctlproc_init()`.
- `rctl_register()` registers a new named control, allocates its system value, assigns an ID, inserts global dictionary/list state, and panics on duplicate registration.
- `rctl_build_name_buf()`, `rctl_dict_lookup()`, `rctl_hndl_lookup()`, `rctl_dict_lookup_hndl()` expose lookup helpers.
- `rctl_set_create()`, `rctl_set_init_prealloc()`, `rctl_set_init()`, `rctl_set_dup_prealloc()`, `rctl_set_dup()`, `rctl_set_free()`, `rctl_set_reset()`, and `rctl_set_tearoff()` manage entity-local sets and fork/exec-style duplication.
- `rctl_local_get()`, `rctl_local_insert()`, `rctl_local_delete()`, `rctl_local_replace()`, `rctl_local_insert_all()`, and `rctl_local_replace_all()` implement local value mutation.
- `rctl_rlimit_get()`, `rctl_rlimit_set_prealloc()`, and `rctl_rlimit_set()` bridge POSIX-style soft/hard limits to resource-control values.
- `rctl_test()`, `rctl_test_entity()`, `rctl_action()`, and `rctl_action_entity()` perform enforcement and action delivery.
- `rctl_incr_locked_mem()`, `rctl_decr_locked_mem()`, `rctl_incr_swap()`, `rctl_decr_swap()`, `rctl_incr_lofi()`, and `rctl_decr_lofi()` charge and uncharge project/zone resources.
- `rctl_kstat_create_zone()`, `rctl_kstat_create_project()`, and `rctl_kstat_create_task()` create caps kstats.

## Locking and Allocation Model

- Documented lock order is `p_lock`, `rctl_dict_lock`, `rctl_lists_lock`, then `entity->rcs_lock`.
- The file avoids `KM_SLEEP` allocations while holding dictionary/list locks by using preallocation groups (`rctl_alloc_gp_t`) for set initialization, duplication, and rlimit mutation.
- `rctl_local_op()` requires `p_lock` and then locks the selected entity set.
- `rctl_local_action()` may drop `p_lock` and `rcs_lock` to allocate `sigqueue_t` or find a recipient process; it returns `RCT_LK_ABANDONED` so callers can reacquire and rewalk safely.
- Memory/resource charges use zone locks (`zone_mem_lock`, `zone_rctl_lock`) around accounting and rctl tests.

## Enforcement Behavior

- Global action logs exceeded controls through `strlog()` when `RCTL_GLOBAL_SYSLOG` is set and may force deny via `RCTL_GLOBAL_DENY_ALWAYS`.
- Local action can signal the violating process/thread or a registered recipient process and can deny operations for local deny actions.
- If an action does not deny and another value exists, enforcement advances `rc_cursor` to the next value and invokes the control's set callback.
- Kernel process `p0` is explicitly exempt from `rctl_test_entity()`.

## Dependencies

Uses kernel facilities including `mod_hash`, `id_space`, `kmem_cache`, process/task/project/zone structures, signals, credentials/policy, kstats, logging, and rctl ops vectors from subsystem registration files such as `rctl_proc.c`.

## Notes for Future Work

- Duplicate registration currently panics; the comments describe possible future unloadable-module support but it is not implemented here.
- The `rc_projdb` paths are sensitive to preallocation correctness because they intentionally mutate active and cached value lists under locks.
- Signal-recipient delivery has non-trivial lock dropping and entity membership revalidation; changes here should be tested against process exit, project/task movement, and unobservable controls.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rctl_proc.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rctl_proc.c

## Purpose

Registers and initializes process-scoped resource controls, including the controls that back legacy `RLIMIT_*` behavior and several System V IPC, event port, and signal queue process limits.

## Key Interfaces and State

- `rctlproc_legacy[RLIM_NLIMITS]` maps legacy rlimit indices to rctl handles.
- `rctlproc_flags[]` and `rctlproc_signals[]` define default local action flags and signals for legacy rlimits.
- Exported handles include `rc_process_msgmnb`, `rc_process_msgtql`, `rc_process_semmsl`, `rc_process_semopm`, `rc_process_portev`, and `rc_process_sigqueue`.
- `rctlproc_default_init()` seeds `init` process defaults for CPU, file size, data, stack, core, file descriptors, and virtual memory.
- `rctlproc_init()` registers all process controls and creates the initial `curproc->p_rctls` set for the scheduler process.

## Control-Specific Behavior

- `process.max-cpu-time` uses `proc_cpu_time_test()` and fires when the passed increment is greater than or equal to the current value.
- `process.max-file-size` updates `p_fsz_ctl` through `proc_filesize_set()`.
- `process.max-stack-size` updates `p_stk_ctl` and records the old stack control in the current LWP so post-syscall handling can adjust user stack bounds.
- `process.max-file-descriptor` updates `p_fno_ctl` and uses `rcop_absolute_test()`.
- `process.max-address-space` updates `p_vmem_ctl`.
- Data and core size use default operations.

## Dependencies

Depends on `rctl.c` registration and rlimit translation helpers, process model fields (`p_fsz_ctl`, `p_stk_ctl`, `p_fno_ctl`, `p_vmem_ctl`), signal constants, system tunables such as `rlim_fd_cur`/`rlim_fd_max`, and legacy System V IPC module variables read via `rctl_add_legacy_limit()`.

## Notes for Future Work

- Architecture-specific stack maxima differ across SPARC, non-SPARC LP64, and non-LP64 builds.
- The stack callback intentionally has special handling for the calling LWP and is not a general safe way to resize another process's stack.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rctl_proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/refstr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/refstr.c

## Purpose

Small reference-counted string utility for kernel users that need immutable strings with shared ownership.

## Key Interfaces

- `refstr_alloc()` allocates one object containing size, 32-bit reference count, and NUL-terminated string data.
- `refstr_value()` returns the stored string pointer or `NULL`.
- `refstr_hold()` atomically increments the reference count.
- `refstr_rele()` atomically decrements and frees the exact allocation size when the count reaches zero.

## Dependencies

Uses `kmem_alloc()`, `kmem_free()`, `strlen()`, `strcpy()`, and `atomic_inc_32()`/`atomic_dec_32_nv()`.

## Notes for Future Work

- `refstr_alloc()` asserts the computed allocation size fits in `uint32_t`.
- The API assumes callers do not mutate the returned string and do not release more times than held.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/refstr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/retire_store.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/retire_store.c

## Purpose

Implements the persistent I/O retire store backed by `/etc/devices/retire_store`. It decodes retired device paths from an nvlist-backed cache, tracks them in memory, writes updates back through the devcache framework, and answers whether a device path is retired for the current boot.

## Data Model

- On-disk entries are keyed by device path and contain version, magic, and flags.
- `RIO_STORE_F_RETIRED` is persisted; `RIO_STORE_F_BYPASS` is an in-memory boot-time override and is intentionally not encoded.
- In-memory entries are `rio_store_t` nodes containing a duplicated device path, flags, and list linkage.

## Key Interfaces

- `retire_store_init()` handles optional boot-time path override or `/dev/null` bypass, registers nvf file ops, and initializes the in-core list.
- `retire_store_read()` reads the store under the nvf write lock.
- `rio_store_decode()` validates version/magic/flags and appends a retired entry, adding the bypass flag when `ddi_retire_store_bypass` is set.
- `rio_store_encode()` serializes active retired entries to nested nvlists.
- `e_ddi_retire_persist()` adds or refreshes a retired device path, marks the store dirty, and wakes the nvf daemon.
- `e_ddi_retire_unpersist()` removes matching entries and wakes the daemon if the store changed.
- `e_ddi_device_retired()` returns true if the device path itself or one of its parents is in the retired list and not bypassed.

## Locking and Lifetime

- The nvf lock protects the list; decode/free/encode assert write ownership and lookup uses reader ownership.
- List entries own their path string and are freed by `rio_store_free()`.
- `retire_list_free()` frees all in-core entries during devcache lifecycle operations.

## Dependencies

Depends on devcache/nvf APIs, nvlists, kernel lists, boot flags, console input for `RB_ASKNAME`, and DDI path duplication helpers.

## Notes for Future Work

- The bypass mode deliberately reads existing store content so later explicit unretire operations can still remove persisted decisions.
- `e_ddi_device_retired()` treats a retired parent path as retiring descendants by checking exact match or slash boundary.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/retire_store.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rmap.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rmap.c

## Purpose

Compatibility wrapper implementing legacy resource-map allocation interfaces on top of the kernel `vmem` allocator.

## Key Interfaces

- `rmallocmap()` and `rmallocmap_wait()` create a `vmem` arena named `rmap` with non-sleeping or sleeping allocation behavior.
- `rmfreemap()` destroys the arena.
- `rmalloc()` and `rmalloc_wait()` allocate from the arena and return the address as `ulong_t`.
- `rmfree()` frees an existing contained range, or adds the range to the arena if it was not already contained.

## Dependencies

Uses `vmem_create()`, `vmem_destroy()`, `vmem_alloc()`, `vmem_contains()`, `vmem_free()`, `vmem_add()`, and `cmn_err()`.

## Notes for Future Work

- `rmfree()` warns if it cannot add an out-of-arena segment back to the vmem arena.
- The legacy `mapsize` parameter is ignored because `vmem` supplies the backing behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rwlock.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rwlock.c

## Purpose

Full kernel readers/writer lock implementation with direct turnstile handoff, priority-aware wakeup policy, lockstat probes, panic diagnostics, try/upgrade/downgrade operations, and ownership introspection.

## Lock Representation

The lock is a single machine word containing reader hold count or writer owner pointer plus three low bits: waiters, writer wanted, and write locked.

## Key Interfaces

- `rw_init()` and `rw_destroy()` initialize/destroy the word and detect double destroy or active destroy.
- `rw_enter_sleep()` handles contended acquisitions for reader, writer, and starve-writer reader modes.
- `rw_exit_wakeup()` handles final release, turnstile wakeup, and handoff.
- `rw_tryenter()` implements nonblocking read/write acquisition.
- `rw_downgrade()` converts writer ownership to reader ownership and may wake compatible readers.
- `rw_tryupgrade()` converts a sole reader to writer when no other readers/writers block it.
- State helpers include `rw_read_held()`, `rw_write_held()`, `rw_lock_held()`, `rw_read_locked()`, `rw_iswriter()`, and `rw_owner()`.

## Dependencies

Uses turnstiles, sleep object ops, dispatcher priorities, CPU stats, lockstat, atomic primitives, and thread pointers encoded in the lock word.

## Notes for Future Work

- Recursive read acquisition can deadlock when a writer arrives between acquisitions; `RW_READER_STARVEWRITER` exists for specific lock-ordering cases.
- Panic diagnostics save the offending lock address and word before panicking.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rwlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rwstlock.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rwstlock.c

## Purpose

Implements an alternate reader/writer lock that is interruptible and may be released by a thread other than the acquirer. It lacks priority inheritance and is built from a mutex plus reader/writer condition variables.

## Key Interfaces

- `rwst_enter()`, `rwst_enter_sig()`, and `rwst_tryenter()` acquire the lock.
- `rwst_exit()` releases reader or writer state and wakes readers or one writer according to writer-wanted state.
- `rwst_lock_held()` checks reader or writer state.
- `rwst_init()`/`rwst_destroy()` initialize and destroy internal synchronization.
- `rwst_owner()` returns the encoded owner.

## Dependencies

Uses `rwstlock_t` macros from `sys/rwstlock.h`, mutexes, condition variables, panic state, lockstat probes, and `krw_t` modes.

## Notes for Future Work

- This lock intentionally trades away priority inheritance and strict owner release in exchange for interruptibility and cross-thread release.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rwstlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sched.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sched.c

## Purpose

Implements the historical memory scheduler/swapper. It swaps LWPs and process address spaces in or out based on free-memory pressure, scheduling-class swap priorities, sleep time, and safe swap points.

## Key Interfaces and Flow

- `sched()` is the main loop: processes queued safe-point swapouts, detects desperate memory conditions, scans processes, chooses swap-in candidates, performs soft/hard swapout, and blocks on `runout` or `runin`.
- `swapin()` faults swapped kernel stacks back into memory, sets `TS_LOAD`, decrements process swap counts, updates stats, and requeues runnable threads.
- `swapout()` marks or removes swappable threads, unlocks stack pages, increments process swap counts, and swaps out the address space when all LWPs are out.
- `swapout_lwp()` is called by an LWP reaching a safe point after `TS_SWAPENQ`.
- `process_swap_queue()` drains `tswap_queue`, unloads stacks, and swaps address spaces when all LWPs are swapped.

## Dependencies

Uses scheduling-class callbacks `CL_SWAPIN`/`CL_SWAPOUT`, dispatcher queues, segkp stack backing, address-space swapout, module reclaim, CPR callbacks, DTrace scheduler probes, CPU VM stats, and process/thread state flags.

## Notes for Future Work

- The code is deeply tied to legacy swapping semantics and safe-point flags such as `TS_DONT_SWAP`, `TS_SWAPENQ`, `TS_ON_SWAPQ`, and `TS_LOAD`.
- Error from stack soft-unlock during swapout is treated as fatal panic.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/schedctl.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/schedctl.c

## Purpose

Implements scheduler-control shared pages mapped between kernel and user space. These pages allow libc/libthread and the kernel scheduler to exchange LWP scheduling, preemption, cancellation, signal-blocking, and parking state efficiently.

## Key Interfaces

- `schedctl()` allocates and maps a shared slot for the current LWP if missing, installs context ops, initializes scheduling fields, and returns the user address.
- `schedctl_lwp_cleanup()` removes context ops for an exiting/execing LWP and frees its slot bitmap entry without unmapping the page.
- `schedctl_proc_cleanup()` unmaps all scheduler-control pages and frees page-control metadata during process exec/exit.
- Context ops update state/CPU or remove inherited child mappings.
- Scheduler hooks update or read no-preempt, yield, class ID/priority, signal-blocking, cancellation, and park flags.
- Page helpers manage allocation, mapping, lookup, and teardown.

## Dependencies

Uses context-operation infrastructure, VM address-space mapping, anonymous memory, segkp/segvn, bitmaps, thread scheduling fields, signal masks, cancellation flags, and process lifecycle hooks.

## Notes for Future Work

- Cleanup deliberately leaves pages mapped after LWP cleanup because user-level adaptive mutex code can rely on stale mappings until process teardown.
- `schedctl_page_lookup()` returns `NULL` for a condition marked as should-not-happen; callers assume a valid page.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/schedctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sctp_crc32.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sctp_crc32.c

## Purpose

Provides SCTP CRC32 checksum support using the reflected polynomial required by RFC 3309 and a four-table word-at-a-time algorithm.

## Key Interfaces

- `sctp_crc32_init()` builds four 256-entry CRC tables from `SCTP_POLY`.
- `sctp_crc32()` updates a supplied CRC over a byte buffer, handling unaligned leading/trailing bytes and aligned word chunks.
- Internal helpers `reflect_32()`, `sctp_crc_byte()`, and `sctp_crc_word()` perform bit reflection and byte/word updates.
- `flip32()` is compiled only for big-endian systems.

## Notes for Future Work

- `sctp_crc32()` aligns by processing leading bytes before casting to `uint32_t *`.
- Big-endian and little-endian table layout differs, so checksum changes should be verified on both endian modes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sctp_crc32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/semaphore.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/semaphore.c

## Purpose

Implements kernel counting semaphores with dispatcher sleep queues, priority-ordered waiters, interruptible waits, cancellation integration, wakeup handling, and sleep-object operations.

## Key Interfaces

- `sema_init()` initializes count and empty sleep queue.
- `sema_destroy()` asserts no waiters.
- `sema_p()` performs uninterruptible acquire, blocking while count is zero.
- `sema_p_sig()` performs interruptible acquire and returns `1` on signal, abort, must-return, or pending cancellation.
- `sema_v()` increments count and wakes the highest-priority waiter if present.
- `sema_tryp()` attempts nonblocking acquire.
- `sema_held()` returns whether count is nonpositive.

## Dependencies

Uses sleep queues, dispatcher locks, class sleep/wakeup hooks, signal and cancellation checks, schedctl cancellation helpers, DTrace scheduler probes, and LWP accounting.

## Notes for Future Work

- `sema_p_sig()` handles the race where `sema_v()` and interruption happen together by passing the semaphore count/wakeup to the next sleeping thread.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/semaphore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/serializer.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/serializer.c

## Purpose

Implements kernel serializers: a general-purpose mechanism that executes submitted callbacks one at a time in arrival order, commonly as a lighter alternative to STREAMS outer perimeters.

## Key Interfaces

- `serializer_init()` creates the kmem cache.
- `serializer_create()` allocates a serializer.
- `serializer_enter()` executes immediately if unowned, otherwise queues the request and returns. The owner drains queued work up to `serializer_credit`, then may schedule taskq drain work.
- `serializer_wait()` waits until no owner, no pending taskq drain, and no queued messages remain.
- `serializer_destroy()` waits and then frees the serializer.
- Internal helpers execute, enqueue, and drain callback work.

## Dependencies

Uses kernel mutexes, condition variables, taskq dispatch, kmem caches, STREAMS message blocks, and DTrace SDT probes for enqueue and execution boundaries.

## Notes for Future Work

- Callers must pass an `mblk_t` with `b_next` and `b_prev` clear; the serializer temporarily owns these fields.
- If taskq dispatch fails, direct draining can continue in later `serializer_enter()` calls.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/serializer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/session.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/session.c

## Purpose

Manages process sessions and controlling terminal lifecycle: session reference counts, session creation, safe controlling-tty lookup, ctty assignment, ctty release, SIGHUP delivery, and compatibility `vhangup()` behavior.

## Key Interfaces

- `sess_hold()` and `sess_rele()` manage session references.
- `tty_hold()` obtains a stable current session and ctty-related hold, waiting if the session leader is exiting and clearing the ctty.
- `tty_rele()` releases a ctty hold and session reference.
- `sess_create()` creates a new session for `curproc`, updates process group/session links, and releases the old session.
- `strctty()` makes a stream the controlling tty for a session leader after validating stream/session state and waiting for outstanding tty holds.
- `freectty()` releases the current session leader's controlling tty, sends SIGHUP/stream hangup once, waits for outstanding holds, clears bindings, closes/releases vnode and credentials, and releases pid holds.
- `vhangup()`, `cttydev()`, and `ctty_clear_sighuped()` provide compatibility and query helpers.

## Dependencies

Depends on process/session/pid structures, STREAMS `stdata_t`, vnode close/release operations, credentials, signal delivery, stream hangup, and security policy for `vhangup()`.

## Notes for Future Work

- The comments highlight intentionally complex lock ordering; changes must preserve the temporary hold patterns around lock drops.
- `freectty()` returns `EIO` when there is no releasable ctty and `1` on successful release, which is unusual but established here.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/session.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/share.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/share.c

## Purpose

Implements vnode share reservations, including DOS/Windows-compatible deny modes, compatibility-mode semantics, cleanup by process or remote system ID, remote-share detection, and NBMAND share conflict checks for local/NFS/CIFS interoperability.

## Key Interfaces

- `add_share()` validates and adds a `shrlock` reservation to `vp->v_shrlocks` after checking conflicts.
- `del_share()` removes matching reservations and wakes waiters if an NBMAND share was removed.
- `cleanshares()` removes local shares for a process.
- `cleanshares_by_sysid()` removes remote shares for a system ID.
- `shr_has_remote_shares()` reports whether any remote share, or a share by a specific remote ID, exists.
- `nbl_share_conflict()` checks mandatory share reservations against read, write, read/write, remove, and rename operations.
- `proc_has_nbmand_share_on_vp()` reports whether a local process has an NBMAND share on a vnode.

## Dependencies

Uses vnode state, share/lock constants, NBMAND lock helpers, DTrace conflict probes, `vn_is_readonly()`, NLM sysid encoding macros, and caller context for remote/local operation identity.

## Notes for Future Work

- `add_share()` permits zero access only for remote systems for compatibility with older clients.
- `nbl_share_conflict()` intentionally skips mandatory share reservations owned by the same `(sysid, pid)` for I/O checks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/share.c -->