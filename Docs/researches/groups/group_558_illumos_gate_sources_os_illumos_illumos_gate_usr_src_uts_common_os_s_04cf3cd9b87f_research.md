# Group Research: group_558_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_s_04cf3cd9b87f

Scope: `Docs/research_subset_a.md`, source tree `sources/os/illumos/illumos-gate`.

Read completely: `shm.c`, `sid.c`, `sig.c`, `sleepq.c`, `smb_subr.c`, `softint.c`, `space.c`.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/shm.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/shm.c

Implements the illumos System V shared memory syscall module. It registers the `shmsys` syscall entry, exposes `shmat`, `shmctl`, `shmdt`, `shmget`, and `shmids`, and stores segment state in the generic IPC service layer.

Key responsibilities:
- Creates the `shmids` IPC service in `_init()` with project and zone resource controls for ID count and memory consumption.
- Enforces `zone.max-shm-ids`, `project.max-shm-ids`, `zone.max-shm-memory`, and `project.max-shm-memory`.
- Preserves obsolete `shminfo_*` tunables for compatibility.
- Maps shared memory through anonymous memory, `segvn`, and shared page table segments for ISM/DISM.
- Tracks per-process shared-memory mappings in `proc_t.p_segacct`, an AVL tree used by detach, fork, exit, and `/proc` lookup.

Important paths:
- `shmget()` creates or looks up a segment. New segments reserve anonymous memory with `anon_resv()`, allocate an `anon_map`, initialize IPC metadata, then commit through `ipc_commit_begin()` / `ipc_commit_end()`.
- `shmat()` validates permissions and flags, chooses normal `segvn_create` mapping or ISM/DISM `segspt_shmattach`, performs address alignment/range checks, maps into the process address space, and records a `segacct_t`.
- `shmdt()` removes the exact starting-address entry from `p_segacct`, unmaps the address range, updates detach accounting, and releases the IPC hold.
- `shmctl()` implements `IPC_SET`, `IPC_STAT`, 64-bit variants, `IPC_RMID`, `SHM_LOCK`, and `SHM_UNLOCK`.
- `shmfork()` duplicates parent segment-accounting records into a child and increments IPC references.
- `shmexit()` detaches all segments during process exit.
- `shmgetid()` supports `/proc` address-to-shmid lookup without taking `p_lock`.

Memory and locking model:
- IPC object locks come from `ipc_lookup()`, `ipc_get()`, and `ipc_lock()`.
- Address-space changes are protected by `as_rangelock()`.
- Anonymous map size/refcount/page state uses `ANON_LOCK_ENTER`.
- Per-process mapping records use `p_lock` plus `prbarrier()` to coordinate with `/proc`.
- Locked shared memory uses a temporary address space, `MC_LOCK`, page lookup, page lock counts, and locked-memory rctl accounting.

Filesystem relevance:
- This is VM/IPC rather than filesystem code, but it is directly relevant to the OS memory substrate used alongside VFS behavior. It exercises anon/swap objects, vnode-backed swap translation through `swap_xlate()`, and address-space segment operations that interact with page and vnode abstractions.

Notable edge cases:
- `share_page_table` and `ism_off` tunables rewrite attach flags.
- ISM/DISM attach mode cannot be changed once a shared page table segment exists.
- Segment size accounting uses rounded page size for resource controls but preserves the original requested byte size for user-visible `IPC_STAT`.
- `shm_dtor()` releases ISM resources, locked pages, anon reservations, and project/zone usage only after all references and `IPC_RMID` are gone.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/shm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sid.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sid.c

Implements kernel SID and SID-list support used by credentials. Despite the file comment calling these “stubs,” the file contains real domain interning, refcounting, credential SID copy-on-write, lookup helpers, and sorted membership checks.

Key responsibilities:
- Interns SID domain strings in a global AVL tree protected by `sid_lock`.
- Maintains atomic reference counts for `ksiddomain_t`, `ksidlist_t`, and `credsid_t`.
- Provides hold/release helpers for individual SIDs, SID lists, and credential SID containers.
- Supports UID/GID to SID lookup through kernel idmap functions when `_KERNEL` is enabled.
- Converts oversized POSIX GIDs into SIDs for credential supplemental groups.

Important paths:
- `ksid_lookupdomain()` lazily initializes `sid_tree`, finds or creates a domain, and returns it held.
- `ksiddomain_rele()` removes and frees a domain only after the atomic refcount reaches zero and a locked recheck confirms it.
- `ksidlist_has_sid()` searches by RID/domain, using linear search for small lists and binary search for larger sorted lists.
- `ksidlist_has_pid()` searches POSIX IDs through `ksl_sorted`, the pointer array sorted by `ks_id`.
- `kcrsid_dup()` implements copy-on-write for credential SID metadata.
- `kcrsid_setsid()` updates one indexed SID while preserving or dropping the auxiliary structure when empty.
- `kcrsid_setsidlist()` installs a SID list and sorts it both by SID and POSIX ID.
- `kcrsid_gidstosids()` builds a SID list from supplemental groups above `MAXUID`.

Memory and locking model:
- Domain AVL tree mutations require `sid_lock`.
- Object lifetime is atomic-refcount based.
- `kcrsid_dup()` may return the original object when uniquely owned, so callers must treat returned pointers as the authoritative object.
- `kcrsid_setsidlist()` assumes the incoming list already carries proper held domain references and a reference count including the new owner.

Filesystem relevance:
- SID metadata is part of credential identity and access-control plumbing. It matters to filesystem research where Windows-compatible ACLs, SMB/NFS identity mapping, or ZFS/illumos ACL decisions depend on kernel credentials containing SID state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sig.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sig.c

Implements core illumos signal delivery, signal selection, process/thread stops, default actions, signal queues, `SIGCLD` notification, real-time profiling signal dispatch, and 32-bit `siginfo` conversion.

Key global policy:
- Defines canonical masks: `nullsmask`, `fillset`, `cantmask`, `cantreset`, `ignoredefault`, `stopdefault`, `coredefault`, and `holdvfork`.
- Integrates with `/proc`, DTrace, audit, process contracts, `signalfd`, scheduler control signal blocking, and process/thread lifecycle flags.
- Tracks user-thread stop requests with `num_utstop`, `utstop_cv`, and `thread_stop_lock`.

Signal posting:
- `psignal()` posts to a process; `tsignal()` posts to a thread.
- `sigtoproc()` handles directed and process-wide posting, including SIGKILL, SIGCONT, job-control stop signals, ignored-signal discard, `sigfd` poll wakeups, and external-contract signal tracking.
- `eat_signal()` marks a thread for signal checking and wakes or pokes it when possible.
- `sig_discardable()` avoids unnecessary queueing when a signal is ignored, unblocked, untraced, not waited for, and the process is single-threaded.

Signal selection and stopping:
- `issig()` dispatches to `issig_justlooking()` or `issig_forreal()`.
- `issig_justlooking()` is a lockless fast check for pending work before doing the expensive path.
- `issig_forreal()` handles DTrace-generated stops/signals, process kill/exit state, single-step suppression, `/proc` stop requests, checkpoint/hold/pause stops, current signals, pending thread/process signals, tracing stops, and `SIGCLD` reposting.
- `fsig()` selects the next unheld signal, prioritizing `SIGKILL` and `SIGPROF`, respecting vfork and `lwp_nostop`.
- `isjobstop()`, `jobstopped()`, and `stop()` implement job-control and `/proc` stop semantics, including parent notifications and thread-state transitions.

Signal action execution:
- `psig()` performs the current signal action.
- For handlers, it prepares optional `siginfo`, updates masks, honors reset/no-defer/restart/on-stack flags, calls `sendsig()` or `sendsig32()`, and converts failed handler setup into `SIGSEGV`.
- For default terminating signals, it coordinates LWP exit, core dumps, audit events, process contracts, and final `exit()`.
- Core-producing defaults are listed in `coredefault`; ignored defaults are listed in `ignoredefault`.

Disposition and child notification:
- `setsigact()` updates dispositions and related masks, clears pending ignored signals, and handles `SIGCLD` `SA_NOCLDWAIT` / `SA_NOCLDSTOP`.
- `sigdefault()` resets caught signals during exec or vfork-child setup.
- `sigcld()`, `post_sigcld()`, and `sigcld_repost()` implement serialized child-state notification so `SIGCLD` events are not lost when multiple children change state.

Signal queues:
- `sigsendproc()` and `sigsendset()` implement permission-checked signal sending over process sets.
- `sigdeq()`, `sigdelq()`, `sigcld_delete()`, `sigaddqins()`, `sigaddqa()`, and `sigaddq()` manage per-process and per-thread `sigqueue_t` lists.
- Explicitly queued signals can accumulate when `SI_CANQUEUE()` and `p_siginfo` permit it; otherwise queue depth is one per signal.
- `SIGKILL` queue metadata is stashed separately in `p_killsqp`.
- `sigqhdralloc()`, `sigqalloc()`, `sigqhdrfree()`, `sigqfree()`, `sigqrel()`, and `siginfofree()` manage bounded per-process preallocated signal queue pools.

Other interfaces:
- `stop_on_fault()` supports debugger stop-on-fault handling.
- `sigorset()`, `sigandset()`, and `sigdiffset()` are low-level kernel signal-set operations.
- `sigcheck()` tests whether a thread needs signal processing on kernel return.
- `sigintr()` and `sigunintr()` temporarily restrict interruptible signals for NFS/UFS-style interruptible mount operations.
- `sigreplace()` swaps a thread signal mask.
- `sigwillqueue()` identifies queue-capable signal codes.
- `trapsig()` posts synchronous hardware/trap signals.
- `realsigprof()` chooses slow traced or fast direct `SIGPROF` delivery.
- `siginfo_kto32()` and `siginfo_32tok()` translate native kernel `siginfo` to/from 32-bit ABI structures.

Locking model:
- Most process signal state is protected by `p_lock`.
- Parent/child notification uses `pidlock`.
- Thread state transitions use `thread_lock()`.
- Several routines deliberately drop and reacquire locks around operations that can sleep, notify `/proc`, allocate memory, or switch thread state.

Filesystem relevance:
- This is process-control infrastructure, but filesystem code depends on it for interruptible blocking operations, especially NFS/UFS paths using `sigintr()` / `sigunintr()`, syscall interruption, cancellation, and signal-driven wakeups from sleeps.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sleepq.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sleepq.c

Implements sleep queue operations for kernel threads waiting on synchronization objects or wait channels.

Core structure:
- Global `sleepq_head[NSLEEPQ]` stores sleep queue buckets.
- Each sleep queue is a singly linked list in descending dispatch priority order.
- Threads of the same priority form circular doubly linked sublists via `t_priforw` and `t_priback`.
- The main chain uses `t_link`; membership is recorded in `t_sleepq`.

Important paths:
- `sleepq_insert()` inserts a thread in priority order. For `lwp_rwlock_t`, writers are treated as a half-priority higher than readers through `CMP_PRIO()`.
- `sleepq_unlink()` removes a thread from both the main list and the priority sublist, then clears all queue linkage fields.
- `sleepq_dequeue()` removes a specific thread without waking it.
- `sleepq_unsleep()` removes a sleeping thread and transitions it toward runnable state.
- `sleepq_wakeone_chan()` wakes the first thread waiting on a specific channel, marks `TS_SIGNALLED`, calls class wakeup, and drops the run queue lock.
- `sleepq_wakeall_chan()` wakes all threads waiting on a channel.

Locking and invariants:
- Callers must hold the appropriate thread/sleepq lock; assertions check `THREAD_LOCK_HELD`.
- Removal is optimized by using `t_sleepq` and priority-sublist backlinks rather than full-list scans in the common case.
- Wake functions clear `t_wchan`, `t_wchan0`, and `t_sobj_ops` before calling scheduler-class wakeup hooks.

Filesystem relevance:
- Sleep queues are core blocking/wakeup infrastructure. Filesystems, VFS, drivers, and VM code rely on this machinery indirectly through condition variables, locks, and wait channels.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sleepq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/smb_subr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/smb_subr.c

Provides small kernel support shims for SMBIOS library code, not SMB filesystem protocol code.

Functions:
- `smb_strerror()` is a stub that currently returns `NULL`.
- `smb_alloc()` wraps `kmem_alloc()` and returns `NULL` for zero-length requests.
- `smb_zalloc()` wraps `kmem_zalloc()` and returns `NULL` for zero-length requests.
- `smb_free()` wraps `kmem_free()`.
- `smb_dprintf()` prints debug output through `vcmn_err(CE_CONT, ...)` only when `SMB_FL_DEBUG` is set on the SMBIOS handle.

Filesystem relevance:
- No direct filesystem behavior. The `smb_` prefix here means SMBIOS, not Server Message Block. It is kernel utility glue for resident SMBIOS parsing/debug code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/smb_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/softint.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/softint.c

Implements the kernel softcall mechanism used to run deferred callbacks at software interrupt priority.

Core model:
- A fixed pool of `NSOFTCALLS` entries backs a FIFO callback queue.
- Duplicate `(function, argument)` softcalls are coalesced.
- State is tracked with `SOFT_IDLE`, `SOFT_PEND`, `SOFT_DRAIN`, and `SOFT_STEAL`.
- `softcall_lock` protects the queue, free list, CPU-set state, and state machine.

Important paths:
- `softcall_init()` allocates the softcall pool and CPU set, initializes the spin mutex, sets initial state, and scales `softcall_delay` into clock ticks.
- `softcall()` enqueues a callback, triggers `siron()` when idle, and detects when the current draining CPU appears stuck.
- `softcall_choose_cpu()` selects another CPU to poke when the queue is not progressing, avoiding CPUs already poked, disabled CPUs, CPUs being offlined, and on x86 virtual CPUs not currently scheduled on a physical CPU.
- `softint()` drains the queue in FIFO order, releases the lock while executing callbacks, returns entries to the free list, and prevents multiple active drainers except during steal recovery.
- `kdi_softcall()` and the tail of `softint()` support kernel debugger deferred callbacks via `kdi_siron()`.

Reliability behavior:
- If higher-priority interrupt load prevents the soft interrupt from running, `SOFT_STEAL` allows another CPU to drain the queue.
- Poke frequency is rate monitored with `softcall_pokemax`; excessive poking increases `softcall_delay`.
- Quiesced or offline CPUs do not process the queue and are removed from the active CPU set.

Filesystem relevance:
- Deferred callback execution is broad kernel infrastructure. Filesystems and storage drivers can depend on soft interrupts for work that must be delayed out of high-level interrupt or scheduling contexts.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/softint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/space.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/space.c

Holds resident kernel data and a small persistent key/value pointer registry. The file centralizes globals that must remain loaded in the kernel.

Resident globals:
- Buffer and VM/system accounting: `bfreelist`, `sysinfo`, `vminfo`.
- Physical memory descriptors: `physmax`, `physinstalled`.
- Kernel vnode page storage: `kvps[KV_MAX]`.
- Root device state: `rootvp`, `rootdev`, `root_is_ramdisk`, `ramdisk_size`.
- Netboot/DHCP state: `netboot`, `obpdebug`, `dhcack`, `dhcacklen`, `netdev_path`, `dhcifname`.
- Network constant: `etherbroadcastaddr`.
- Console/input device state: keyboard, mouse, stdin, diagnostic, framebuffer, workstation console, real console, user console, serial virtual console, abort policy, and terminal-emulator mode.
- CPC key: `kcpc_key`.
- CRC support: `crc32_table`.
- MAC soft ring default: `mac_soft_ring_enable`.
- iSCSI boot property pointer: `iscsiboot_prop`.

Initialization:
- `space_init()` initializes PTY resident data and the store/fetch hash.
- `store_fetch_initspace()` creates `space_hash`, a string-keyed `mod_hash`.

Persistent pointer registry:
- `space_store()` validates a non-empty key, copies the string, and inserts a `uintptr_t` value. Duplicate or allocation errors return `-1`; debug builds log details.
- `space_fetch()` returns the stored pointer value or zero.
- `space_free()` removes the key from the hash.
- Comments recommend this mechanism for module data that must survive unload/load cycles instead of adding more globals to this file.

Filesystem relevance:
- Contains direct VFS-adjacent state: `rootvp`, `rootdev`, resident vnode storage, console vnodes, and boot device metadata.
- The persistent pointer registry can be used by modules, including filesystem/storage modules, to retain kernel-resident data across reloads.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/space.c -->