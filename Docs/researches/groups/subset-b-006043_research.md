# subset-b-006043 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/printk_ringbuffer.c -->
# sources/distributed-fs/ceph-client/kernel/printk/printk_ringbuffer.c

## Purpose
`printk_ringbuffer.c` implements the lockless storage engine behind printk records. It manages two coordinated rings: a descriptor ring containing record metadata, sequence numbers, state, and logical text-block locations, and a text data ring containing ID-prefixed text payload blocks. The design lets writers reserve and commit records from any context while readers detect overwritten, missing, unfinalized, or finalized records without taking writer-side locks.

## Important APIs, types, and functions
The public writer APIs are `prb_reserve()`, `prb_reserve_in_last()`, `prb_commit()`, `prb_final_commit()`, `prb_init()`, and `prb_record_text_space()`. Public reader APIs are `prb_read_valid()`, `prb_read_valid_info()`, `prb_first_seq()`, `prb_first_valid_seq()`, `prb_next_seq()`, and `prb_next_reserve_seq()`. Internally, descriptor lifecycle is handled by `desc_reserve()`, `desc_read()`, `desc_push_tail()`, `desc_make_reusable()`, `desc_make_final()`, and `desc_update_last_finalized()`. Text storage is handled by `data_alloc()`, `data_realloc()`, `data_push_tail()`, `data_make_reusable()`, `get_data()`, `copy_data()`, and helpers for logical-position wrapping.

## Control flow
A writer initializes a `printk_record`, saves local IRQ flags, reserves a descriptor, assigns the next sequence number, finalizes the previous committed record if needed, allocates text storage, fills `r->info` and `r->text_buf`, then commits. `prb_commit()` leaves the newest record reopenable until a newer reservation or explicit finalization, while `prb_final_commit()` makes it immediately readable. `prb_reserve_in_last()` reopens the newest committed descriptor if the caller ID matches and extends or allocates its text block within a caller-supplied maximum.

Readers map sequence numbers to descriptors, validate descriptor ID and state before and after metadata/text copies, and skip lost records. `_prb_read_valid()` catches readers up to the current tail, skips records whose payload was overwritten, and has panic-CPU logic to continue past non-finalized gaps when panic printing must drain finalized data.

## State and persistence behavior
All state is in caller-provided memory: descriptor array, `printk_info` array, text buffer, atomic head/tail IDs, atomic data head/tail logical positions, `last_finalized_seq`, and reserve-failure counter. Records persist only until overwritten by ring reuse. Special logical positions represent empty-line records and failed/lost data. The bootstrap state uses the final descriptor as initial head/tail so the first real record gets sequence 0 while early readers see an empty buffer.

## Dependencies and integration points
The file depends on Linux atomics, interrupt flag management, memory barriers, KUnit visibility exports, printk internals (`panic_on_this_cpu()`, `debug_non_panic_cpus`, `legacy_allow_panic_sync`), and metadata structures from `printk_ringbuffer.h`. It is consumed by the printk core and directly stress-tested by the KUnit ringbuffer test.

## Risks and invariants
The highest-risk area is memory ordering. The implementation documents barrier pairs with `LMM(...)` labels, and regressions can expose stale descriptors, torn metadata/text reads, ABA failures on 32-bit, or unsafe reuse before readers have validated state. Descriptor tail must always point at a finalized or reusable descriptor. Data tail movement must make associated descriptors reusable before storage reuse. `text_len` must be sane relative to allocated text space for readers and extension logic. Reserve/commit windows disable local interrupts to reduce self-deadlock and full-ring stalls.

## Test signals
Strong signals are KUnit concurrent reader/writer stress, wraparound tests, empty and failed data blocks, reopen/extend cases, panic read behavior, sequence gap detection, and lockdep/KCSAN coverage around atomics and barriers. Failures usually appear as bad sequence reads, invalid text payloads, warnings from strict block validation, or reserve failures increasing under heavy contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/printk_ringbuffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/printk_ringbuffer.h -->
# sources/distributed-fs/ceph-client/kernel/printk/printk_ringbuffer.h

## Purpose
`printk_ringbuffer.h` defines the public and internal data contract for the printk ringbuffer. It describes metadata records, descriptor and data rings, descriptor states, bootstrap constants, static-definition macros, and reader/writer helper APIs used by printk and KUnit.

## Important APIs, types, and functions
`struct printk_info` carries sequence number, timestamp, text length, facility, flags, level, caller ID, optional execution context data, and device-printk metadata. `struct printk_record` is the reader/writer buffer descriptor. `struct prb_desc`, `struct prb_data_ring`, `struct prb_desc_ring`, `struct printk_ringbuffer`, and `struct prb_reserved_entry` define storage and reservation state. `enum desc_state` encodes `reserved`, `committed`, `finalized`, `reusable`, plus the pseudo-state `desc_miss`.

The header declares all public `prb_*` APIs and provides `prb_rec_init_wr()`, `prb_rec_init_rd()`, `prb_for_each_record()`, and `prb_for_each_info()`. `DEFINE_PRINTKRB()` and `_DEFINE_PRINTKRB()` allocate and initialize a ready-to-use static ringbuffer.

## Control flow
Writers initialize a `printk_record` with requested text size, reserve through the C implementation, fill returned buffers, and commit or final-commit through the declared APIs. Readers initialize output buffers and use either one-shot reads or iteration macros. Sequence helpers expose the oldest valid sequence, oldest descriptor sequence, next finalized sequence, and next reserve sequence.

## State and persistence behavior
The header fixes the in-memory format for ringbuffer persistence across runtime operations. It encodes descriptor ID and state in one atomic word using high bits for state and low bits for ID. It defines `FAILED_LPOS` and `EMPTY_LINE_LPOS` as impossible aligned logical positions for records without data blocks. Bootstrap comments explain why the initial tail/head descriptor is the last descriptor and why sequence values are seeded to make record 0 possible while initial readers still see an empty ring.

## Dependencies and integration points
The definitions depend on Linux atomic, bit, type, and dev_printk interfaces. Optional fields depend on `CONFIG_PRINTK_EXECUTION_CTX`. The static-definition macros are used by printk core instances and tests; the `__u64seq_to_ulseq()` conversion helpers bridge 64-bit sequence logic with 32-bit atomic storage.

## Risks and invariants
Any layout or macro change must preserve descriptor-state packing, bootstrap sequence assumptions, power-of-two buffer sizing, and alignment requirements. The 32-bit sequence conversion assumes readers cannot lag by more than 2^31 records. `text_len` is `u16`, so users must not advertise payload lengths beyond representable or allocated data. The header is shared by low-level printk paths, so ABI-like source compatibility matters.

## Test signals
Build coverage across 32-bit/64-bit, `CONFIG_PRINTK_EXECUTION_CTX`, and KUnit export configurations is important. Runtime signals come from the KUnit ringbuffer stress test, normal printk output under load, sequence iteration from consoles, and warnings from implementation-side validation of descriptor and logical-position invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/printk_ringbuffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/printk_ringbuffer_kunit_test.c -->
# sources/distributed-fs/ceph-client/kernel/printk/printk_ringbuffer_kunit_test.c

## Purpose
`printk_ringbuffer_kunit_test.c` is a KUnit stress test for lockless printk ringbuffer data integrity. It creates a private ringbuffer, starts per-CPU writer kthreads, and validates records from a reader thread for a configurable runtime.

## Important APIs, types, and functions
The test uses `DEFINE_PRINTKRB()`, `prb_init()`, `prb_rec_init_wr()`, `prb_reserve()`, `prb_commit()`, `prb_rec_init_rd()`, and `prb_read_valid()`. `struct prbtest_rbdata` is the embedded payload format with a size field and repeated-character text. `struct prbtest_data` tracks the KUnit instance, ringbuffer, and waitqueue. `prbtest_writer()` generates records, `prbtest_reader()` validates them, and `test_readerwriter()` orchestrates CPU selection and kthread startup.

## Control flow
The test snapshots online CPUs under the CPU hotplug read lock, chooses one CPU for the reader, and uses remaining CPUs for writers. Each writer repeatedly picks a random text size, reserves a record, fills an embedded size plus repeated byte pattern based on CPU/thread identity, commits it, and wakes the reader. The reader waits until a requested sequence can be read, checks monotonicity, validates size, terminator, and repeated content, then advances to the next sequence.

## State and persistence behavior
State is entirely test-local. The static test ringbuffer is reinitialized at test start because KUnit may rerun suites. KUnit cleanup actions free the cpumask and stop writer kthreads. A stack timer wakes the reader after `runtime_ms` by setting `TIF_NOTIFY_SIGNAL`, ending the wait loop.

## Dependencies and integration points
The file integrates KUnit resources/actions, CPU masks and hotplug locking, kthreads, timers, waitqueues, scheduler rescheduling, random number generation, and KUnit-only exported ringbuffer symbols via `MODULE_IMPORT_NS("EXPORTED_FOR_KUNIT_TESTING")`.

## Risks and invariants
The test intentionally ignores reservation failure because it drives unbounded concurrent writers. That means it detects corruption and sequence problems, not throughput success. CPU hotplug changes after the snapshot can reduce ideal isolation but are treated as non-fatal. The reader loop depends on the wake timer to terminate, so timer cleanup must run reliably.

## Test signals
Failures are explicit `KUNIT_FAIL()` reports for bad sequence reads or malformed records. Useful stress signals include running on many CPUs, increasing `runtime_ms`, enabling KCSAN/lockdep, and seeing no malformed repeated strings despite descriptor/data wrap and concurrent overwrite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/printk_ringbuffer_kunit_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/printk_safe.c -->
# sources/distributed-fs/ceph-client/kernel/printk/printk_safe.c

## Purpose
`printk_safe.c` tracks printk contexts where legacy console printing must be deferred or forced to avoid recursion, deadlock, or unsafe spinning. It also routes `vprintk()` through KDB when kernel debugger printk trapping is active.

## Important APIs, types, and functions
`printk_force_console_enter()`, `printk_force_console_exit()`, and `is_printk_force_console()` maintain an atomic force-console nesting counter. `__printk_safe_enter()` and `__printk_safe_exit()` update a per-CPU `printk_context`. `__printk_deferred_enter()` and `__printk_deferred_exit()` wrap those updates with `cant_migrate()`. `is_printk_legacy_deferred()` evaluates global forced-kthread mode, per-CPU context, NMI state, and printk CPU-sync ownership. `vprintk()` dispatches either to `vkdb_printf()` or `vprintk_default()`.

## Control flow
Callers enter safe or deferred sections before printk-deadlock-prone activity and exit afterward. Legacy printk paths ask `is_printk_legacy_deferred()` to decide whether synchronous console work should be deferred. If KGDB/KDB traps printk and the current CPU is not already in KDB printf recursion, `vprintk()` sends the formatted output to KDB.

## State and persistence behavior
State is volatile runtime-only: an atomic global force counter and per-CPU nesting count. The per-CPU count is safe to read in any context because migration is disabled while it is set. No state persists across boot or module boundaries.

## Dependencies and integration points
The file depends on preemption/migration checks, NMI detection, KDB/KGDB optional support, SMP/per-CPU primitives, printk internal helpers, and exported `vprintk` ABI used by kernel code.

## Risks and invariants
Enter/exit nesting must remain balanced. Per-CPU context increments can be preempted by NMI, so operations must remain simple and NMI-tolerant. Incorrect deferral decisions can deadlock legacy console paths or suppress urgent console output. KDB routing must avoid recursion via `kdb_printf_cpu`.

## Test signals
Signals include nested safe/deferred printk paths, NMI printk, console lock recursion testing, KDB printk trapping, and lockdep reports around console and port locks. Balanced force-console and per-CPU nesting can be asserted indirectly by verifying later printk paths return to normal synchronous behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/printk_safe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/sysctl.c -->
# sources/distributed-fs/ceph-client/kernel/printk/sysctl.c

## Purpose
`printk/sysctl.c` registers the `/proc/sys/kernel` sysctl controls for printk behavior, rate limiting, devkmsg policy, dmesg restrictions, and kernel pointer exposure restrictions.

## Important APIs, types, and functions
`printk_sysctls[]` declares entries for `printk`, `printk_ratelimit`, `printk_ratelimit_burst`, `printk_delay`, `printk_devkmsg`, `dmesg_restrict`, and `kptr_restrict`. `proc_dointvec_minmax_sysadmin()` wraps `proc_dointvec_minmax()` and requires `CAP_SYS_ADMIN` on writes. `printk_sysctl_init()` registers the table under `kernel`.

## Control flow
During printk sysctl initialization, the table is registered once. Reads and writes then dispatch to standard proc handlers. `printk_delay` is bounded between zero and `ten_thousand`. `dmesg_restrict` and `kptr_restrict` use the CAP_SYS_ADMIN-enforcing wrapper and min/max bounds. `printk_devkmsg` delegates parsing to `devkmsg_sysctl_set_loglvl()`.

## State and persistence behavior
The file exposes existing kernel variables rather than owning persistent state: `console_loglevel`, `printk_ratelimit_state.interval`, `printk_ratelimit_state.burst`, `printk_delay_msec`, `devkmsg_log_str`, `dmesg_restrict`, and `kptr_restrict`. Changes persist only for the running kernel unless userspace reapplies them.

## Dependencies and integration points
It integrates proc sysctl registration, capability checks, printk internals, ratelimit state, and security-sensitive kernel information controls consumed by `/proc/kmsg`, `dmesg`, and pointer formatting.

## Risks and invariants
Permission and bounds are the key risks. Relaxing write checks for `dmesg_restrict` or `kptr_restrict` can expose sensitive data; missing bounds on `printk_delay` can create pathological stalls. The table data pointers must match object sizes and handler expectations.

## Test signals
Useful tests are sysctl read/write permission checks as privileged and unprivileged users, min/max validation, `printk_devkmsg` string parsing, rate-limit behavior changes, and verifying `register_sysctl_init("kernel", ...)` creates the expected entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/printk/sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/profile.c -->
# sources/distributed-fs/ceph-client/kernel/profile.c

## Purpose
`profile.c` implements legacy kernel profiling. It parses boot-time `profile=` configuration, allocates a direct-mapped atomic counter buffer for kernel text samples, records CPU/scheduler/KVM profiling hits, and exposes binary data through `/proc/profile` when procfs is enabled.

## Important APIs, types, and functions
Global state includes exported `prof_on`, `prof_buffer`, `prof_len`, and `prof_shift`. `profile_setup()` parses numeric, `schedule`, and `kvm` modes. `profile_init()` sizes and allocates the buffer. `profile_hits()` and `profile_tick()` update counters. Procfs support is implemented by `read_profile()`, weak `setup_profiling_timer()`, `write_profile()`, `profile_proc_ops`, and `create_proc_profile()`.

## Control flow
At boot, `profile_setup()` selects profiling mode and sample shift. `profile_init()` computes the number of buckets over `_stext.._etext`, tries `kzalloc()`, `alloc_pages_exact()`, then `vzalloc()`, and disables profiling if the shift leaves no buckets. At runtime, `profile_tick()` samples the interrupt register PC for kernel-mode ticks, while other code can call `profile_hits()`. Proc reads return the sample step followed by raw atomic counters; writes reset counters and optionally set an architecture-specific profiling timer multiplier.

## State and persistence behavior
Profile counters persist in memory for the running boot until reset through `/proc/profile`. Data is binary and direct-mapped by `(pc - _stext) >> prof_shift`; collisions are expected at coarse shifts. No on-disk state is maintained.

## Dependencies and integration points
The file integrates boot parameters, kernel text section symbols, IRQ register access, architecture `profile_pc()`, scheduler stats, procfs, user copy helpers, memory allocators, and weak architecture override of `setup_profiling_timer()`.

## Risks and invariants
The buffer must cover only kernel text and must not be used before allocation. `prof_shift` must be clamped to avoid undefined shifts. Proc read offsets mix an `unsigned int` header with `atomic_t` counters, so size calculations must remain consistent with the historical readprofile ABI. Writes reset all counters and can alter profiling timer frequency only where supported.

## Test signals
Boot with `profile=N`, `profile=schedule,N`, and `profile=kvm,N`; verify allocation success/failure paths, `/proc/profile` size and binary header, counter increments on kernel workload, write reset behavior, and architecture timer multiplier error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/profile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/kernel/ptrace.c

## Purpose
`ptrace.c` provides the architecture-independent ptrace syscall core. It manages tracee attachment, permission checks, parent/child ptrace linkage, traced-task freezing, detach/reap behavior, tracee memory access, signal/regset/syscall-info requests, seccomp/rseq/syscall-user-dispatch requests, and compat syscall dispatch.

## Important APIs, types, and functions
Key exported or shared functions include `ptrace_access_vm()`, `__ptrace_link()`, `__ptrace_unlink()`, `ptrace_may_access()`, `exit_ptrace()`, `ptrace_readdata()`, `ptrace_writedata()`, `ptrace_request()`, `generic_ptrace_peekdata()`, `generic_ptrace_pokedata()`, and compat variants. Internal control helpers include `ptrace_check_attach()`, `ptrace_freeze_traced()`, `ptrace_unfreeze_traced()`, `__ptrace_may_access()`, `ptrace_attach()`, `ptrace_traceme()`, `ptrace_detach()`, `ptrace_resume()`, regset helpers, and syscall-info get/set helpers.

## Control flow
`SYSCALL_DEFINE4(ptrace)` handles `PTRACE_TRACEME` directly, looks up the target task, routes attach/seize through `ptrace_attach()`, otherwise verifies the task is traced by current and frozen unless the request allows asynchronous state. Architecture-specific `arch_ptrace()` gets first chance for requests; common `ptrace_request()` handles generic operations. Resume requests update syscall tracing flags, single-step/block-step state, exit signal, and wake the tracee. Detach disables arch-specific tracing, restores parentage, handles stopped state, and notifies proc connector.

## State and persistence behavior
Ptrace state lives in `task_struct`: `ptrace` flags, parent/real_parent, ptraced lists, `ptracer_cred`, jobctl flags, `last_siginfo`, `ptrace_message`, blocked masks, and syscall work bits. Attach persists until detach, tracer exit, tracee exit, or exec-specific transitions. Memory access is transient through `access_remote_vm()` after dumpability and credential checks.

## Dependencies and integration points
The file integrates tasklist locking, sighand locks, credentials, user namespaces, capabilities, LSM hooks, audit, proc connector, signals/job control, seccomp, rseq, syscall user dispatch, arch ptrace hooks, user regsets, compat siginfo/iovec handling, and remote memory GUP flags.

## Risks and invariants
Permission ordering is security critical: credentials are read before dumpability with an `smp_rmb()` pairing `commit_creds()`. Tasklist and sighand locks protect parentage and stop-state transitions. `JOBCTL_PTRACE_FROZEN` prevents tracees from running during sensitive operations. Detach and tracer-exit paths must correctly handle zombies and group stops. Compat and syscall-info setters must validate sizes, reserved fields, and sign extension to avoid ABI corruption.

## Test signals
Signals include ptrace selftests for attach/seize/traceme, permission denial across UIDs/user namespaces/dumpability, signal injection, group-stop/listen/interrupt semantics, regset get/set, syscall-info get/set, seccomp filter/metadata, rseq configuration, memory peek/poke partial failures, tracer exit with zombies, and compat ptrace on supported architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/range.c -->
# sources/distributed-fs/ceph-client/kernel/range.c

## Purpose
`range.c` provides small helper routines for adding, merging, subtracting, cleaning, and sorting arrays of half-open `struct range` intervals.

## Important APIs, types, and functions
The public helpers are `add_range()`, `add_range_with_merge()`, `subtract_range()`, `clean_sort_range()`, and `sort_range()`. `cmp_range()` is the local comparator used by `sort()`. The file operates on caller-owned `struct range` arrays with fixed slot count `az`.

## Control flow
`add_range()` appends a non-empty `[start, end)` interval if there is a free slot. `add_range_with_merge()` scans existing non-empty ranges for overlap or adjacency according to the `common_start > common_end` test, folds matching entries into the new start/end, removes consumed slots with `memmove()`, then appends the merged range. `subtract_range()` walks all slots and handles full removal, trimming from the front, trimming from the back, or splitting into a spare slot. `clean_sort_range()` compacts non-empty ranges toward the front, zeroes vacated slots, counts active ranges, and sorts by start. `sort_range()` sorts an already compact range array.

## State and persistence behavior
All mutations are in-place in the supplied array. Empty slots are represented by `end == 0` with start also usually zeroed. There is no synchronization, allocation, or persistent global state.

## Dependencies and integration points
The file depends on `linux/range.h`, min/max helpers, `memmove()`, kernel sort, and printk for split-without-slot errors. It is suitable for boot or architecture memory/resource range construction where fixed arrays are common.

## Risks and invariants
Callers must provide correct array size and external synchronization. Subtract splitting can lose the right-side fragment if no empty slot exists, logging an error but preserving the left fragment. The interval convention is effectively half-open because empty ranges satisfy `start >= end`; overlap/merge behavior treats touching intervals as mergeable when `common_start == common_end`.

## Test signals
Tests should cover empty additions, full arrays, overlapping and touching merges, non-overlapping ranges, subtract full/left/right/middle split, split without spare slot, compaction with holes, and sorted order after cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/rcu/Kconfig

## Purpose
`kernel/rcu/Kconfig` defines build-time configuration for Linux RCU implementations, SRCU variants, task-based RCU flavors, stall diagnostics, tree fanout, callback offloading, priority boosting, lazy callbacks, and expert-only tuning.

## Important APIs, types, and functions
This is declarative Kconfig rather than C API. Core symbols include `TREE_RCU`, `PREEMPT_RCU`, `TINY_RCU`, `TINY_SRCU`, `TREE_SRCU`, `TASKS_RCU`, `TASKS_RUDE_RCU`, `TASKS_TRACE_RCU`, `RCU_STALL_COMMON`, `RCU_NEED_SEGCBLIST`, `RCU_FANOUT`, `RCU_FANOUT_LEAF`, `RCU_BOOST`, `RCU_NOCB_CPU`, `RCU_LAZY`, and `RCU_DOUBLE_CHECK_CB_TIME`.

## Control flow
Symbol defaults select the implementation based on SMP, preemption, and expert options. `PREEMPT_RCU` selects `TREE_RCU`; UP non-preemptible builds default to `TINY_RCU`. SRCU defaults to tiny or tree according to the RCU flavor. Task-based RCU options are normally selected by need/force symbols. Offload, lazy, boosting, and fanout options are gated by `RCU_EXPERT`, `NO_HZ_FULL`, `PREEMPT_RT`, and related architecture capabilities.

## State and persistence behavior
The file controls compiled-in code paths and default boot behavior, not runtime state. Some symbols enable runtime boot/module parameters elsewhere, such as callback offload, lazy callback behavior, stall timeouts, and tree geometry.

## Dependencies and integration points
It feeds `kernel/rcu/Makefile`, RCU headers, tree/tiny/SRCU/task implementations, IRQ work, context tracking, RT mutexes, NOCB kthreads, and testing/torture infrastructure. Selection of `RCU_NEED_SEGCBLIST` determines whether segmented callback list support is compiled.

## Risks and invariants
Bad dependencies can compile incompatible combinations or silently remove required RCU infrastructure. Expert defaults must avoid prompting ordinary `oldconfig` users for obscure settings. `RCU_FANOUT` ranges must preserve tree scalability constraints. Offload and boosting options have latency and scheduling side effects.

## Test signals
Signals include allnoconfig/defconfig/SMP/PREEMPT/PREEMPT_RT/NO_HZ_FULL build matrices, Kconfig dependency checks, booting tiny and tree RCU kernels, RCU torture/scalability tests under selected flavors, and verifying generated objects match the selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/Makefile -->
# sources/distributed-fs/ceph-client/kernel/rcu/Makefile

## Purpose
`kernel/rcu/Makefile` selects the RCU subsystem objects built for the active configuration and adjusts instrumentation flags for RCU code.

## Important APIs, types, and functions
The Makefile always builds `update.o` and `sync.o`. It conditionally builds `srcutree.o`, `srcutiny.o`, `rcutorture.o`, `rcuscale.o`, `refscale.o`, `tree.o`, `tiny.o`, and `rcu_segcblist.o` according to Kconfig symbols.

## Control flow
Kbuild evaluates configuration variables and appends objects to `obj-y` or `obj-$(CONFIG_...)`. KCOV instrumentation is disabled for this directory because coverage is non-deterministic and generally not syscall-input-driven. When KCSAN is enabled, the file adds debug-friendly flags `-g -fno-omit-frame-pointer`.

## State and persistence behavior
This file has no runtime state. It controls which object files become part of the kernel or module build.

## Dependencies and integration points
It integrates with Kbuild, Kconfig symbols from `kernel/rcu/Kconfig`, KCOV, KCSAN, and the RCU source files. `CONFIG_RCU_NEED_SEGCBLIST` is the build gate for segmented callback list support used by tree RCU, tree SRCU, and generic Tasks RCU.

## Risks and invariants
Object selection must match Kconfig semantics. Missing `rcu_segcblist.o` for a configuration that references segmented callback lists would cause link failures; building incompatible tree/tiny files would create duplicate or missing symbols. Instrumentation choices matter because RCU internals are sensitive to recursion, timing, and data-race observation.

## Test signals
Build matrix coverage across tiny, tree, SRCU, torture, scale, refscale, KCOV, and KCSAN configurations is the main signal. Link errors and unexpected instrumentation recursion are the likely regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/rcu.h -->
# sources/distributed-fs/ceph-client/kernel/rcu/rcu.h

## Purpose
`kernel/rcu/rcu.h` is an internal shared header for RCU implementations. It provides grace-period sequence arithmetic, debug-object hooks for `rcu_head`, stall suppression/ftrace dump helpers, RCU tree geometry iteration, ordered rcu_node locking wrappers, and declarations/stubs shared across tiny, tree, SRCU, tasks, torture, lazy, and NOCB paths.

## Important APIs, types, and functions
Sequence helpers include `rcu_seq_ctr()`, `rcu_seq_state()`, `rcu_seq_set_state()`, `rcu_seq_start()`, `rcu_seq_endval()`, `rcu_seq_end()`, `rcu_seq_snap()`, `rcu_seq_current()`, `rcu_seq_started()`, `rcu_seq_done()`, `rcu_seq_done_exact()`, `rcu_seq_completed_gp()`, `rcu_seq_new_gp()`, and `rcu_seq_diff()`. Debug helpers include `debug_rcu_head_queue()`, `debug_rcu_head_unqueue()`, `debug_rcu_head_callback()`, and `rcu_barrier_cb_is_done()`. Tree helpers include `rcu_init_levelspread()`, node iteration macros, and raw spinlock wrappers ending in `_rcu_node`.

## Control flow
Grace-period updaters call `rcu_seq_start()` before a GP and `rcu_seq_end()` afterward; waiters take snapshots with `rcu_seq_snap()` and poll for completion. Tree RCU code uses breadth-first and leaf iteration macros to traverse `rcu_state.node[]`. Tree-level locking must go through wrappers that add `smp_mb__after_unlock_lock()` to preserve ordering while moving across different node locks.

## State and persistence behavior
The header manipulates sequence counters whose low bits encode state and high bits encode completed grace periods. It references global RCU state such as fanout settings, stall controls, GP kthreads, lazy callback timing, torture data, and CPU-online tracking, but does not allocate state itself.

## Dependencies and integration points
It depends on trace events, slab/debug objects, RCU node tree definitions, ftrace, lockdep, tiny/tree configuration, tasks RCU, SRCU, NOCB, lazy RCU, torture, and architecture support for context tracking and CPU rescheduling.

## Risks and invariants
Sequence arithmetic must handle wraparound and state-bit masking. `rcu_seq_done_exact()` intentionally avoids the broad ULONG guard band for full polling APIs because root and global GP sequences can lag. rcu_node lock wrappers are required for transitive ordering across the tree; bypassing them can break GP visibility. Debug-object hooks must stay cheap or compiled out when disabled.

## Test signals
RCU torture, SRCU torture, tasks-RCU torture, stall warning tests, polled GP API tests, KCSAN/lockdep, tiny/tree build matrices, and wraparound simulation via torture controls are the best coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/rcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/rcu_segcblist.c -->
# sources/distributed-fs/ceph-client/kernel/rcu/rcu_segcblist.c

## Purpose
`rcu_segcblist.c` implements simple and segmented RCU callback lists. Segmented lists divide callbacks into done, waiting, next-ready, and next segments so RCU can advance callbacks as grace periods start and finish without relinking each callback individually.

## Important APIs, types, and functions
Simple-list APIs are `rcu_cblist_init()`, `rcu_cblist_enqueue()`, `rcu_cblist_flush_enqueue()`, and `rcu_cblist_dequeue()`. Segmented-list APIs include length helpers, `rcu_segcblist_init()`, `rcu_segcblist_disable()`, `rcu_segcblist_ready_cbs()`, `rcu_segcblist_pend_cbs()`, `rcu_segcblist_first_cb()`, `rcu_segcblist_first_pend_cb()`, `rcu_segcblist_nextgp()`, `rcu_segcblist_enqueue()`, `rcu_segcblist_entrain()`, extract/insert helpers, `rcu_segcblist_advance()`, `rcu_segcblist_accelerate()`, and `rcu_segcblist_merge()`.

## Control flow
Normal callback enqueue increments total and next-segment lengths, appends the callback at `RCU_NEXT_TAIL`, and updates tail pointers. When a grace period advances, `rcu_segcblist_advance()` moves segments whose `gp_seq[]` is complete into `RCU_DONE_TAIL`, compacts remaining segment pointers, and preserves pending sequence labels. `rcu_segcblist_accelerate()` merges later segments into an earlier GP sequence when better GP information is available. Extract/insert helpers move done or pending callbacks to temporary `rcu_cblist`s for invocation, migration, or CPU hotplug merging.

## State and persistence behavior
State is stored in `struct rcu_segcblist`: callback head, segment tail pointers, per-segment lengths, total length, flags, and GP sequence labels. Total length may temporarily disagree with actual linked callbacks while invocation batches are extracted; comments explicitly direct callers to use count-based checks when needed.

## Dependencies and integration points
The code depends on callback-list definitions from public/internal RCU headers, `CONFIG_RCU_NOCB_CPU` atomic length handling, CPU hotplug locking for merge, memory barriers required by `rcu_barrier()`, and RCU implementations that post, accelerate, invoke, and migrate callbacks.

## Risks and invariants
Length transitions between zero and nonzero are barrier-sensitive because `rcu_barrier()` samples lengths locklessly and must not miss callbacks before module unload. Tail pointers must preserve segment ordering and emptiness semantics. `rcu_segcblist_entrain()` is only for barrier-like callbacks and waits for prior callbacks, not necessarily a grace period. Merging pending callbacks makes them restart GP waiting, so callers should advance/accelerate first.

## Test signals
Signals include RCU torture callback flooding, `rcu_barrier()` under module unload races, NOCB offload tests, CPU hotplug callback migration, segment length consistency checks, and KCSAN/lockdep around lockless length sampling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/rcu_segcblist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/rcu_segcblist.h -->
# sources/distributed-fs/ceph-client/kernel/rcu/rcu_segcblist.h

## Purpose
`rcu_segcblist.h` is the internal declaration and inline-helper header for RCU callback list management. It wraps public `linux/rcu_segcblist.h` definitions with helpers used by RCU implementation files.

## Important APIs, types, and functions
The header exposes `rcu_cblist_n_cbs()`, `rcu_segcblist_empty()`, `rcu_segcblist_n_cbs()`, flag helpers, `rcu_segcblist_is_enabled()`, `rcu_segcblist_is_offloaded()`, `rcu_segcblist_restempty()`, and `rcu_segcblist_segempty()`, plus prototypes for all simple-list and segmented-list operations implemented in `rcu_segcblist.c`.

## Control flow
Callers use inline predicates before posting, advancing, extracting, or invoking callbacks. `rcu_segcblist_ready_cbs()` and `rcu_segcblist_pend_cbs()` are implemented in the C file, while these inline helpers provide low-level emptiness and flag decisions. `rcu_segcblist_n_cbs()` chooses atomic or plain reads depending on NOCB support.

## State and persistence behavior
No state is owned by the header. It defines how to read `struct rcu_cblist` and `struct rcu_segcblist` fields safely enough for RCU internals. A key documented behavior is that `head == NULL` does not always mean there are no callbacks, because invocation may temporarily extract callbacks while length accounting remains authoritative.

## Dependencies and integration points
It depends on `linux/rcu_segcblist.h`, RCU segment constants, `CONFIG_RCU_NOCB_CPU`, and flags such as `SEGCBLIST_ENABLED` and `SEGCBLIST_OFFLOADED`. It is included by RCU callback handling code, tree/tiny/SRCU/tasks implementations where segmented lists are enabled, and tests/torture indirectly.

## Risks and invariants
Emptiness helpers must match the tail-pointer representation exactly. Misreading `head` instead of `len` can break barrier or invocation logic. Offload detection must remain conditional on NOCB support. Flag helpers use `WRITE_ONCE()`/`READ_ONCE()` and should not be replaced with plain operations in lockless paths.

## Test signals
Build coverage with and without `CONFIG_RCU_NOCB_CPU`, callback enqueue/invoke torture, CPU offload/deoffload tests, and barrier tests that validate length-based callback detection are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/rcu_segcblist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/rcuscale.c -->
# sources/distributed-fs/ceph-client/kernel/rcu/rcuscale.c

## Purpose
`rcuscale.c` is a module/built-in scalability test for RCU grace-period primitives and `kfree_rcu()` behavior. It creates reader and writer kthreads, measures synchronous, expedited, or asynchronous grace-period durations, optionally stresses callback allocation/freeing, and reports per-writer measurements.

## Important APIs, types, and functions
Module parameters include `scale_type`, `gp_async`, `gp_async_max`, `gp_exp`, `holdoff`, `minruntime`, `nreaders`, `nwriters`, `shutdown_secs`, writer holdoffs, and kfree-related knobs. `struct rcu_scale_ops` abstracts RCU flavors with read lock/unlock, GP sequence, async callback, barrier, sync, expedited sync, stats, and GP-kthread accessors. Implemented flavors include `rcu`, `srcu`, dynamic `srcud`, and optional tasks/tasks-rude/tasks-tracing. Main threads are `rcu_scale_reader()`, `rcu_scale_writer()`, and `kfree_scale_thread()`.

## Control flow
`rcu_scale_init()` selects the ops vector by `scale_type`, initializes flavor state, allocates arrays, starts reader kthreads, initializes optional async freelists, and starts writer kthreads. Readers repeatedly enter and exit read-side critical sections with interrupts disabled to provide load. Writers wait for holdoff and system running state, then repeatedly measure normal, expedited, or async grace-period operations until minimum runtime and sample thresholds are met. Cleanup stops threads, prints counts and durations, frees arrays, runs flavor cleanup, and may power off for automated testing. If `kfree_rcu_test` is enabled, initialization routes to kfree-specific setup and threads.

## State and persistence behavior
State is runtime-only: task arrays, duration arrays, writer completion flags, async freelists, atomic counters, timestamps, GP batch snapshots, kfree test counters, and optional SRCU structure. Measurements are printed to the kernel log; no file output is owned by this module.

## Dependencies and integration points
The file depends on torture infrastructure, kthreads, scheduler policy APIs, CPU affinity, completions/atomics/llists, SRCU, Tasks RCU variants, lazy RCU controls, memory allocation, reboot poweroff for test automation, ftrace dumps on completion, and RCU internal helpers from `rcu.h`.

## Risks and invariants
This is test code but can stress production paths heavily. Async mode must cap in-flight callbacks and return all `writer_mblock`s to freelists before cleanup. Built-in tests must account for boot-time expedited GP behavior before measuring normal GPs. `shutdown_secs` can power off the system. Kfree lazy self-test temporarily changes lazy flush timing and must restore it. Affinity and FIFO-low scheduling can affect host responsiveness.

## Test signals
Expected signals are kernel log lines with module parameters, writer measurement counts, total duration, GP batches, per-writer durations, kfree total time/memory footprint, and warnings when requested normal/expedited mode is unavailable. RCU torture automation, boot-time built-in runs, module load/unload, async callback accounting warnings, and lazy-callback timing checks provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/rcuscale.c -->
