# Group Research: group_412_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_kern_hhook_c_sources_45e60706e906

Scope: `Docs/research_subset_a.md`; all files are under the included `sources/os/bsd/freebsd-src` source tree.

This group covers FreeBSD kernel infrastructure around helper hooks, idle thread setup, interrupt events/ithreads, jail lifecycle and jail descriptors/metadata, kernel coverage tracing, and kexec image staging. The common themes are kernel object lifetime, lock ordering, user-visible control planes, and confinement/security boundaries.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_hhook.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_hhook.c

## Purpose
Implements the helper hook (`hhook`) KPI: kernel subsystems can register hook points, and helper modules can attach callbacks that run at those points. It supports both global and VNET-local hook heads.

## Main Elements
- `struct hhook` stores a callback, optional helper metadata, user data, and STAILQ linkage.
- Global state consists of `hhook_head_list`, per-VNET `hhook_vhead_list`, `hhook_head_list_lock`, and `n_hhookheads`.
- `hhook_run_hooks()` read-locks a hook head and invokes all registered hooks, supplying helper OSD data when `HELPER_NEEDS_OSD` is set.
- `hhook_add_hook()` / `hhook_remove_hook()` modify a single `struct hhook_head`.
- `hhook_add_hook_lookup()` / `hhook_remove_hook_lookup()` apply a helper hook to all currently registered matching hook heads, including virtual instances.
- `hhook_head_register()`, `hhook_head_deregister()`, and lookup/release routines manage hook head allocation, list membership, and refcounts.
- VNET sysinit/sysuninit initializes per-VNET hook lists and forcibly cleans up any leaked virtualized hook heads during VNET teardown.

## Dependencies And Integration
Uses `rm` locks for per-hook-head reader/writer synchronization, a global mutex for hook-head list membership, `refcount` for lifetime safety, kernel helper/module OSD APIs, and VNET infrastructure when `HHOOK_HEADISINVNET` is used.

## Risk Notes
The file is concurrency-sensitive. `hhook_add_hook_lookup()` deliberately snapshots and refcounts hook heads without holding `hhook_head_list_lock` across `M_WAITOK` allocation. `hhook_remove_hook_lookup()` calls `hhook_remove_hook()` while holding the global list lock, so lock ordering with per-head write locks is part of the implicit contract. Misused VNET hook heads are cleaned up at teardown, but only after warning.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_hhook.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_idle.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_idle.c

## Purpose
Creates and initializes kernel idle threads during scheduler idle subsystem startup.

## Main Elements
- `SYSINIT(idle_setup, SI_SUB_SCHED_IDLE, SI_ORDER_FIRST, ...)` installs early idle setup.
- `idle_setup()` creates one idle kthread per CPU on SMP systems, or one idle thread on non-SMP systems.
- Each idle thread is created stopped via `kproc_kthread_add(sched_idletd, ...)`, marked runnable, flagged `TDF_IDLETD | TDF_NOLOAD`, assigned idle scheduler class, and given `PRI_MAX_IDLE`.
- The process backing idle threads is marked `P_IDLEPROC`.

## Dependencies And Integration
Integrates with scheduler entry `sched_idletd`, per-CPU state (`pc_idlethread` or `PCPU_SET(idlethread)`), kernel process/thread creation, and scheduler priority/class APIs.

## Risk Notes
The implementation intentionally avoids locking per-CPU idle-thread assignment because application processors should not be running yet. Any boot-order change that allows APs to observe idle thread state earlier would invalidate that assumption.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_idle.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_intr.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_intr.c

## Purpose
Implements FreeBSD interrupt event management, interrupt handler registration/removal, interrupt threads, software interrupts, affinity control, interrupt dispatch, and interrupt statistics exposure.

## Main Elements
- `struct intr_event` instances are tracked in `event_list`; each event has handlers, optional interrupt thread, source callbacks, affinity state, and flags.
- `struct intr_thread` represents an ithread and tracks `IT_DEAD`, `IT_WAIT`, pending service, and waiting state.
- `intr_priority()` maps interrupt type flags to scheduler priorities.
- `intr_event_create()` / `intr_event_destroy()` allocate and destroy event objects.
- `_intr_event_bind()`, `intr_setaffinity()`, and `intr_getaffinity()` bind IRQs and/or ithreads to CPUs or cpusets.
- `intr_event_add_handler()` validates exclusive/sleepable rules, creates an ithread when needed, and inserts handlers by priority.
- `intr_event_remove_handler()`, suspend/resume, and barrier helpers coordinate safe handler removal with either lockless fast-path execution or ithread-mediated removal.
- `intr_event_handle()` is the hardware interrupt dispatch path: it runs filters in interrupt context, manages active counters/phases, invokes pre/post callbacks, and schedules ithreads when required.
- `ithread_loop()` services pending handlers, enters NET_EPOCH for network handlers, throttles interrupt storms, and re-enters interrupt wait state.
- `swi_add()`, `swi_sched()`, and `swi_remove()` implement software interrupt events and handler scheduling.
- Sysctls expose `hw.intrnames` and `hw.intrcnt`; DDB commands dump interrupt events and counts.

## Dependencies And Integration
Uses CK singly linked lists for handler lists, mutexes for event state, scheduler and thread locking, cpuset APIs, random entropy harvesting, NET_EPOCH, PMC hooks when enabled, machine interrupt/stat arrays, and DDB/debug infrastructure.

## Risk Notes
This is a high-risk synchronization file. Handler lists are traversed locklessly by `intr_event_handle()`, so removal relies on active phase counters and memory fences. Ithread state transitions depend on scheduler locks and atomic `it_need`/`ih_need` ordering. Affinity changes cross event locks, cpuset permission checks, and platform `assign_cpu` callbacks. Storm throttling and NET_EPOCH batching are performance-sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_intr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_jail.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_jail.c

## Purpose
Implements FreeBSD jail core: jail creation, update, lookup, removal, attachment, hierarchy/lifetime rules, jail parameters/sysctls, IP and VNET restrictions, credential confinement checks, privilege policy, process linkage, RACCT integration, and DDB inspection.

## Main Elements
- Defines `prison0`, global jail lists/locks (`allprison`, `allprison_lock`), jail ID allocation state, default allow/statfs/devfs settings, and parameter flag tables.
- `prison0_init()` completes host jail initialization, including cpuset, OS release values, MAC label setup, and optional preloaded host UUID validation.
- Legacy `jail(2)` compatibility is translated into the `jail_set(2)` iovec option model by `kern_jail()`.
- `kern_jail_set()` is the central create/update implementation. It parses options, validates permissions and descriptor modes, resolves paths, handles JID/name lookup, creates or updates `struct prison`, applies host/IP/allow/statfs/devfs parameters, invokes jail OSD methods, optionally attaches the caller, and returns descriptors/errors to user space.
- IP support uses epoch-safe `struct prison_ip` buffers, primary-address-preserving sorting, duplicate/validity checks, parent-subset checks, conflict checks, descendant restriction, and deferred freeing via `NET_EPOCH_CALL`.
- `kern_jail_get()` implements parameter retrieval by descriptor, lastjid, jid, or name, including descriptor return, MAC checks, module parameters, and user copyout.
- `sys_jail_remove()`, `sys_jail_remove_jd()`, `prison_remove()`, `sys_jail_attach()`, and `sys_jail_attach_jd()` implement removal and attachment entry points.
- `do_jail_attach()` updates cpuset, root/current directory, credentials, process jail list linkage, OSD attach hooks, knotes, and MAC notifications.
- Lookup helpers (`prison_find`, `prison_find_child`, `prison_find_name`) enforce hierarchy visibility under `allprison_lock`.
- Reference/lifetime routines split structural refs (`pr_ref`) from user refs (`pr_uref`) and use a `jail_remove` taskqueue to complete teardown outside unsafe contexts.
- `prison_deref()` and `prison_deref_kill()` transition jails to dying/invalid, kill descendant processes, detach descriptors, call module remove hooks, release VNETs, roots, IP lists, cpusets, OSD, RACCT, and memory.
- Confinement helpers implement address-family checks, IP ownership checks, NFS daemon allowance, parent/child visibility, hostname/domain/UUID/hostid accessors, mount visibility/statfs rewriting, and VNET ownership tests.
- `prison_priv_check()` is the jail privilege policy switch, granting or denying individual privileges based on jail state and `allow.*` bits.
- Sysctls expose jail listing, jailed/vnet state, deprecated defaults, child counters, parameter descriptions, allow flags, and dynamic `allow.mount.<fs>` flags.
- RACCT code maps jail names to shared resource accounting buckets and handles rename migration.
- DDB support dumps prison structure state, flags, allow bits, and IP lists.

## Dependencies And Integration
Integrates with VFS options and path lookup, vnode roots/chroot, MAC framework, cpuset, credentials, process lists, VNET, network epoch, OSD jail methods, descriptor support from `kern_jaildesc.c`, metadata methods from `kern_jailmeta.c`, RACCT/RCTL, kqueue notes, sysctl jail parameters, devfs/statfs policy, and network address-family helpers.

## Risk Notes
The file is security-critical. Correctness depends on preserving jail hierarchy visibility, parent-imposed restrictions, immutable creation-time properties (`vnet`, IP mode, path, OS release), and lock ordering among `allprison_lock`, prison mutexes, allproc, vnode, and descriptor locks. IP lists are read by network fast paths and must remain epoch-safe. Reference accounting is subtle because persistent jails, attached processes, descriptors, and removal all hold different references.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_jail.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_jaildesc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_jaildesc.c

## Purpose
Implements jail descriptors: passable file descriptors that refer to a jail, support permission-carrying operations, allow kqueue/poll notifications, and optionally own jail lifetime/removal.

## Main Elements
- Defines `jaildesc_ops` as a `DTYPE_JAILDESC` fileops table with invalid read/write/ioctl/truncate and custom poll, kqfilter, stat, close, kinfo, and compare operations.
- `jaildesc_alloc()` creates an unassociated descriptor, checks `PRIV_JAIL_REMOVE` for owning descriptors, allocates a file, sets read/write access based on `PRIV_JAIL_SET`, and initializes locks/knlist state.
- `jaildesc_find()` resolves a descriptor fd, validates type and prison liveness, and optionally returns held prison and descriptor credentials.
- `jaildesc_set_prison()` attaches a descriptor to a locked prison and holds the prison.
- `jaildesc_prison_cleanup()` detaches all descriptors from a prison during jail teardown.
- `jaildesc_knote()` propagates jail lifecycle/child/attach events to descriptor listeners and marks removed descriptors hung up.
- `jaildesc_close()` detaches or removes the referenced prison depending on `JDF_OWNING`, drains selection/kqueue state, destroys locks, and frees the descriptor.
- Kqueue logic supports `EVFILT_JAILDESC`, filters selected `NOTE_JAIL_*` events, stores child/attach IDs in `kn_data`, and EOF/oneshot behavior on removal.
- `jaildesc_stat()`, `jaildesc_fill_kinfo()`, and `jaildesc_cmp()` expose descriptor status and comparison behavior.

## Dependencies And Integration
Integrates with the file descriptor table, file capabilities, jail core locking/lifetime APIs, poll/select, kqueue, `kinfo_file`, privilege checks, and prison descriptor lists.

## Risk Notes
Lock ordering is central: close may need to drop the descriptor lock, hold the prison, and then acquire jail locks before unlink/removal. Owning descriptors can remove jails on close, so descriptor lifetime directly affects jail lifecycle and must not race prison cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_jaildesc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_jailmeta.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_jailmeta.c

## Purpose
Adds generic OSD-backed jail metadata parameters: private `meta` hidden from the jail and shared `env` readable by the jail.

## Main Elements
- `security.jail.meta_maxbufsize` manages hard and soft maximum metadata buffer sizes under `allprison_lock`.
- Sysctl parameter announcements expose `security.jail.param.meta` and `.env` as key/value-style jail parameters sized by the soft limit.
- `struct meta` describes each metadata namespace, its OSD slot, and OSD method table.
- Hunk-chain helpers (`jm_h_*`) edit final metadata buffers by replacing the whole buffer or cutting/replacing/removing individual `key=value` lines.
- `jm_osd_method_set()` scans jail options with the namespace prefix, validates size and NUL termination, copies existing OSD data, applies edits, assembles a final buffer, and compares/swaps under `pr_mtx` with limited retries to avoid lost concurrent updates.
- `jm_osd_method_get()` returns whole metadata or a single key value to matching vfsopts.
- `jm_osd_method_check()` marks matching options seen during jail validation.
- `jm_sysctl_env()` lets a jail read its shared `env` metadata.
- Sysinit registers two jail OSD slots with destructors and method tables; sysuninit deregisters them.

## Dependencies And Integration
Uses jail OSD methods invoked from `kern_jail.c`, vfs option parsing, jail locks, `allprison_lock`, sysctl jail parameter discovery, and `M_PRISON` storage.

## Risk Notes
The buffer editing logic is compact but subtle. It treats metadata as newline-separated `key=value` strings, depends on vfsopt NUL-terminated values, and uses hunk slicing to avoid in-place mutation of shared OSD buffers. The get path’s single-key extraction assumes newline-delimited records; malformed metadata could affect lookup boundaries, though set-side validation and assembly constrain normal data.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_jailmeta.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_kcov.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_kcov.c

## Purpose
Implements the `/dev/kcov` kernel coverage tracing device used by fuzzing and testing tools to collect per-thread program-counter or comparison coverage.

## Main Elements
- `struct kcov_info` tracks the traced thread, physical VM object, kernel mapping, entry count/size, state, and trace mode.
- State machine: `OPEN` after device open, `READY` after buffer allocation, `RUNNING` while probes record into the buffer, and `DYING` after close cleanup begins.
- `get_kinfo()` filters tracing to the current non-interrupt thread with a running KCOV state.
- `trace_pc()` stores return addresses in PC mode; `trace_cmp()` stores type/arg/return comparison tuples in CMP mode.
- `kcov_open()` allocates per-fd state and installs cdevpriv cleanup.
- `kcov_close()` rejects closing while tracing is still running.
- `kcov_mmap_single()` exposes the allocated buffer object read/write but not executable.
- `kcov_alloc()` allocates wired physical pages, maps them in KVA, and prepares a VM object sized/aligned for mmap.
- `kcov_ioctl()` implements `KIOSETBUFSIZE`, `KIOENABLE`, and `KIODISABLE`, registering/unregistering global coverage callbacks as active users appear/disappear.
- `kcov_thread_dtor()` disables tracing and frees or returns buffers to READY on thread exit.
- Sysinit creates `/dev/kcov` mode `0600` and registers the thread destructor.

## Dependencies And Integration
Integrates with sanitizer/coverage compiler hooks (`cov_register_pc`, `cov_register_cmp`), devfs cdevpriv, VM objects/pages/radix, pmap KVA mappings, thread destructor eventhandler, and `kern.kcov.max_entries` sysctl.

## Risk Notes
Memory ordering is explicit around transitions into and out of `RUNNING`, because instrumentation can fire from difficult contexts. The implementation avoids tracing interrupts and uses a spin mutex plus atomics for global callback registration. VM object cleanup must unwind wired pages and KVA mappings exactly once, including close-vs-thread-exit races.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_kcov.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_kexec.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_kexec.c

## Purpose
Implements kernel-side staging for `kexec_load(2)`: loads a replacement kernel image into memory and arranges for reboot to jump directly to it instead of firmware reboot.

## Main Elements
- Global staging state includes `staged_image`, mapped staging address, staging VM object, shutdown eventhandler tag, and a mutex.
- `kexec_reboot()` runs during final shutdown when `RB_KEXEC` is set, stops secondary CPUs, disables interrupts, marks the scheduler stopped, and calls machine-dependent `kexec_reboot_md()`.
- `seg_cmp()` sorts segments by destination memory address.
- `segment_fits()` validates that each destination segment lies entirely within a single physical memory segment.
- `pa_for_pindex()` maps staged object page indices back to target physical addresses for page placement.
- `kern_kexec_load()` serializes loads, copies and sorts user segment descriptors, validates segment counts/sizes/ranges, creates a physical VM object, wires pages, swaps object pages so pages already located at target physical addresses are placed at matching indices, maps the object, copies user segment data, zero-fills BSS/MD pages, flushes cache, calls machine-dependent load preparation, and atomically replaces the staged image.
- Passing `nseg == 0` unloads any existing staged image and deregisters the shutdown handler.
- `sys_kexec_load()` enforces securelevel and `PRIV_REBOOT` before delegating.

## Dependencies And Integration
Uses VM physical segment metadata, VM objects/pages/radix, kernel map, pmap/cache operations, shutdown eventhandlers, SMP CPU stop, interrupt disable, reboot flags, and machine-dependent `machine/kexec.h` hooks.

## Risk Notes
This path is inherently risky: it stages physical memory that will be copied during reboot. Validation prevents segments from crossing physical memory regions and avoids target corruption by careful page sorting. Cleanup error paths must match mappings and object sizes precisely; this file contains an error cleanup expression using `kexec_obj->size` while cleaning `new_segments`, which is worth auditing if this code is exercised before any previous image exists.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/kern_kexec.c -->