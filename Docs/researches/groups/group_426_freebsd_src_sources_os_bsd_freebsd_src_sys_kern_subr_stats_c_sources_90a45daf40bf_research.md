# Group Research: FreeBSD kernel support routines subset A group 426

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/freebsd-src` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_stats.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_stats.c

## Purpose
Implements the FreeBSD `stats(9)` version-1 stats blob/template subsystem. It provides compact in-memory templates and per-entity stats blobs for values of interest (VOIs), supporting numeric aggregations, histograms, t-digests, string/JSON rendering, snapshot/reset, template lookup, and kernel sysctl exposure.

## Main Data Model
- `struct statsblobv1` is the serialized/cloneable blob header plus packed `struct voi[]`, `struct voistat[]`, and voistatdata regions.
- `struct voi` describes one value of interest: ID, data type, stats offset, maximum stat slot, and flags such as `VOI_REQSTATE`.
- `struct voistat` describes a stat attached to a VOI: stat type, data type, data offset/size, validity flag, and capped error count.
- `struct statsblobv1_tpl` combines template metadata (`struct metablob`) and a template stats blob.
- Data type metadata is centralized in `vsd_dtype2name`, `vsd_dtype2size`, `vsd_compoundtype`, and `numeric_limits`.

## Template Lifecycle
- `stats_v1_tpl_alloc()` creates a named template, initializes ABI/endian/size fields, stores it in global `tpllist`, and computes a stable template hash.
- `stats_v1_tpl_add_voistats()` adds a new VOI and its stats to a template. It supports adding new VOIs but explicitly rejects expanding an existing VOI with `EOPNOTSUPP`.
- `stats_v1_blob_expand()` grows and reshuffles the blob layout, preserving offsets and initializing newly inserted VOI/stat/data regions.
- `stats_tpl_update_hash()` hashes the template name, VOI names, and blob bytes.
- `stats_tpl_fetch()`, `stats_tpl_fetch_allocid()`, and `stats_tpl_id2name()` provide lookup by slot, name, and/or hash.

## Blob Lifecycle
- `stats_v1_blob_alloc()` allocates a stats blob sized from a template and initializes it.
- `stats_v1_blob_init()`/`stats_v1_blob_init_locked()` copy template bytes into an instance, set creation/reset timestamps, and stamp the template hash.
- `stats_v1_blob_clone()` copies a blob to kernel or user memory, preserving destination `maxsz` semantics and returning `EOVERFLOW` if the destination cannot hold the full source.
- `stats_v1_blob_snapshot()` clones a blob, optionally resets the source stats, and calls the currently stubbed `stats_v1_blob_finalise()`.
- `stats_v1_blob_destroy()` frees blob storage.
- `stats_v1_voistat_fetch_dptr()` returns the data pointer, type, and size for a VOI/stat pair.

## Stat Helpers
- `stats_vss_numeric_hlpr()` initializes SUM/MIN/MAX numeric stats for integer and fixed-point Q types.
- `stats_vss_hist_hlpr()` builds histogram initial values using linear, exponential, linear-exponential, or user-specified buckets; it supports count/range/value histogram forms and optional infinite bounds for compatible histogram types.
- `stats_vss_tdgst_hlpr()` initializes 32-bit or 64-bit t-digest centroid storage using the array-backed red-black (`ARB`) tree.
- `stats_vss_hlpr_init()` and `stats_vss_hlpr_cleanup()` run and clean helper-provided initial values.

## Update Behavior
- `stats_v1_voi_update()` validates blob ABI, VOI ID/type, and relative-update state, then updates all configured stats for the VOI.
- Relative updates use the hidden `VS_STYPE_VOISTATE` stat to accumulate the supplied delta into the previous value before updating stats.
- Numeric updates are split into:
  - `stats_v1_voi_update_sum()`
  - `stats_v1_voi_update_min()`
  - `stats_v1_voi_update_max()`
- Histogram updates search buckets from the end and increment the matching bucket or out-of-bounds count.
- T-digest updates convert the VOI value to the centroid precision, merge into an eligible centroid or allocate a new centroid, and compress/reinsert when full.
- Per-stat errors increment a capped `errs` field via `VS_INCERRS()`.

## Rendering and Visiting
- `stats_v1_blob_iter()` iterates VOIs and voistats with flags for first/last callback, VOI, and voistat.
- `stats_v1_blob_tostr()` renders freeform or JSON output, optionally including template metadata and object-dump internals.
- `stats_voistatdata_tostr()` renders primitive numeric, Q, histogram, t-digest, and VOISTATE data.
- `stats_v1_blob_visit()` exposes each stat through a caller-provided callback with `struct sb_visit`.

## Kernel Integration
- Uses `rwlock` in kernel and `pthread_rwlock_t` in userland compatibility builds for global template list protection.
- Kernel allocation uses `M_STATS`; userland mode uses libc allocation wrappers.
- Exposes `kern.stats.templates` sysctl for available templates.
- `stats_tpl_sample_rates()` is a reusable sysctl handler for subsystem-specific template sampling rate lists. It renders and parses CSV-like `template:hash=percent` specifications, validates cumulative sampling at <=100%, and calls subsystem callbacks to get/put rate arrays.
- `stats_tpl_sample_rollthedice()` chooses a sampled template using either PRNG output or deterministic hash of seed bytes.

## Concurrency and Invariants
- Global template list is protected by `TPL_LIST_*` locks.
- Template mutation is under write lock; blob instance updates appear caller-synchronized and are not internally locked.
- Blob offsets are 16-bit; `SB_V1_MAXSZ` prevents v1 blobs from exceeding 65535 bytes.
- Numerous `KASSERT`s guard ABI layout, stat initialization, type validity, t-digest tree consistency, and size/offset expectations.

## Notable Limitations and Risks
- Existing VOI expansion is not implemented.
- `stats_v1_blob_finalise()` is a stub.
- Histogram update uses a linear reverse bucket scan.
- T-digest compression uses pseudo-random centroid reinsertions and contains comments about fidelity/underflow tracking not yet implemented.
- Template uniqueness after hash update is noted but not fully enforced after VOI additions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_syscall.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_syscall.c

## Purpose
Provides common syscall entry and return handling used by machine-dependent syscall paths. It centralizes syscall argument fetching, tracing, Capsicum enforcement, audit/DTrace hooks, syscall execution, return value setup, and ptrace syscall-stop behavior.

## Main Flow
- `syscallenter(struct thread *td)`:
  - Increments syscall VM counter and resets per-syscall tick accounting.
  - Updates thread copy-on-write generation if process COW generation changed.
  - Handles traced syscall-entry state and debugger writeback (`TDB_USERWR`).
  - Fetches syscall number/arguments through the process ABI vector.
  - Emits KTRACE and KTR syscall-start events.
  - Stops for `PTRACE_SCE`; if debugger changed user registers/memory, refetches syscall args.
  - Enforces Capsicum capability mode by rejecting non-`SYF_CAPENABLED` syscalls with `ECAPMODE`.
  - Fetches fast signal-block state when required.
  - Handles dynamic syscall thread accounting with `syscall_thread_enter()`/`syscall_thread_exit()`.
  - Fires audit and KDTrace syscall entry/return hooks around `se->sy_call`.
  - Stores the syscall error in `td_errno` unless the syscall used `TDP_NERRNO`.
  - Sets ABI-specific return values via `sv_set_syscall_retval()`.
  - Copies extended error state to userspace when `TDP2_UEXTERR` is active.

- `syscallret(struct thread *td)`:
  - Converts Capsicum violations into `SIGTRAP/TRAP_CAP` when configured.
  - Calls `userret()` to handle scheduler, signal, profiling, and user-return checks.
  - Emits KTRACE syscall-return records.
  - Handles traced syscall-exit stops, including Linux ABI exec-stop compatibility.
  - Clears syscall tracing/debug flags.

## Dependencies
Uses process ABI vectors (`p_sysent`), syscall table entries (`struct sysent`), ptrace flags, Capsicum, audit, KDTrace hooks, KTRACE, and `userret()` from `subr_trap.c`.

## Concurrency and State
- Uses `PROC_LOCK()` around debug/tracing flag updates and ptrace-stop checks.
- Assumes syscall argument and return state is stored in the current thread (`td_sa`, `td_retval`, `td_errno`).
- Dynamic syscall entries may require per-syscall thread enter/exit bookkeeping.

## Filesystem Relevance
All filesystem syscalls pass through this path. This file is where VFS-facing syscalls receive common tracing, capability-mode validation, audit framing, debugger stops, and return-value handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_syscall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_taskqueue.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_taskqueue.c

## Purpose
Implements FreeBSD taskqueues: priority-ordered deferred execution queues backed by software interrupts or kernel threads. Taskqueues are used broadly by drivers and kernel subsystems for asynchronous work.

## Core Structures
- `struct taskqueue` stores queued tasks, active/running tasks, sequence counters, callout count, lock, enqueue callback, context, name, worker threads, flags, and optional lifecycle callbacks.
- `struct taskqueue_busy` tracks a running task, active sequence number, and cancellation state.
- Queue flags include active, blocked, and unlocked-enqueue behavior.
- Timeout task flags track armed callouts and drains in progress.

## Queue Creation and Destruction
- `_taskqueue_create()` allocates queue/name storage, initializes lists and mutex, stores enqueue callback/context, detects queues that may drop the lock before enqueue callbacks, and marks the queue active.
- `taskqueue_create()` creates a normal mutex-backed taskqueue.
- `taskqueue_create_fast()` creates a spin-mutex-backed fast taskqueue.
- `taskqueue_free()` marks inactive, waits for workers/callouts to terminate, asserts no active tasks or armed timeout tasks remain, then frees resources.

## Enqueue and Scheduling
- `taskqueue_enqueue_locked()` inserts tasks by descending priority, counts repeated enqueues via `ta_pending`, supports `TASKQUEUE_FAIL_IF_PENDING` and `TASKQUEUE_FAIL_IF_CANCELING`, and calls the queue enqueue hook unless blocked.
- `taskqueue_enqueue_flags()` and `taskqueue_enqueue()` wrap locked enqueue.
- Timeout tasks use `_timeout_task_init()`, `taskqueue_enqueue_timeout_sbt()`, `taskqueue_enqueue_timeout()`, and `taskqueue_timeout_func()` around callouts.

## Execution
- `taskqueue_run_locked()` removes tasks from the pending queue, marks them active, drops the queue lock while running `ta_func`, reenters NET_EPOCH for network tasks, then wakes drain waiters.
- `taskqueue_run()` wraps execution with locking.
- `taskqueue_thread_loop()` runs worker-thread lifecycle callbacks, drains tasks until inactive, runs shutdown callbacks, decrements worker count, and exits.

## Draining, Cancellation, and Quiescence
- `taskqueue_cancel()` removes pending tasks and marks running tasks as canceling.
- `taskqueue_cancel_timeout()` stops the callout and cancels the queued task.
- `taskqueue_drain()` waits for a specific task to be neither pending nor active.
- `taskqueue_drain_all()` waits for tasks queued before the drain and tasks already active.
- `taskqueue_drain_timeout()` prevents timeout rearming, drains the callout, then drains the task.
- `taskqueue_quiesce()` loops until both queued and active work are empty.
- `taskqueue_block()`/`taskqueue_unblock()` suppress and resume enqueue-triggered execution.

## Built-In Queues
Defines:
- `taskqueue_swi`
- `taskqueue_swi_giant`
- `taskqueue_thread`
- `taskqueue_fast`

Software interrupt queues schedule SWIs; thread queues wake worker threads.

## Concurrency and Invariants
- Queue locking switches between normal mutex and spin mutex based on `tq_spin`.
- Running tasks are tracked in `tq_active`; drain and cancellation logic depends on this list.
- Some enqueue hooks are allowed after releasing the queue lock to avoid lock-order or spin-lock issues.
- `tq_callouts` also blocks queue teardown while timeout/drain operations are outstanding.

## Filesystem Relevance
Filesystem and storage drivers commonly use taskqueues for completion callbacks, deferred cleanup, timeout handling, and work that must not run directly in interrupt or lock-heavy contexts.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_taskqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_terminal.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_terminal.c

## Purpose
Bridges terminal emulator state, TTY devices, and console devices. It wraps the `teken` terminal emulator with a `struct terminal` interface and exposes both ttydevsw and consdev operations.

## Terminal Allocation and Setup
- `terminal_alloc()` allocates and initializes a terminal, sets terminal class callbacks and driver softc.
- `terminal_init()` initializes console spin locking when needed, initializes `teken`, reads `teken.fg_color`/`teken.bg_color` tunables, adjusts default/kernel attributes, and sets default emulator attributes.
- `terminal_maketty()` allocates and publishes a TTY device using formatted terminal name.
- `terminal_set_winsize_blank()` updates terminal and teken dimensions, optionally blanks the display, calls driver fill, and syncs TTY window size.
- `terminal_set_winsize()` is the default blanking resize wrapper.
- `terminal_set_cursor()` forwards cursor updates to teken.
- `terminal_mute()` suppresses terminal input/rendering temporarily.

## Input Paths
- `terminal_input_char()` converts terminal characters to UTF-8 and injects into TTY discipline, ignoring the right half of CJK full-width characters.
- `terminal_input_raw()` injects one raw byte into TTY discipline.
- `terminal_input_special()` asks teken for a key sequence and injects it into the TTY.

## TTY Binding
The `terminal_tty_class` operations:
- `termtty_open()` and `termtty_close()` notify driver `tc_opened`.
- `termtty_outwakeup()` drains TTY output into teken, calls `tc_done()`, and rings the bell if teken requested it.
- `termtty_ioctl()` handles `CONS_GETINFO` locally, forwards other ioctls to the terminal class while temporarily dropping the TTY lock, and resets cursor after `CONS_CLRHIST`.
- `termtty_mmap()` forwards mmap requests to the terminal class.

## Console Binding
- `termcn_cnregister()` allocates or reuses a `consdev`, marks the terminal as console, initializes console mode, and registers with `cnadd()`.
- `termcn_cnprobe()` initializes and delegates console probing.
- `termcn_cngetc()` and `termcn_cnputc()` call terminal-class console get/put operations.
- `termcn_cnputc()` temporarily applies kernel-message attributes while feeding a byte to teken.
- `termcn_cngrab()`/`termcn_cnungrab()` delegate debugger/console grab transitions.

## Teken Callbacks
`termteken_*` functions translate emulator events to terminal-class methods:
- bell, cursor, putchar, fill, copy, pre/post input, parameter changes.
- `termteken_respond()` is disabled because injecting emulator responses can cause lock and feedback-loop problems.

## Concurrency
- Normal TTY output relies on TTY locking.
- Console output can race with TTY output and uses `tm_mtx` spin locking when `TF_CONS` is set.
- Separate lock macros distinguish generic, TTY-side, and console-side paths.

## Filesystem Relevance
Not filesystem-specific, but it is part of the kernel’s common I/O surface and console diagnostics path used during filesystem/storage errors, boot logs, and debugger interaction.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_terminal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_ticks.S -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_ticks.S

## Purpose
Defines the kernel tick counters at assembly/linkage level.

## Symbols
- `ticksl`: global long-sized tick counter storage in `.bss`.
- `ticks`: global int-sized alias over the low-address or endian-correct portion of `ticksl`.
- `jiffies`: LinuxKPI-compatible alias of `ticksl`.

## Endianness Handling
- Little-endian builds set `TICKS_OFFSET` to `0`.
- Big-endian builds place `ticks` at `__SIZEOF_LONG__ - __SIZEOF_INT__` within `ticksl` so it aliases the low-order integer bits.

## Architecture Notes
- On AArch64, emits the GNU property note via `GNU_PROPERTY_AARCH64_FEATURE_1_NOTE`.
- Adds `.note.GNU-stack` marker.

## Filesystem Relevance
Many kernel subsystems, including filesystems and storage code, use `ticks` for timeout, aging, and scheduling logic. This file supplies the shared storage/aliasing contract.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_ticks.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_trap.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_trap.c

## Purpose
Provides common user-return and asynchronous software trap (AST) handling for trap and syscall paths.

## `userret()`
Runs before returning to user mode:
- Asserts the process is not exiting.
- In diagnostic builds, verifies pending signal AST state for single-threaded processes.
- Charges profiling ticks with `addupc_task()` when process profiling is enabled.
- Calls HWPMC user-return hook when samples are pending.
- Calls `sched_userret()` for scheduler priority/accounting updates.
- Performs strict invariants: no critical section, no locks, no read locks, no shared sx/lockmanager locks, no nofaulting, sleep enabled, not pinned except callchain, no reserved vnode, no deferred stop signals, no wired vslock space.
- With VIMAGE, asserts no leaked current vnet.

## AST Registration
- `struct ast_entry` maps AST slot to flags, thread pflags mask, and handler function.
- Default `TDA_AST` handler is `ast_prep()`, which increments trap count, resets ticks, and updates thread COW generation.
- `ast_register()` installs handlers with memory ordering.
- `ast_deregister()` clears handlers but explicitly does not drain possible in-flight executions.
- `ast_sched_locked()`, `ast_unsched_locked()`, `ast_sched()`, and `ast_sched_mask()` manipulate thread AST bits.

## AST Execution
- `ast_handler()` optionally stores the trapframe in `td_frame`, clears scheduled AST bits, validates user-mode trapframes, then scans registered handlers.
- Handler execution depends on flags:
  - unconditional handlers,
  - handlers requiring a scheduled AST bit,
  - kernel-clear handlers for destructor/cleanup paths,
  - optional thread-pflag constraints.
- `ast()` handles current-thread ASTs and then calls `userret()`.
- `ast_kclear()` clears kernel AST state, including for thread teardown.

## Utility
- `syscallname()` maps syscall code to ABI-specific syscall name, returning `"unknown"` if unavailable.

## Filesystem Relevance
Filesystem syscalls return through this code. The lock and reserved-vnode assertions are important guardrails for VFS/file operation implementations returning to userspace.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_trap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_turnstile.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_turnstile.c

## Purpose
Implements turnstiles: wait queues for non-sleepable locks with priority inheritance. Turnstiles are assigned dynamically to locks via a hash table instead of being embedded in every lock.

## Core Model
- Each thread owns a preallocated turnstile (`td_turnstile`).
- The first waiter lends its turnstile to the contended lock.
- Later waiters put their own turnstiles on the lock turnstile’s free list.
- Woken threads reclaim a turnstile from the lock’s free list or the lock turnstile itself.
- Turnstiles maintain separate exclusive/shared blocked queues plus a pending wake queue.

## Main Structures
- `struct turnstile` contains a spin lock, blocked queues, pending queue, hash/free/list links, referenced lock object, and owner thread.
- `struct turnstile_chain` is a hash bucket protected by a spin mutex.
- `td_contested_lock` protects per-thread lists of contested locks.

## Initialization
- `init_turnstiles()` initializes the chain table, contested lock, and thread0 contested list very early.
- `init_turnstile0()` creates the UMA zone and gives thread0 a turnstile.
- Optional `TURNSTILE_PROFILING` sysctls track chain depth and max depth.

## Waiting and Priority Propagation
- `turnstile_trywait()` locks the chain, finds or prepares a turnstile for a lock.
- `turnstile_wait()` inserts the current thread into the correct shared/exclusive priority queue, lends or free-lists turnstiles, sets thread blocked state, unlocks the chain, propagates priority, emits sleep probe, and context-switches.
- `propagate_priority()` walks owner chains, lending priority through nested lock dependencies. It panics if a sleeping thread owns a non-sleepable lock.
- `turnstile_adjust()` and `turnstile_adjust_thread()` reposition waiters when priority changes and propagate lowered effective priority when needed.

## Ownership and Wakeup
- `turnstile_claim()` gives ownership of a turnstile to the current thread and lends priority from the first waiter.
- `turnstile_signal()` moves the highest-priority waiter in one queue to pending and assigns it a turnstile.
- `turnstile_broadcast()` moves all waiters in one queue to pending and assigns each a turnstile.
- `turnstile_unpend()` clears ownership, recalculates current thread’s lent priority, marks pending threads runnable, clears their blocked state, and releases the turnstile lock.
- `turnstile_disown()` removes ownership without waking, then recomputes current thread priority.

## Lookup and Locking APIs
- `turnstile_chain_lock()`/`turnstile_chain_unlock()` lock hash buckets.
- `turnstile_lookup()` locates and locks a turnstile for a lock under chain lock.
- `turnstile_lock()` safely locks a turnstile from a turnstile pointer if its lock object is stable.
- `turnstile_unlock()` and `turnstile_cancel()` release locks and clear stale current-thread lock object state.
- `turnstile_head()` and `turnstile_empty()` inspect waiter queues.

## Debugging
DDB commands show:
- a turnstile by lock/turnstile address,
- lock chains,
- all chains,
- lock trees/waiter trees.

## Concurrency and Invariants
- Chain spin locks protect hash membership.
- Turnstile spin locks protect blocked/pending queues and owner-sensitive state.
- `td_contested_lock` protects per-thread contested-lock lists.
- Thread lock pointer is switched to the turnstile lock while the thread is blocked.
- Priority queues are ordered by effective priority.

## Filesystem Relevance
Filesystem code frequently uses mutexes/rwlocks around vnode, mount, buffer, and device state. Turnstiles provide priority inheritance for non-sleepable lock contention that can occur on those paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_turnstile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_uio.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_uio.c

## Purpose
Implements common `uio`/`iovec` movement helpers and related user/kernel copy utilities. This is central to read/write paths, including VFS and filesystem code.

## Copy Helpers
- `copyin_nofault()` and `copyout_nofault()` disable page faults around `copyin()`/`copyout()`.
- `physcopyin()` and `physcopyout()` build a one-element `uio` and use `uiomove_fromphys()` to copy to/from physical pages.
- `physcopyin_vlist()` and `physcopyout_vlist()` copy through bus DMA segment lists with offsets.

## `uiomove`
- `uiomove()` copies between kernel buffer and `uio`, allowing faults.
- `uiomove_nofault()` performs the same operation with nofault behavior.
- `uiomove_faultflag()` handles the core loop:
  - validates direction, segment type, current thread for userspace `uio`, and nonnegative residual;
  - sets thread flags for deadlock treatment and optional nofault behavior;
  - iterates iovecs, skips empty entries, caps copy size, and updates base/length/residual/offset;
  - handles `UIO_USERSPACE` via `copyin`/`copyout`, `UIO_SYSSPACE` via `bcopy`, and `UIO_NOCOPY` by only advancing state.

## UIO State Utilities
- `uioadvance()` advances a `uio` by a known offset without copying.
- `uiomove_frombuf()` validates buffer/uio offsets and copies from a bounded kernel buffer.
- `ureadc()` appends a single character to a `uio`.

## IOV/UIO Allocation
- `copyiniov()` copies user iovec array into kernel memory after max-count validation.
- `copyinuio()` allocates a `uio`, copies user iovecs, sets `UIO_USERSPACE`, computes residual, and rejects overflow above `IOSIZE_MAX`.
- `allocuio()`, `freeuio()`, and `cloneuio()` manage uio+iovec storage.

## User Mapping Helpers
- `copyout_map()` maps anonymous user memory after the process data limit area for copyout-style operations.
- `copyout_unmap()` removes that mapping.

## User Word Wrappers
- `fuword32()`, `fuword64()`, `fuword()` wrap `fueword*` APIs and return `-1` on failure.
- `casuword32()` and `casuword()` wrap userspace compare-and-swap helpers.

## Kernel Interface
- Exposes `kern.iov_max` sysctl as `UIO_MAXIOV`.

## Filesystem Relevance
This file is directly used by filesystem read/write, directory read, extended attribute, ioctl, and device I/O paths. It defines the canonical semantics for advancing `uio_resid`/`uio_offset` and handling user versus kernel buffers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_uio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_unit.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_unit.c

## Purpose
Implements compact unit-number allocation (`unrhdr`) with lowest-free-number-first policy. It is used by kernel subsystems that need integer IDs, minor/unit numbers, or similar finite/infinite-ish number spaces.

## Representation
- `struct unrhdr` tracks low/high bounds, compact leading allocated run (`first`), trailing free run (`last`), busy count, allocated chunk count, active chunk list, postponed-free list, and optional mutex.
- `struct unr` is the basic chunk:
  - `ptr == NULL`: free run,
  - `ptr == uh`: allocated run,
  - other pointer: bitmap (`struct unrb`) representing mixed allocation.
- `NBITS` is the number of allocatable bits stored in a bitmap the size of `struct unr`.

## Locking and Allocation Constraints
- If no mutex is supplied, a global `unitmtx` is used.
- `UNR_NO_MTX` disables locking.
- `alloc_unrl()` requires the mutex already held and never sleeps.
- `alloc_unr()` locks, allocates, cleans postponed frees, and unlocks.
- `free_unr()` may allocate memory and may sleep; it preallocates two chunks before locking.
- `clean_unrhdrl()` frees postponed chunks while temporarily dropping the allocator mutex.

## Lifecycle
- `init_unrhdr()` initializes an existing header.
- `new_unrhdr()` allocates and initializes a header.
- `delete_unrhdr()` asserts no busy allocations, no memory leak, and no postponed frees.
- `clear_unrhdr()` frees all chunks and reinitializes the range.

## Allocation
- `alloc_unrl()` returns the lowest free number:
  - ideal compact case uses only `first`/`last`;
  - otherwise consumes from the first chunk, either shrinking a free run or setting the first clear bitmap bit;
  - then calls `collapse_unr()` to simplify representation.
- `alloc_unr_specific()` preallocates memory and calls `alloc_unr_specificl()` to allocate a requested item.
- `alloc_unr_specificl()` rejects out-of-range or already allocated items, creates/splits chunks as needed, updates `last`, increments busy count, and collapses/optimizes.

## Freeing
- `free_unr()` preallocates chunks, locks, calls `free_unrl()`, cleans postponed frees, unlocks, and frees unused preallocations.
- `free_unrl()` validates range and that the item is allocated, then:
  - adjusts compact ideal/leading regions,
  - clears bitmap bits,
  - converts single allocated runs to free runs,
  - shifts boundary frees into neighboring free runs,
  - or splits an allocated run around the freed item.
- `collapse_unr()` converts full/empty bitmaps to runs, deletes zero-length chunks, merges adjacent same-kind runs, folds leading allocated/trailing free runs into `first`/`last`, and calls `optimize_unr()`.

## Compaction
- `optimize_unr()` finds adjacent chunks that can fit into one bitmap and saves memory by combining runs/bitmaps into bitmap representation.
- Bitmap conversion uses postponed frees via `delete_unr()` so memory can be freed safely later.

## Iteration and Debugging
- `create_iter_unr()`, `next_iter_unr()`, and `free_iter_unr()` iterate allocated unit numbers in increasing order.
- Diagnostic `check_unrhdr()` verifies busy count and chunk allocation count.
- DDB/userland debug helpers print allocator headers, runs, and bitmaps.
- DDB commands can show `unrhdr` and iterator state.

## Userland Test Driver
When not built in `_KERNEL`, the file includes:
- libc/pthread-free shims for mutex/allocation assertions,
- stochastic allocation/free tests,
- iterator tests,
- command-line options for repetitions, iterator mode, and verbosity.

## Filesystem Relevance
Filesystems and storage drivers often need compact ID spaces for units, devices, clone IDs, request IDs, or minor numbers. This allocator provides a memory-efficient kernel primitive for those uses.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_unit.c -->