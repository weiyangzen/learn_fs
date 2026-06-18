# subset-b-000856 Research

Grouped source-tree-aligned research for the requested UML/SKAS and x86 build files.


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/ptrace.c -->

# sources/distributed-fs/ceph-client/arch/um/kernel/ptrace.c

## Purpose
Implements UML's architecture ptrace hooks and syscall tracing bridge. It translates generic ptrace requests into UML register accessors, controls user single-step state, and emits audit/tracepoint/ptrace syscall entry and exit events around UML syscall dispatch.

## Important APIs, Types, and Functions
`user_enable_single_step()`, `user_disable_single_step()`, and `ptrace_disable()` manipulate `TIF_SINGLESTEP` plus optional subarchitecture hooks. `arch_ptrace()` handles `PTRACE_PEEKUSR`, `PTRACE_POKEUSR`, register get/set, TLS thread-area requests, and delegates unknown operations to generic and subarch ptrace handlers. `syscall_trace_enter()` and `syscall_trace_leave()` integrate audit, tracepoints, ptrace syscall stops, and synthetic SIGTRAP delivery for single stepping.

## Control Flow, State, and Persistence
State is per-task thread flags and ptrace state; no persistent storage is used. Syscall entry records audit data, emits tracepoints when enabled, and can stop for ptrace. Syscall exit audits, injects single-step traps, emits exit tracepoints, and sets `TIF_SIGPENDING` when a ptraced task needs signal processing.

## Dependencies and Integration Points
Depends on UML register helpers (`getreg`, `putreg`, `peek_user`, `poke_user`), generic ptrace/audit/tracepoint infrastructure, and subarch TLS/ptrace hooks. It is called from `arch/um/kernel/skas/syscall.c` during syscall handling and from generic kernel ptrace paths.

## Risks and Test Signals
Risk centers on register offset validation and ptrace semantics matching x86 expectations. Test with `strace`, `gdb`, syscall tracepoints, single-step debugging, TLS ptrace requests, and audit records; failures typically show as wrong syscall stops, missed SIGTRAPs, or corrupted register state.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/ptrace.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/reboot.c -->

# sources/distributed-fs/ceph-client/arch/um/kernel/reboot.c

## Purpose
Provides UML machine restart, halt, poweroff, and cleanup behavior. It terminates userspace address-space helper processes, runs UML exit hooks, and routes restart/poweroff into SKAS longjmp exits.

## Important APIs, Types, and Functions
Exports `pm_power_off`. `uml_cleanup()` disables normal allocation, runs `do_uml_exitcalls()`, and kills all process-backed UML address spaces. `machine_restart()`, `machine_power_off()`, and `machine_halt()` are the architecture machine control hooks. `register_power_off()` installs a generic `sys_off` poweroff handler.

## Control Flow, State, and Persistence
`kill_off_processes()` walks the task list under `tasklist_lock`, finds tasks with an mm, extracts the host pid from `mm->context.id.pid`, and kills/reaps the ptraced process. No data persists after shutdown; the goal is process and host resource cleanup.

## Dependencies and Integration Points
Uses scheduler task iteration, `find_lock_task_mm()`, UML `os_kill_ptraced_process()`, SKAS `reboot_skas()`/`halt_skas()`, and sys-off registration. It is invoked by panic/exit/reboot paths and by `main.c` during host-process teardown.

## Risks and Test Signals
Risks are tasklist races, stale/invalid child pids, and exitcall ordering. Test reboot, halt, poweroff, panic, and failed boot exits; watch for leaked `uml-userspace` processes, unreaped children, and repeated poweroff callbacks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/reboot.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/sigio.c -->

# sources/distributed-fs/ceph-client/arch/um/kernel/sigio.c

## Purpose
Provides the kernel-side lock used by host SIGIO support. It exists to serialize access to host-side SIGIO/epoll state in `arch/um/os-Linux/sigio.c`.

## Important APIs, Types, and Functions
`sigio_lock()` and `sigio_unlock()` wrap a static `DEFINE_MUTEX(sigio_mutex)`. These functions are intentionally minimal and are exported through internal UML headers rather than as module symbols.

## Control Flow, State, and Persistence
The only state is the mutex. Host-side code enters this lock before adding/removing SIGIO file descriptors or starting the SIGIO workaround thread, preventing concurrent mutation of epoll data structures and helper-thread state.

## Dependencies and Integration Points
Depends on Linux mutexes and is consumed by `os-Linux/sigio.c`. It is part of the bridge between UML kernel IRQ code and host async I/O notification.

## Risks and Test Signals
Deadlocks or missing lock coverage would manifest as SIGIO workaround races, epoll control failures, or missed I/O interrupts. Test by exercising UML consoles/PTYs and async device FDs under concurrent open/close and shutdown.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/sigio.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/signal.c -->

# sources/distributed-fs/ceph-client/arch/um/kernel/signal.c

## Purpose
Implements UML signal delivery and signal-related IRQ tracing. It builds user signal frames, handles syscall restart rules, and keeps lockdep IRQ trace state aligned with UML signal blocking.

## Important APIs, Types, and Functions
`block_signals_trace()`, `unblock_signals_trace()`, `um_trace_signals_on()`, and `um_trace_signals_off()` wrap host signal masking with hardirq tracing. `handle_signal()` prepares signal frames using `setup_signal_stack_si()` or compat `setup_signal_stack_sc()`. `do_signal()` loops over `get_signal()`, handles syscall restart return codes, and restores saved masks when no signal is delivered.

## Control Flow, State, and Persistence
State is per-thread signal masks, ptrace single-step state, saved sigmask, and pt_regs syscall fields. On signal delivery it may rewrite syscall return/original-number fields to restart or convert interrupted syscalls to `-EINTR`. No persistent storage is used.

## Dependencies and Integration Points
Integrates generic signal core, UML frame setup, ptrace flags, syscall register macros, and host signal block/unblock functions from `os-Linux/signal.c`. It is reached from trap/fatal paths and the SKAS userspace loop.

## Risks and Test Signals
Risks include wrong syscall restart semantics, bad alternate-stack selection, and mismatched hardirq trace state. Test POSIX signal handlers, `SA_RESTART`, ptraced single-step signal delivery, altstack, and lockdep IRQ tracing under signal-heavy workloads.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/signal.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/skas/Makefile -->

# sources/distributed-fs/ceph-client/arch/um/kernel/skas/Makefile

## Purpose
Builds the UML SKAS kernel-side objects and the embedded stub executable used for user address-space helper processes.

## Important APIs, Types, and Functions
Defines `obj-y` for `stub.o`, `mmu.o`, `process.o`, `syscall.o`, `uaccess.o`, and `stub_exe_embed.o`. Builds `stub_exe.dbg` with a custom `STUB_EXE` link command, strips it into `stub_exe`, then embeds it through `stub_exe_embed.S`.

## Control Flow, State, and Persistence
The build flow compiles `stub_exe.o`, links a static no-stdlib executable with `STUB_EXE_LDFLAGS = -Wl,-n -static`, strips it, and treats the result as an object dependency for embedding. No runtime state is present.

## Dependencies and Integration Points
Includes `arch/um/scripts/Makefile.rules`, disables profiling/hardening for stub objects, disables KCOV, and filters profiling/gcov flags from the stub executable. It feeds `os-Linux/skas/process.c`, which writes the embedded executable into a memfd or temp file at boot.

## Risks and Test Signals
Risks are accidental instrumentation, hardening flags requiring unavailable registers, or stub binary rebuild dependency breakage. Test by clean-building UML with gcc/clang, profiling/gcov/KCOV configs, and verifying `stub_exe_start`/`stub_exe_end` produce a runnable stub.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/skas/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/skas/mmu.c -->

# sources/distributed-fs/ceph-client/arch/um/kernel/skas/mmu.c

## Purpose
Creates, tracks, and destroys UML SKAS memory contexts. Each Linux `mm_struct` receives a host userspace helper process plus shared stub-data pages used for register and memory-management coordination.

## Important APIs, Types, and Functions
`__get_turnstile()`, `enter_turnstile()`, and `exit_turnstile()` serialize operations on a memory context. `init_new_context()` allocates stub data pages, links the mm into `mm_list`, starts the host userspace process, and clears unwanted mappings. `destroy_context()` kills the host child, closes seccomp sockets, and frees pages. `mm_sigchld_irq()` reaps unexpected child exits and marks affected contexts dead.

## Control Flow, State, and Persistence
Persistent runtime state lives in `mm->context`: turnstile mutex, TLB sync lock, `mm_id` pid/socket/stack, and list linkage. A global `mm_list` protected by `mm_list_lock` lets SIGCHLD handling map dead host pids back to mm contexts.

## Dependencies and Integration Points
Depends on SKAS process startup, `map()`/`unmap()` syscall stubs, SIGCHLD IRQ, `stub_data`, futex waking, and host process kill/close helpers. It is the central lifecycle owner for user address-space backing processes.

## Risks and Test Signals
Risks include leaking child processes, dead contexts causing later faults, and turnstile deadlocks. Test fork/exec/exit storms, seccomp child crashes, OOM during context creation, and SMP page-fault/mmap concurrency.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/skas/mmu.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/skas/process.c -->

# sources/distributed-fs/ceph-client/arch/um/kernel/skas/process.c

## Purpose
Starts the UML kernel on the initial SKAS thread, manages idle-thread longjmp setup, exposes current mm helpers, and synchronizes current TLB state before entering host userspace.

## Important APIs, Types, and Functions
`start_uml()` installs the boot CPU signal stack, initializes signal handlers, and starts the idle thread. `start_kernel_proc()` blocks signals and calls `start_kernel()`. `current_stub_stack()`, `current_mm_id()`, and `current_mm_sync()` expose active memory-context state. `initial_jmpbuf_lock()` and `initial_jmpbuf_unlock()` serialize jumps through the initial thread buffer.

## Control Flow, State, and Persistence
State includes per-CPU IRQ stacks and a spinlock around the initial jump buffer. Boot control transitions from host `linux_main()` into `start_idle_thread()`, then into `start_kernel()`. Current-mm helpers are read-only except `current_mm_sync()`, which flushes pending TLB updates.

## Dependencies and Integration Points
Integrates with host SKAS thread switching in `os-Linux/skas/process.c`, TLB sync in `kernel/tlb.c`, signal-stack setup in `os-Linux/signal.c`, and generic kernel boot.

## Risks and Test Signals
Risks are signal delivery on wrong stacks, unsynchronized initial jump-buffer use, and missing TLB sync before userspace. Test boot, reboot, panic paths, nested callbacks from initial thread, and page-table changes before userspace resumes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/skas/process.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/skas/stub.c -->

# sources/distributed-fs/ceph-client/arch/um/kernel/skas/stub.c

## Purpose
Implements code that is mapped into each UML userspace helper process. It executes queued mmap/munmap operations and, in seccomp mode, handles SIGSYS/SIGALRM/fault signals cooperatively with the UML kernel through shared `stub_data` and futexes.

## Important APIs, Types, and Functions
`syscall_handler()` executes `STUB_SYSCALL_MMAP` and `STUB_SYSCALL_MUNMAP` requests, optionally translating compact FD indexes. `stub_syscall_handler()` runs queued syscalls and traps back to the kernel in ptrace mode. `stub_signal_interrupt()` records signal/mcontext offsets, wakes the kernel, waits for futex handoff, receives FDs, flushes syscalls, and restores architecture state. `stub_signal_restorer()` performs raw `rt_sigreturn`.

## Control Flow, State, and Persistence
State is shared in `struct stub_data`: signal number, siginfo/mcontext offsets, futex state, syscall queue, errors, FD map, restart flag, and arch scratch data. The seccomp path alternates FUTEX_IN_CHILD/FUTEX_IN_KERN ownership until the host updates register/mapping state.

## Dependencies and Integration Points
Built into the `.__syscall_stub` section and mapped by `stub_exe.c`. It relies on raw syscall wrappers, seccomp-filter allowances, `stub-data.h`, and host coordination in `os-Linux/skas/process.c` and `os-Linux/skas/mem.c`.

## Risks and Test Signals
The file explicitly documents security limitations: userspace reaching stub code may access physical memory or interfere with scheduling. Test seccomp and ptrace modes, mmap/munmap batching, FD passing, signal delivery, malicious user IP attempts, and futex wake/wait races.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/skas/stub.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/skas/stub_exe.c -->

# sources/distributed-fs/ceph-client/arch/um/kernel/skas/stub_exe.c

## Purpose
Defines the tiny executable image launched as `uml-userspace`. It maps the syscall stub code/data at fixed guest addresses, installs signal handling, optionally installs a seccomp filter, and then stops/traps for kernel control.

## Important APIs, Types, and Functions
`real_init()` reads `stub_init_data` from stdin, maps stub code and data with fixed shared mappings, sets alternate signal stack, registers SIGSEGV or seccomp signal handlers, installs seccomp BPF when requested, or uses `PTRACE_TRACEME` plus SIGSTOP in ptrace mode. `_start()` adjusts the startup stack through `stub_start(real_init)`.

## Control Flow, State, and Persistence
The executable starts with raw syscalls only. It inherits a socket/stdin for init data and, in seccomp mode, retains FD 0 for FD passing. It persists as the long-lived host process backing a UML mm context.

## Dependencies and Integration Points
Uses generated asm offsets, raw syscall helpers, `stub-data.h`, `sysdep/stub.h`, seccomp BPF constants, and fixed layout constants such as `STUB_START`. It is linked by the SKAS Makefile and embedded by `stub_exe_embed.S`.

## Risks and Test Signals
Risks are wrong fixed mappings, unsupported syscalls in the BPF allowlist, close-range incompatibility, bad signal-restorer setup, and insecure seccomp policy. Test stub startup in ptrace/seccomp modes, old kernels/libcs, i386/x86_64, noexec tempdir fallback, and signal fault paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/skas/stub_exe.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/skas/stub_exe_embed.S -->

# sources/distributed-fs/ceph-client/arch/um/kernel/skas/stub_exe_embed.S

## Purpose
Embeds the built `arch/um/kernel/skas/stub_exe` binary into UML kernel init data so runtime code can materialize it without relying on an external file.

## Important APIs, Types, and Functions
Defines global data symbols `stub_exe_start` and `stub_exe_end` around an `.incbin` of the stripped stub executable. Uses `SYM_DATA_START`, `SYM_DATA_END_LABEL`, `__INITDATA`, and `__FINIT`.

## Control Flow, State, and Persistence
No executable control flow exists here. The embedded byte range is init data consumed by `init_stub_exe_fd()` in `os-Linux/skas/process.c`, which writes it to a memfd or temporary executable file.

## Dependencies and Integration Points
Depends on the SKAS Makefile rule that builds `stub_exe` before this object. Integrates with linker sections and the runtime stub executable loader.

## Risks and Test Signals
Risks are missing rebuild dependencies, wrong symbol visibility, or section placement causing the embedded bytes to be discarded too early. Test clean incremental builds and runtime `uml-userspace` startup from the embedded range.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/skas/stub_exe_embed.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/skas/syscall.c -->

# sources/distributed-fs/ceph-client/arch/um/kernel/skas/syscall.c

## Purpose
Dispatches syscalls trapped from UML userspace into the kernel syscall table while integrating ptrace, audit, seccomp, and time-travel scheduling behavior.

## Important APIs, Types, and Functions
`handle_syscall()` copies the syscall number from UML pt_regs, initializes `-ENOSYS`, calls `syscall_trace_enter()`, runs `secure_computing()`, invokes `sys_call_table[syscall]` with up to six arguments, stores the return value, and calls `syscall_trace_leave()`.

## Control Flow, State, and Persistence
The function mutates only the current pt_regs and time-travel accounting. In infinite/external time travel, `sched_yield` and error-returning syscalls advance `tt_extra_sched_jiffies` or sleep briefly to avoid pathological busy loops that would starve simulated time.

## Dependencies and Integration Points
Called from the SKAS userspace loop on SIGSYS or ptrace syscall stops. Depends on syscall trace hooks, Linux seccomp, UML syscall/register macros, delay helpers, and the architecture syscall table.

## Risks and Test Signals
Risks include wrong syscall number/argument extraction, seccomp ordering mismatches, and time-travel livelocks. Test normal syscalls, invalid syscall numbers, ptrace syscall tracing, seccomp denial, ASAN spinlocks, and time-travel external simulations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/skas/syscall.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/skas/uaccess.c -->

# sources/distributed-fs/ceph-client/arch/um/kernel/skas/uaccess.c

## Purpose
Implements UML SKAS user-memory access primitives and futex atomics by walking guest page tables, faulting pages in as needed, and temporarily mapping the backing host page into kernel address space.

## Important APIs, Types, and Functions
`virt_to_pte()` resolves a user virtual address to a PTE. `maybe_map()` invokes `handle_page_fault()` if the PTE is absent or not writable. `buffer_op()` runs page-split operations. Exports `raw_copy_from_user()`, `raw_copy_to_user()`, `strncpy_from_user()`, `__clear_user()`, `strnlen_user()`, `arch_futex_atomic_op_inuser()`, and `futex_atomic_cmpxchg_inatomic()`.

## Control Flow, State, and Persistence
State is transient: current mm page tables, highmem mappings on 32-bit, preemption/pagefault-disable windows, and returned remaining-byte counts. Faults may update page tables and TLB sync state through the normal page-fault path.

## Dependencies and Integration Points
Depends on `handle_page_fault()` from `trap.c`, page-table helpers, highmem APIs, futex operation definitions, and exported uaccess ABI expected by generic kernel code.

## Risks and Test Signals
Risks include partial-copy accounting, missing access checks, highmem kmap misuse, non-atomic futex behavior under contention, and pagefault-disabled interactions. Test copy_to/from_user boundary crossings, unmapped userspace pointers, futex operations, 32-bit highmem, and fault injection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/skas/uaccess.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/smp.c -->

# sources/distributed-fs/ceph-client/arch/um/kernel/smp.c

## Purpose
Provides UML's kernel-side SMP support: virtual CPU startup, IPI delivery semantics, CPU possible map setup, and cross-CPU call/reschedule operations.

## Important APIs, Types, and Functions
`arch_smp_send_reschedule()`, `arch_send_call_function_single_ipi()`, `arch_send_call_function_ipi_mask()`, and `smp_send_stop()` issue host IPIs. `ipi_handler()` maps UML IPI vectors to scheduler, call-function, and stop handling. `uml_start_secondary()`, `smp_prepare_cpus()`, and `__cpu_up()` coordinate AP boot. `prefill_possible_map()` and `uml_ncpus_setup()` configure CPU counts.

## Control Flow, State, and Persistence
Persistent state includes `uml_ncpus`, `cpu_states[]`, and `cpu_tasks[]`. AP threads wait on a futex until `__cpu_up()` publishes the idle task and marks the CPU runnable, then install stacks/timers and enter idle.

## Dependencies and Integration Points
Pairs with host pthread/signal IPI code in `os-Linux/smp.c`, timer setup in `time.c`, signal stacks, generic SMP call-function code, and scheduler CPU hotplug startup.

## Risks and Test Signals
Risks are AP boot races, missed IPIs, invalid stop behavior, and lack of ptrace-userspace SMP support unless seccomp is used. Test `ncpus=`, SMP boot, call_function stress, scheduler reschedules, CPU stop, and time-travel/SMP interactions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/smp.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/stacktrace.c -->

# sources/distributed-fs/ceph-client/arch/um/kernel/stacktrace.c

## Purpose
Implements stack walking and reliable stack trace capture for UML tasks.

## Important APIs, Types, and Functions
`dump_trace()` scans from the current stack pointer to the thread-stack end, recognizes kernel text addresses, and marks entries reliable when they align with the frame pointer chain. `save_stack_trace()` and `save_stack_trace_tsk()` collect reliable entries through `dump_ops` and export GPL symbols.

## Control Flow, State, and Persistence
The walker uses transient stack contents, optional `tsk->thread.segv_regs`, and frame-pointer state. It stores addresses only in the caller-provided `struct stack_trace`; no global state persists.

## Dependencies and Integration Points
Uses UML stack pointer/frame pointer helpers in `asm/stacktrace.h`, `__kernel_text_address()`, and generic stacktrace APIs. `sysrq.c` uses `dump_trace()` for printable call traces.

## Risks and Test Signals
Risks include unreliable traces when frame pointers are absent/corrupt and reading stale stack slots during faults. Test sysrq stack dumps, WARN/OOPS traces, KASAN/fault paths, and stack traces for non-current tasks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/stacktrace.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/sysrq.c -->

# sources/distributed-fs/ceph-client/arch/um/kernel/sysrq.c

## Purpose
Provides UML's `show_stack()` implementation for sysrq, oops, and scheduler debugging paths.

## Important APIs, Types, and Functions
`show_stack()` prints a short raw stack window and then emits a call trace using `dump_trace()`. `_print_addr()` formats each address with symbol resolution and reliability marker. `stackops` wires the callback into the stacktrace walker.

## Control Flow, State, and Persistence
No persistent state. The function uses the supplied stack pointer or derives one from task/segv register state, prints up to three stack lines, then delegates symbolic trace printing.

## Dependencies and Integration Points
Depends on `stacktrace.c`, `kallsyms`, task stack helpers, and current thread fault register tracking. Called by generic debug paths and panic/oops reporting.

## Risks and Test Signals
Risks are bad stack pointer selection after nested faults and misleading unreliable markers. Test SysRq task dumps, kernel oops, fatal SIGSEGV, and non-current task stack printing.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/sysrq.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/time.c -->

# sources/distributed-fs/ceph-client/arch/um/kernel/time.c

## Purpose
Implements UML clocksource, clockevent, timer IRQ handling, persistent clock, and optional time-travel simulation modes. It supports normal host POSIX timers, basic time skipping, infinite CPU simulation, and externally coordinated simulated time.

## Important APIs, Types, and Functions
Exports `time_travel_mode`, `time_travel_ndelay()`, `time_travel_add_irq_event()`, `__time_travel_wait_readable()`, and `__time_travel_propagate_time()`. Key internals include `time_travel_ext_req()`, `time_travel_handle_message()`, event-list management, `timer_handler()`, `itimer_*` clockevent callbacks, `timer_read()`, `um_setup_timer()`, `time_init()`, and boot options `time-travel`/`time-travel-start=`.

## Control Flow, State, and Persistence
Time-travel state persists in globals: current simulated ns, start time, event lists, IRQ-delivery list, external scheduler fd, shared-memory scheduler pointers, sequence numbers, pending broadcasts, and timer interval/next event. Clock events schedule either host timers or simulated events; simulated reads may advance time and deliver pending events. External mode exchanges request/wait/update/get/broadcast messages and may share current/free-until time through mapped scheduler shared memory.

## Dependencies and Integration Points
Integrates Linux clockevents/clocksource, IRQ `TIMER_IRQ`, host timer wrappers in `os-Linux/time.c`, signal delivery through `deliver_alarm()`, time-travel-aware virtio/IRQ code, sysfs broadcast control, and suspend idle sleep.

## Risks and Test Signals
Risks include backwards time panics, external protocol sequence mismatches, event-list recursion, IRQ delivery while disabled, and starvation in infinite CPU mode. Test all time-travel modes, external scheduler disconnects, periodic/oneshot timers, idle sleep, broadcast sysfs, suspend, and workloads that poll time in loops.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/time.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/tlb.c -->

# sources/distributed-fs/ceph-client/arch/um/kernel/tlb.c

## Purpose
Synchronizes UML page-table changes into host mappings. UML marks PTE/PMD/PUD/P4D/PGD ranges as needing sync, then this file maps/unmaps the matching host virtual ranges for kernel or user mm contexts.

## Important APIs, Types, and Functions
`struct vm_ops` abstracts kernel direct map operations versus user SKAS stub operations. `update_pte_range()` computes `UM_PROT_*` from PTE read/write/exec/young/dirty bits and calls `mmap` or `unmap`. Higher-level `update_*_range()` functions walk page-table levels. `um_tlb_sync()`, `flush_tlb_all()`, and `flush_tlb_mm()` are the public hooks. `report_enomem()` gives host-side memory diagnostics.

## Control Flow, State, and Persistence
Persistent sync state lives in `mm->context.sync_tlb_range_from/to` and page-table needsync bits. `um_tlb_sync()` holds `page_table_lock` and `sync_tlb_lock`, walks the marked range, clears needsync bits, and resets the range even on errors.

## Dependencies and Integration Points
Uses host `os_map_memory()`/`os_unmap_memory()` for `init_mm` and SKAS `map()`/`unmap()` queued syscalls for user mm contexts. Fault handling in `trap.c` can trigger kernel TLB sync for vmalloc faults.

## Risks and Test Signals
Risks include lost sync ranges, wrong dirty/young permission emulation, ENOMEM from host map limits, and batching errors. Test mmap/munmap/mprotect, vmalloc faults, fork/exec, host `vm.max_map_count` exhaustion, and TLB flush stress.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/tlb.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/trap.c -->

# sources/distributed-fs/ceph-client/arch/um/kernel/trap.c

## Purpose
Handles page faults and host-delivered trap signals for UML. It adapts Linux VM fault handling to UML's lack of exception tables and maps host SIGSEGV/SIGBUS/SIGILL/SIGFPE/SIGTRAP/SIGWINCH into guest faults, signals, or IRQs.

## Important APIs, Types, and Functions
`handle_page_fault()` locates/extends VMAs, calls `handle_mm_fault()`, and reports constrained error codes. `segv_handler()` and `segv()` decide whether to resolve a fault, sync kernel TLBs, recover pagefault-disabled regions, panic, or deliver SIGSEGV/SIGBUS. `fatal_sigsegv()` forces fatal SIGSEGV and core dump. `relay_signal()` sanitizes signal forwarding. `winch()` raises `WINCH_IRQ`.

## Control Flow, State, and Persistence
Fault state is stored transiently in `current->thread.arch.faultinfo`, `current->thread.segv_regs`, and optional recovery target `segv_continue`. Kernel faults in vmalloc range first try `um_tlb_sync(&init_mm)`; user faults take mmap locks carefully and may expand grow-down stacks.

## Dependencies and Integration Points
Depends on Linux mm fault core, UML faultinfo macros, TLB sync, signal core, arch fixup hooks, and host signal dispatch in `os-Linux/signal.c`/SKAS process loop.

## Risks and Test Signals
Risks include deadlocks on mmap locks after kernel bugs, wrong user/kernel fault classification, missing pagefault-disabled recovery, and unsafe signal relay layouts. Test user page faults, stack expansion, vmalloc faults, copy_from_user faults, SIGBUS from full `/dev/shm`, and fatal kernel faults.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/trap.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/um_arch.c -->

# sources/distributed-fs/ceph-client/arch/um/kernel/um_arch.c

## Purpose
Owns UML architecture boot setup: command-line normalization, host CPU/capability reporting, memory layout calculation, panic behavior, architecture setup, text-patching stubs, and suspend integration.

## Important APIs, Types, and Functions
`linux_main()` parses UML setup options, adds default `root=`/`console=`, computes `stub_start`, `task_size`, physical/vmalloc layout, reads host CPU features, and enters `start_uml()`. `setup_arch()` initializes physical memory, DTB/initrd, command line, host info, CPU map, and RNG seed. `uml_finishsetup()` registers panic notifier and postsetup calls. `cpuinfo_op` backs `/proc/cpuinfo`. PM hooks implement suspend-to-mem through UML idle sleep.

## Control Flow, State, and Persistence
Boot-time globals include `command_line`, `host_info`, `uml_physmem`, `uml_reserved`, `physmem_size`, `start_vm`, `end_vm`, `stub_start`, `task_size`, and `brk_start`. These are initialized before SMP and remain effectively stable. Panic exits dump kmsg and core.

## Dependencies and Integration Points
Integrates with host early checks, physical memory setup, initrd/DTB hooks, CPU feature parsing from `start_up.c`, signal wake support, suspend core, and x86 text-patching call sites that UML mostly stubs out.

## Risks and Test Signals
Risks are address-layout miscalculation, command-line overflow, insufficient vmalloc/physmem space, host CPU flag parsing drift, and suspend wake behavior in time-travel mode. Test varied argv/envp sizes, `mem=`, default root/console, `/proc/cpuinfo`, panic, suspend, and ASLR-disabled reexec.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/um_arch.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/um_arch.h -->

# sources/distributed-fs/ceph-client/arch/um/kernel/um_arch.h

## Purpose
Declares UML architecture boot helpers shared by `um_arch.c` and optional platform code.

## Important APIs, Types, and Functions
Declares `uml_load_file()`, `uml_dtb_init()` when `CONFIG_OF` is enabled, a no-op inline `uml_dtb_init()` otherwise, and weak/overridable `read_initrd()`.

## Control Flow, State, and Persistence
No state or control flow beyond the conditional inline. It defines compile-time linkage for optional DTB and initrd loading.

## Dependencies and Integration Points
Included by `um_arch.c`; optional implementations are expected elsewhere under UML architecture code when OF/initrd support is enabled.

## Risks and Test Signals
Risk is mostly configuration drift: missing optional implementations or wrong prototypes break boot-time initrd/DTB support. Test builds with and without `CONFIG_OF` and with initrd-enabled configs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/um_arch.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/umid.c -->

# sources/distributed-fs/ceph-client/arch/um/kernel/umid.c

## Purpose
Handles the kernel-facing `umid=` setup parameter, which assigns a unique UML instance identity used by host-side pid and management files.

## Important APIs, Types, and Functions
`set_umid_arg()` parses `umid=`, suppresses passing it to the generic kernel command line, calls host-side `set_umid()`, warns on duplicate initialization or existing use, and records successful initialization. `__uml_setup("umid=", ...)` registers help text.

## Control Flow, State, and Persistence
The only state is `umid_inited`, preventing multiple `umid=` applications. The actual persistent directory/pid file lifecycle is implemented in `os-Linux/umid.c`.

## Dependencies and Integration Points
Depends on setup parameter scanning in `um_arch.c` and host functions `set_umid()`/warnings from `os-Linux/umid.c` and `os-Linux/util.c`.

## Risks and Test Signals
Risks are duplicate or too-long IDs, failure to suppress host-only options, and collision handling. Test explicit `umid=`, duplicate args, concurrent UML instances with same ID, and fallback random IDs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/umid.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/uml.lds.S -->

# sources/distributed-fs/ceph-client/arch/um/kernel/uml.lds.S

## Purpose
Static UML linker script defining executable layout, section order, symbols, and discard/debug handling.

## Important APIs, Types, and Functions
Sets ELF output format/architecture and entry `_start`, aliases `jiffies = jiffies_64`, hides symbols by default with a version script, defines `__binary_start`, `_text`, `_stext`, `__syscall_stub_start/end`, `__init_begin/end`, data/bss boundaries, and standard debug/modinfo/discard sections.

## Control Flow, State, and Persistence
No runtime flow; layout decisions persist in the linked kernel image. The `.syscall_stub` section is page-aligned after `.text` so stub code can be mapped/copied precisely.

## Dependencies and Integration Points
Includes kernel linker fragments such as `asm/common.lds.S`, relies on `START`, `PAGE_SIZE`, `ELF_FORMAT`, and UML section macros. Consumed by `vmlinux.lds.S` for static links.

## Risks and Test Signals
Risks include wrong stub section bounds, glibc relocation symbol omissions, discarded init/runtime sections, or symbol visibility surprises. Test static UML links, boot, syscall stub mapping, kallsyms, and module/debug section generation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/uml.lds.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/vmlinux.lds.S -->

# sources/distributed-fs/ceph-client/arch/um/kernel/vmlinux.lds.S

## Purpose
Selects the UML top-level linker script variant and defines kernel stack size for the link.

## Important APIs, Types, and Functions
Defines `RUNTIME_DISCARD_EXIT` and `KERNEL_STACK_SIZE = 4096 * (1 << CONFIG_KERNEL_STACK_ORDER)`. Includes `uml.lds.S` when `CONFIG_LD_SCRIPT_STATIC` is set, otherwise includes `dyn.lds.S`.

## Control Flow, State, and Persistence
No runtime control flow. Its output affects the final vmlinux layout and stack-size-dependent linker symbols.

## Dependencies and Integration Points
Integrated by Kbuild as the architecture linker script. It selects between static and dynamic UML link layouts.

## Risks and Test Signals
Risks are stack-size mismatch and wrong static/dynamic script selection. Test static and dynamic UML builds with different `CONFIG_KERNEL_STACK_ORDER` values.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/vmlinux.lds.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/Makefile -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/Makefile

## Purpose
Builds the host-Linux userspace support layer for UML.

## Important APIs, Types, and Functions
Lists core objects: ELF aux scanning, exec/path helpers, file/process/memory/IRQ/signal/time/TTY/UMID utilities, SKAS support, and optional SMP support. Disables KCOV instrumentation, adjusts frame-size warnings, and sets `USER_OBJS` for files compiled with user C flags.

## Control Flow, State, and Persistence
No runtime control flow. Build state controls which objects are compiled as user-side objects and how instrumentation is suppressed.

## Dependencies and Integration Points
Includes `arch/um/scripts/Makefile.rules`, pulls `skas/`, and conditionally builds `smp.o` for `CONFIG_SMP`. This layer is called by kernel-side UML code through `os.h` and related headers.

## Risks and Test Signals
Risks are accidentally instrumenting user-side code, omitting an object from `USER_OBJS`, or frame-size regressions in signal/main. Test allnoconfig/defconfig/SMP builds and clang/gcc warning behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/elf_aux.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/elf_aux.c

## Purpose
Scans the host-provided ELF auxiliary vector early in UML startup to record platform and hardware capability information.

## Important APIs, Types, and Functions
Defines `elf_aux_platform` and `elf_aux_hwcap`. `scan_elf_aux()` skips past the environment vector, iterates `Elf32_auxv_t` or `Elf64_auxv_t`, and records `AT_HWCAP` and `AT_PLATFORM`.

## Control Flow, State, and Persistence
The globals are initialized very early and then treated as immutable boot facts. No allocation or persistent files are involved.

## Dependencies and Integration Points
Called from `os-Linux/main.c` before `linux_main()`. Uses host ELF ABI types and is exposed through `internal.h`.

## Risks and Test Signals
Risks are ABI differences in auxv layout and stale platform pointers if environment memory assumptions change. Test 32-bit/64-bit UML startup and feature consumers that read `elf_aux_hwcap/platform`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/elf_aux.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/execvp.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/execvp.c

## Purpose
Provides an allocation-controlled `execvp` implementation for UML helper processes.

## Important APIs, Types, and Functions
`execvp_noalloc()` searches `PATH` for a command unless the file contains `/`, using a caller-supplied buffer for path construction. It preserves glibc-like error priority for `EACCES` and ignores path-search misses such as `ENOENT`, `ESTALE`, `ENOTDIR`, `ENODEV`, `ETIMEDOUT`, and `ENOEXEC`.

## Control Flow, State, and Persistence
No persistent state. The function attempts `execv()` repeatedly and only returns negative errno on failure. A `TEST` block supplies a standalone test harness.

## Dependencies and Integration Points
Used by `helper.c` to exec host helper commands after clone without allocating in the child. Depends on environment `PATH` and a buffer sized by the caller, normally `PATH_MAX`.

## Risks and Test Signals
Risks are buffer sizing assumptions, PATH corner cases, and differing shell fallback semantics for `ENOEXEC`. Test empty file name, direct paths, empty PATH components, permission-denied binaries, and missing helpers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/execvp.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/file.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/file.c

## Purpose
Wraps host Linux file, socket, fd-passing, polling, fallocate, and shared-memory syscalls behind UML's `os_*` API with consistent negative-errno returns.

## Important APIs, Types, and Functions
Provides stat/access/open/close/read/write/pread/pwrite/sync/seek, file type/mode/size/modtime, FD flags and async SIGIO setup, Unix socket connect/create/shutdown/accept, `os_pipe()`, `os_rcv_fd_msg()`, `os_sendmsg_fds()`, device major/minor helpers, fallocate punch/zero, eventfd, `os_poll()`, and shared `mmap`/`mremap` helpers.

## Control Flow, State, and Persistence
No global state except host file descriptors managed by callers. Functions convert host errors to `-errno`; FD-passing uses ancillary `SCM_RIGHTS` data and fixed maximum receive/send counts.

## Dependencies and Integration Points
Heavily used by time-travel external sockets, SKAS FD passing, block/hostfs/console devices, temp memory files, and generic host wrappers. It bridges kernel code to libc/syscall behavior.

## Risks and Test Signals
Risks include partial I/O not retried, fd leaks on error, insufficient `MAX_RCV_FDS`, `os_poll()` fixed two-FD limit, async signal ownership issues, and shared-memory remap failures. Test fd passing, time-travel shared memory, host file-backed block devices, SIGIO setup, and fallocate support.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/file.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/helper.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/helper.c

## Purpose
Runs external helper programs and helper threads while respecting UML allocation/signal constraints.

## Important APIs, Types, and Functions
`run_helper()` clones a child with a small allocated stack, optionally runs a pre-exec callback, calls `execvp_noalloc()`, and reports exec errno through a close-on-exec socketpair. `run_helper_thread()` runs a clone child with optional stack ownership. `helper_wait()` validates exit status. `os_run_helper_thread()`/`os_kill_helper_thread()` manage pthread helpers. `os_fix_helper_thread_signals()` masks UML signals in helper threads.

## Control Flow, State, and Persistence
State is transient per helper: allocated stack, socketpair, PID or pthread handle, and a PATH buffer. Pthread helper descriptors persist until killed/joined.

## Dependencies and Integration Points
Used by SIGIO workaround threads, host command helpers, and callbacks that need execution on the initial thread. Depends on `alloc_stack()`, `execvp_noalloc()`, signal masking, pthreads, clone, and `um_malloc`.

## Risks and Test Signals
Risks are stack leaks, exec errno races, helper thread signal handling, and using `CLONE_VM` in the wrong API. Test successful/missing helpers, pre-exec callbacks, cancellation cleanup, signal storms, and atomic allocation contexts.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/helper.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/internal.h -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/internal.h

## Purpose
Collects private declarations shared inside the host-Linux UML support layer.

## Important APIs, Types, and Functions
Declares `scan_elf_aux()`, `check_tmpexec()`, thread-local `signals_enabled`, `timer_alarm_pending()`, SKAS wait helpers, and defines `IPI_SIGNAL` as `SIGRTMIN`.

## Control Flow, State, and Persistence
No control flow. The header exposes shared state contracts, especially signal-enabled state and timer pending checks.

## Dependencies and Integration Points
Included by `main.c`, `signal.c`, `time.c`, `start_up.c`, and SKAS/SMP host files. It joins otherwise separate host-side modules without exporting them as public UML APIs.

## Risks and Test Signals
Risks are declaration drift and incompatible realtime-signal choices. Test SMP builds, seccomp builds, and host signal/timer idle paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/internal.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/irq.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/irq.c

## Purpose
Implements host epoll wrappers used by UML IRQ file-descriptor polling.

## Important APIs, Types, and Functions
`os_setup_epoll()`, `os_waiting_for_events_epoll()`, `os_add_epoll_fd()`, `os_mod_epoll_fd()`, `os_del_epoll_fd()`, `os_epoll_get_data_pointer()`, `os_epoll_triggered()`, `os_event_mask()`, `os_set_ioignore()`, and `os_close_epoll_fd()` form the API.

## Control Flow, State, and Persistence
State is a global `epollfd` and fixed `epoll_events[MAX_EPOLL_EVENTS]`. Waits are nonblocking (`timeout=0`) and return event counts or negative errno; event data pointers link back to kernel-side IRQ descriptors.

## Dependencies and Integration Points
Used by UML IRQ core and fd activation/deactivation paths. It maps UML read/write IRQ types to host EPOLL masks and closes epoll on reboot.

## Risks and Test Signals
Risks include fixed event array overflow, edge-triggered missed events, fd leaks across reboot, and silent delete behavior hiding bugs. Test many fd-backed devices, fd add/mod/delete races, reboot cleanup, and SIGIO ignore transitions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/irq.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/main.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/main.c

## Purpose
Provides the host process `main()` for UML, including ASLR disabling/reexec, stack limit setup, environment PATH adjustment, fatal signal handling, boot entry, shutdown, reboot exec, and malloc/free interposition.

## Important APIs, Types, and Functions
`main()` prepares host process state, calls `scan_elf_aux()` and `linux_main()`, then disables timers/SIGIO before optional reboot exec. `set_stklim()`, `setup_env_path()`, and `install_fatal_handler()` are boot helpers. `__wrap_malloc()`, `__wrap_calloc()`, and `__wrap_free()` route libc allocations to kmalloc/vmalloc after `kmalloc_ok`.

## Control Flow, State, and Persistence
Persistent process effects include disabled ASLR personality, session creation, adjusted PATH, fatal handlers, duplicated argv for reboot, and malloc routing based on UML memory ranges. Shutdown unblocks pending signals after deactivating timers/fds.

## Dependencies and Integration Points
Entry point to `linux_main()` in `um_arch.c`. Depends on host personality, signals, `uml_cleanup()`, timer/fd deactivation, physical/vmalloc layout globals, and memory allocators.

## Risks and Test Signals
Risks are failed reexec, PATH memory lifetime, malloc wrapper misclassification, pending signal delivery during shutdown, and reboot argv handling. Test boot with ASLR enabled, reboot, SIGINT/SIGTERM, profiling builds, and allocations before/after `kmalloc_ok`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/main.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/mem.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/mem.c

## Purpose
Manages host temporary memory backing files and KASAN shadow mappings for UML.

## Important APIs, Types, and Functions
`kasan_map_memory()` maps noreserve anonymous shadow memory and marks it DONTDUMP/DONTFORK. `choose_tempdir()` prefers environment temp dirs or `/dev/shm` on tmpfs. `make_tempfile()`, `create_tmp_file()`, and `create_mem_file()` create unlinked or `O_TMPFILE` host files sized for UML physical memory. `check_tmpexec()` verifies executable mappings are allowed from the tempdir.

## Control Flow, State, and Persistence
Global `tempdir` is set once during early boot. Temporary files are unlinked or anonymous and persist only as open FDs. `check_tmpexec()` exits early if no executable mapping can be created.

## Dependencies and Integration Points
Used by physical memory setup, SKAS stub executable fallback, host memory mapping, and early host checks. Depends on tmpfs behavior, `O_TMPFILE`, `mkstemp`, `mmap`, and `madvise`.

## Risks and Test Signals
Risks include non-tmpfs dirty throttling, noexec temp dirs, failed sparse file sizing, KASAN shadow fork/dump flags, and tempdir environment lifetime. Test TMPDIR variants, `/dev/shm` absence, noexec mounts, KASAN configs, and large memory sizes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/mem.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/process.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/process.c

## Purpose
Wraps host process, signal, memory-map, futex, and child-reaping operations for UML runtime code.

## Important APIs, Types, and Functions
Includes `os_alarm_process()`, `os_kill_process()`, `os_kill_ptraced_process()`, `os_reap_child()`, raw `os_getpid()`, `os_map_memory()`, `os_protect_memory()`, `os_unmap_memory()`, `os_drop_memory()`, `can_drop_memory()`, `init_new_thread_signals()`, `os_set_pdeathsig()`, `os_futex_wait()`, and `os_futex_wake()`.

## Control Flow, State, and Persistence
No long-lived state except host signal handlers installed by `init_new_thread_signals()`. Kill paths block UML signals while killing/reaping children. Mapping helpers create fixed shared host mappings for UML memory.

## Dependencies and Integration Points
Used by TLB sync, reboot cleanup, SKAS process management, SMP startup, memory discard, and signal initialization. It bridges kernel abstractions to host syscalls.

## Risks and Test Signals
Risks are killing wrong process groups/pids, ptrace kill races, `MADV_REMOVE` support detection, signal-handler installation mismatch with seccomp, and futex wait wakeups. Test child crash/reap, memory mapping/protection, discard support, and signal initialization in ptrace/seccomp modes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/process.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/registers.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/registers.c

## Purpose
Captures and provides safe initial register templates for new UML userspace contexts.

## Important APIs, Types, and Functions
Globals `exec_regs[MAX_REG_NR]` and `exec_fp_regs` store boot-time general and floating-point register templates. `init_pid_registers()` reads registers from a ptraced child, runs arch-specific initialization, allocates fp storage, and captures fp registers. `get_safe_registers()` copies the templates to callers.

## Control Flow, State, and Persistence
Register templates are initialized once during early boot and persist for the life of UML. They are copied into new contexts or syscall-stub setup paths.

## Dependencies and Integration Points
Called from `start_up.c` in ptrace mode and used by `os-Linux/skas/mem.c` to initialize syscall-stub registers. Depends on ptrace and arch register helpers.

## Risks and Test Signals
Risks include wrong host FP size, allocation failure not handled, and stale arch register defaults. Test x86_64/i386, FPU/SIMD availability, ptrace startup checks, and new process register state.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/registers.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/sigio.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/sigio.c

## Purpose
Detects and works around host PTY SIGIO limitations by using an epoll helper thread to generate SIGIO for UML.

## Important APIs, Types, and Functions
`__add_sigio_fd()`/`add_sigio_fd()` and `__ignore_sigio_fd()`/`ignore_sigio_fd()` manage the workaround epoll set. `write_sigio_thread()` waits on epoll and sends SIGIO to the UML process. `sigio_broken()` and `maybe_sigio_broken()` start the workaround. `os_check_bugs()` runs the PTY SIGIO probe. `sigio_cleanup()` kills the helper at exit.

## Control Flow, State, and Persistence
Persistent state includes `write_sigio_td`, `epollfd`, `epoll_events`, `pty_output_sigio`, and probe flag `got_sigio`. The workaround starts lazily and is protected by the kernel-side sigio mutex.

## Dependencies and Integration Points
Uses `helper.c` pthread helpers, `sigio_lock()` from `kernel/sigio.c`, PTY setup, raw terminal mode, and host SIGIO handlers. It supports UML console and fd IRQ delivery.

## Risks and Test Signals
Risks include helper-thread leaks, epoll edge-trigger missed writes, wrong signal target, and probe false negatives. Test PTY output on different kernels, console I/O, add/remove fd races, and shutdown cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/sigio.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/signal.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/signal.c

## Purpose
Implements host signal handling and signal masking for UML threads. It converts host signals into UML IRQs, traps, faults, child reaping, timers, and time-travel pending events.

## Important APIs, Types, and Functions
Global `sig_info[]` dispatches kernel-level signal handlers. `sig_handler_common()`, `sig_handler()`, and `timer_alarm_handler()` handle host signals. `set_handler()`, `set_sigstack()`, `timer_set_signal_handler()`, `deliver_alarm()`, `send_sigio_to_self()`, `change_sig()`, `block_signals()`, `unblock_signals()`, `um_set_signals()`, and time-travel hard block helpers form the API.

## Control Flow, State, and Persistence
Thread-local `signals_enabled`, `signals_pending`, and `signals_active` implement UML interrupt masking on top of host signals. With time-travel support, `signals_blocked` and atomic `signals_blocked_pending` prevent nested external-scheduler SIGIO handling until safe.

## Dependencies and Integration Points
Integrated with `trap.c`, `time.c`, SIGIO, SIGCHLD tracking, SMP IPI masking, and lockdep trace wrappers in `kernel/signal.c`. Handlers use alternate stacks and preserve errno.

## Risks and Test Signals
Risks are lost pending signals, reentrant timer handling, hard-block underflow, SIGIO/time-travel ACK ordering bugs, and wrong masks in seccomp mode. Test signal storms, timer interrupts while blocked, external time travel, seccomp child death, and SMP IPIs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/signal.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/skas/Makefile -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/skas/Makefile

## Purpose
Builds host-side SKAS support objects.

## Important APIs, Types, and Functions
Defines `obj-y := mem.o process.o` and marks them as `USER_OBJS`, then includes shared UML user-object build rules.

## Control Flow, State, and Persistence
No runtime behavior. It ensures SKAS memory syscall batching and userspace process control are compiled with user-side flags.

## Dependencies and Integration Points
Feeds the parent `os-Linux/Makefile` via the `skas/` directory. Includes `arch/um/scripts/Makefile.rules`.

## Risks and Test Signals
Risks are wrong user/kernel CFLAGS for host syscall code or missing SKAS objects. Test ptrace and seccomp SKAS boot paths after clean builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/skas/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/skas/mem.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/skas/mem.c

## Purpose
Queues and flushes memory-management syscalls that must execute inside a UML userspace helper process, supporting both ptrace and seccomp transport.

## Important APIs, Types, and Functions
`init_syscall_regs()` builds register state to enter `stub_syscall_handler`. `syscall_stub_alloc()`, `map()`, and `unmap()` append mmap/munmap requests, compressing adjacent compatible operations. `syscall_stub_flush()` and `do_syscall_stub()` execute pending requests. `get_stub_fd()` maps host FDs to compact seccomp FD indexes. `syscall_stub_dump_error()` prints failed stub request details.

## Control Flow, State, and Persistence
Per-mm state lives in `mm_id`: `syscall_data_len`, `syscall_fd_num`, and `syscall_fd_map`; request payload lives in shared `stub_data`. Seccomp mode passes FDs over the mm socket and wakes the child via futex; ptrace mode sets registers and continues to the stub trap.

## Dependencies and Integration Points
Called by `kernel/tlb.c` for user mappings and by the SKAS userspace loop before running guest code. Depends on `stub.c`, `os-Linux/skas/process.c`, register templates, and fixed stub layout constants.

## Risks and Test Signals
Risks include queue overflow, compressed mapping offset mistakes, stale error state, FD map exhaustion, and seccomp/ptrace divergence. Test mmap-heavy workloads, mprotect/munmap batching, FD passing, stub failures, and ENOMEM diagnostics.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/skas/mem.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/skas/process.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/skas/process.c

## Purpose
Implements host-side SKAS process control: creating `uml-userspace` helpers, waiting for ptrace/seccomp stops, shuttling registers, running guest userspace, and switching UML kernel threads.

## Important APIs, Types, and Functions
`start_userspace()` clones a trampoline that execs the embedded stub executable. `init_stub_exe_fd()` materializes the embedded stub into a sealed memfd or executable temp file. `wait_stub_done()` and `wait_stub_done_seccomp()` synchronize stub completion. `userspace()` is the main loop that syncs TLBs, flushes stub syscalls, sets/restores registers, resumes ptrace or seccomp child execution, decodes host stop signals, and dispatches to page fault, syscall, or signal handlers. Thread switching uses `new_thread()`, `switch_threads()`, `start_idle_thread()`, callbacks, halt, and reboot longjmps.

## Control Flow, State, and Persistence
Persistent state includes `stub_exe_fd`, `using_seccomp`, initial jump buffer, thread-local callback slots, `noreboot`, and unscheduled userspace iteration counters. Per-mm state is protected by the turnstile while manipulating a shared child process.

## Dependencies and Integration Points
This is the hub between kernel UML execution, host ptrace/seccomp, stub executable, TLB sync, signal/trap/syscall handlers, time travel, SMP constraints, and reboot/halt paths.

## Risks and Test Signals
Risks are high: register corruption, lost SIGSYS/SIGALRM ordering, stub child death, insecure seccomp mode, turnstile deadlocks, unreaped temp stub files, and longjmp misuse. Test boot in ptrace/seccomp, `seccomp=on/auto/off`, SMP rejection in ptrace mode, syscall/page-fault stress, signal delivery, gdb/strace, panic/reboot/noreboot, and time-travel workloads.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/skas/process.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/smp.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/smp.c

## Purpose
Provides host pthread and realtime-signal mechanics for UML SMP virtual CPUs and IPIs.

## Important APIs, Types, and Functions
`uml_curr_cpu()` returns thread-local CPU id. `os_start_cpu_thread()` creates a masked pthread for a CPU. `os_start_secondary()` restores masks and longjmps into the UML idle-thread context. `os_send_ipi()` sends `IPI_SIGNAL` with vector data. `os_local_ipi_enable()`/`os_local_ipi_disable()` manage local IPI masking. `os_init_smp()` installs the realtime signal handler and records boot CPU pthread.

## Control Flow, State, and Persistence
Persistent state includes thread-local `__curr_cpu` and `cpu_threads[]`. Each AP starts with all signals blocked, receives boot data, then transitions into kernel-side `uml_start_secondary()` and later unblocks relevant signals.

## Dependencies and Integration Points
Pairs with `kernel/smp.c`, host signal state in `signal.c`, and pthread APIs. IPI values are delivered as `sigqueue` payloads and handled on the alternate signal stack.

## Risks and Test Signals
Risks include signal-mask mistakes, lost vector payloads, CPU thread creation failures, and pthread lifetime assumptions. Test multi-CPU boot, IPI storms, call_function, rescheduling, local IRQ disable/enable, and shutdown.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/smp.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/start_up.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/start_up.c

## Purpose
Runs early host capability checks before UML kernel boot, selecting seccomp or ptrace userspace mode and validating required host features.

## Important APIs, Types, and Functions
`check_ptrace()` verifies syscall-number rewriting, then `check_sysemu()` verifies `PTRACE_SYSEMU_SINGLESTEP`. `init_seccomp()` tests installing a seccomp trap filter and extracts startup register/fp state from a signal mcontext. `uml_seccomp_config()` parses `seccomp=off|auto|on`. `get_host_cpu_features()` parses `/proc/cpuinfo`. `os_early_checks()` runs coredump, temp exec, seccomp, ptrace, SMP compatibility, and register initialization checks.

## Control Flow, State, and Persistence
Boot-time globals include `seccomp_config` and temporary `seccomp_test_stub_data`. Successful seccomp sets global `using_seccomp`; fallback ptrace initializes register templates from a ptraced child. The decisions persist for all userspace contexts.

## Dependencies and Integration Points
Works with `registers.c`, `mem.c`, SKAS process code, signal stacks, raw syscalls, seccomp BPF, ptrace constants, and command-line setup. It gates whether SMP can be used.

## Risks and Test Signals
Risks include false capability detection, host kernel ptrace/seccomp quirks, seccomp already-filtered environments, close_range dependency, and mandatory `seccomp=on` failures. Test across kernels/containers, `seccomp=on/auto/off`, SMP configs, coredump limits, and noexec tempdirs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/start_up.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/time.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/time.c

## Purpose
Wraps host POSIX clocks/timers and idle sleep primitives for UML timekeeping.

## Important APIs, Types, and Functions
`os_persistent_clock_emulation()` reads `CLOCK_REALTIME`; `os_nsecs()` reads `CLOCK_MONOTONIC`. `os_timer_create()`, `os_timer_set_interval()`, `os_timer_one_shot()`, and `os_timer_disable()` manage per-CPU POSIX timers targeting SIGALRM. `os_idle_prepare()` creates a signalfd for SIGALRM/IPI wakeups; `os_idle_sleep()` blocks SIGALRM around resched checks and polls wake signals.

## Control Flow, State, and Persistence
Persistent state includes `event_high_res_timer[CONFIG_NR_CPUS]` and thread-local `wake_signals`. Timers are per UML CPU and use `SIGEV_THREAD_ID` to target the host thread returned by `gettid()`.

## Dependencies and Integration Points
Used by `kernel/time.c`, suspend idle entry, and SMP IPI signaling. Depends on `timer_alarm_pending()`, `uml_need_resched()`, `os_poll()`, and `IPI_SIGNAL`.

## Risks and Test Signals
Risks are incorrect per-thread timer delivery, missing signalfd wakeups, SIGALRM race around idle checks, and ignored timer_settime errors in oneshot. Test timers on SMP, idle wake by timer/IPI, suspend, high-res timer availability, and time-travel mode switching.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/time.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/tty.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/tty.c

## Purpose
Allocates and prepares host PTY master devices for UML console/terminal use.

## Important APIs, Types, and Functions
`get_pty()` opens `/dev/ptmx`, runs `grantpt()` via `initial_thread_cb()` using `grantpt_cb()`, calls `unlockpt()`, and returns the master fd or negative errno.

## Control Flow, State, and Persistence
No global state. The returned PTY fd persists with the caller; errors close the fd before returning. Running `grantpt()` on the initial thread avoids threading/libc assumptions around PTY permission changes.

## Dependencies and Integration Points
Depends on SKAS initial-thread callback plumbing and host PTY APIs. Used by UML line/console drivers.

## Risks and Test Signals
Risks are missing `/dev/ptmx`, failed grant/unlock, callback deadlocks, and fd leaks. Test console allocation, PTY exhaustion, container PTY permissions, and initial-thread callback behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/tty.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/umid.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/umid.c

## Purpose
Manages host-side UML instance identity directories and pid files under `~/.uml/` or `uml_dir=`.

## Important APIs, Types, and Functions
`set_umid()` records an explicit ID. `make_uml_dir()` expands `~`, normalizes a trailing slash, and creates the parent directory. `make_umid()` creates or takes over an instance directory, generating a random ID when needed. `is_umdir_used()`, `umdir_take_if_dead()`, and `remove_files_and_dir()` handle stale directories. `umid_file_name()`, `get_umid()`, `set_uml_dir()`, and `remove_umid_dir()` expose lifecycle helpers.

## Control Flow, State, and Persistence
Persistent host state is a per-instance directory containing a `pid` file. Runtime globals are `umid`, `uml_dir`, and `umid_setup`. Exitcall cleanup removes files in the instance directory and then the directory itself.

## Dependencies and Integration Points
Works with kernel `umid.c`, command-line setup, management console/socket naming, and exitcall cleanup. Uses host filesystem, pid liveness checks, and environment `$HOME`.

## Risks and Test Signals
Risks include races between stale directory removal and new mkdir, path length limits, pid reuse/liveness false positives, unsafe directory contents, and cleanup errors. Test concurrent same-umid boots, stale pid files, `uml_dir=`, missing HOME, long IDs, and shutdown cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/umid.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/user_syms.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/user_syms.c

## Purpose
Exports selected compiler/libc string helper symbols that UML modules may need when user-side code is linked into the kernel environment.

## Important APIs, Types, and Functions
Conditionally exports `strstr`, and on non-x86_64 exports `memcpy`, `memmove`, and `memset`. When fortify is enabled, exports `__sprintf_chk`. Defines `__NO_FORTIFY` before includes to avoid fortify rewrites in this file.

## Control Flow, State, and Persistence
No runtime control flow or state. It only affects module symbol resolution.

## Dependencies and Integration Points
Integrates with module export infrastructure and architecture string implementation choices. Comments warn against expanding this as a broad hostfs/user-code API boundary.

## Risks and Test Signals
Risks are missing exports on specific compiler/libc/architecture combinations or encouraging improper module dependencies on host-side functions. Test module builds on i386/x86_64 and fortify-enabled configs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/user_syms.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/util.c -->

# sources/distributed-fs/ceph-client/arch/um/os-Linux/util.c

## Purpose
Provides miscellaneous host utility functions for stacks, terminals, host identity, random bytes, helper signal defaults, core dumping, early printing, and boot info/warning output.

## Important APIs, Types, and Functions
`stack_protections()`, `raw()`, `setup_machinename()`, `setup_hostinfo()`, `os_getrandom()`, `os_fix_helper_signals()`, `os_dump_core()`, `um_early_printk()`, `quiet_cmd_param()`, `os_info()`, and `os_warn()` are the main APIs. `uml_abort()` avoids glibc abort behavior that is unsafe for UML kernel threads.

## Control Flow, State, and Persistence
Persistent state is `quiet_info`, set by the `quiet` UML setup option. `os_dump_core()` resets SIGSEGV, terminates the process group, tries to kill ptraced children, then self-aborts.

## Dependencies and Integration Points
Used throughout boot, panic, helper, console, and architecture setup paths. Depends on host `uname`, termios, signals, getrandom, waitpid, and kernel `vscnprintf` for small-stack-safe formatting.

## Risks and Test Signals
Risks include process-group overkill during core dump, stack-protection mprotect failures, terminal raw-mode partial application, and quiet suppressing needed diagnostics. Test panic/core dump, helper signal behavior, `quiet`, host info in `/proc/cpuinfo`, and terminal setup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/os-Linux/util.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/scripts/Makefile.rules -->

# sources/distributed-fs/ceph-client/arch/um/scripts/Makefile.rules

## Purpose
Defines shared Kbuild rules for compiling UML user-side objects with the correct flags and instrumentation filtering.

## Important APIs, Types, and Functions
Computes `USER_SINGLE_OBJS`, expands `USER_OBJS` into object paths, customizes `c_flags` for user objects to include `USER_CFLAGS`, `kern_levels.h`, and `user.h`, defines `UNPROFILE_OBJS` with profiling/gcov stripped, removes kernel `NOSTDINC_FLAGS` from `CHECKFLAGS`, and defines the `unprofile` make function.

## Control Flow, State, and Persistence
No runtime behavior. Build-time state determines how host-side UML code and stubs are compiled.

## Dependencies and Integration Points
Included by `os-Linux/Makefile`, `os-Linux/skas/Makefile`, and `kernel/skas/Makefile`. It enforces the boundary between kernel-style and host-user-style compilation.

## Risks and Test Signals
Risks are incorrect flag filtering, missing generated dependency flags, or profiling instrumentation entering stub code. Test with KCOV, gcov, `-pg`, sparse/CHECKFLAGS, and clang/gcc builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/scripts/Makefile.rules -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/Kbuild -->

# sources/distributed-fs/ceph-client/arch/x86/Kbuild

## Purpose
Top-level x86 architecture Kbuild file selecting major x86 subdirectories for compilation.

## Important APIs, Types, and Functions
Adds branch-profiling disable define for `CONFIG_TRACE_BRANCH_PROFILING`, then includes boot startup, confidential computing, entry, perf events, KVM, Xen, PVH, Hyper-V, realmode, kernel, mm, crypto, IA32 emulation, platform, net, kexec purgatory, and virt subtrees based on configuration. Also lists `boot` and `tools` for cleaning.

## Control Flow, State, and Persistence
No runtime state. It controls build graph inclusion for x86 kernels.

## Dependencies and Integration Points
Used by top-level Kbuild for x86. Although adjacent to UML in this subset, it is a generic x86 build selector and not UML-specific.

## Risks and Test Signals
Risks are config-conditional directory omissions, branch profiling entering noinstr code, or clean targets missing generated files. Test x86 defconfigs, KVM/Xen/Hyper-V toggles, tracing configs, and `make clean`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/Kbuild -->
