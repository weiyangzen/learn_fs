# Group Research: group_1404_openbsd_src_sources_os_bsd_openbsd_src_sys_kern_subr_pool_c_sources_69a6eb758013

Scope confirmed against `Docs/research_subset_a.md`: `sources/os/bsd/openbsd-src` is included in subset A. All ten listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_pool.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_pool.c

Implements OpenBSD’s kernel pool allocator: fixed-size object allocation from page-sized or larger backing chunks. It maintains per-pool empty/full/partial page lists, optional off-page page headers indexed by an RB tree, allocator backends, low/high/hard watermarks, deferred waiters, DDB diagnostics, sysctl export, stale-page garbage collection, and optional per-CPU caches on multiprocessor kernels.

Core state centers on `struct pool`, `struct pool_page_header`, `struct pool_item`, and the global `pool_head` list protected by `pool_lock`. `pool_init()` computes item alignment, page size, items per page, header placement, cache-coloring space, backing allocator choice, lock type, request queue state, and global serial registration. Large pools use multi-page allocators; small/aligned pools can store headers in-page, while off-page headers come from `phpool` and are tracked in `phtree`.

Allocation flows through `pool_get()` and `pool_do_get()`. `pool_get()` checks waitability, hard limits, optional per-CPU cache, then either obtains an item immediately or enqueues a `pool_request` and sleeps until `pool_get_done()` supplies memory. `pool_do_get()` reserves `pr_nout` before possibly dropping the pool lock to allocate a page, inserts a fresh page if needed, validates free-list magic, removes one item, moves pages between empty/partial/full queues, updates counters, and returns the object. `PR_ZERO` zeroes the item after allocation.

Freeing flows through `pool_put()` and `pool_do_put()`. `pool_put()` may hand the item to a per-CPU cache, otherwise returns it to its page, decrements outstanding counts, frees old idle empty pages above the high-water policy, and wakes queued requests. `pool_do_put()` locates the owning page via in-page header math or RB lookup, detects double free under diagnostics, restores free-list magic, poisons freed payloads when enabled, and moves pages between full/partial/empty queues.

Backing allocators are wrapped by `pool_allocator_alloc()`/`pool_allocator_free()`. Provided allocators include `pool_page_alloc()` for page-sized interrupt-safe allocations, `pool_multi_alloc()` for larger interrupt-safe allocations with `splvm()`, and `_ni` variants using `kv_any` and the kernel lock for non-interrupt-safe waitable allocation.

Reclamation includes explicit `pool_reclaim()`, global `pool_reclaim_all()`, and asynchronous GC through `pool_gc_tick`/`pool_gc_task`. GC scans all pools, optionally drains per-CPU cache lists, tries nonblocking pool locks, and frees stale empty pages older than `POOL_WAIT_GC`.

Under `MULTIPROCESSOR`, `pool_cache_init()` creates per-CPU fast caches backed by a separate `pool_caches` pool. `pool_cache_get()` and `pool_cache_put()` operate with `cpumem_enter()`, raised IPL, generation counters, list magic, poisoning checks, and per-CPU stats. Shared cache-list contention dynamically grows or shrinks `pr_cache_items`; sysctl helpers export aggregate and per-CPU cache metrics.

Diagnostics include `pool_chk_page()`, `pool_chk()`, `pool_walk()`, DDB pool printers, randomized free-list ordering, item magic tied to page magic, optional freed-item poisoning, and sysctl data via `sysctl_dopool()`. Lock abstraction supports either mutex-backed or rwlock-backed pools through `pool_lock_ops`; rwlock pools require `PR_WAITOK`.

Filesystem relevance: this is a foundational allocator used by kernel subsystems including VFS, vnode/namei-style pools, buffer-related structures, and many OpenBSD object caches. Its wait semantics, interrupt constraints, and page reclamation behavior directly influence filesystem allocation paths and memory pressure behavior.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_pool.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_prf.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_prf.c

Implements kernel printf, logging, panic printing, assertion failure reporting, terminal-directed output, DDB printing hooks, `snprintf()`/`vsnprintf()`, and small compiler helper wrappers for `puts()`/`putchar()`.

Output routing is controlled by internal flags: console, controlling tty, kernel message buffer, buffer-only formatting, DDB, and count-only formatting. `kputchar()` is the common character sink, routing to `constty`, `msgbuf_putchar()`, `v_putc`, or `db_putchar()` depending on flags and debugger/panic state.

`panic()` records the first panic message in the current CPU’s panic buffer using `atomic_cas_ptr()` on `panicstr`, disables SPL assertions, forces console printing under quiet boot, prints through DDB-aware panic functions, enters DDB or dumps a stack when configured, then calls `reboot()` with dump/autoboot flags and `RB_NOSYNC` on recursive panic.

Logging functions include `log()`, `logpri()`, and `addlog()`. They write priority-prefixed messages to the kernel log buffer at high SPL, mirror to console when `/dev/klog` is not open, and wake log readers. `printf()` and `vprintf()` use `kprintf_mutex` for console/log serialization and wake log readers unless already panicking.

TTY-specific paths include `uprintf()` for the current process controlling tty, NFS-gated `tprintf_open()`/`tprintf()`/`tprintf_close()` for process-targeted messages with session references, and `ttyprintf()` for direct tty output.

`kprintf()` is a compact kernel formatter derived from BSD libc formatting. It supports common integer, string, char, pointer, width, precision, flags, `h/l/ll/q/z` modifiers, and OpenBSD/BSD `%b` bitfield decoding. It explicitly panics on `%n`. Buffer formatting uses a tail pointer to enforce `snprintf()` truncation semantics while still counting produced characters.

DDB integration provides `db_printf()`/`db_vprintf()` and panic-time preference for debugger output. `splassert_fail()` reports IPL mismatches and, depending on `splassert_ctl`, ignores, dumps stack, enters DDB, or panics.

Filesystem relevance: not filesystem-specific, but heavily used by VFS, device, and storage code for diagnostics, panic reporting, mount/buffer warnings, and DDB inspection. The formatter and log behavior define what can safely be printed from interrupt, panic, or normal kernel contexts.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_prf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_prof.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_prof.c

Implements kernel profiling support for `GPROF`/`DDBPROF` and userland `profil(2)` sampling support, including process profiling output to `gmon.<comm>.<pid>.out`.

When kernel profiling is enabled, `prof_init()` allocates one `struct gmonparam` region per CPU using boot/kernel memory, lays out `tos`, `kcount`, and `froms` tables, computes text boundaries from `KERNBASE` to `etext`, and binds/staggers `ci_gmonclock` clock interrupts. `gmoninit` gates instrumented `mcount()` use until sysctl declares profiling safe.

`prof_state_toggle()` transitions per-CPU profiling on or off. Enabling may patch profiling call sites through DDB profiling support when not built as a profiling kernel, increments `gmon_cpu_count`, starts the profiling clock on first CPU, and advances the CPU clock request. Disabling cancels the CPU clock request, stops the global profiling clock on last CPU, and disables DDB profiling patches.

`sysctl_doprof()` exposes kernel profiling state and buffers per CPU: state, count histogram, froms table, tos arcs, and `gmonparam`. `gmonclock()` updates kernel text histogram buckets when the interrupted frame is kernel mode and profiling is on.

`sys_profil()` implements process profiling. It requires binaries marked with `PSI_PROFILE`, validates scale, stops profiling on scale zero, prevents changing an already established buffer, captures output directory and credentials on first use, records offset/scale/base/sample-size/buffer fields under `splstatclock()`, starts the process profiling clock, and requests rescheduling.

`prof_fork()` holds profiling directory/credential references across fork. `prof_exec()` releases profiling resources and clears the buffer on exec. `prof_write()` writes `gmon` output for a profiling process: it validates user header `totarc`, builds a `gmon.<comm>.<pid>.out` filename from `namei_pool`, temporarily restores the original profiling cwd and credentials, safely opens a regular owner-only file with restrictive checks, truncates it, and writes the user profiling buffer through `vn_rdwr()`.

`profclock()` samples either user PC or process kernel PC when `PS_PROFIL` is set. `addupc_intr()` records pending profile tick state from interrupt context and requests a profiling AST. `addupc_task()` performs faultable user memory update of the profiling counter and disables profiling if copyin/copyout fails.

Filesystem relevance: `prof_write()` is the key filesystem-facing path. It changes process cwd/credential context, uses namei/vnode open/attribute/setattr/close/read-write primitives, and enforces safety constraints before writing profiling output.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_prof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_suspend.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_suspend.c

Coordinates system suspend, hibernate, resume, and wakeup-device accounting. It is a compact but system-wide control path that quiesces devices, filesystems, buffer queues, CPUs, timers, entropy, sensors, profiling, and optional hibernate state before entering platform sleep.

`device_register_wakeup()` increments the global active wakeup-device count. `sleep_state()` is the main suspend/hibernate state machine. It rejects suspend when no wakeup devices exist, asks platform code to show/validate sleep state, suspends wsdisplay when present, stops periodic RTC updates, and for hibernate discards buffer cache/page daemon state and allocates hibernate memory.

Before sleeping, it quiesces sensors and all devices with `DVACT_QUIESCE`, stalls VFS via `vfs_stall(curproc, 1)`, quiesces softraid when configured, quiesces buffer queues, stops secondary CPUs, disables kernel profiling execution state, and performs MP sleep preparation. For hibernate it again trims dirty memory before snapshotting.

The critical suspend section raises IPL, disables interrupts, marks `cold = 2` so other code uses delays instead of sleeps, enables wakeup interrupts, sends `DVACT_SUSPEND`, suspends randomness, calls platform `sleep_setstate()`, optionally powers down devices for regular suspend via `DVACT_POWERDOWN`, drops performance to minimum, and invokes `gosleep()`.

Resume unwinds through labeled failure/resume paths: device resume, interrupt/wakeup restoration, time and clock interrupt reinitialization, `resume_time` update, platform `sleep_resume()`, randomness resume with hibernate entropy if available, MP resume, profiling restore, secondary CPU restart, VFS unstalls, buffer queues restart, device wakeup, sensor restart, hibernate memory cleanup, periodic RTC restart, wsdisplay resume, `sys_sync()`, and performance-level restoration. `suspend_finish()` can request another sleep loop.

`resuming()` reports whether current uptime is within ten seconds after the latest resume.

Filesystem relevance: `vfs_stall()`, `bufq_quiesce()`, `bufq_restart()`, hibernate buffer-cache suspension/resume, and final `sys_sync()` make this important for filesystem consistency during suspend/hibernate. It explicitly prevents normal filesystem progress while storage/device state is unstable.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_suspend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_tree.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_tree.c

Provides the generic runtime implementation behind OpenBSD red-black tree macros in `sys/tree.h`. It works on caller-owned objects using `struct rb_type` metadata: entry offset, comparison function, and optional augmentation callback.

Internal helpers translate between object pointers and embedded `struct rb_entry` pointers, access left/right/parent/color fields, initialize red entries, color parent/child nodes, and run optional augmentation after rotations or structural changes.

Insertion is implemented by `_rb_insert()`: descend by `t_compare`, reject duplicates by returning the existing node, link a new red entry under its parent, augment the parent if needed, and rebalance via `rbe_insert_color()` using standard red-black rotations and recoloring.

Removal is implemented by `_rb_remove()` and `rbe_remove()`: handle zero/one-child cases directly, replace two-child nodes with their inorder successor, repair parent/child links, run augmentation up the affected chain, and rebalance black-height via `rbe_remove_color()`.

Lookup and traversal APIs include `_rb_find()`, `_rb_nfind()` for first greater-or-equal match, `_rb_next()`, `_rb_prev()`, `_rb_root()`, `_rb_min()`, `_rb_max()`, and direct accessor/mutator helpers for left/right/parent links. `_rb_poison()` and `_rb_check()` support debugging of removed or uninitialized tree nodes.

The code assumes callers provide synchronization and valid comparison semantics. Optional augmentation is carefully called after rotations and parent changes so augmented interval or cached subtree metadata can remain consistent.

Filesystem relevance: generic kernel RB trees are used by many subsystems that need ordered lookup. In this group, `subr_pool.c` uses generated RB tree operations to map off-page pool page headers by page address.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_userconf.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_userconf.c

Implements OpenBSD’s interactive User Kernel Config shell, used early in boot to inspect and modify kernel autoconfiguration tables before normal device attachment. It edits `cfdata`, pseudo-device counts, locator values, flags, and device enabled/disabled states.

Global state tracks number base, max/total device slots, locator-name count, pagination, command history, command buffers, and external config arrays such as `cfdata`, `locnames`, `locnamp`, `cfroots`, `pv`, `pdevnames`, and `pdevinit`.

`userconf_init()` scans `cfdata` to find active and free slots and determines the highest locator name index. Display helpers print numbers in selected base, print device names/states, print full device records including parents, locators, flags, and pseudo-device counts, and paginate output with `userconf_more()`.

Parsing helpers include `userconf_number()` for signed decimal/octal/hex input, `userconf_device()` for device tokens like `sd0` or `sd*`, and `userconf_attr()` for locator attribute names. History helpers append compact command records for later replay or visibility.

Mutation commands include `userconf_change()` for changing locators/flags or pseudo-device counts, `userconf_disable()` and `userconf_enable()` for real devices and pseudo devices, and `userconf_add()` for cloning a device entry into a free `cfdata` slot. Adding shifts `cfdata`, fixes parent-vector and root indices, updates max device count, and adjusts star-unit handling for wildcard entries.

Query commands include `userconf_help()`, `userconf_list()`, `userconf_show()`, `userconf_show_attr()`, `userconf_common_attr_val()`, and `userconf_common_dev()`. These support listing all devices, attributes, matching devices by locator value, and finding devices by name/unit/wildcard.

`userconf_parse()` dispatches commands and aliases: add, base, change, optional ddb, disable, enable, exit/quit, find, help, list, lines, show, verbose, and `?`. `user_config()` enters console polling mode, runs the `UKC>` prompt until quit, then resumes boot.

Filesystem relevance: primarily device-autoconfiguration rather than filesystem logic. It can enable/disable/change storage controller and block-device configuration before VFS mounts root, so it can indirectly determine which filesystem devices exist at boot.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_userconf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_witness.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_witness.c

Implements WITNESS, OpenBSD’s kernel lock-order verifier. It enrolls lock objects by lock type/subtype/class, tracks locks currently held by threads and CPUs, records observed lock-order edges, detects lock-order reversals and misuse, supports optional stack traces, and exposes debugger/sysctl controls.

Main model types include `struct lock_class`, `struct witness`, `struct lock_instance`, `struct lock_list_entry`, witness hash tables, lock-order-data hash tables, and per-CPU witness caches. Sleep locks are tracked per thread in `p_sleeplocks`; spin locks are tracked per CPU in `witness_cpu[].wc_spinlocks`. Relationship state is stored in `w_rmatrix`, with flags for parent/ancestor/child/descendant/reversal/known-order.

`witness_initialize()` boot-allocates witness objects, relationship matrix rows, lock-list entries, optional lock stack storage, initializes free lists and hashes, enrolls pending cold-boot locks, and marks WITNESS usable. `witness_init()` validates lock flags against class capabilities, defers or enrolls locks, or disables witness tracking for uninteresting locks.

`witness_checkorder()` is the main pre-acquire verifier. It handles uninitialized lock reporting, enrolls missing witnesses, enforces no sleep locks while spin locks are held, handles recursion/exclusive/shared mismatch checks, validates interlocks, quickly accepts known direct orders, records new observed orders, detects duplicate same-type locks unless allowed, checks all already-held locks for reversals, handles special kernel-lock/sleepable rules, suppresses known vnode-vnode reversal noise, prints cycle information, and optionally enters DDB.

`witness_lock()` records a successfully acquired lock in the appropriate held-lock list, including recursion count and optional stack trace. `witness_unlock()` validates unlock mode, recursion, no-release flags, stack cleanup, and list removal. `witness_upgrade()` and `witness_downgrade()` validate shared/exclusive state transitions for upgradable sleep locks.

Graph maintenance is handled by `itismychild()` and `adopt()`, which add direct parent-child relationships and propagate ancestor/descendant transitive closure through `w_rmatrix`. Inconsistencies disable witness. `witness_lock_order_add()` stores a known direct order and stack trace in `w_lohash`; `witness_lock_order_check()` fast-paths known valid relations.

Diagnostics include `witness_warn()` for “locks held here” checks, `witness_assert()` for lock assertion semantics, `witness_thread_exit()` panic-on-exit-with-locks, `witness_display_spinlock()` for suspected spinlock owner inspection, `witness_norelease()`/`witness_releaseok()`, DDB list/display/fullgraph/bad-stack commands, and cycle printing with short path search.

Runtime controls are through `witness_sysctl()` and `witness_sysctl_watch()`. `witness_watch` ranges from disabled forever to checking/dump/debugger modes; `witness_locktrace` can be enabled if stack buffers can be allocated.

Filesystem relevance: WITNESS is central to validating VFS, vnode, buffer-cache, and filesystem lock ordering. The code explicitly recognizes vnode lock-order reversals as a known noisy class and suppresses escalation for vnode-vnode LORs while still recording the relationship.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_witness.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_xxx.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_xxx.c

Contains small generic kernel helper stubs and device-number conversion routines.

Error/null helpers are straightforward: `enodev()` returns `ENODEV`, `enxio()` returns `ENXIO`, `eopnotsupp()` returns `EOPNOTSUPP`, and `nullop()` returns success. These are commonly used as operation-table placeholders.

`bdevsw_lookup()` returns the block-device switch entry for `major(dev)`. `chrtoblk()` maps character device numbers to corresponding block device numbers using `chrtoblktbl`, validating character major bounds and returning `NODEV` for missing mappings. `blktochr()` scans `chrtoblktbl` to convert a block device major back to a character device major.

`assertwaitok()` verifies the current context is allowed to sleep. It skips checks during panic or DDB, asserts IPL is `IPL_NONE`, asserts not in an SMR critical section, and under diagnostics panics if the current CPU holds mutexes.

Filesystem relevance: block/character device conversion is important for storage device paths, raw/block device handling, mount/root-device selection, and driver tables. `assertwaitok()` is also used by allocation and wait paths, including `pool_get(PR_WAITOK)`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/subr_xxx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sys_futex.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/sys_futex.c

Implements OpenBSD’s futex syscall support with wait, wake, and requeue operations over hashed sleep queues. Futex identity is derived either from the private process plus address or from shared UVM backing object/amap plus offset.

`struct futex` represents one waiting thread on one user address. It stores current sleep queue, list entry, private process key, UVM object/amap/offset key, and volatile waiting `struct proc *`. A futex is considered waiting while `ft_proc` is non-NULL. Wakeup-side ownership of list references ends when the sleep-queue lock holder clears `ft_proc`.

`futex_init()` initializes 64 cacheline-aligned `futex_slpque` buckets, each with a TAILQ, rwlock, and randomized `fsq_id` low bits preserving bucket order for deadlock-free double locking.

`sys_futex()` dispatches by `FUTEX_OP_MASK`: `FUTEX_WAIT`, `FUTEX_WAKE`, and `FUTEX_REQUEUE`; unknown ops return `ENOSYS`.

`futex_addrs()` computes the futex key. Private futexes use `p->p_p`; shared futexes inspect the process VM map and, only for shared-inherited mappings, key on backing `uvm_object` plus offset or amap plus page offset. Otherwise they fall back to raw virtual offset with no shared object key.

`futex_wait()` validates optional relative timeout, initializes a stack-local `struct futex`, inserts it into the hashed sleep queue before reading user memory, then `copyin32()` checks the current value. If the value differs it returns `EAGAIN`; if timeout is zero it returns `ETIMEDOUT`. It sleeps with `sleep_setup()`/`sleep_finish()` while requiring that the futex be removed from the queue before returning. Timeout/restart results are translated to `ETIMEDOUT`/`ECANCELED`.

`futex_wake()` builds a key, locks the bucket, removes up to `n` matching waiters into a temporary list, wakes them via `futex_list_wakeup()`, and returns the count. Wakeup clears `ft_proc` under scheduler lock and calls `wakeup_proc()`.

`futex_requeue()` wakes up to `n` waiters from one futex and requeues up to `m` remaining waiters to another futex. It locks old/new buckets by `fsq_id` order, handles same-bucket requeue, updates each moved futex’s queue pointer and key fields, and returns the number woken.

Filesystem relevance: not filesystem-specific. It is a synchronization primitive used by user processes; its UVM mapping key logic matters for shared memory backed by files or objects, but it does not itself perform VFS operations.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sys_futex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sys_generic.c -->
# File Research: sources/os/bsd/openbsd-src/sys/kern/sys_generic.c

Implements generic file-descriptor syscalls and helpers: `read`, `readv`, `write`, `writev`, positioned read/write helpers, `ioctl`, `select`, `pselect`, `poll`, `ppoll`, select/poll conversion through per-thread kqueue state, `selwakeup()`, and `utrace`.

I/O vector handling is centralized in `iovec_copyin()` and `iovec_free()`. It copies user iovecs into either stack storage or allocated memory, rejects zero/too many vectors, validates each length and total residual against `SSIZE_MAX`, and emits ktrace structure records when enabled.

`sys_read()`/`sys_readv()` build `uio` structures and call `dofilereadv()`. `dofilereadv()` obtains an `FREAD` file reference, validates positioned-read constraints for vnode/FIFO/TTY and negative offsets, sets user-space read `uio` fields, optionally snapshots iovecs for ktrace, calls `fo_read`, converts partial interrupt/restart/would-block errors to success, updates file read transfer/byte counters under `f_mtx`, emits genio ktrace, returns byte count, and releases the file.

`sys_write()`/`sys_writev()` mirror the read path through `dofilewritev()`. The write helper obtains `FWRITE`, denies `UF_PLEDGEOPEN`, validates positioned writes, calls `fo_write`, converts partial interrupt/restart/would-block errors, sends `SIGPIPE` on `EPIPE`, updates write counters, traces successful writes, and returns bytes written.

`sys_ioctl()` obtains a read/write-capable file, rejects DNS sockets, applies `pledge_ioctl()`, directly handles `FIONCLEX`/`FIOCLEX`, allocates or uses stack ioctl buffers based on `IOCPARM_LEN`, copies in/out according to command direction, special-cases `FIONBIO` and `FIOASYNC`, dispatches to `fo_ioctl`, and copies output back deterministically after zero-initializing output buffers.

`sys_select()` and `sys_pselect()` validate timeout and optional signal masks, then call `dopselect()`. `dopselect()` bounds `nd` by open files, allocates six fd-set buffers, copies in input sets, optionally installs temporary signal mask, initializes kqueue polling, registers selected fds through `pselregister()`, handles empty interest sets by sleeping on `nowake`, otherwise scans the process kqueue and maps ready events back into output fd sets through `pselcollect()`. It copies output sets back, traces fd sets, and tears down kqpoll state.

`pselregister()` converts read/write/exception fd bits into `EVFILT_READ`, `EVFILT_WRITE`, and `EVFILT_EXCEPT` kqueue registrations with `__EV_SELECT`, tolerating unsupported/unimplemented filters. `pselcollect()` validates per-thread serial tagging and maps ready filters back to fd-set bits.

`selwakeup()` submits kqueue notes under the kernel lock. Poll support uses the same kqueue machinery with `pollfd` encoding. `sys_poll()` converts millisecond timeout to timespec; `sys_ppoll()` accepts timespec and signal mask; both call `doppoll()`. `doppoll()` copies pollfd arrays, registers events through `ppollregister()`, sleeps if no events exist, scans kqueue, maps events through `ppollcollect()`, and copies only `revents` back with `pollout()` even for interrupted poll semantics.

`ppollregister()` builds up to three kqueue events per pollfd and uses `ppollregister_evts()` to handle EBADF/POLLNVAL, detach/POLLERR, FIFO write EPERM/POLLHUP fallback, and unsupported filters. `ppollcollect()` decodes `udata` as poll-array index, validates fd identity, maps filter events and hangups to `revents`, avoids double-counting already seen pollfds, and rate-limits warnings for unclaimed events.

`sys_utrace()` forwards user trace records to ktrace when enabled and otherwise returns success.

Filesystem relevance: this file is a primary syscall boundary into file and vnode operations. It invokes file operation vectors (`fo_read`, `fo_write`, `fo_ioctl`), handles vnode-specific positioned I/O validation, maintains per-file I/O counters, interacts with sockets/devices/FIFOs/TTYs, and implements readiness notification over kqueue for descriptors used by filesystems and storage-backed objects.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/kern/sys_generic.c -->