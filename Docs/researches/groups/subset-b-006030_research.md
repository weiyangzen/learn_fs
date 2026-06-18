# subset-b-006030 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/events/hw_breakpoint.c -->
# sources/distributed-fs/ceph-client/kernel/events/hw_breakpoint.c

Purpose: implements the architecture-independent perf PMU for hardware breakpoints. It mediates user and kernel breakpoint registration through perf events, enforces per-CPU and per-task hardware slot limits, exposes wide and task-targeted registration helpers, and wires breakpoint trap notification into the architecture-specific handlers.

Important APIs/types/functions: `struct bp_slots_histogram` tracks how many CPUs or tasks consume N breakpoint slots; `struct bp_cpuinfo` stores per-CPU CPU-pinned counts and task-pinned histograms; `reserve_bp_slot()`, `release_bp_slot()`, `modify_user_hw_breakpoint_check()`, `register_perf_hw_breakpoint()`, `register_user_hw_breakpoint()`, `register_wide_hw_breakpoint()`, `unregister_wide_hw_breakpoint()`, and `hw_breakpoint_is_used()` form the main exported or cross-subsystem surface. The `perf_breakpoint` PMU supplies `.event_init`, `.add`, `.del`, `.start`, `.stop`, and `.read`, while `hw_breakpoint_exceptions_nb` registers the architecture die notifier. Architecture dependencies include `hw_breakpoint_slots()`, `hw_breakpoint_arch_parse()`, `arch_install_hw_breakpoint()`, `arch_uninstall_hw_breakpoint()`, `hw_breakpoint_exceptions_notify()`, and optional `hw_breakpoint_weight()`.

Control flow: initialization builds the task breakpoint rhltable, initializes static or dynamically allocated slot histograms, marks constraints initialized, registers the perf PMU as `PERF_TYPE_BREAKPOINT`, and registers the die notifier. Event initialization rejects non-breakpoint events and unsupported breakpoint types, reserves capacity, parses the architecture breakpoint, and installs a destroy callback that releases the slot. Registration first reserves accounting capacity and only then parses architecture constraints; on parse failure it rolls the accounting back. Modification disables the perf event, parses the new attributes, optionally validates that only breakpoint fields changed, moves slot accounting if the breakpoint type changed, updates `bp->attr`, and re-enables if appropriate.

State and persistence: all state is in-memory kernel accounting. Per-CPU `bp_cpuinfo[TYPE_MAX]`, global `cpu_pinned[]`, global CPU-independent `tsk_pinned_all[]`, and `task_bps_ht` together model whether a new breakpoint can fit on every CPU where it may execute. `constraints_initialized` gates runtime operations after boot allocation. There is no disk persistence; lifetime is tied to perf event objects and boot-time static data. Task-targeted breakpoints are keyed by `hw.target` in `task_bps_ht`, and lifecycle updates must stay consistent with perf event destruction.

Locking and slot accounting: `bp_cpuinfo_sem` is a static percpu rwsem. CPU breakpoints take the write side for stable global snapshots and mutation. Task breakpoints take the target task's `perf_event_mutex` plus the read side, allowing concurrent atomic histogram updates for independent tasks; operations needing stable snapshots take the write side. `toggle_bp_slot()` handles the hard cases where task breakpoints transition between all-CPU accounting and per-CPU accounting. It removes task breakpoints from the rhltable before disable-side recomputation, inserts after enable-side accounting, and updates histograms via atomic indexed counts. `max_bp_pinned_slots()` computes the worst-case aggregate of CPU-pinned and task-pinned consumers, using a fast path when a task's breakpoints are CPU-independent.

Dependencies and integration points: this file integrates perf event creation/release, task perf mutexes, CPU hotplug iteration, RCU rhashtable lookup, kernel capabilities (`CAP_SYS_ADMIN` for kernel-space breakpoints), architecture debug register operations, and die notifiers. It is also referenced by ptrace cleanup and KUnit tests. `dbg_reserve_bp_slot()` and `dbg_release_bp_slot()` intentionally bypass normal locking for debugger use, but refuse to run if the constraint locks are already held.

Risks: correctness depends on histogram transitions matching the rhltable content exactly; a missed transition can either leak slots or permit overcommit of scarce debug registers. Lock ordering around `perf_event_mutex` and `bp_cpuinfo_sem` is subtle, especially for inherited events and debugger paths. Kernel-address breakpoints are security-sensitive and require capability checks to prevent trap-path recursion attacks. Dynamic slot allocation can fail at boot and causes later reservations to return `-ENOMEM`.

Test signals: `hw_breakpoint_test.c` directly stresses CPU-only, task-only, mixed task/CPU, all-CPU, and multi-task accounting and checks `hw_breakpoint_is_used()` at teardown. Wider system signals include perf breakpoint selftests, ptrace hardware breakpoint tests, lockdep coverage for nested mutex/percpu-rwsem ordering, and architecture debug-register tests that exercise PMU add/delete callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/events/hw_breakpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/events/hw_breakpoint_test.c -->
# sources/distributed-fs/ceph-client/kernel/events/hw_breakpoint_test.c

Purpose: KUnit coverage for hardware breakpoint constraint accounting. It does not test low-level debug-register trapping; it validates that the generic slot reservation logic rejects impossible CPU/task combinations and restores state after unregistering breakpoints.

Important APIs/types/functions: `register_test_bp()` creates a kernel perf breakpoint using `perf_event_create_kernel_counter()` with `HW_BREAKPOINT_RW`; `unregister_test_bp()` releases it through `unregister_hw_breakpoint()`; `get_test_bp_slots()` caches `hw_breakpoint_slots(TYPE_DATA)`; `fill_one_bp_slot()` and `fill_bp_slots()` build saturated breakpoint sets. The suite uses `TEST_EXPECT_NOSPC()` for expected `-ENOSPC`, `TEST_REQUIRES_BP_SLOTS()` for architectures with too few debug registers, and a helper kthread from `get_other_task()` to model a second task.

Control flow: each case fills one or more breakpoint dimensions, attempts one additional registration that should fail, optionally unregisters a previous breakpoint, and checks whether the freed capacity can be reused by a CPU or task target. `test_init()` skips when fewer than two CPUs are online or if existing breakpoints would contaminate accounting. `test_exit()` unregisters all created breakpoints, stops the dummy task, and asserts `hw_breakpoint_is_used()` is false.

State and persistence: the test keeps static arrays `break_vars[]` for watched addresses and `test_bps[]` for live perf event pointers. `__other_task` is a lazily created kthread shared by cases but cleaned up by suite exit. No persistent state exists beyond the KUnit run; the critical postcondition is that all breakpoint accounting is empty.

Dependencies and integration points: the tests depend on KUnit, online CPU iteration, kthreads, perf event kernel counters, `linux/hw_breakpoint.h`, and architecture `hw_breakpoint_slots()`. They exercise the public registration path rather than internal helpers, so failures are meaningful for real perf users.

Risks: tests are environment-sensitive: they skip if another subsystem is already using hardware breakpoints, if CPU count is too low, or if architecture slot count cannot satisfy a scenario. The fixed `MAX_TEST_BREAKPOINTS` bounds large CPU systems and causes `fill_bp_slots()` to stop when it would exceed the array. A failed cleanup would poison later cases, so `test_exit()` aggressively unregisters all non-null entries.

Test signals: the cases cover one CPU full, many CPUs independent, one task across all CPUs, two tasks across all CPUs, task-on-one-CPU, mixed task all-CPU plus CPU-specific breakpoints, two tasks on one CPU, one task on one CPU plus another task on all CPUs, and transitions between CPU-dependent and CPU-independent accounting. Expected `-ENOSPC` and final `hw_breakpoint_is_used() == false` are the core signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/events/hw_breakpoint_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/events/internal.h -->
# sources/distributed-fs/ceph-client/kernel/events/internal.h

Purpose: shared private definitions for the perf events implementation, centered on `struct perf_buffer` and inline helpers for ring-buffer output, AUX buffer sizing, recursion protection, and user stack support. It is an internal contract between `ring_buffer.c` and the wider perf event core.

Important APIs/types/functions: `struct perf_buffer` holds refcounts, RCU/freeing state, data ring metadata, poll/wakeup state, mmap ownership and accounting, AUX buffer metadata, and flexible `data_pages[]`. Public-to-internal declarations include `rb_alloc()`, `rb_free()`, `rb_alloc_aux()`, `rb_free_aux()`, `ring_buffer_get()`, `ring_buffer_put()`, `perf_mmap_to_page()`, and `perf_event_aux_event()`. Inline helpers include `rb_free_rcu()`, `rb_toggle_paused()`, `rb_has_aux()`, `page_order()`, `data_page_nr()`, `perf_data_size()`, and `perf_aux_size()`.

Control flow: output-copy helpers are generated with `DEFINE_OUTPUT_COPY()` around `__DEFINE_OUTPUT_COPY_BODY`. They copy, skip, or copy from user memory into the current `perf_output_handle`, advance across data pages, wrap page indices, and return any remaining length. `__output_custom()` lets callers supply a callback. User copies disable page faults and use `__copy_from_user_inatomic()`. Recursion helpers use `interrupt_context_level()` as an index to block re-entry in the same interrupt context.

State and persistence: `perf_buffer` state is transient kernel memory associated with mmaped perf events. It maintains writer `head`, nested writer count, lost record count, wakeup stamps, user-page pointers, mmap refcounts, user accounting, and AUX producer/consumer metadata. No disk persistence exists, but the mmap user page exposes state to userspace readers and must obey memory-ordering rules enforced in `ring_buffer.c`.

Dependencies and integration points: this header depends on hardirq context helpers, uaccess, refcounts, perf event types, page allocation configuration, and architecture overrides such as `arch_perf_out_copy_user()` and `CONFIG_HAVE_PERF_USER_STACK_DUMP`. The macros are tightly coupled to `struct perf_output_handle` fields managed by the perf output path.

Risks: the copy macro mutates handle fields and wraps pages, so callers must initialize `handle->addr`, `handle->size`, and `handle->page` correctly. User copies deliberately run with page faults disabled, so partial copies must be handled. Recursion counters rely on balanced `get_recursion_context()`/`put_recursion_context()` calls. `rb_toggle_paused()` treats zero-page buffers as always paused, preventing writes into missing storage.

Test signals: validation comes mostly from perf ring-buffer tests, mmap sampling tests, AUX tracing tests, and architecture perf tests. Static analysis and lockdep are useful for refcount and RCU lifetime paths, while user-copy fault injection can stress `__output_copy_user()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/events/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/events/ring_buffer.c -->
# sources/distributed-fs/ceph-client/kernel/events/ring_buffer.c

Purpose: implements perf event data and AUX ring buffers. It reserves space for perf records, publishes producer heads to mmap consumers with strict memory ordering, emits lost-record notifications, manages wakeups, allocates/free ring storage, and coordinates AUX tracing buffers used by PMU drivers.

Important APIs/types/functions: normal data path APIs are `perf_output_begin_forward()`, `perf_output_begin_backward()`, `perf_output_begin()`, `perf_output_copy()`, `perf_output_skip()`, and `perf_output_end()`. AUX APIs are `perf_aux_output_begin()`, `perf_aux_output_end()`, `perf_aux_output_skip()`, `perf_aux_output_flag()`, `perf_get_aux()`, `perf_output_copy_aux()`, `rb_alloc_aux()`, and `rb_free_aux()`. Allocation/mapping APIs are `rb_alloc()`, `rb_free()`, and `perf_mmap_to_page()`.

Control flow: `__perf_output_begin()` resolves inherited events to the parent, obtains the RCU-protected ring buffer, rejects paused or missing buffers, accounts pending lost samples, enters the nested writer protocol, atomically advances `rb->head` after checking consumer `data_tail` unless overwrite mode is active, computes the page/offset handle, and optionally writes a `PERF_RECORD_LOST`. `perf_output_end()` calls `perf_output_put_handle()` and drops the RCU read lock. Head publication is delayed until the outermost nested writer exits; if an NMI/IRQ advanced the head during publication, it retries to avoid publishing a stale or backward head.

State and persistence: the data ring state lives in `struct perf_buffer`: `head`, `user_page->data_head`, `user_page->data_tail`, `lost`, `wakeup`, `poll`, `nest`, `paused`, and `overwrite`. AUX state includes `aux_head`, `user_page->aux_head`, `aux_tail`, `aux_nest`, `aux_wakeup`, `aux_watermark`, `aux_refcount`, `aux_mmap_count`, page arrays, and PMU private `aux_priv`. All persistence is mmap-visible memory for the lifetime of the perf event mapping; no filesystem persistence exists.

Dependencies and integration points: integrates with perf event ownership and fasync wakeups, irq_work, PMU AUX `setup_aux()`/`free_aux()` callbacks, page allocator or vmalloc-backed buffer strategies, RCU lifetime helpers, mmap page fault translation, and `internal.h` output copy helpers. PMU drivers are responsible for hardware ordering before `perf_aux_output_end()` publishes AUX data.

Risks: memory barriers are central: the data path pairs kernel data writes and `data_head` stores with userspace `data_tail` updates, and AUX ordering partly relies on PMU driver correctness. Nested writers can run from NMI context, so normal serialization is not available. AUX nesting is explicitly unsupported and warns. Refcount ordering between `aux_mmap_count`, `aux_refcount`, and `rb->refcount` prevents freeing AUX pages from atomic contexts. Large AUX allocation can fail or fragment; `PERF_PMU_CAP_AUX_NO_SG` in overwrite mode requires a single contiguous allocation.

Test signals: perf mmap sampling tests should verify forward and backward writes, wakeups, lost samples, overwrite/non-overwrite behavior, and userspace head/tail visibility. AUX tests through Intel PT or other AUX-capable PMUs exercise AUX begin/end, truncation, watermark wakeups, and mmap page translation. Fault injection around page allocation and PMU setup tests unwind paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/events/ring_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/events/uprobes.c -->
# sources/distributed-fs/ceph-client/kernel/events/uprobes.c

Purpose: implements generic user-space probes and return probes. It tracks probe points by inode and file offset, patches executable private mappings with software breakpoints, dispatches registered consumers on breakpoint hits, executes original instructions out of line, manages return-probe trampolines, and follows mmap/munmap/fork/exit lifecycle changes.

Important APIs/types/functions: `struct uprobe` stores the rb-tree key, refcount, register and consumer semaphores, consumer list, inode/offset/ref-counter offset, flags, and architecture-specific `arch_uprobe`. `struct xol_area` stores execute-out-of-line slots. Public functions include `uprobe_register()`, `uprobe_unregister_nosync()`, `uprobe_unregister_sync()`, `uprobe_apply()`, `uprobe_mmap()`, `uprobe_munmap()`, `uprobe_copy_process()`, `uprobe_free_utask()`, `uprobe_notify_resume()`, `uprobe_pre_sstep_notifier()`, `uprobe_post_sstep_notifier()`, `handle_syscall_uprobe()`, and `uprobes_init()`. Weak architecture hooks cover breakpoint/trap recognition, instruction analysis, XOL preparation/postprocessing, trampoline generation, return address hijacking, and exception notification.

Control flow: registration validates a consumer, mapping support, offsets, and alignment; `alloc_uprobe()` inserts or reuses an inode:offset node in the global RCU rb-tree; `consumer_add()` links the consumer; `register_for_each_vma()` scans current VMAs mapping that file offset and installs breakpoints where the consumer filter allows. Installing a breakpoint prepares the original instruction once, marks `MMF_HAS_UPROBES`, and calls `set_swbp()` to patch the mapping. Unregistration removes the consumer, scans VMAs to remove breakpoints when no consumer remains for an mm, and releases the uprobe after RCU/SRCU grace periods.

Runtime breakpoint flow: the architecture notifier sets `TIF_UPROBE`; `uprobe_notify_resume()` runs in task context. `handle_swbp()` computes the breakpoint address, handles return-trampoline hits separately, finds the active uprobe through speculative or locked VMA lookup plus the rb-tree, resets IP to the original address, checks that the instruction copy is prepared, allocates `current->utask`, runs the consumer handler chain, optionally sets up a return probe, then either skips single-step via arch support or allocates an XOL slot and prepares out-of-line execution. `handle_singlestep()` completes or aborts XOL, releases the uprobe reference, frees the slot, restores deferred signal state, and reports `SIGILL` on post-XOL failure.

State and persistence: global state includes `uprobes_tree`, `uprobes_treelock`, `uprobes_seqcount`, hashed mmap mutexes, `dup_mmap_sem`, `uretprobes_srcu`, and `delayed_uprobe_list`. Per-mm state includes `MMF_HAS_UPROBES`, `MMF_RECALC_UPROBES`, architecture state, and the lazily created `[uprobes]` special XOL mapping. Per-task state is `task_struct::utask`, with active uprobe, XOL address, return-instance stack, reusable return-instance pool, timer, and signal-denial flags. Probe state is not durable; it is reconstructed by live registration and mapping events.

Dependencies and integration points: this file is tightly coupled to mm/VMA internals, page cache and shmem reads, COW page modification, folio walking, MMU notifiers, THP collapse, RCU tasks trace, SRCU, task work, signal handling, ptrace-style single stepping, kdebug die notifiers, and trace/perf consumers. It uses reference counters for SDT-style probes through writable private ref-counter VMAs and delayed increments when the ref-counter VMA appears after the executable VMA.

Risks: patching user instructions must preserve COW semantics, avoid PMD-mapped folios the implementation cannot safely edit, respect userfaultfd write protection, and recover reference-counter updates if patching fails. Uprobe lifetime is complex: normal handlers use RCU tasks trace, return probes may hold SRCU leases across user-mode execution, and fork duplicates return instances with stable or gone hprobe state. XOL slots are limited to one page and wait when exhausted. Races with unregister, munmap, fork, longjmp, fatal signals, and speculative mmap lookup are expected and handled through retries, flags, and conservative restarts.

Test signals: useful coverage includes perf/ftrace uprobe registration, SDT reference counters, filtered consumers, mmap-after-register and unregister-while-running races, return probes with nesting and longjmp, fork/vfork/exec behavior, signal delivery during XOL, userfaultfd/THP/COW mapping cases, and architecture-specific single-step exception paths. Lockdep, RCU stall detection, and fault injection around allocation/GUP paths are important because most failures occur in lifecycle races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/events/uprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/exec_domain.c -->
# sources/distributed-fs/ceph-client/kernel/exec_domain.c

Purpose: provides the remaining generic execution-domain/personality support. In this version the historical exec-domain registry is gone; the file exposes a procfs compatibility view and the `personality(2)` syscall for setting per-task ABI personality flags.

Important APIs/types/functions: `execdomains_proc_show()` writes the static `Linux [kernel]` entry to `/proc/execdomains` when procfs is enabled. `proc_execdomains_init()` creates that proc file at module init time. `SYSCALL_DEFINE1(personality)` returns the current task personality and updates it with `set_personality()` unless the caller passes `0xffffffff`, which is the query-only sentinel.

Control flow: proc initialization creates a single seq-file style proc entry. Reads always show the same Linux domain line. The syscall snapshots `current->personality`, conditionally changes it, and returns the old value as required by the user ABI.

State and persistence: the only mutable state is `current->personality` in each task. `/proc/execdomains` is generated on demand and has no persistent backing. Personality changes persist for the task and across the normal kernel personality inheritance rules handled elsewhere.

Dependencies and integration points: integrates with syscall dispatch, scheduler task state, procfs, seq_file, and `linux/personality.h`. User-space loaders, emulation personalities, and compatibility layers depend on `personality(2)` semantics even though this file no longer manages a dynamic domain table.

Risks: the query sentinel `0xffffffff` must not be treated as a real personality. Any behavioral change is ABI-visible. The proc output is compatibility-oriented and intentionally minimal, so consumers expecting old dynamic exec-domain listings only see Linux.

Test signals: syscall tests should verify query-only behavior, old-value returns, setting personality flags, inheritance behavior through exec/fork as covered elsewhere, and `/proc/execdomains` content when `CONFIG_PROC_FS` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/exec_domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/exit.c -->
# sources/distributed-fs/ceph-client/kernel/exit.c

Purpose: implements process and thread termination, parent notification, reparenting, zombie reaping, wait-family syscalls, oops death handling, and supporting cleanup. It is the central lifecycle path from `exit(2)`, `exit_group(2)`, fatal signals, and kernel oopses to task release.

Important APIs/types/functions: exit-side APIs include `do_exit()`, `make_task_dead()`, `do_group_exit()`, `release_task()`, `put_task_struct_rcu_user()`, `mm_update_next_owner()`, `rcuwait_wake_up()`, and syscall wrappers for `exit` and `exit_group`. Wait-side APIs include `kernel_waitid_prepare()`, `kernel_wait4()`, `kernel_wait()`, `__do_wait()`, `pid_child_should_wake()`, `__wake_up_parent()`, and syscall wrappers for `waitid`, `wait4`, optional `waitpid`, and compat waits. Internal helpers manage signal accounting, orphaned process groups, coredump synchronization, reapers, and zombie/stopped/continued wait cases.

Control flow: `do_exit()` first normalizes kthread and sanitizer state, synchronizes group exit and coredumps, emits ptrace/user-events notifications, cancels io_uring file work, marks `PF_EXITING`, collects accounting, handles last-thread group cleanup, records taskstats and sched tracepoints, shuts down perf before `exit_mm()`, tears down memory, IPC, files, fs, controlling tty, namespaces, task work, thread state, autogroup and cgroups, flushes ptrace hardware breakpoints, enters tasks-RCU exit, notifies parents/reparents children, releases policies and cached futex state, checks locks and stack use, runs RCU exit, frees lockdep task state, and ends in `do_task_dead()`. `make_task_dead()` repairs unsafe oops context enough to call `do_exit()` or parks recursive faults as dead.

Wait control flow: `do_wait()` installs a waitqueue entry, repeatedly calls `__do_wait()`, and sleeps unless a child event or signal interrupts it. `__do_wait()` validates PID filters, scans direct children and ptraced children unless optimized by `PIDTYPE_PID`, and delegates to `wait_consider_task()`. Zombie waits atomically claim `EXIT_ZOMBIE` to `EXIT_DEAD` or `EXIT_TRACE`, aggregate resource usage into the parent, fill wait status/info, and release tasks when appropriate. Stopped and continued waits consume signal state under `sighand->siglock` and honor `WNOWAIT`.

State and persistence: persistent kernel state includes task `exit_state`, `exit_code`, `signal_struct` group-exit flags and accounting accumulators, pid links, parent/real_parent relationships, child lists, ptrace lists, mm owner, wait queues, and sysfs/sysctl oops counters. State is in memory only but is externally visible through wait syscalls, pidfds, proc, taskstats, connector events, audit, and tracepoints. The `oops_limit` sysctl and `oops_count` sysfs attribute provide runtime policy/visibility for repeated oopses.

Dependencies and integration points: exit ordering touches nearly every core subsystem: scheduler, signals, ptrace, perf/hw breakpoints, memory management, cgroups, namespaces, tty, audit, accounting, taskstats, futexes, io_uring, kcov/kmsan, user events, proc/pidfs, RCU/tasks RCU, lockdep, memcg owner migration, pid namespaces, and compatibility syscall handling. The local `exit.h` shares wait structures with other kernel code.

Risks: ordering is the main hazard. Perf and deferred unwinds must stop before `mm` teardown; parent notification must avoid losing zombies; reparenting must respect child subreapers and PID namespaces; group exit must coordinate coredumps and other exiting threads; wait paths must avoid double reaping with cmpxchg on `exit_state`; and recursive oops handling must not return to broken execution. Locking involves `tasklist_lock`, `sighand->siglock`, stats seqlocks, task locks, RCU, and waitqueue state.

Test signals: kernel selftests and LTP wait/exit coverage should verify exit status encoding, `waitid()` options, pidfd waits, `WNOWAIT`, `WNOHANG`, stopped/continued reporting, ptrace reparenting, clone child selection, child subreaper behavior, orphaned process-group SIGHUP/SIGCONT, coredump interactions, multithreaded `exit_group()`, and fatal oops policy. Runtime tracepoints (`sched_process_exit`, `sched_process_wait`) plus taskstats/proc connector events provide observability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/exit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/exit.h -->
# sources/distributed-fs/ceph-client/kernel/exit.h

Purpose: private header for the kernel exit/wait implementation. It defines the compact data structures used to communicate wait results and options between syscall wrappers and shared wait helpers.

Important APIs/types/functions: `struct waitid_info` carries pid, uid, status, and cause fields used to populate `siginfo`-style wait results. `struct wait_opts` carries the selected PID type and PID, wait flags, optional info/stat/rusage destinations, the waitqueue entry, and `notask_error` state. Function declarations expose `pid_child_should_wake()`, `__do_wait()`, and `kernel_waitid_prepare()` to code that needs the same wait mechanics.

Control flow: syscall entry points in `exit.c` fill `wait_opts` directly or via `kernel_waitid_prepare()`, then pass it into `do_wait()`/`__do_wait()`. The child waitqueue callback uses `pid_child_should_wake()` to decide if a child event matches the blocked waiter.

State and persistence: this header owns no state; it defines stack or caller-owned containers. `wait_opts.child_wait` is temporarily linked into `current->signal->wait_chldexit` while waiting.

Dependencies and integration points: depends on pid types, `struct pid`, `struct rusage`, wait queues, task structs, and wait option constants from UAPI. It is an internal bridge between syscall compatibility code and the core wait scanner.

Risks: fields in `wait_opts` have subtle ownership rules: `wo_pid` references must be released by callers, `wo_info` and `wo_rusage` may be NULL, and `notask_error` is both an error result and a scan-progress signal. Misinitializing flags or PID type changes visible wait semantics.

Test signals: compile coverage is broad through all wait syscalls. Behavioral tests should indirectly validate this header by exercising `wait4()`, `waitid()`, pidfd waits, option validation, and child wake filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/exit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/extable.c -->
# sources/distributed-fs/ceph-client/kernel/extable.c

Purpose: provides generic kernel exception-table lookup and kernel text-address classification. It also owns `text_mutex`, the global lock for delicate kernel text modification.

Important APIs/types/functions: `DEFINE_MUTEX(text_mutex)` protects dynamic text patching. `sort_main_extable()` sorts built-in exception table entries when build tooling did not pre-sort them. `search_kernel_exception_table()` searches the built-in `__ex_table`, and `search_exception_tables()` extends lookup to module and BPF exception tables. `core_kernel_text()`, `kernel_text_address()`, `__kernel_text_address()`, and `func_ptr_is_kernel_text()` classify addresses. On descriptor-based architectures, `dereference_function_descriptor()` and `dereference_kernel_function_descriptor()` translate function descriptors to code addresses.

Control flow: boot calls `sort_main_extable()` before exception lookups rely on sorted tables. Fault fixup paths call `search_exception_tables()` with an instruction address; lookup checks built-in entries, modules, then BPF. Address classification first checks core kernel text/init text, then under RCU-watching safeguards checks module text, ftrace trampolines, kprobe slots, and BPF text. If RCU is not watching, the code temporarily enters an NMI-style context tracking region.

State and persistence: exception table boundaries are linker-provided symbols. `main_extable_sort_needed` is init data cleared by build-time tools if sorting is unnecessary. `text_mutex` is global runtime state. There is no persistent storage; tables are static kernel/module/BPF metadata.

Dependencies and integration points: integrates with ELF/linker sections, module exception tables, BPF exception tables, ftrace, kprobes, architecture section helpers, context tracking, and function descriptor support. `text_mutex` is used by runtime patching facilities such as alternatives, ftrace, and kprobes.

Risks: exception tables must be sorted for binary search correctness. Address classification can run from fragile contexts such as stack dumps, warnings, idle transitions, or CPU hotplug, so RCU/context tracking handling must not sleep. Function descriptor dereferencing uses nofault access because descriptors may not be directly safe to read.

Test signals: boot logs should not show repeated or failed exception-table sorting. Fault-injection and uaccess fixup tests exercise exception table lookup. Kprobe/ftrace/module/BPF stack unwinding and symbolization paths exercise `kernel_text_address()`. Descriptor architectures need coverage for function pointer classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/extable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/fail_function.c -->
# sources/distributed-fs/ceph-client/kernel/fail_function.c

Purpose: implements function-based fault injection using kprobes and debugfs. Users can name injectable functions, configure return values, and use the common fault-injection policy knobs to probabilistically force those functions to return early.

Important APIs/types/functions: `struct fei_attr` stores a list node, kprobe, and forced return value for one symbol. `adjust_error_retval()` clamps defaults and user-provided values to the target function's injectable error type. `fei_write()` is the debugfs control parser for adding, removing, or clearing injection points. `fei_kprobe_handler()` performs the injection by setting the return value and calling `override_function_with_return()`. `fei_retval_get()`/`fei_retval_set()` back per-symbol `retval` files, and `fei_debugfs_init()` creates the `fail_function` debugfs hierarchy.

Control flow: late init creates a debugfs directory through `fault_create_debugfs_attr()`, adds an `injectable` symlink to the global error injection list, and creates the writable `inject` file. Writing a symbol resolves it with `kallsyms_lookup_name()`, verifies it is in the injectable list, rejects duplicates, allocates a `fei_attr`, registers a kprobe with a pre-handler and dummy post-handler, creates a per-symbol debugfs directory, and links it into `fei_attr_list`. Writing `!symbol` removes one probe; writing only whitespace removes all probes. On a probed call, `should_fail()` decides whether to override the function return.

State and persistence: runtime state is `fei_attr_list`, guarded by `fei_lock`, plus registered kprobes and debugfs dentries. `fei_fault_attr` stores common fault-injection policy such as probability and interval. State is configured through debugfs and is not persistent across reboot or module lifetime.

Dependencies and integration points: depends on kprobes, kallsyms, error-injection metadata, fault-inject debugfs helpers, `regs_set_return_value()`, and architecture support for `override_function_with_return()`. The dummy post handler prevents kprobe jump optimization because optimized paths cannot safely support execution override.

Risks: only functions annotated as injectable should be accepted; bypassing `within_error_injection_list()` would let users override unsafe functions. Return values must match the function's error type (`NULL`, `ERRNO`, `ERRNO_NULL`, or boolean true), or callers may misinterpret results. Debugfs callbacks can race with removal, so getters/setters validate that their `fei_attr` is still on the list under `fei_lock`. Kprobe registration can fail for unavailable or blacklisted symbols.

Test signals: debugfs tests should add an injectable symbol, set valid and invalid return values, trigger configured failures, remove single and all probes, and verify duplicate/unknown/non-injectable symbols return `-EBUSY`, `-EINVAL`, or `-ERANGE` as appropriate. Kprobe selftests and fault-injection tests provide broader integration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/fail_function.c -->
