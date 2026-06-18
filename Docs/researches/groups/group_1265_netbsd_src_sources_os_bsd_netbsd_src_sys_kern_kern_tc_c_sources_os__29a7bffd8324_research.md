# Group Research: group_1265_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_kern_tc_c_sources_os__29a7bffd8324

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_tc.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_tc.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kern_tc.c`.
- Subset scope: `Docs/research_subset_a.md`, which includes `sources/os/bsd/netbsd-src`.
- This file implements NetBSD's kernel timecounter framework, lockless time read paths, boot/realtime base handling, timecounter registration/detach, UTC stepping, NTP second windup, and RFC 2783 PPS support.

## Purpose And Main Interfaces

- Provides early dummy timecounter support until real hardware timecounters are registered.
- Maintains a ring of `struct timehands` snapshots used by readers without taking `timecounter_lock`.
- Exports high-resolution time APIs: `binuptime`, `nanouptime`, `microuptime`, `bintime`, `nanotime`, `microtime`, and cached `get*` variants.
- Exports timecounter lifecycle: `tc_init`, `tc_detach`, `tc_gonebad`, `tc_getfrequency`, `inittimecounter`, and `tc_ticktock`.
- Exports time setting through `tc_setclock`.
- Implements PPS APIs: `pps_ioctl`, `pps_init`, `pps_capture`, `pps_event`, and `pps_ref_event`.

## Key Data Structures

- `struct timehands` contains the active timecounter pointer, counter-to-time scale, counter offset, bintime offset, cached micro/nano realtime, and generation counter.
- `timehands` is a volatile pointer to the current published timehands snapshot.
- `timecounter` is the currently selected hardware counter.
- `timecounters` is the registered counter list.
- `timebase` is a seqlock-like structure storing boot-time offset used to convert uptime to realtime.
- `time__second` / `time__uptime`, or 32-bit fallback storage, provide fast global second snapshots.

## Control Flow

- `tc_init` validates counter frequency relative to `hz`, inserts it into the counter list, and may auto-select it when quality/frequency is better than the current counter.
- `tc_windup` copies the current timehands into the next ring slot, applies hardware counter deltas, handles NTP second updates, caches realtime values, recalculates scaling, publishes the new generation, and advances `timehands`.
- Readers loop on `th_generation` to avoid torn reads while `tc_windup` updates a slot.
- `tc_detach` removes a counter, switches away if necessary, bumps a removal generation, and waits until all LWPs have stopped referencing old counter state.
- `tc_setclock` changes UTC by updating `timebase`, then winds up timehands and optionally logs the step.
- `tc_ticktock` periodically calls `tc_windup` and switches counters if a selected counter was marked bad.
- PPS handling captures counter values, converts them to timestamps against captured timehands, handles reference modes, applies offsets, updates sequences, and optionally feeds `hardpps`.

## Concurrency And Invariants

- `timecounter_lock` serializes counter list changes and windup.
- Lockless readers use generation checks and memory barriers.
- Timecounter detach safety uses per-LWP `l_tcgen`, `timecounter_removals`, and `xc_barrier`.
- `timebase.gen` is odd while changing and even while stable.
- 32-bit architectures emulate atomic 64-bit time snapshots with sentinel high words and producer/consumer barriers.

## Risks And Edge Cases

- Incorrect generation or barrier changes can create torn or non-monotonic time reads.
- `tc_detach` must not free a counter until all readers have left old generations.
- Large time steps are capped for NTP update looping by `LARGE_STEP`.
- PPS paths depend on stable captured timehands; events are dropped if windup or counter changes invalidate captured state.
- Low-quality or insufficient-frequency counters are demoted to avoid overflow between hardclock updates.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_tc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_threadpool.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_threadpool.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kern_threadpool.c`.
- Subset scope: `Docs/research_subset_a.md`.
- This file implements NetBSD kernel thread pools: shared unbound pools and shared per-CPU pools keyed by priority.

## Purpose And Main Interfaces

- Provides reusable kernel worker threads so scheduling a job avoids allocation/sleep in the common path.
- Public pool lifecycle: `threadpools_init`, `threadpool_get`, `threadpool_put`, `threadpool_percpu_get`, `threadpool_percpu_put`, `threadpool_percpu_ref`, and `threadpool_percpu_ref_remote`.
- Public job lifecycle and control: `threadpool_job_init`, `threadpool_job_destroy`, `threadpool_schedule_job`, `threadpool_cancel_job_async`, `threadpool_cancel_job`, and `threadpool_job_done`.

## Key Data Structures

- `struct threadpool` owns `tp_lock`, one dispatcher pseudo-thread record, queued jobs, idle worker thread list, pool refcount, dying flag, optional bound CPU, and priority.
- `struct threadpool_thread` tracks an LWP, saved LWP name, assigned pool, assigned job, condition variable, and idle-list entry.
- `struct threadpool_unbound` wraps an unbound pool with a global reference count.
- `struct threadpool_percpu` wraps a `percpu_t` containing one `struct threadpool *` per CPU.
- `struct threadpool_job` fields are initialized here but defined externally; jobs carry a callback, interlock, refcount, condition variable, running thread pointer, and display name.

## Control Flow

- `threadpool_get` looks up an unbound pool by priority, creates one outside `threadpools_lock` if absent, then handles races by destroying unused duplicate pools.
- `threadpool_percpu_get` similarly creates a per-CPU pool collection and verifies each CPU initialized successfully.
- `threadpool_create` initializes pool state and creates a dispatcher kthread bound to the requested CPU if applicable.
- `threadpool_schedule_job` requires the caller to hold the job lock. If the job is already running or assigned, scheduling is ignored. Otherwise it takes a job reference and assigns either an idle worker or the dispatcher.
- The dispatcher waits for queued jobs. If no idle workers exist, it creates a worker. If workers exist, it transfers the queued job to one.
- Worker threads wait for assigned jobs, temporarily rename their LWP to the job name, run the job function, require the job to call `threadpool_job_done`, then return to the idle list.
- Idle workers exit after `kern.threadpool.idle_ms` without work, or when the pool is dying.
- `threadpool_destroy` marks the pool dying, wakes dispatcher/workers, and waits for pool refcount to reach zero.

## Concurrency And Invariants

- Global pool registries are protected by `threadpools_lock`.
- Per-pool queues and thread state are protected by `tp_lock`.
- Job completion/cancellation is synchronized through the caller-provided `job_lock`.
- Job refcounts prevent destruction while dispatcher or workers temporarily drop locks.
- Workers assert that jobs call `threadpool_job_done`; otherwise the LWP name is not restored and the assertion fires.
- Remote per-CPU references disable preemption around `percpu_getptr_remote`.

## Risks And Edge Cases

- `threadpool_cancel_job_async` can conservatively fail when the caller passes a different pool than the dispatcher-assigned pool; the code documents this safe false-negative behavior.
- Dispatcher thread creation failure sleeps and retries, leaving queued jobs pending.
- Pool destruction requires no queued jobs and waits for dispatcher/workers to exit.
- Priority validation only accepts `PRI_NONE` or priorities in `[PRI_USER, PRI_COUNT)`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_threadpool.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_time.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_time.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kern_time.c`.
- Subset scope: `Docs/research_subset_a.md`.
- This file implements time-related syscalls, time setting, nanosleep, BSD interval timers, POSIX timers, virtual/profiling timers, and timer signal delivery.

## Purpose And Main Interfaces

- Initializes timer subsystem with `time_init`.
- Provides clock syscalls: `sys___clock_gettime50`, `sys___clock_settime50`, `sys___clock_getres50`, `sys_clock_nanosleep`, and `sys_clock_getcpuclockid2`.
- Provides legacy time syscalls: `sys___gettimeofday50`, `sys___settimeofday50`, `sys___adjtime50`, `sys___getitimer50`, and `sys___setitimer50`.
- Provides POSIX timer syscalls: `sys_timer_create`, `sys_timer_delete`, `sys___timer_settime50`, `sys___timer_gettime50`, and `sys_timer_getoverrun`.
- Exports helper APIs for process timer cleanup and ticks: `ptimers_free` and `ptimer_tick`.

## Key Data Structures

- `itimer_mutex` protects interval timer state.
- `struct itimer` is the generic timer representation used for realtime, monotonic, virtual, and profiling timers.
- Realtime/monotonic timers use callouts and absolute deadlines.
- Virtual/profiling timers use per-process delta lists.
- `struct ptimers` stores the per-process timer array and virtual/prof lists.
- `struct ptimer` wraps an `itimer` with signal event state, owning process, overrun counters, timer index, and softint queue flag.
- `ptimer_queue` collects fired process timers for softint signal delivery.

## Control Flow

- `settime1` validates the target time, authorizes privileged time changes, calls `tc_setclock`, updates the RTC with `resettodr`, and notifies realtime timers.
- `clock_settime1` only allows setting `CLOCK_REALTIME`; monotonic is read-only.
- `clock_getres1` reports timecounter-derived resolution for realtime, monotonic, process CPU, and thread CPU clocks.
- `nanosleep1` converts requested time to ticks, sleeps with `kpause`, recomputes remaining time, and retries if woke early without an error.
- `adjtime1` reads or sets `time_adjtime` under `timecounter_lock`, saturating extreme deltas.
- `itimer_init`, `itimer_poison`, `itimer_fini`, `itimer_settime`, and `itimer_gettime` implement the generic interval timer lifecycle.
- `itimer_callout` fires realtime/monotonic timers, computes overruns, and rearms periodic timers.
- `timer_create1` allocates a POSIX timer slot, validates `sigevent`, initializes the right clock type, and assigns defaults when no event is supplied.
- `dotimer_settime` validates and converts absolute/relative values, then arms the generic timer.
- `dosetitimer` lazily allocates the BSD timers and maps timer kinds to signals.
- `ptimer_tick` decrements virtual/prof timers from hardclock.
- `ptimer_intr` drains the softint queue and posts `SI_TIMER` signals, compressing signals when one is already pending.

## Concurrency And Invariants

- `itimer_lock`/`itimer_unlock` wrap `itimer_mutex`.
- `itimer_fini` intentionally releases `itimer_mutex` before destroying callouts.
- `itimer_settime` can return `ERESTART` when a real timer callout fired and lock dropping may invalidate looked-up state.
- Virtual timer lists are delta-encoded; insert/remove adjusts neighboring timers.
- Process signal delivery takes `proc_lock` and drops/reacquires `itimer_mutex` around `kpsignal`.

## Risks And Edge Cases

- `time_wraps` protects against extreme time setting and negative deltas.
- Realtime timer deadlines must be updated when wall clock time changes.
- Real timer callout delays compress multiple expirations into one signal while recording overrun counts.
- POSIX timers are bounded by `TIMER_MAX`; BSD timers occupy low reserved slots.
- `SIGEV_NONE` and non-signal notifications do not enqueue signals.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_time.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_timeout.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_timeout.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kern_timeout.c`.
- Subset scope: `Docs/research_subset_a.md`.
- This file implements NetBSD callouts with per-CPU hierarchical timing wheels and soft interrupt execution.

## Purpose And Main Interfaces

- Startup and per-CPU initialization: `callout_startup` and `callout_init_cpu`.
- Callout lifecycle: `callout_init`, `callout_destroy`, `callout_setfunc`, `callout_reset`, `callout_schedule`, `callout_stop`, and `callout_halt`.
- Callout status: `callout_expired`, `callout_active`, `callout_pending`, `callout_invoking`, and `callout_ack`.
- Tick/dispatch: `callout_hardclock` and internal `callout_softclock`.
- DDB support: `db_show_callout`.

## Key Data Structures

- `struct callout_cpu` contains the per-CPU lock, sleep queue for halt waiters, tick count, active callout and active LWP, late/block event counters, todo queue, 1024 timing wheel buckets, and CPU identity.
- Timing wheel constants define four 256-bucket levels.
- Circular queue macros implement intrusive queue insert, remove, append, and traversal.
- `callout_impl_t` is the private implementation stored inside public `callout_t`.
- `callout_syncobj` defines sleep behavior for threads waiting on active callouts.

## Control Flow

- `callout_startup` initializes the boot CPU callout state early enough for registration.
- `callout_init_cpu` allocates or finalizes per-CPU callout state, establishes the shared softclock softint on the boot CPU, initializes sleep queues, and attaches event counters.
- `callout_init` chooses the current CPU for MPSAFE callouts when possible; otherwise binds to CPU0.
- `callout_schedule_locked` computes absolute expiration ticks, handles rescheduling, may migrate unbound callouts to the current CPU, and queues them on `cc_todo`.
- `callout_stop` removes pending callouts and clears pending/fired state without waiting for already-running callbacks.
- `callout_halt` cancels pending work and waits if the callout is active on another LWP.
- `callout_wait` sleeps on the per-CPU callout sleep queue, optionally drops/reacquires an interlock, and repeats because callouts may reschedule themselves.
- `callout_hardclock` advances ticks, cascades timing wheel buckets into the todo queue, and schedules softclock when work exists.
- `callout_softclock` drains due callouts, re-buckets future callouts, marks due callouts fired/invoking, runs callbacks with or without kernel lock based on `CALLOUT_MPSAFE`, and wakes halt waiters after callback completion.

## Concurrency And Invariants

- Each `callout_cpu` has its own spin mutex.
- `callout_lock` loops until it locks the same CPU that still owns the callout, handling concurrent migration.
- `cc_active` plus `cc_lwp` identify in-flight callbacks.
- `callout_destroy` asserts the callout is neither pending nor running elsewhere.
- `callout_halt` is forbidden from hard interrupt context.
- Non-MPSAFE callbacks run under the kernel lock.

## Risks And Edge Cases

- Tick comparisons intentionally use unsigned arithmetic cast through signed deltas to handle wraparound.
- Re-scheduling an already-pending callout earlier moves it to `todo`; later schedules leave it in place for later reclassification.
- Halt can return with `expired=true` if it had to wait for an active callback.
- DDB inspection avoids locking because other CPUs may be paused while holding callout locks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_timeout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_todr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_todr.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kern_todr.c`.
- Subset scope: `Docs/research_subset_a.md`.
- This file implements the kernel time-of-day register bridge for reading and writing hardware RTC/TOD clocks.

## Purpose And Main Interfaces

- Initialization and locking: `todr_init`, `todr_lock`, `todr_unlock`, and `todr_lock_owned`.
- Device attachment: `todr_attach`.
- System time synchronization: `todr_set_systime`, `todr_save_systime`, `inittodr`, and `resettodr`.
- Internal hardware operations: `todr_gettime` and `todr_settime`.

## Key Data Structures

- `todr_mutex` serializes TODR access.
- `todr_handle` stores the selected `todr_chip_handle_t`.
- `todr_initialized` catches early attachment misuse.
- `timeset` tracks whether system time has been established and should be saved back.
- `PREPOSTEROUS_YEARS` defines the minimum reasonable RTC year threshold, based on 2021.

## Control Flow

- `todr_attach` rejects non-system TODR devices if the backing device supports `DEVICE_IS_SYSTEM_TODR`, and only permits one configured TODR.
- `todr_set_systime` takes a filesystem-derived base time, rejects preposterous bases, reads the TODR if present, compares RTC and filesystem time, decides whether RTC or filesystem/default time is more trustworthy, seeds randomness with observed time data, and calls `tc_setclock`.
- If the RTC is absent or invalid, `todr_set_systime` logs warnings and uses filesystem/default base.
- `todr_save_systime` writes current kernel time back to the TODR only if system time was previously set and is nonzero.
- `resettodr` uses `mutex_tryenter` during shutdown to avoid hanging if another thread is using the RTC.
- `todr_gettime` supports either seconds-based or `clock_ymdhms` driver callbacks, enables TODR writes around operations if required by the device, applies `rtc_offset`, and validates calendar fields.
- `todr_settime` supports seconds-based or `clock_ymdhms` callbacks, subtracts `rtc_offset`, rounds microseconds for YMDHMS devices, and toggles write enable.

## Concurrency And Invariants

- Public time setting/saving functions require the TODR lock as documented and asserted.
- Driver callbacks can require write-enable even for reads.
- `todr_attach` asserts initialization has occurred.
- Only one global TODR handle is accepted.

## Risks And Edge Cases

- Bad RTC values before the 2021-derived threshold are rejected.
- Filesystem base time below five common years is treated as preposterous, except base zero suppresses one warning because it may mean unknown.
- RTC behind filesystem time by two or more days is treated as lost clock and rejected; RTC ahead is accepted with verbose warning.
- Shutdown writeback deliberately avoids blocking forever on `todr_mutex`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_todr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_turnstile.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_turnstile.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kern_turnstile.c`.
- Subset scope: `Docs/research_subset_a.md`.
- This file implements NetBSD turnstiles: lock wait queues with priority inheritance.

## Purpose And Main Interfaces

- Initialization and construction: `turnstile_init` and `turnstile_ctor`.
- Lookup and operation control: `turnstile_lookup` and `turnstile_exit`.
- Blocking and waking: `turnstile_block` and `turnstile_wakeup`.
- Sleep queue integration: `turnstile_unsleep` and `turnstile_changepri`.
- Debug support under `LOCKDEBUG`: `turnstile_print`.

## Key Data Structures

- `turnstile_chains[128]` maps synchronization object addresses to active turnstiles.
- `turnstile_locks[128]` are cacheline-padded chain locks.
- Each LWP owns a turnstile. A lock object only borrows a turnstile while one or more threads wait on it.
- Active turnstiles contain separate reader and writer sleep queues, wait counts, free turnstile list, object pointer, and priority-inheritance metadata.

## Control Flow

- `turnstile_lookup` hashes the lock object, takes the chain lock, and returns the active turnstile if any. The chain lock remains held.
- `turnstile_exit` releases the chain lock when a caller decides not to block.
- `turnstile_block` either lends the current LWP's turnstile to a lock with no active turnstile or puts the LWP's turnstile on the active turnstile free list. It enqueues the LWP on the selected reader/writer sleep queue, lends priority, then blocks.
- `turnstile_lendpri` walks the blocking chain via syncobj owner callbacks and lends the current effective priority to lower-priority owners to avoid priority inversion.
- `turnstile_unlendpri` removes a turnstile from the inheritor's lender list and recalculates inherited priority.
- `turnstile_wakeup` wakes a specified waiter or the first `count` waiters from the requested queue, restores priority inheritance if needed, removes waiters, and releases the chain lock.
- `turnstile_remove` returns an inactive turnstile to each awakened LWP or removes the active turnstile from the hash when the last waiter leaves.

## Concurrency And Invariants

- Hash chain locks double as sleep queue interlocks.
- Blocking is non-interruptible; `turnstile_unsleep` panics if called.
- Preemption is disabled during the delicate block/priority-lending/sleep sequence.
- The code uses try-lock restart logic while walking owner chains to avoid LWP lock deadlocks.
- Assertions check queue type, waiter counts, active object consistency, and inherited-priority ownership.

## Risks And Edge Cases

- A lock destroyed or corrupted while still in use is likely to trip assertions in priority inheritance paths.
- Priority inheritance is chain-walking and must handle owner changes while locks are dropped.
- `turnstile_changepri` delegates to `sleepq_changepri`; the comment marks priority inheritance handling as incomplete there.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_turnstile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_uidinfo.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_uidinfo.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kern_uidinfo.c`.
- Subset scope: `Docs/research_subset_a.md`.
- This file implements per-UID resource accounting and sysctl exposure.

## Purpose And Main Interfaces

- Initialization: `uid_init`.
- UID lookup: `uid_find`.
- Resource counter updates: `chgproccnt`, `chglwpcnt`, `chgsemcnt`, and `chgsbsize`.
- Sysctl and hash statistics: `kern.uidinfo.{proccnt,lwpcnt,lockcnt,semcnt,sbsize}` and `uid_stats`.

## Key Data Structures

- `uihashtbl` is an SLIST hash table of `struct uidinfo`.
- `uihash` is the hash mask from `hashinit`.
- `UIHASH(uid)` selects the bucket by UID.
- Each `uidinfo` holds counts such as processes, LWPs, locks, semaphores, and socket buffer usage.

## Control Flow

- `uid_init` creates a larger hash on MP systems, ensures UID 0 exists for interrupt-context socket buffer accounting, installs sysctls, and registers hash stats.
- `uid_find` searches a bucket locklessly. If absent, it allocates a zeroed `uidinfo`, initializes `ui_uid`, and atomically inserts it with `atomic_cas_ptr`; races restart and free the unused allocation.
- `chgproccnt`, `chglwpcnt`, and `chgsemcnt` find the UID record and atomically adjust the relevant count, asserting it does not go negative.
- `chgsbsize` atomically adjusts socket buffer usage and rolls back if a positive change exceeds the supplied limit.
- Sysctl reads find the effective UID's `uidinfo` and expose selected counters as quad values.

## Concurrency And Invariants

- UID table insertion intentionally bypasses SLIST abstraction to make head insertion atomic.
- Readers use `membar_datadep_consumer` while traversing buckets.
- Resource counters are modified with atomic add operations.
- UID records are not removed, avoiding reclamation hazards for lockless readers.
- UID 0 must always be present after initialization.

## Risks And Edge Cases

- `chgsbsize` casts the counter through `long *`; correctness depends on field type/layout matching.
- Sysctl counter lookup uses offsets into `struct uidinfo`; field name and layout changes must keep the table synchronized.
- Hash table size is tuned to reduce MP cacheline writeback pressure from long chains.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_uidinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_uuid.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_uuid.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kern_uuid.c`.
- Subset scope: `Docs/research_subset_a.md`.
- This file implements kernel UUID generation, printing, and endian encode/decode helpers.

## Purpose And Main Interfaces

- UUID creation: `sys_uuidgen` and `uuidgen`.
- Formatting: `uuid_snprintf` and `uuid_printf`.
- Binary encoding/decoding: `uuid_enc_le`, `uuid_dec_le`, `uuid_enc_be`, and `uuid_dec_be`.

## Key Data Structures

- `struct uuid` is asserted to be 16 bytes.
- UUID fields follow DCE layout: `time_low`, `time_mid`, `time_hi_and_version`, `clock_seq_hi_and_reserved`, `clock_seq_low`, and six-byte node.

## Control Flow

- `uuid_generate` fills all 16 bytes using `cprng_fast`, then sets version bits to version 4 and variant bits to the RFC/DCE reserved pattern.
- `sys_uuidgen` validates the requested count is between 1 and 2048, generates UUIDs one at a time, and copies each to userspace.
- `uuidgen` generates UUIDs into a kernel buffer, though its loop uses `while (--count > 0)`, so it generates `count - 1` UUIDs for positive input.
- `uuid_snprintf` formats canonical lowercase hexadecimal UUID text with hyphens.
- Endian helpers encode/decode the first three integer fields in little- or big-endian order and copy the remaining sequence/node bytes directly.

## Concurrency And Dependencies

- Randomness comes from the kernel CPRNG fast path.
- No persistent state, locks, allocation, or global counters are used.
- Userspace syscall output uses `copyout`.

## Risks And Edge Cases

- `sys_uuidgen` has an explicit batch upper bound of 2048.
- The internal `uuidgen` helper appears to skip generation when `count == 1` because it pre-decrements in the loop condition.
- Endian encode/decode functions require callers to provide at least 16 bytes of storage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_uuid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_veriexec.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_veriexec.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kern_veriexec.c`.
- Subset scope: `Docs/research_subset_a.md`.
- This file implements NetBSD Veriexec fingerprint registration, per-file verification state, mount-specific tables, strict-mode policy, and enforcement hooks.

## Purpose And Main Interfaces

- Initialization: `veriexec_init` and `veriexec_fpops_add`.
- Lookup and verification: `veriexec_lookup`, `veriexec_verify`, and internal `veriexec_file_verify`.
- Policy hooks: `veriexec_openchk`, `veriexec_removechk`, `veriexec_renamechk`, `veriexec_unmountchk`, and raw device kauth callback.
- Table/file management: `veriexec_file_add`, `veriexec_file_delete`, `veriexec_table_delete`, `veriexec_purge`, `veriexec_convert`, `veriexec_dump`, and `veriexec_flush`.

## Key Data Structures

- `struct veriexec_fpops` describes one hash algorithm: name, digest length, context size, and init/update/final callbacks.
- `struct veriexec_file_entry` stores one monitored file's lock, optional filename, access type flags, status, fingerprint bytes, hash ops, and filename length.
- `struct veriexec_table_entry` stores per-mount entry count and sysctl node.
- `veriexec_hook` is the fileassoc key binding entries to vnodes.
- `veriexec_mountspecific_key` stores per-mount Veriexec table metadata.
- `veriexec_op_lock` serializes global Veriexec operations.

## Control Flow

- `veriexec_init` registers fileassoc cleanup, device/system kauth listeners, mount-specific storage, global lock, and configured SHA fingerprint algorithms.
- `veriexec_fp_calc` reads a vnode page by page through `vn_rdwr`, updates the selected hash context, and returns the digest.
- `veriexec_file_verify` checks regular files only, looks up the vnode entry, enforces strict mode for missing entries, evaluates fingerprints when needed, validates requested access type, and enforces mismatch policy according to strictness.
- Strictness levels affect behavior:
  - learning can bypass when no table is loaded.
  - IDS denies fingerprint mismatches and protects monitored files from removal.
  - IPS additionally enforces access type, blocks writes to monitored files, and blocks monitored raw writes/unmounts.
  - lockdown denies non-monitored access and broad filesystem changes.
- `veriexec_file_add` resolves a path, validates regular file and fingerprint algorithm/length, validates entry flags, optionally evaluates on load, ignores exact duplicate hardlink entries, creates mount table state as needed, and associates the entry with the vnode.
- `veriexec_openchk` verifies opened files, blocks creation in lockdown, and handles write/truncate requests by denying or purging cached status.
- `veriexec_removechk` and `veriexec_renamechk` enforce monitored file deletion/rename policy and adjust stored filenames/entries.
- `veriexec_raw_cb` handles raw device writes: in lower modes it purges cached fingerprints for the mounted device; in IPS/lockdown it denies.
- Dump/convert functions serialize entries into proplib dictionaries for userland.

## Concurrency And Invariants

- Global operations take `veriexec_op_lock`; per-entry status/data uses `vfe->lock`.
- Verification may upgrade to writer when evaluation is needed, then downgrade to reader after status is established.
- Table deletion and file deletion use writer mode to coordinate with verification.
- Fileassoc cleanup calls `veriexec_file_free`.
- Mount-specific destructor frees sysctl nodes and table metadata.

## Risks And Edge Cases

- Raw disk write handling documents a race where fingerprints can be cached again while raw writes are possible.
- `VERIEXEC_RW_UPGRADE` busy-loops until upgrade succeeds.
- `veriexec_file_verify` returns with `vfe->lock` held on successful found entries; callers must release it.
- Filename retention is optional; dump skips entries without stored filenames.
- The active hash algorithm list depends on compile-time `VERIFIED_EXEC_FP_SHA*` options.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kern_veriexec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kgdb_stub.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/kgdb_stub.c

## Scope

- Source file read completely: `sources/os/bsd/netbsd-src/sys/kern/kgdb_stub.c`.
- Subset scope: `Docs/research_subset_a.md`.
- This file implements the machine-independent KGDB remote protocol stub for kernel debugging over a device such as a serial line.

## Purpose And Main Interfaces

- Attachment: `kgdb_attach`.
- Trap handling and command loop: `kgdb_trap`.
- Miscellaneous: `kgdb_disconnected`, weak `kgdb_entry_notice`, and `kgdb_voidop`.

## Key State

- `kgdb_dev`, `kgdb_rate`, `kgdb_active`, `kgdb_debug_init`, and `kgdb_debug_panic` configure global KGDB behavior.
- `kgdb_getc`, `kgdb_putc`, and `kgdb_ioarg` are installed by a device driver through `kgdb_attach`.
- `kgdb_recover` points to a recovery label while the KGDB command loop is active.
- `buffer[KGDB_BUFLEN]` is the packet buffer.
- `gdb_regs[KGDB_NUMREGS]` caches register state in GDB wire format.

## Control Flow

- `kgdb_attach` installs character I/O callbacks and callback argument.
- `kgdb_waitc` spins until the input callback returns a character.
- `kgdb_send` emits `$payload#checksum` packets and retries until it receives an acknowledgement other than bad-packet.
- `kgdb_recv` waits for a start marker, accumulates payload and checksum, validates packet length/checksum, acknowledges good/bad packets, and strips optional sequence prefixes.
- `kgdb_trap` is entered from trap handling:
  - ignores traps if KGDB is not configured.
  - clears single-step state.
  - calls optional `db_trap_callback`.
  - recovers unexpected traps during KGDB memory access with `longjmp`.
  - handles first breakpoint entry by advancing PC and marking KGDB active.
  - sends signal packets on later traps.
  - converts MD registers into `gdb_regs`.
  - loops processing remote commands until continue/step/detach/kill.
- Supported commands include signal query, register read/write, memory read/write, detach/kill, continue, and single-step.
- Memory access commands check `kgdb_acc` before using `db_read_bytes` or `db_write_bytes`.

## Helper Functions

- `kgdb_copy` is a local byte copy routine so `bcopy` can be debugged.
- `digit2i`, `i2digit`, `mem2hex`, `hex2mem`, and `hex2i` implement remote protocol conversions.
- `kgdb_disconnected` currently always returns `1`.

## Concurrency And Invariants

- The command loop assumes a stopped-kernel debugging context.
- Packet I/O is synchronous and blocking.
- `kgdb_recover` is only non-null while inside the command loop.
- MD hooks provide breakpoint PC fixup, register conversion, single-step control, signal mapping, and memory-access validation.

## Risks And Edge Cases

- Packet receive rejects overlong packets and malformed hex.
- Register writes require the whole converted packet to terminate exactly.
- Memory reads use the upper half of `buffer` as a temporary raw byte area before hex encoding.
- Detach and kill both clear `kgdb_active`, clear single-step, send `OK`, and leave the loop.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/kgdb_stub.c -->