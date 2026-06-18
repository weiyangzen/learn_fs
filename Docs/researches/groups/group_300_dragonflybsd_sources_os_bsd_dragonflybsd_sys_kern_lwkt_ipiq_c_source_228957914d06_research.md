# Group Research: group_300_dragonflybsd_sources_os_bsd_dragonflybsd_sys_kern_lwkt_ipiq_c_source_228957914d06

Scope: subset A from `Docs/research_subset_a.md`, covering the listed DragonFlyBSD `sys/kern` files. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/lwkt_ipiq.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/lwkt_ipiq.c

## Scope

This file implements DragonFlyBSD's machine-independent LWKT IPI queue layer. It queues cross-CPU function calls, drains incoming IPI FIFOs, supports passive non-urgent IPIs, synchronizes CPUs through IPI-driven barriers, and exposes debug/statistics sysctls including latency probes.

## Public And Internal APIs Covered

- IPI send APIs: `lwkt_send_ipiq3()`, `lwkt_send_ipiq3_passive()`, `lwkt_send_ipiq3_bycpu()`, `lwkt_send_ipiq3_mask()`.
- Completion wait: `lwkt_wait_ipiq()`.
- IPI processing: `lwkt_process_ipiq()`, `lwkt_process_ipiq_frame()`, internal `lwkt_process_ipiq_nested()`, `lwkt_process_ipiq_core()`.
- Synchronization helpers: `lwkt_synchronize_ipiqs()`, `lwkt_cpusync_simple()`, `lwkt_cpusync_interlock()`, `lwkt_cpusync_deinterlock()`, `lwkt_cpusync_quick()`.
- Remote synchronization callbacks: `lwkt_cpusync_remote1()`, `lwkt_cpusync_remote2()`.
- Debug/sysctl support: aggregate `ipiq_*` statistics, optional panic-debug counters, and `debug.ipiq.latency_test` plus per-CPU latency logs.

## Control Flow And Behavior

- Each CPU owns a sender-to-target IPI FIFO for every possible target CPU. `lwkt_send_ipiq3()` appends a function/argument tuple to the sender's FIFO for the target CPU and sets the sender bit in the target's `gd_ipimask`.
- Local sends short-circuit by invoking the callback directly.
- Normal sends enter a critical section, raise `gd_intr_nesting_level`, and use store/load fences around FIFO publication and consumption.
- If a sender FIFO is too full, the sender enables physical interrupts and processes inbound IPIQs while waiting for the target to drain. This avoids APIC and cross-FIFO deadlocks when CPUs are mutually blocked sending IPIs.
- Nested senders use a higher FIFO threshold and a drain target so callbacks can queue more IPIs without exhausting the ring. `lwkt_process_ipiq_nested()` only processes queues whose senders requested draining.
- The actual hardware IPI is coalesced through `target->gd_npoll`; if another IPI is already pending or being processed, the sender avoids another hardware interrupt and increments `ipiq_avoided`.
- Passive sends enqueue without sending a hardware IPI until the queue reaches one-quarter full; these are intended for non-critical work such as deferred frees.
- `lwkt_wait_ipiq()` waits for a target to execute through a sequence number by repeatedly processing local IPIs and warning/panicking if progress stalls.
- `lwkt_process_ipiq()` and `_frame()` walk `gd_ipimask`, process each source CPU's FIFO for the current CPU, clear/re-set mask bits based on remaining work, then process the local `gd_cpusyncq`.
- `lwkt_process_ipiq_core()` snapshots `ip_windex`, uses a load fence, executes callbacks through that stable bound, advances `ip_rindex`, and updates `ip_xindex` only after the callback returns.
- CPU sync interlock sends stage-1 callbacks to target CPUs; remote CPUs acknowledge and requeue themselves on `gd_cpusyncq` until the master clears `cs_mack`, then execute the sync function and acknowledge stage 2.
- `lwkt_cpusync_quick()` skips the quiescent spin stage and only waits for remote execution acknowledgements.

## State And Data Structures

- Per-CPU `ipiq_stats_percpu` tracks sends, FIFO-full waits, avoided hardware IPIs, passive sends, and CPU sync counts.
- Per-CPU globaldata fields used here include `gd_ipiq[]`, `gd_ipimask`, `gd_npoll`, `gd_processing_ipiq`, `gd_intr_nesting_level`, `gd_cpusyncq`, `gd_other_cpus`, and thread `td_cscount`.
- FIFO state is tracked by `ip_windex`, `ip_rindex`, `ip_xindex`, `ip_drain`, and `ip_info[]` entries.
- CPU sync state uses `lwkt_cpusync` fields `cs_mask`, `cs_mack`, `cs_func`, and `cs_data`.

## Dependencies

- Depends on SMP CPU routing (`cpu_send_ipiq()`, `globaldata_find()`, cpumask operations), critical sections, atomic cpumask operations, CPU fences, TSC timing, and `tsleep`/`wakeup`.
- Used by LWKT scheduling, thread migration, message ports, and other cross-CPU kernel subsystems needing callback execution on a target CPU.

## Risks And Invariants

- FIFO index publication requires strict memory ordering: callback data must be visible before `ip_windex`, and callback completion must precede `ip_xindex`.
- The send path intentionally enables interrupts while waiting for FIFO space; doing otherwise can deadlock the IPI subsystem.
- `gd_processing_ipiq` prevents redundant hardware IPIs and informs nested drain behavior.
- CPU sync masters must avoid recursively reflagging cpusync work while `td_cscount` is non-zero, or synchronization can livelock.
- Callback functions run in hard/critical IPI context and must respect nesting, blocking, and reentrancy constraints.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/lwkt_ipiq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/lwkt_msgport.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/lwkt_msgport.c

## Scope

This file implements the LWKT message-port abstraction: asynchronous and synchronous message submission, replies, forwarding, abort handling, and multiple backend implementations for thread-owned, spinlocked, serializer-protected, reply-only, put-only, and panic ports.

## Public And Internal APIs Covered

- Message lifecycle: `lwkt_sendmsg()`, `lwkt_sendmsg_oncpu()`, `lwkt_sendmsg_prepare()`, `lwkt_sendmsg_start()`, `lwkt_sendmsg_start_oncpu()`, `lwkt_domsg()`, `lwkt_forwardmsg()`, `lwkt_abortmsg()`.
- Port initialization: `lwkt_initport_thread()`, `lwkt_initport_spin()`, `lwkt_initport_serialize()`, `lwkt_initport_replyonly_null()`, `lwkt_initport_replyonly()`, `lwkt_initport_putonly()`, `lwkt_initport_panic()`.
- Queue helpers: `_lwkt_pushmsg()`, `_lwkt_pullmsg()`, `_lwkt_pollmsg()`, `_lwkt_enqueue_reply()`.
- Backend vectors for thread, spin, serializer, null, and panic ports.

## Control Flow And Behavior

- `lwkt_sendmsg()` clears reply/sync/done flags and invokes the target port put operation. If the target completes synchronously instead of returning `EASYNC`, it immediately queues a reply through `lwkt_replymsg()`.
- `lwkt_domsg()` marks `MSGF_SYNC`, submits the message, and either waits for an asynchronous reply or marks the message done when the target completed inline.
- `lwkt_forwardmsg()` forwards a not-queued, not-done, not-reply message to another target without rewriting send flags.
- `lwkt_abortmsg()` runs a caller-supplied abort callback only when `MSGF_ABORTABLE` is still set and the message has not already completed or replied.
- Message ports maintain normal and priority queues. `_lwkt_pollmsg()` always returns priority work first.
- `_lwkt_pushmsg()` sets `MSGF_QUEUED`, inserts into the selected queue, and invokes receipt callbacks once by clearing `MSGF_RECEIPT`.
- Thread ports assume one owning thread. Cross-CPU puts/replies are delivered by IPI to the owning thread's current CPU, chasing migrations until `td_gd == mycpu`.
- Thread-port synchronous replies can avoid queueing by setting `MSGF_DONE | MSGF_REPLY` and scheduling the waiter if needed.
- Spin ports protect queues and wait flags with `mpu_spin`, support multiple waiters, and wake either the port or message depending on synchronous/asynchronous mode.
- `lwkt_spin_putport_oncpu()` asserts that fixed-CPU ports are used only from their assigned CPU and wakes with `wakeup_mycpu()`.
- Serializer ports require the caller to hold `mpu_serialize`; sleeps use `zsleep()` so the serializer is released/reacquired correctly around blocking.
- Panic ports intentionally trap illegal operations for restricted port types. The null reply port only marks messages done/replied.

## State And Data Structures

- Message flags drive protocol state: `MSGF_DONE`, `MSGF_QUEUED`, `MSGF_REPLY`, `MSGF_SYNC`, `MSGF_PRIORITY`, `MSGF_RECEIPT`, `MSGF_ABORTABLE`, `MSGF_DROPABLE`, `MSGF_WAITING`, and debug-only `MSGF_INTRANSIT`.
- `lwkt_port` stores function vectors, queue heads, wait flags, optional owner thread, optional spinlock, optional serializer, and optional fixed CPU.
- `ms_reply_port`, `ms_target_port`, `ms_error`, receipt callback, abort callback, and queue links are updated by the backend implementations.

## Dependencies

- Depends on LWKT thread scheduling, IPI delivery, spinlocks, serializers, sleep/wakeup primitives, and message/port definitions from `sys/msgport2.h`.
- Used by kernel services that need structured request/reply handoff across threads or CPUs.

## Risks And Invariants

- `lwkt_sendmsg()` and `lwkt_domsg()` must not be used to forward already active messages because they rewrite `ms_flags`.
- Thread-port queue access is only safe on the owning thread/CPU or through IPI redirection.
- Spin-port wait flags can produce extra wakeups; the waking side clears `MSGPORTF_WAITING`.
- `MSGF_DROPABLE` messages cannot be waited on.
- Serializer ports rely on external serialization; using them without holding the serializer violates their locking contract.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/lwkt_msgport.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/lwkt_serialize.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/lwkt_serialize.c

## Scope

This file implements DragonFlyBSD's low-level LWKT serializer: a non-recursive exclusive interlock that may be held across blocking operations and has integrated interrupt-handler enable/disable support for driver code.

## Public And Internal APIs Covered

- Lifecycle and locking: `lwkt_serialize_init()`, `lwkt_serialize_enter()`, `lwkt_serialize_try()`, `lwkt_serialize_exit()`, `lwkt_serialize_adaptive_enter()`.
- Interrupt handler gating: `lwkt_serialize_handler_disable()`, `lwkt_serialize_handler_enable()`, `lwkt_serialize_handler_call()`, `lwkt_serialize_handler_try()`.
- Sleep/wakeup callbacks: internal `lwkt_serialize_sleep()` and `lwkt_serialize_wakeup()`.

## Control Flow And Behavior

- `lwkt_serialize_init()` initializes the atomic interrupt-aware interlock and sets `last_td` to a sentinel.
- `lwkt_serialize_enter()` asserts non-ownership, enters through `atomic_intr_cond_enter()`, and records `curthread`.
- `lwkt_serialize_try()` attempts nonblocking acquisition through `atomic_intr_cond_try()` and returns non-zero on success.
- `lwkt_serialize_exit()` asserts ownership, clears `last_td` to a sentinel, and releases via `atomic_intr_cond_exit()` with wakeup callback.
- Handler disable/enable use the interrupt-handler bit in the same interlock word.
- `lwkt_serialize_handler_call()` checks that the handler is enabled, acquires the serializer, rechecks enablement, invokes the handler if still enabled, then releases.
- `lwkt_serialize_handler_try()` provides the same handler wrapper without sleeping.
- `lwkt_serialize_sleep()` interlocks a sleep against missed wakeups by checking the atomic condition after `tsleep_interlock()`.
- `lwkt_serialize_adaptive_enter()` first tries immediate acquisition, spins for `SLZ_ADAPTIVE_SPINMAX`, then increments sleeper state and sleeps, restarting after wake.

## State And Data Structures

- `lwkt_serialize` contains an `atomic_intr` interlock and `last_td` debug/ownership tracking field.
- KTR events trace enter, exit, sleep, wakeup, try, and adaptive-spin stages.

## Dependencies

- Depends on machine atomic interrupt-condition primitives, `tsleep`, `wakeup`, critical interlocks, and assertion macros from `sys/serialize.h`.
- Used by drivers and message-port serializer backends where interrupt handlers and thread context must be mutually excluded.

## Risks And Invariants

- Serializers are explicitly non-recursive; callers must not enter while already serialized.
- Handler wrappers must recheck handler enablement after acquiring the serializer to close disable races.
- Sleep path must avoid lost wakeups between contention detection and actual sleep.
- This is not a mutex; it is a lower-level primitive with different ownership and interrupt semantics.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/lwkt_serialize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/lwkt_thread.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/lwkt_thread.c

## Scope

This file implements the DragonFlyBSD LWKT per-CPU kernel thread scheduler: run queue management, thread allocation/caching, initialization, context switching, token release/reacquisition, preemption, yield paths, remote scheduling, CPU migration, priority management, and thread exit cleanup.

## Public And Internal APIs Covered

- Scheduler queues: `lwkt_schedule_self()`, `lwkt_deschedule_self()`, `lwkt_schedule()`, `lwkt_schedule_noresched()`, `lwkt_deschedule()`.
- Thread setup/lifecycle: `lwkt_gdinit()`, `lwkt_alloc_thread()`, `lwkt_init_thread()`, `lwkt_set_comm()`, `lwkt_hold()`, `lwkt_rele()`, `lwkt_free_thread()`, `lwkt_create()`, `lwkt_exit()`, `lwkt_remove_tdallq()`.
- Switching/preemption: `lwkt_switch()`, `lwkt_switch_return()`, `lwkt_preempt()`, `splz_check()`, `lwkt_maybe_splz()`.
- Yield and user-scheduler interaction: `lwkt_yield()`, `lwkt_yield_quick()`, `lwkt_user_yield()`, `lwkt_passive_release()`.
- Priority and clock handling: `lwkt_setpri()`, `lwkt_setpri_initial()`, `lwkt_setpri_self()`, `lwkt_schedulerclock()`.
- Migration: `lwkt_giveaway()`, `lwkt_acquire()`, `lwkt_setcpu_self()`, `lwkt_migratecpu()`, internal `lwkt_setcpu_remote()`.
- Panic/debug support: `crit_exit_wrapper()`, `crit_panic()`, `lwkt_smp_stopped()`.

## Control Flow And Behavior

- Each CPU owns a local LWKT run queue and all-thread queue. Remote CPUs schedule/deschedule via IPI rather than directly manipulating another live CPU's queues.
- `_lwkt_enqueue()` orders runnable threads by LWKT priority and user priority, scans from both head and tail to avoid degeneracy with large runnable sets, and requests reschedule if the inserted thread becomes queue head.
- `_lwkt_dequeue()` removes a runnable thread and clears `RQF_RUNNING` if the queue becomes empty.
- Thread structures and kernel stacks are cached through an objcache-backed `thread_cache`; `gd_freetd` preserves one exiting thread until it is safe to recycle.
- `lwkt_alloc_thread()` allocates or reuses a thread and stack, selects a CPU if none is specified, and calls `lwkt_init_thread()`.
- `lwkt_init_thread()` zeros and initializes core fields, installs a thread or spin message port, initializes pmap state, and inserts the thread into the target CPU's all-thread queue locally or by IPI.
- `lwkt_switch()` is the main scheduling loop. It releases current-thread user designation when needed, releases all held tokens before switching, avoids switching from hard interrupt/IPI context except panic/trap fallback, and chooses the next runnable thread or idle thread.
- Token contention is central to scheduling: candidate threads must reacquire their held tokens. Persistent contention eventually uses sorted token reacquisition and may skip to another runnable thread or the idle thread.
- Preempted threads are resumed before normal run-queue selection. Preemption chains use `td_preempted`, `TDF_PREEMPT_LOCK`, and `TDF_PREEMPT_DONE`.
- `lwkt_switch_return()` clears the old thread's running state, completes pending migration by IPI to the destination CPU, and signals exiting threads through `TDF_MP_EXITSIG`.
- `lwkt_preempt()` allows high-priority interrupt-support threads to directly run over the current thread only when critical-section depth, nesting, CPU ownership, token state, and preemption flags permit it.
- Yield helpers run pending soft interrupt work via `splz()` where allowed and switch only when reschedule conditions justify it.
- Remote scheduling uses `lwkt_schedule_remote()`; when invoked from an interrupt return frame it temporarily drops the IPI critical section so preemption can occur.
- Migration uses a pull/hand-off model. Current-thread migration deschedules itself, removes itself from the old CPU list, switches away, then finishes on the target CPU. Non-current migration waits for the old CPU to stop running/preempting the thread before changing `td_gd`.
- `lwkt_exit()` completes blocking cleanup first, waits for references to drain, removes the thread from queues, caches/freezes final resources, and exits via machine code.

## State And Data Structures

- Per-CPU state: `gd_tdrunq`, `gd_tdrunqcount`, `gd_tdallq`, `gd_idlethread`, `gd_curthread`, `gd_freetd`, `gd_reqflags`, `gd_spinlocks`, and indefinite wait diagnostics.
- Thread state: flags such as `TDF_RUNQ`, `TDF_RUNNING`, `TDF_MIGRATING`, `TDF_PREEMPT_LOCK`, `TDF_PREEMPT_DONE`, `TDF_EXITING`, `TDF_TSLEEPQ`, `TDF_ALLOCATED_THREAD`, `TDF_ALLOCATED_STACK`; priorities `td_pri`/`td_upri`; token stack; message port; CPU pointer; preemption links; migration target.
- Tunables/sysctls control spin-port debugging, scheduler debug, token contention spin loops, preemption enablement, and thread cache sizing.

## Dependencies

- Integrates with LWKT tokens, message ports, IPIs, critical sections, spinlocks, `splz`, user scheduler callbacks, pmap thread initialization, disk scheduler hooks, kernel stack VM allocation, objcache, and machine context switch handlers.
- Used by virtually all kernel execution contexts above early boot and interrupt trap glue.

## Risks And Invariants

- Queue operations must occur in the correct CPU's critical section; live foreign queue manipulation is routed through IPIs.
- Threads must not switch while holding spinlocks or while in hard interrupt/IPI context, except controlled panic/trap fallback.
- Tokens are released before a blocking switch and reacquired before resuming a thread; interrupts/IPIs must not run in the unsafe gap.
- Migration requires the thread to be descheduled and not running or preempt-locked before changing CPU ownership.
- Preemption deliberately rejects token-holding targets and heavily nested/current critical contexts to avoid corrupting scheduler invariants.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/lwkt_thread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/lwkt_token.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/lwkt_token.c

## Scope

This file implements LWKT soft token locks. Tokens serialize running threads, but are released automatically when a thread blocks and reacquired by the scheduler when the thread resumes. The file also defines global subsystem tokens and a pool-token hash for type-stable per-object serialization.

## Public And Internal APIs Covered

- Global tokens: `mp_token`, `pmap_token`, `dev_token`, `vm_token`, `vmspace_token`, `kvm_token`, `sigio_token`, `tty_token`, `vnode_token`, `vga_token`, `kbd_token`.
- Boot and pool support: `cpu_get_initial_mplock()`, `lwkt_token_pool_init()`, `lwkt_token_pool_lookup()`, `lwkt_getpooltoken()`, `lwkt_relpooltoken()`.
- Token lifecycle and acquisition: `lwkt_token_init()`, `lwkt_token_uninit()`, `lwkt_gettoken()`, `lwkt_gettoken_shared()`, `lwkt_trytoken()`, `lwkt_reltoken()`, `lwkt_cnttoken()`, `lwkt_token_swap()`.
- Scheduler hooks: `lwkt_getalltokens()`, `lwkt_relalltokens()`, internal `_lwkt_getalltokens_sorted()`.
- Core internals: `_lwkt_token_pool_lookup()`, `_lwkt_tokref_init()`, `_lwkt_trytokref()`, `_lwkt_trytokref_spin()`, `_lwkt_reltokref()`.

## Control Flow And Behavior

- Tokens are represented by a shared count word plus an optional exclusive holder tokref. Shared holders increment by `TOK_INCR`; exclusive holders set `TOK_EXCLUSIVE`; contended blocking exclusive attempts can set `TOK_EXCLREQ`.
- `lwkt_gettoken()` pushes a tokref onto the current thread's token stack, tries to acquire exclusive ownership, and if it fails yields through `lwkt_switch()` with `td_toks_have` indicating the scheduler-owned reacquisition boundary.
- `lwkt_gettoken_shared()` follows the same model but acquires shared ownership. Debug builds warn about shared pool-token acquisition because unrelated objects can hash to the same token.
- Recursive exclusive acquisition by the same thread is allowed: the deeper reference owns `t_ref`; later recursive acquisitions are treated count-wise like shared refs for simpler release.
- `lwkt_trytoken()` sets up a temporary exclusive tokref, attempts nonblocking acquisition without setting `TOK_EXCLREQ`, and rolls back `td_toks_stop` on failure.
- `lwkt_reltoken()` enforces strict reverse-order release from the thread token stack and panics with diagnostic output if the token does not match the top ref.
- `_lwkt_trytokref_spin()` uses exponential backoff for exclusive contention and TSC windowing for shared contention before giving up to the scheduler.
- `lwkt_getalltokens()` is called by the scheduler when resuming a thread. It reacquires all tokrefs in forward order, or address-sorted order after enough contention, releasing partial acquisitions on failure.
- `_lwkt_getalltokens_sorted()` sorts tokrefs by token address while preserving recursive acquisition order for equal tokens, reducing deadlock risk during decontention.
- `lwkt_relalltokens()` releases all current thread tokens in reverse order when a thread switches away.
- Pool tokens hash arbitrary pointers into a 16,384-entry cache-aligned token pool using two prime-modulo hash components.
- `lwkt_token_swap()` swaps the top two tokrefs so callers can correct release order, while preserving `t_ref` identity for exclusive holders.

## State And Data Structures

- `struct lwkt_token` fields used include `t_count`, `t_ref`, `t_collisions`, and `t_desc`.
- `struct lwkt_tokref` records `tr_tok`, requested/held count bits in `tr_count`, and owning thread.
- Thread token stack spans `td_toks_base` through `td_toks_stop`, with `td_toks_have` used during scheduler reacquisition.
- Contention tuning is exposed through `lwkt.token_backoff_max`, `lwkt.token_window_shift`, per-token collision counters, and `tokens_debug_output`.

## Dependencies

- Depends on atomic compare/set and fetch-add operations, TSC reads, CPU pause/fence operations, LWKT scheduler switching, current-thread token stack state, and optional DDB/debug tracing.
- Closely coupled to `lwkt_thread.c`, which releases and reacquires tokens around context switches.

## Risks And Invariants

- Tokens must be released in exact reverse acquisition order unless `lwkt_token_swap()` is used deliberately.
- Blocking token acquisition is forbidden from hard interrupt/nesting contexts unless panic handling owns the CPU.
- Shared-to-exclusive upgrade while already holding only shared refs can livelock; debug builds assert this pattern.
- `t_ref` must be cleared before the exclusive bit is released and must continue to point at the deepest exclusive recursive ref.
- Scheduler token reacquisition is part of the deadlock-avoidance design; bypassing it would break the "released while blocked" token model.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/lwkt_token.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/makesyscalls.sh -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/makesyscalls.sh

## Scope

This shell script generates DragonFlyBSD syscall metadata and C headers/tables from a `syscalls.master`-style input file, optionally parameterized by a configuration file.

## Public And Internal APIs Covered

- Inputs: required syscall master file and optional config file sourced by the script.
- Generated outputs by default: `syscalls.c`, `../sys/sysproto.h`, `../sys/sysunion.h`, `../sys/syscall.h`, `../sys/syscall.mk`, and `init_sysent.c`.
- Temporary files: syscall declarations, compat declarations, switch entries, include fragments, argument structs, and syscall union fragments.
- Configurable symbols: syscall prefix, switch table name, names array name, header guard, and output paths.

## Control Flow And Behavior

- The script exits on error and registers a trap to remove temporary files.
- It preprocesses the master file with `sed`: removes dollar signs, joins backslash-continuation lines, and spaces punctuation tokens for easier AWK parsing.
- The AWK program writes boilerplate "DO NOT EDIT" headers for all generated files.
- Preprocessor include/conditional lines are copied into the appropriate generated fragments while preserving syscall number state across `#if`/`#else`.
- The parser validates monotonically increasing syscall numbers and emits an error if the current line number does not match the expected syscall index.
- `parseline()` handles syscall signatures, optional function aliases, argument aliases, and return types. It extracts argument type/name pairs and computes argument struct size macros.
- For `STD`, `NODEF`, `NOARGS`, `NOPROTO`, and `NOIMPL` entries, it emits argument structs where needed, syscall prototypes, sysent table rows, syscall name strings, syscall number defines, and makefile object names.
- `NOIMPL` maps the sysent handler to `sys_nosys` while preserving the exposed name.
- `OBSOL` emits obsolete comments and `sys_nosys` table rows.
- `UNIMPL` emits unnamed `#number` syscall names and `sys_nosys` rows.
- At END, it emits `AS()` sizing macro, optional compat macro, closing guards/braces, and `SYS_MAXSYSCALL`, then concatenates fragments into final output files.

## State And Data Structures

- AWK variables track `syscall`, saved syscall index across preprocessor branches, parsed argument arrays, aliases, return type size, generated file paths, and duplicate `nosys`/`lkmnosys` emission state.
- Generated `struct sysent` entries include argument size, return size, and function pointer cast.
- Generated `union sysunion` contains per-syscall argument structs for messaging.

## Dependencies

- Requires POSIX shell, `sed`, `awk`, and DragonFlyBSD syscall master syntax.
- The generated files are consumed by kernel syscall dispatch, syscall prototypes, syscall number headers, syscall name tables, and syscall object build lists.

## Risks And Invariants

- The master file's syscall numbers must remain contiguous with parser state, including across conditional sections.
- Function signatures must match the parser's expected brace/semicolon/parenthesis token layout.
- Temporary file cleanup depends on the trap and unique `$$` suffixes.
- Generated files are authoritative build artifacts; manual edits are overwritten by rerunning the script.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/makesyscalls.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/md4c.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/md4c.c

## Scope

This file is the in-kernel RSA Data Security MD4 message-digest implementation, adapted for DragonFlyBSD kernel headers and memory helpers.

## Public And Internal APIs Covered

- Public digest functions: `MD4Init()`, `MD4Update()`, `MD4Final()`.
- Internal helpers: `__kern__MD4Pad()`, `__kern__MD4Transform()`, `Encode()`, `Decode()`.
- MD4 round macros: `F`, `G`, `H`, `ROTATE_LEFT`, `FF`, `GG`, `HH`.

## Control Flow And Behavior

- `MD4Init()` zeroes the bit count and initializes the four MD4 state words to standard constants.
- `MD4Update()` updates the bit count, buffers partial blocks, transforms complete 64-byte blocks, and stores leftover bytes in the context buffer.
- `__kern__MD4Pad()` saves the original length, pads with `0x80` plus zero bytes to 56 mod 64, then appends the 64-bit little-endian length.
- `MD4Final()` pads, encodes the final 128-bit digest, and zeroes the context.
- `__kern__MD4Transform()` decodes one 64-byte block into sixteen 32-bit words, runs MD4's three rounds, adds the result back into the state, and zeroes the local block array.
- `Encode()` and `Decode()` explicitly convert between little-endian byte arrays and 32-bit words.

## State And Data Structures

- `MD4_CTX` stores `count[2]`, `state[4]`, and a 64-byte buffer.
- Static `PADDING[64]` supplies the MD-style padding block.

## Dependencies

- Includes `sys/md4.h` for context definition and uses kernel `bcopy()`/`bzero()` helpers.
- Suitable for kernel consumers needing MD4-compatible digest calculation, not for modern cryptographic security.

## Risks And Invariants

- Length accounting is 64-bit split across two 32-bit words and must be updated before buffering decisions.
- Encoding assumes MD4's required little-endian byte order independent of host representation.
- MD4 is cryptographically broken; this implementation should only be used for compatibility protocols or non-security checksums.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/md4c.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/md5c.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/md5c.c

## Scope

This file is the DragonFlyBSD in-kernel MD5 implementation, derived from RSA Data Security code and intended to stay in sync with the userland `libmd` implementation.

## Public And Internal APIs Covered

- Public digest functions: `MD5Init()`, `MD5Update()`, `MD5Final()`.
- Internal helpers: `__kern__MD5Pad()`, `__kern__MD5Transform()`, and endian-dependent `Encode()`/`Decode()` helpers.
- MD5 round macros: `F`, `G`, `H`, `I`, `ROTATE_LEFT`, `FF`, `GG`, `HH`, `II`.

## Control Flow And Behavior

- `MD5Init()` initializes the bit counters and standard MD5 state words, returning `1`.
- `MD5Update()` updates the 64-bit bit count in `Nl`/`Nh`, fills any partial 64-byte block, transforms complete blocks, and buffers the remainder.
- On little-endian machines, `Encode` and `Decode` are aliases for `memcpy`; otherwise explicit byte-order conversion is compiled in.
- `__kern__MD5Pad()` saves the bit length, pads to 56 mod 64, and appends the saved length.
- `MD5Final()` pads, encodes the four-word state into the 16-byte digest, and clears the context.
- `__kern__MD5Transform()` runs the standard 64 MD5 operations across four rounds and adds the transformed state back into the context.

## State And Data Structures

- `MD5_CTX` contains state words `A` through `D`, counters `Nl`/`Nh`, and a data buffer.
- Static `PADDING[64]` contains the `0x80` prefix and zero fill.

## Dependencies

- Builds both in-kernel and outside the kernel: kernel builds use `sys/systm.h`, non-kernel builds use `<string.h>`.
- Includes endian headers and `sys/md5.h`.

## Risks And Invariants

- MD5 byte order is little-endian; non-little-endian platforms depend on the explicit conversion helpers.
- The context is zeroed after finalization, so callers must not reuse it without `MD5Init()`.
- MD5 is cryptographically broken and should be treated as compatibility/checksum code rather than a secure digest.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/md5c.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_alist.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_alist.c

## Scope

This file implements `alist`, a general bitmap allocator based on a radix tree with hinting. It supports unlimited-size requests in the sense that allocations can exceed one leaf, but allocations are rounded/structured around power-of-two size and alignment constraints. The code can also be compiled stand-alone for debugging.

## Public And Internal APIs Covered

- Public allocator API: `alist_create()`, `alist_init()`, `alist_destroy()`, `alist_alloc()`, `alist_free()`, `alist_free_info()`.
- Debug API when enabled: `alist_print()` and stand-alone `main()`.
- Internal allocation/free helpers: `alst_leaf_alloc()`, `alst_meta_alloc()`, `alst_leaf_free()`, `alst_meta_free()`, `alst_radix_init()`, and debug `alst_radix_print()`.

## Control Flow And Behavior

- `alist_create()` computes the root radix and skip values needed to cover the requested block count, allocates the `struct alist` and linear radix-node array, initializes all nodes as allocated, and returns the allocator.
- `alist_init()` performs the same initialization using caller-supplied storage and asserts enough records are provided.
- `alist_alloc()` accepts any nonzero count. Non-power-of-two requests are rounded up to a power of two, allocated recursively, then the unused tail is freed.
- Power-of-two allocations search from `start` and require size-aligned results. Successful allocation decreases `bl_free`.
- `alist_free()` frees arbitrary ranges, not just power-of-two ranges, and increases `bl_free`.
- `alist_free_info()` walks toward the trailing free area and returns total free blocks plus an approximate start/count for a trailing contiguous range.
- Leaf nodes use a 32-bit bitmap where `1` means free and `0` means allocated. Single-block allocation uses a binary-search-style bit scan; larger leaf allocations scan aligned masks.
- Meta nodes use two bits per child: `00` all allocated, `01` partially free, `10` reserved/unknown, `11` all free.
- Meta allocation can allocate directly at a meta level when the requested size is at least the child radix, otherwise it descends into children whose `bm_bighint` can satisfy the request.
- Hints are conservative in the safe direction: they may be too high but are not supposed to be too low. Allocation failures reduce hints to avoid repeated futile descent.
- Freeing whole child ranges marks the child all-free at the parent. Partial frees initialize stale child state if needed, recurse, and then mark the parent entry all-free or partial based on the child's bitmap.
- `alst_radix_init()` computes memory requirements and initializes the compact linear tree without terminator nodes, relying instead on block-limit checks during allocation/free.

## State And Data Structures

- `struct alist` tracks `bl_blocks`, `bl_radix`, `bl_skip`, `bl_rootblks`, `bl_root`, and `bl_free`.
- `almeta_t` stores `bm_bitmap` and `bm_bighint`.
- Leaf radix is `ALIST_BMAP_RADIX`; meta radix is `ALIST_META_RADIX`.
- Stand-alone mode maps kernel allocation/assert/print primitives to libc equivalents.

## Dependencies

- Kernel builds include VM and malloc headers plus `sys/alist.h`; userland debug builds include standard C headers and local compatibility macros.
- The allocator is suitable for resource maps where allocation units are abstract blocks and all metadata must be preallocated.

## Risks And Invariants

- Allocation results are power-of-two aligned to the allocation size.
- Freeing an already-free leaf bit panics.
- Callers must not free outside `bl_blocks`.
- `bm_bighint` correctness is performance-critical and can affect address-specific allocation success; frees deliberately overstate hints when exact recomputation would be expensive.
- Non-power-of-two allocation works by overallocating and freeing the tail, so the free path must correctly handle arbitrary ranges.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_alist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_autoconf.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_autoconf.c

## Scope

This file implements interrupt-driven autoconfiguration hooks: ordered callbacks that run after cold autoconfiguration when interrupts are available, plus registration and deregistration functions for device code.

## Public And Internal APIs Covered

- Public API: `config_intrhook_establish()`, `config_intrhook_disestablish()`.
- SYSINIT entry: `run_interrupt_driven_config_hooks()` at `SI_SUB_INT_CONFIG_HOOKS`.
- Internal state: hook list, `ran_config_hooks`, and `intr_config_lk`.

## Control Flow And Behavior

- Hooks are stored in an ordered tail queue of `struct intr_config_hook`.
- `run_interrupt_driven_config_hooks()` locks the list, marks a run generation, and repeatedly finds a hook whose `ich_ran` is zero.
- Each selected hook is marked ran, the lock is released, the callback executes, and the lock is reacquired. This lets callbacks disestablish themselves or allow other hook list changes.
- If all remaining hooks have already run but still remain on the list, the runner sleeps on the hook list and prints warnings every ten seconds.
- After thirty seconds, or on repeated runner invocation, it gives up with a warning that interrupt routing is likely broken.
- On real kernels, the first run waits up to five seconds after start to give USB/U4B configuration time before root mount probing.
- `config_intrhook_establish()` inserts a hook by `ich_order`, rejects duplicate registration, clears `ich_ran`, and if hooks already ran, invokes the runner immediately for late registration.
- `config_intrhook_disestablish()` removes a registered hook, wakes waiters, and panics if the hook was not registered.

## State And Data Structures

- `intr_config_hook_list` is protected by `intr_config_lk`.
- `ich_order` controls registration order; `ich_ran` prevents immediate repeated execution during a pass.
- `ich_desc`, `ich_func`, and `ich_arg` are used for diagnostics and callback invocation.

## Dependencies

- Depends on `lockmgr`, `lksleep`, `tsleep`, `wakeup`, global `ticks`/`hz`, and SYSINIT ordering.
- Used by drivers that need interrupts before completing device configuration.

## Risks And Invariants

- Hooks must disestablish themselves or be removed by their owners; otherwise boot can wait and warn.
- Callback execution occurs without the list lock, so hook storage must remain valid according to the hook owner's lifetime rules.
- Duplicate establish and unestablished disestablish are treated as programmer errors.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_autoconf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_blist.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_blist.c

## Scope

This file implements `blist`, DragonFlyBSD's radix-tree bitmap allocator/deallocator used for block resources such as swap. It wires all metadata at creation time, supports fast allocation/free under fragmentation, supports allocation at or after a target block, filling ranges, resizing, and stand-alone debug mode.

## Public And Internal APIs Covered

- Public allocator API: `blist_create()`, `blist_destroy()`, `blist_alloc()`, `blist_allocat()`, `blist_free()`, `blist_fill()`, `blist_resize()`.
- Debug API when enabled: `blist_print()` and stand-alone `main()`.
- Internal helpers: `blst_leaf_alloc()`, `blst_meta_alloc()`, `blst_leaf_free()`, `blst_meta_free()`, `blst_leaf_fill()`, `blst_meta_fill()`, `blst_copy()`, `blst_radix_init()`, and debug `blst_radix_print()`.

## Control Flow And Behavior

- `blist_create()` computes a root radix large enough to cover the requested block count, computes skip values for the linearized tree layout, allocates the root node array, and initializes all blocks allocated.
- `blist_alloc()` allocates the first range of `count` contiguous free blocks. `blist_allocat()` does the same but only considers ranges at or beyond `blkat`.
- `blist_free()` frees an arbitrary range and panics if consistency checks detect freeing already-free blocks.
- `blist_fill()` marks a range allocated regardless of prior state and returns how many blocks were actually free before the fill.
- `blist_resize()` creates a new allocator, copies free extents from the old tree into the new one, optionally frees newly added space, swaps the pointer, and destroys the old tree.
- Leaf nodes store one bit per block; `1` means free. Single-block allocation uses a fast bit search; multi-block allocation scans contiguous masks.
- Meta nodes store available-block counts in `bmu_avail` and largest-free hints in `bm_bighint`.
- Meta nodes collapse two states: all allocated (`bmu_avail == 0`) and all free (`bmu_avail == radix`). In collapsed states, lower-level node data is considered stale and reinitialized only when descent is required.
- Allocation descends only into children whose hint can satisfy the request and whose range is beyond `blkat`. Failures lower hints to avoid repeated futile searches.
- Freeing an all-allocated meta node initializes child state unless the free covers the whole node, then recursively frees the affected range and raises hints from child hints.
- Filling can short-circuit whole-node allocation and otherwise descends to count and clear free bits.
- `blst_copy()` reconstructs free space in a destination allocator by walking free state in a source tree.

## State And Data Structures

- `struct blist` tracks `bl_blocks`, `bl_radix`, `bl_skip`, `bl_rootblks`, `bl_root`, and `bl_free`.
- `blmeta_t` uses `bm_bighint` and a union for either leaf bitmap (`bmu_bitmap`) or meta available count (`bmu_avail`).
- Terminator nodes are represented by `bm_bighint == (swblk_t)-1` when the linear tree allocation stops before the nominal root radix.
- Kernel builds allocate metadata from `M_SWAP`.

## Dependencies

- Kernel builds depend on `sys/blist.h`, kernel malloc, and panic/assert helpers.
- The allocator is designed for consumers such as swap where allocation/free paths should not allocate additional memory.

## Risks And Invariants

- Allocation larger than a child radix can panic in recursive paths; comments note the allocator historically cannot allocate more than `BLIST_BMAP_RADIX` blocks per call in some cases.
- `bm_bighint` must never be too low; stale high hints are tolerated but cost extra descent.
- Collapsed meta states intentionally invalidate lower tree contents; code must reinitialize before descending.
- Resizing preserves free extents by copying source state into a fresh all-allocated destination.
- Free and fill ranges must remain inside the allocator's represented block count.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/subr_blist.c -->