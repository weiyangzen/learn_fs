# Group Research: group_1270_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_subr_specificdata_c_s_ca8fb90cbfc8

Scope checked against `Docs/research_subset_a.md`; all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Every source file listed for this group was read completely and summarized separately below.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_specificdata.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_specificdata.c

Read completely: 415 lines.

This file implements NetBSD's generic keyed "specific data" facility. A `specificdata_domain` owns numbered keys and destructor callbacks, while each object using the domain has a `specificdata_reference` that points to a variable-sized container of `void *` slots.

Key behavior: domains are created with a mutex and list of live containers; keys are allocated by reusing free destructor-table slots or growing the key table; per-object containers are lazily allocated or resized in `specificdata_setspecific`; `specificdata_key_delete` walks all containers and destroys data for one key; `specificdata_fini` unlinks a container and destroys all populated data.

Locking is central. The source documents the required order: domain lock before reference lock when writing `specdataref_container`; readers use either the domain lock or reference lock. The unlocked getter is explicitly unsafe unless callers externally prevent resize/destruction.

Reliability notes: `specificdata_domain_delete` panics because it is unimplemented. Key creation allocates while holding the domain lock. Destructors run while the domain lock is held, so destructors must avoid re-entering the same domain in deadlocking ways.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_specificdata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_spldebug.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_spldebug.c

Read completely: 122 lines.

This is a small interrupt-priority-level debugging aid. When `spldebug` is enabled, it records per-CPU call return addresses for transitions raising to `IPL_HIGH` and tracks the last lower operation.

State includes `splraise_retaddrs[MAXCPUS][32][4]`, `splraise_depth`, `spllowered_to`, and `spllowered_from`. `spldebug_start`/`spldebug_stop` toggle tracing; `spldebug_lower` resets the per-CPU raise stack for lower IPLs; `spldebug_raise` records up to four return addresses for each high-priority raise.

Integration: this relies on `curcpu()`, `cpu_index`, and machine-dependent `return_address(i)`. There is no explicit synchronization beyond current-CPU access assumptions.

Reliability notes: the fixed per-CPU raise stack silently stops recording after 32 entries. The `spllowered_from` return-address capture is disabled with `#if 0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_spldebug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_syscall_stats.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_syscall_stats.c

Read completely: 78 lines.

This file provides optional global syscall statistics storage and sysctl publication when `SYSCALL_STATS` is compiled in.

It defines `syscall_counts[SYS_NSYSENT]`, context counters for user/system/interrupt syscall accounting, and optionally `syscall_times[SYS_NSYSENT]` under `SYSCALL_TIMES`. `SYSCTL_SETUP` creates `kern.syscalls.counts` and optionally `kern.syscalls.times` as struct sysctl nodes backed directly by those arrays.

Integration: increments are performed elsewhere through `sys/syscall_stats.h`; this file owns the storage and sysctl registration.

Reliability notes: when `SYSCALL_STATS` is disabled, the file contributes no runtime logic. Consumers of the sysctl output must know the exact syscall table layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_syscall_stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_tftproot.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_tftproot.c

Read completely: 459 lines.

This file downloads a root RAM disk over TFTP during root mount setup. It reuses NFS diskless boot discovery to identify the interface, server address, timeout behavior, and boot filename, then fetches that file over UDP.

Main flow: `tftproot_dhcpboot` selects the boot interface from `rootspec` or `bootdv`, sets `root_device`, initializes an `nfs_diskless` structure with `nfs_boot_init`, strips a leading `tftp:` prefix, and calls `tftproot_getfile`. `tftproot_getfile` creates a UDP socket, builds a TFTP RRQ in octet mode, loops through `nfs_boot_sendrecv`, converts outgoing packets to ACKs, and finally calls `md_root_setconf`. `tftproot_recv` validates packet size/opcode/block number, handles TFTP ERROR packets, detects final short DATA packet, reallocates the receive buffer, and copies payload data.

Integration: this ties NFS boot metadata, mbufs, sockets, network interfaces, and memory-disk root configuration together.

Reliability/security notes: TFTP is unauthenticated by design. Packet sizes are bounded to the TFTP 512-byte segment size, but the accumulated file is grown in kernel memory to the full downloaded size, so boot server trust and root image size matter.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_tftproot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_thmap.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_thmap.c

Read completely: 1077 lines.

This file implements `thmap`, a concurrent trie-hash map. It stores entries in a radix trie over hashed keys: the root has 64 slots, subsequent internal nodes have 16 slots, and deeper levels derive additional 32-bit hash material using a secret seeded BLAKE2s hash. Level 0 uses MurmurHash.

Core structures: internal nodes carry an atomic state with `NODE_LOCKED`, `NODE_DELETED`, and count bits; leaves store key offset/reference, length, and value; pointers are offsets from `baseptr`; leaf pointers are tagged with bit 0. `THMAP_NOCOPY` stores caller-owned keys, otherwise keys are copied.

Main operations: `thmap_get` descends lock-free and validates leaf keys; `thmap_put` preallocates a leaf, tries root CAS insertion, locks edge nodes for insertion, and expands collision chains with new internal nodes; `thmap_del` removes leaves, collapses empty internal nodes, marks deleted nodes so readers fail/restart, clears empty root slots, and stages memory for later GC. `thmap_stage_gc` detaches staged garbage and `thmap_gc` frees it.

Concurrency/integration: root publication uses CAS/release semantics; readers use consume loads. Writers use per-node spin-style locks and bottom-up locking. Removed nodes are not freed immediately, so callers must pair staged GC with an external reader-quiescence mechanism.

Reliability notes: correctness depends on the caller not running GC while lock-free readers may still hold old node observations. `thmap_destroy` drains staged GC and frees the root only when owned by the map; it does not itself walk and free live entries.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_thmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_time.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_time.c

Read completely: 239 lines.

This file provides kernel time helpers for converting absolute or relative timeouts to ticks and for retrieving selected clocks.

Key functions: `tvhzto`, `tshzto`, and `tshztoup` compute ticks until absolute wall/monotonic targets; `inittimeleft` and `gettimeleft` maintain remaining relative timeout using monotonic uptime; `clock_timeleft` recomputes remaining time for a chosen clock; `clock_gettime1` implements realtime, monotonic, process CPU time, and thread CPU time; `ts2timo` validates/normalizes a `timespec`, handles `TIMER_ABSTIME`, and returns a positive callout timeout.

Integration: process CPU time uses `calcru` plus process visibility authorization; thread CPU time uses `addrulwp`; realtime/monotonic use timecounter APIs; low-level arithmetic comes from `subr_time_arith.c`.

Reliability notes: `ts2timo` rejects invalid nanoseconds and returns `ETIMEDOUT` for zero effective timeout. CPU-clock process lookup/authorization is lifetime-sensitive and depends on existing process-lock conventions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_time.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_time_arith.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_time_arith.c

Read completely: 582 lines.

This file centralizes overflow-aware time arithmetic and timeout normalization for both kernel builds and `_TIME_TESTING` userland builds.

Key functions: `tvtohz` converts validated `timeval` durations to ticks with rounding/clamping; `tstohz` rounds nanoseconds to microseconds and delegates to `tvtohz`; `itimerfix` and `itimespecfix` validate timer values and round sub-tick nonzero intervals up; `timespecaddok` and `timespecsubok` check whether existing macro arithmetic can be done without signed `time_t` overflow; `itimer_transition` computes the next periodic timer expiry and overrun count.

Integration: sleeps, interval timers, `ts2timo`, and timer syscalls rely on these helpers to avoid scattered overflow policy.

Reliability notes: add/sub overflow checks assume normalized `timespec` inputs and enforce that with assertions. `itimer_transition` falls back to clearing `next` if addition overflows or if values cannot be represented as signed 64-bit nanoseconds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_time_arith.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_userconf.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_userconf.c

Read completely: 824 lines.

This file implements the interactive boot-time `userconf` console configurator for kernel autoconfiguration data. It lets an operator list devices, find by device name/unit, change locator values, enable/disable devices, set numeric display base, and configure pagination.

It operates directly on global `cfdata[]` and uses `cfiattr_lookup` for locator descriptions. Static buffers hold command input, prompt input, history text, and history formatting state.

Important functions: `userconf_init` counts configured devices; `userconf_pdev` prints a full device line; `userconf_number` parses signed decimal/octal/hex input; `userconf_device` parses names like `sd0` and `sd*`; `userconf_change` prompts locator edits; `userconf_disable`/`userconf_enable` mutate `cf_fstate`; `userconf_common_dev` applies operations to matching devices; `userconf_parse` dispatches commands; `userconf_prompt` runs the `uc> ` loop.

Reliability notes: input buffers are fixed size but bounded by console input APIs. Numeric overflow handling is limited. `userconf_enable` records history command `'d'` instead of `'e'`, which appears inconsistent with enable replay/history behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_userconf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_vmem.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_vmem.c

Read completely: 1941 lines.

This file implements NetBSD's `vmem` arbitrary-resource allocator, based on Bonwick-style vmem arenas. It manages address/resource spans with boundary tags, segregated free lists, busy-allocation hash tables, import/release callbacks to parent arenas, optional quantum caches, DDB diagnostics, sanity checks, and a unit-test build.

Core model: boundary tags represent static spans, imported spans, free regions, and busy allocations. Free tags are organized by size order; busy tags are hashed by start address; `vm_seglist` preserves order for coalescing and diagnostics. In-kernel boundary tags come from a special pool plus a static reserve to avoid allocator recursion.

Key operations: `vmem_init`/`vmem_create`/`vmem_xcreate` initialize arenas; `vmem_add` adds static spans; `vmem_alloc` delegates to `vmem_xalloc`; `vmem_xalloc` handles size rounding, alignment, phase, nocross, min/max constraints, best-fit/instant-fit search, import, splitting, and busy insertion; `vmem_free`/`vmem_xfree` release allocations; `vmem_xfree_bt` coalesces adjacent free tags and releases whole imported spans when possible.

Maintenance: `vmem_subsystem_init` creates metadata arenas and boundary-tag pool. `vmem_rehash_start` schedules periodic workqueue-based busy-hash resizing. DDB helpers implement `vmem_whatis`, `vmem_printall`, and `vmem_print`.

Reliability notes: alignment and exact-free invariants are assertion-heavy. Comments note limitations around importing a region large enough for restrictive min/max/alignment requests. Boundary-tag reserve and lock ordering are critical low-memory paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_vmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_workqueue.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_workqueue.c

Read completely: 484 lines.

This file implements kernel workqueues: deferred `struct work` callbacks executed by kernel worker threads, either one shared queue or one queue per CPU.

A `workqueue` stores callback metadata, flags, name, priority, and original allocation pointer. Each `workqueue_queue` stores a pending simple queue, mutex, condvar, generation counter, and worker LWP.

Main behavior: `workqueue_create` allocates cacheline-aligned storage and creates worker threads; `workqueue_worker` sleeps for pending work, moves pending items into a local batch, marks `q_gen` odd while running, executes callbacks outside the queue lock, increments `q_gen`, and wakes waiters; `workqueue_enqueue` appends work; `workqueue_wait` waits for a target work item to leave pending/running state; `workqueue_destroy` replaces the callback with `workqueue_exit`, queues exit work, joins workers, and frees storage.

Integration: `subr_vmem.c` uses workqueues for periodic rehashing. SDT probes cover create, destroy, enqueue, callback entry/return, wait, and exit.

Reliability notes: callers must prevent new enqueue of a target work item before relying on `workqueue_wait`. Waiting from the worker itself returns without blocking to avoid deadlock. Debug builds detect duplicate pending enqueue.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_workqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_xcall.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_xcall.c

Read completely: 594 lines.

This file implements CPU cross-calls: executing a function on one CPU or all CPUs. It has a low-priority kthread path and a high-priority softint/IPI path.

Global state boxes `xc_low_pri` and `xc_high_pri` store lock, condvar, current function/arguments, head/done tickets, and high-priority IPL. Per-CPU `cpu_xcall_pending` and `cpu_xcall` condvars drive low-priority workers. `xc_sihs[]` stores softint handles for supported `IPL_SOFT*` levels.

Key functions: `xc_init_cpu` initializes global state once and starts an `xcall/N` kthread per CPU; `xc_broadcast` and `xc_unicast` publish requests and return tickets; `xc_wait` waits for completion; `xc_barrier` broadcasts a no-op; `xc_lowpri` serializes one low-priority request and signals target worker threads; `xc_thread` runs low-priority calls; `xc_highpri` sends IPIs or local softint scheduling; `xc__highpri_intr` executes high-priority callbacks and advances completion.

Reliability notes: cross-calls must be made from sleepable non-interrupt context. Low-priority calls are globally serialized and share one function/argument box. High-priority callbacks run in soft interrupt context and must be lightweight and nonblocking.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/subr_xcall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_aio.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_aio.c

Read completely: 2260 lines.

This file implements NetBSD's POSIX asynchronous I/O module and syscall package. It registers AIO syscalls at module init, maintains global limits and pools, and gives each process a private AIO service pool.

Main structures: `aioproc` stores per-process AIO state; `aiosp` owns pending jobs, active/free worker lists, a hash from user `aiocb *` to kernel jobs, and an RB tree of regular-file groups; `aiost` is a worker thread; `aio_job` stores copied `aiocb`, file reference, wait links, operation, process, and completion state; `lio_req` tracks list-I/O requests.

Core flow: `aio_enqueue_job` copies in an `aiocb`, validates signal/buffer/opcode, initializes process AIO if needed, allocates a job, holds the file, inserts the user-pointer hash entry, checks limits, queues the job, and updates list-I/O references. `aiosp_distribute_jobs` assigns queued jobs to workers, grouping regular-file jobs by `struct file *` and assigning non-regular jobs directly. Workers run `io_read`, `io_write`, or `io_sync`, mark completion, flush waitgroups, and send configured signals.

Syscalls: `aio_read`, `aio_write`, `aio_fsync`, and `lio_listio` enqueue work; `aio_error` returns stored errno; `aio_return` detaches and frees completed jobs; `aio_suspend` waits on any listed job; `aio_cancel` cancels queued, not currently running, jobs. Sysctls expose POSIX AIO support, `aio_listio_max`, and `aio_max`.

Reliability notes: actual read/write use synchronous fallback file operations in worker threads; nonblocking regular-file optimization is not implemented. The user-pointer hash is central to correctness for `aio_error`, `aio_return`, and duplicate-submission checks. Thread-pool teardown, global/per-process job accounting, and cancellation races are sensitive areas. `io_sync` copies the completed kernel `aiocb` back to userspace, while read/write completion is primarily observed through the AIO query syscalls.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_aio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_descrip.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_descrip.c

Read completely: 746 lines.

This file implements descriptor-oriented system calls: duplication, `fcntl`, close, stat/pathconf, advisory locks, `posix_fadvise`, and pipe creation.

Key paths: `sys_dup`, `dodup`, `sys_dup2`, and `sys___dup3100` duplicate file descriptors with close-on-exec/close-on-fork handling. `sys_fcntl` handles `F_CLOSEM`, `F_MAXFD`, POSIX locks, filesystem-specific `F_FSCTL` commands through `fcntl_forfs`, descriptor flag operations, file status flag changes, signal ownership, path retrieval, and seals. `sys_close` validates and closes descriptors, translating `ERESTART` to `EINTR`. `do_sys_fstat`, `sys_fpathconf`, `sys_flock`, `do_posix_fadvise`, `sys_pipe`, and `sys_pipe2` provide the remaining descriptor operations.

Integration: this code is a syscall-facing wrapper around `filedesc`, file operation vectors, vnode path conversion, advisory locking callbacks, ioctl/fcntl hooks, and pipe creation.

Reliability notes: `fcntl_forfs` bounds parameter copies with `F_PARAM_MAX` and uses a stack buffer for small payloads. `F_SETFL` attempts to roll back nonblocking/async ioctl changes if later steps fail, but comments note the operation is not guaranteed atomic. Lock syscalls depend on each file type's `fo_advlock` implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_descrip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_epoll.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_epoll.c

Read completely: 682 lines.

This file implements Linux-style epoll compatibility on top of NetBSD kqueue/kevent. `epoll_create1` creates a kqueue file descriptor; `epoll_ctl_common` translates epoll operations to kevent changes; `epoll_wait_common` calls `kevent1` and converts returned events back to `struct epoll_event`.

Translation details: read masks map to `EVFILT_READ`, write masks to `EVFILT_WRITE`, `EPOLLONESHOT` maps to `EV_DISPATCH`, `EPOLLET` to `EV_CLEAR`, and `EPOLLRDHUP` to `EV_EOF`. User epoll data plus epoll fd and target fd are stored in kevent extension fields. A zero event mask registers a disabled read filter.

Validation: epoll fds must be kqueues; regular/directory/block/link vnodes are rejected with Linux-like `EPERM`; `epfd == fd` is rejected; duplicate add checks use probe kevents; delete removes read and write filters. `epoll_pwait2` supports timeout and temporary signal mask handling.

Loop/depth control: when registering one kqueue inside another, `epoll_check_loop_and_depth` reconstructs the current watch graph from knotes, inserts the proposed edge, and runs DFS to reject loops or depth greater than `EPOLL_MAX_DEPTH`.

Reliability notes: this compatibility layer inherits kqueue semantics where they differ from Linux epoll. `epoll_pwait2` rejects `maxevents >= EPOLL_MAX_EVENTS`, while the common wait path rejects only values greater than the maximum, so boundary behavior differs between entry points. The graph reconstruction scans current descriptors and knote state, so descriptor table mutation is an important concurrency consideration.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/sys_epoll.c -->