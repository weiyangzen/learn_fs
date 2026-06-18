# subset-b-000760 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/perf_regs.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/perf_regs.c

### Purpose
`perf_regs.c` exposes PA-RISC register snapshots to the generic perf sampled-registers API.

### Important APIs, Types, And Functions
`perf_reg_value()` maps `PERF_REG_PARISC_*` indexes to fields in `struct pt_regs`. `perf_reg_validate()` rejects empty masks and masks with bits above `PERF_REG_PARISC_MAX`. `perf_reg_abi()` reports 32-bit or 64-bit ABI based on kernel width and `TIF_32BIT`. `perf_get_regs_user()` fills `struct perf_regs` for the current task.

### Control Flow
Perf asks for a register value by index; the switch reads general, space, instruction queue, and control-derived trap registers. ABI selection is purely conditional. User register collection ignores the passed `regs` argument and uses `task_pt_regs(current)`.

### State, Persistence, And Dependencies
No state is persisted. The code depends on `asm/ptrace.h`, perf register enumerations, task thread flags, and the correctness of `struct pt_regs` layout.

### Integration Points
Used by perf sampling and unwinding when user register masks are requested.

### Risks
The `PERF_REG_PARISC_IAOQ*` case reads `regs->iasq[]`, which appears inconsistent with the index name and could report space queue values instead of instruction offsets. ABI reporting must match compat task handling or user tools decode registers incorrectly.

### Test Signals
Perf tests should sample GPRs, SRs, IASQ/IAOQ, and SAR/IIR/ISR/IOR/IPSW on 32-bit, 64-bit, and compat tasks, and should validate bad masks return `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/perf_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/process.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/process.c

### Purpose
`process.c` implements PA-RISC process lifecycle hooks: restart, poweroff, halt, idle, CPU-dead handling, thread cloning, and blocked-task wait-channel discovery.

### Important APIs, Types, And Functions
`machine_restart()`, `machine_power_off()`, `machine_halt()`, `flush_thread()`, `arch_cpu_idle_dead()`, `arch_cpu_idle()`, `copy_thread()`, and `__get_wchan()` are the main exported architecture hooks. It exports `pm_power_off` and `running_on_qemu`.

### Control Flow
Restart asks firmware/chassis interfaces to reset, disables interrupts, and falls back to the global broadcast reset register. Poweroff returns the soft power button to firmware control, calls generic poweroff handlers, then waits for a firmware console return key to reboot. `copy_thread()` builds either a kernel-thread frame targeting `ret_from_kernel_thread` or a user-thread frame targeting `child_return`, optionally installing TLS in `cr27`. Wait-channel lookup unwinds a blocked task until it escapes scheduler functions.

### State, Persistence, And Dependencies
State is limited to boot-time QEMU detection, exported poweroff hook state, and per-task saved `pt_regs`. It depends on PDC firmware calls, chassis LEDs, cache/TLB flushes, CPU hotplug, scheduler task stacks, and the PA-RISC unwind implementation.

### Integration Points
Called by generic reboot, task cloning, CPU idle/hotplug, and `/proc` stack-wait users.

### Risks
Restart/poweroff paths are firmware-specific and may never return. `copy_thread()` handles 64-bit function descriptors manually; descriptor layout mismatches would break kernel thread startup. Dead CPU handling assumes firmware rendezvous works after local cache/TLB flush.

### Test Signals
Boot, reboot, poweroff fallback, CPU hotplug offline, kernel thread creation, `clone(CLONE_SETTLS)`, and blocked-task `wchan` reporting are the useful runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/processor.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/processor.c

### Purpose
`processor.c` discovers PA-RISC CPU devices, records boot and per-CPU metadata, enables FP support, publishes `/proc/cpuinfo`, and registers the CPU parisc bus driver.

### Important APIs, Types, And Functions
Globals include `boot_cpu_data`, `_parisc_requires_coherency`, and per-cpu `cpu_data`. Key functions are `processor_probe()`, `collect_boot_cpu_data()`, `init_per_cpu()`, `show_cpuinfo()`, and `processor_init()`.

### Control Flow
Boot collection queries PDC model, version, CPUID, capabilities, platform names, and serial data, feeding randomness and architecture descriptors. Device probing assigns logical CPU IDs, optionally reads PAT CPU/module information, fills `cpu_data`, stores topology, and adds secondary CPUs. `init_per_cpu()` sets firmware width, enables the FP coprocessor, records FP revision/model, initializes block TLB state, and panics on 64-bit kernels without FP.

### State, Persistence, And Dependencies
CPU identity and capabilities persist in `boot_cpu_data` and `cpu_data`. Dependencies include PDC/PAT firmware, parisc device inventory, topology, cache reporting, FP control registers, and SMP CPU registration.

### Integration Points
`setup.c` calls boot data collection and `processor_init()`, SMP startup calls `init_per_cpu()`, and procfs uses `show_cpuinfo()`.

### Risks
Probe ordering controls logical CPU numbering and topology. PAT firmware failures are treated as `BUG_ON()`. FP enablement is mandatory for 64-bit kernels and assumed by later kernel code.

### Test Signals
Validate boot logs, `/proc/cpuinfo`, secondary CPU discovery, PAT and legacy firmware paths, FP register availability, and topology output on SMP and UP builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/processor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/ptrace.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/ptrace.c

### Purpose
`ptrace.c` implements PA-RISC debugger control, syscall tracing, native/compat regsets, and register name/stack access helpers.

### Important APIs, Types, And Functions
It provides `ptrace_disable()`, single-step and block-step controls, `arch_ptrace()`, `compat_arch_ptrace()`, `do_syscall_trace_enter()`, `do_syscall_trace_exit()`, regset get/set helpers, `task_user_regset_view()`, `regs_query_register_offset()`, `regs_query_register_name()`, `regs_within_kernel_stack()`, and `regs_get_kernel_stack_nth()`.

### Control Flow
Single stepping manipulates PSW recovery/taken-branch bits and handles nullified instructions by advancing the queue and forcing `SIGTRAP`. Ptrace PEEK/POKE validates offsets and restricts writable registers/PSW bits. Compat ptrace translates 32-bit offsets into 64-bit `pt_regs` slots. Syscall entry performs ptrace, seccomp, tracepoint, and audit processing before returning the possibly modified syscall number; exit reports audit, tracepoints, and ptrace exit events.

### State, Persistence, And Dependencies
State is per-task thread flags and saved `pt_regs`. Regsets depend on ELF note constants, compat layout, `membuf`, audit/seccomp, tracepoints, and PA-RISC PSW semantics.

### Integration Points
Used by `ptrace(2)`, GDB, core dumps, syscall entry assembly, kprobes/perf register lookup, and stacktrace APIs.

### Risks
Only selected registers are writable; mismatches with GDB expectations can break debugging. Compat offset translation is layout-sensitive. Ptrace can alter syscall numbers and return registers, so assembly and C paths must agree on saved register locations.

### Test Signals
Run native and compat GDB single-step/block-step, ptrace register read/write, core dump regset checks, seccomp syscall skipping, syscall tracepoints, and kernel stack nth-entry helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/real2.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/real2.S

### Purpose
`real2.S` provides real-mode firmware call bridges and mode-switch helpers used when kernel virtual mode must call PDC/IODC routines.

### Important APIs, Types, And Functions
Assembly entry points include `real32_call_asm`, `real64_call_asm` on 64-bit builds, `save_control_regs`, `restore_control_regs`, `rfi_virt2real`, `rfi_real2virt`, and `__canonicalize_funcptr_for_compare`. It exports `real_stack` and `real64_stack`.

### Control Flow
The call bridges save return state, adopt a firmware stack, load argument registers from a saved argument area, translate the stack pointer to physical, switch from virtual to real mode with `rfi`, save control registers, call the firmware function, restore control registers, switch back to virtual mode, and restore the original stack/registers. `real32_call_asm` also toggles wide mode when needed.

### State, Persistence, And Dependencies
Temporary control-register snapshots live in static BSS. The code depends on PSW constants, address translation macros, PA-RISC calling conventions, and firmware stack layout.

### Integration Points
Used by PDC/IODC firmware wrappers during boot and runtime firmware calls.

### Risks
Interrupt, Q-bit, PSW, and control-register sequencing is fragile; a fault before control-register restore can strand the CPU in the wrong mode. 64-bit function descriptors require special handling.

### Test Signals
Boot firmware calls, PDC console access, 32-bit firmware on 64-bit kernels, and repeated real-mode calls under interrupt pressure are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/real2.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/relocate_kernel.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/relocate_kernel.S

### Purpose
`relocate_kernel.S` is the PA-RISC kexec relocation stub that copies relocation entries in physical mode and jumps to the new kernel.

### Important APIs, Types, And Functions
It exports `relocate_new_kernel`, `relocate_new_kernel_size`, and kexec parameter slots plus offsets for command line, initrd start/end, and free memory.

### Control Flow
The stub disables interrupts and the Q bit, uses RFI to continue without translation, walks the kimage indirection list, handles done/indirection/destination/source entries, copies each page with register-sized loads and stores, flushes data/instruction caches, then branches to the new kernel start with kexec boot parameters.

### State, Persistence, And Dependencies
The only persistent state is the embedded kexec parameter words patched by the kexec setup path. Dependencies include `kimage->head` entry encoding, PA-RISC PSW/RFI control, cache flush instructions, and page-size constants.

### Integration Points
Used by the generic kexec/kdump path when transferring control to a replacement or crash kernel.

### Risks
Physical-mode relocation cannot rely on normal kernel services. Entry flag interpretation, register width, and cache coherency must be exact or the new kernel receives corrupted pages or parameters.

### Test Signals
Exercise normal kexec and crash-kernel kdump on 32-bit and 64-bit builds, with initrd/cmdline parameters and memory layouts requiring indirection entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/relocate_kernel.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/setup.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/setup.c

### Purpose
`setup.c` handles early PA-RISC architecture boot setup, command-line construction, memory/cache/paging initialization, resource registration, and the final handoff into `start_kernel()`.

### Important APIs, Types, And Functions
Key routines are `setup_cmdline()`, `setup_arch()`, `parisc_init_resources()`, `parisc_init()`, `start_parisc()`, and `cpuinfo_op` sequence callbacks.

### Control Flow
Early boot validates initial kernel mappings, detects QEMU/SeaBIOS, initializes topology and FP, initializes trap vectors, then calls `start_kernel()`. `setup_arch()` initializes unwind data, per-CPU modes, PDC, command line/default console/earlycon, boot CPU data, memory inventory, caches, paging, and scheduler clock stability. Later `parisc_init()` claims bus resources, inventories devices, sets chassis state and OS ID, flushes local caches/TLB, registers CPUs, applies alternatives, and calibrates cache timing.

### State, Persistence, And Dependencies
Boot command line, initrd bounds, resource reservations, `running_on_qemu`, topology, and boot CPU data persist. Dependencies include PDC, PAGE0 firmware data, cache/TLB setup, memory inventory, alternatives, proc cpuinfo, and SMP.

### Integration Points
Called by architecture entry code and generic initcall flow; provides `/proc/cpuinfo` sequencing through `cpuinfo_op`.

### Risks
Command-line defaults can affect console availability. Early mapping warnings occur before printk is reliable. Init ordering matters because PDC, traps, memory inventory, and paging depend on one another.

### Test Signals
Boot with/without bootloader command line, initrd, QEMU marker, serial/graphics console autodetect, large kernels near initial mapping limits, SMP, and resource reservation conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/signal.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/signal.c

### Purpose
`signal.c` implements PA-RISC signal delivery, realtime signal frames, `rt_sigreturn`, syscall restart handling, and user-mode resume work.

### Important APIs, Types, And Functions
Core functions are `sys_rt_sigreturn()`, `get_sigframe()`, `setup_sigcontext()`, `setup_rt_frame()`, `handle_signal()`, `check_syscallno_in_delay_branch()`, `syscall_restart()`, `insert_restart_trampoline()`, `do_signal()`, and `do_notify_resume()`.

### Control Flow
Signal return locates the upward-growing signal frame below the current stack pointer, restores signal mask, register context, and altstack, then fixes `gr31` for syscall-return paths. Delivery builds a native or compat rt frame, saves siginfo/ucontext/mask, resolves PA-RISC function descriptors for handlers, installs VDSO sigtramp/restart return pointers, sets handler arguments, and advances the upward-growing user stack. Syscall restart either converts restart errors to `-EINTR`, rewinds the gateway branch sequence, or plants a VDSO restart trampoline.

### State, Persistence, And Dependencies
State persists in user signal frames, saved masks, `restart_block`, `orig_r28`, and user-visible registers. Dependencies include compat signal helpers, VDSO offsets, PA-RISC function descriptors, delayed-branch syscall ABI, and generic signal core.

### Integration Points
Called from syscall/interrupt return paths and uses VDSO trampolines built under `vdso32` and `vdso64`.

### Risks
PA-RISC stacks grow upward, making frame bounds and altstack logic unusual. Restart logic decodes user instructions in syscall delay slots. Incorrect in-syscall handling can restore the wrong IAOQ or return pointer.

### Test Signals
Test native and compat signal delivery, altstack, handler descriptors, `rt_sigreturn`, interrupted syscalls with all restart classes, ptrace single-step into handlers, and VDSO trampoline unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/signal32.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/signal32.c

### Purpose
`signal32.c` translates between 64-bit kernel register state and 32-bit PA-RISC compat signal frames.

### Important APIs, Types, And Functions
It implements `restore_sigcontext32()` and `setup_sigcontext32()`, using `struct compat_sigcontext` plus the hidden `struct compat_regfile`.

### Control Flow
Setup truncates each 64-bit GPR, IAOQ, IASQ, and SAR into the compat sigcontext while storing upper halves in the hidden regfile. It copies 64-bit FP registers unchanged. Restore rebuilds 64-bit registers from lower sigcontext halves and upper regfile halves, then restores FP, queues, spaces, and SAR.

### State, Persistence, And Dependencies
Persistent state is the user signal frame and hidden upper-half regfile. Dependencies are compat accessors, `pt_regs`, `PARISC_SC_FLAG_*`, and the frame layout declared in `signal32.h`.

### Integration Points
Called from `signal.c` whenever a 32-bit task runs on a 64-bit kernel.

### Risks
The hidden regfile is non-ABI and layout-sensitive, but required to preserve full 64-bit kernel register contents. Any mismatch with `PARISC_RT_SIGFRAME_SIZE32` or userspace unwinding breaks compat signal return.

### Test Signals
Compat signal tests should verify high-half preservation, FP register round trips, syscall and non-syscall delivery, altstack restore, and malformed user frame `-EFAULT` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/signal32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/signal32.h -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/signal32.h

### Purpose
`signal32.h` defines compat signal-frame data structures and helpers for 32-bit user processes on 64-bit PA-RISC kernels.

### Important APIs, Types, And Functions
It declares `struct compat_ucontext`, `struct compat_regfile`, `struct compat_rt_sigframe`, `PARISC_RT_SIGFRAME_SIZE32`, `restore_sigcontext32()`, and `setup_sigcontext32()`.

### Control Flow
The header has no runtime control flow. It establishes that the visible 32-bit ucontext is followed by a hidden register file storing upper halves of truncated registers.

### State, Persistence, And Dependencies
User stack signal frames persist according to these layouts. Dependencies include Linux compat types, `compat_sigcontext`, and PA-RISC frame-size constants.

### Integration Points
Consumed by `signal.c` and `signal32.c`; offsets are also relevant to VDSO signal trampoline unwind metadata.

### Risks
Frame-size and alignment constants must match assembly and GDB expectations. The hidden regfile must remain last because `uc_sigmask` extensibility can move it.

### Test Signals
Build-time offset checks, compat signal delivery/return, GDB backtrace through compat trampolines, and altstack frame alignment validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/signal32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/smp.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/smp.c

### Purpose
`smp.c` implements PA-RISC SMP startup, IPI delivery, CPU hotplug shutdown, and SMP call-function/reschedule hooks.

### Important APIs, Types, And Functions
Important state includes `smp_init_current_idle_task`, `cpu_now_booting`, per-cpu `ipi_lock`, and `cpu_data.pending_ipi`. Main functions are `ipi_interrupt()`, `ipi_send()`, `smp_cpu_init()`, `smp_callin()`, `smp_boot_one_cpu()`, `smp_prepare_cpus()`, `__cpu_up()`, `__cpu_disable()`, `__cpu_die()`, and `arch_cpuhp_cleanup_dead_cpu()`.

### Control Flow
IPI senders set a pending bit under the target CPU's lock and poke the CPU HPA. The interrupt handler drains bits, dispatching reschedule, call-function, stop, test, and KGDB requests. Booting a secondary records the idle task, sends a rendezvous interrupt through firmware-visible HPA, and waits until the CPU marks itself online. Hotplug disable removes topology, migrates IRQs, flushes caches/TLBs, disables interrupts, and rendezvous-locks with firmware cleanup.

### State, Persistence, And Dependencies
Per-CPU pending IPI bits, locks, topology, `time_keeper_id`, and CPU online/present masks persist. Dependencies include PDC rendezvous, IRQ migration, clockevent init, cache/TLB flushes, KGDB, and scheduler CPU hotplug.

### Integration Points
Provides generic SMP operations for reschedule IPIs, smp-call-function, CPU bringup/offline, and KGDB CPU roundup.

### Risks
IPI state is bitmask-based and must be ordered with barriers. CPU startup relies on firmware rendezvous vectors and busy-wait timeouts. Hotplug must not leave the timekeeping master offline.

### Test Signals
SMP boot, repeated CPU online/offline, reschedule/call-function stress, KGDB roundup, interrupt migration, and timer operation on secondary CPUs are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/stacktrace.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/stacktrace.c

### Purpose
`stacktrace.c` adapts PA-RISC unwind support to the generic stacktrace API.

### Important APIs, Types, And Functions
`walk_stackframe()` drives `unwind_once()` and filters entries through `__kernel_text_address()`. `arch_stack_walk()` and `arch_stack_walk_reliable()` are the exported generic hooks.

### Control Flow
The walker initializes unwind state for the target task, repeatedly unwinds one frame, and invokes the consumer callback for kernel text addresses until unwind failure, zero IP, or consumer rejection. The "reliable" variant currently always returns success after walking.

### State, Persistence, And Dependencies
No state is persisted. It depends entirely on `arch/parisc/kernel/unwind.c`, `task_struct`, and kernel text address validation.

### Integration Points
Used by stack dumping, livepatch/reliability consumers, tracing, and generic kernel stacktrace helpers.

### Risks
Reliability reporting is optimistic because it returns `1` even though unwind can fall back to forced stack scanning. User stack tracing is explicitly not implemented.

### Test Signals
Stacktrace collection for current tasks, blocked tasks, interrupt frames, and functions without unwind entries should be compared with expected symbol chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/sys_parisc.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/sys_parisc.c

### Purpose
`sys_parisc.c` supplies PA-RISC-specific syscall wrappers for mmap placement, 64-bit argument splitting, personality compatibility, legacy flag translation, and madvise compatibility.

### Important APIs, Types, And Functions
Core functions include `calc_max_stack_size()`, `mmap_upper_limit()`, `arch_get_unmapped_area()`, `arch_get_unmapped_area_topdown()`, `sys_mmap2()`, `sys_mmap()`, `parisc_truncate64()`, `parisc_ftruncate64()`, `parisc_pread64()`, `parisc_pwrite64()`, `parisc_readahead()`, `parisc_fadvise64_64()`, `parisc_sync_file_range()`, `parisc_fallocate()`, `parisc_personality()`, `FIX_O_NONBLOCK()` wrappers, and `parisc_madvise()`.

### Control Flow
Mmap allocation handles PA-RISC shared mapping cache coloring, fixed-address validation, top-down first search with bottom-up fallback, stack limit calculation, and randomization room. Split-64 wrappers reconstruct `loff_t`/`u64` arguments from high/low words. Legacy wrappers mask the old `O_NONBLOCK` bit after one warning per thread. `parisc_madvise()` remaps old PA-RISC advice constants to generic values.

### State, Persistence, And Dependencies
State is per-mm VMA layout and one thread warning flag for deprecated nonblock values. Dependencies include generic mmap search, file mapping identity, rlimits, personality, compat mode, syscall helpers, and legacy ABI constants.

### Integration Points
Called from the PA-RISC syscall table and ELF mmap layout selection.

### Risks
Cache coloring affects ABI-visible mmap addresses. Legacy compatibility wrappers must remain in sync with userland expectations. Top-down fallback changes allocation direction under pressure.

### Test Signals
Mmap fixed/shared/color-aligned mappings, large stack rlimits, compat stack defaults, 64-bit file-offset syscalls, old `O_NONBLOCK` binaries, and legacy madvise constants should be exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/sys_parisc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/sys_parisc32.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/sys_parisc32.c

### Purpose
`sys_parisc32.c` contains the 32-on-64 syscall fallback for unimplemented compat syscalls.

### Important APIs, Types, And Functions
`sys32_unimplemented()` logs the current command, pid, and syscall number from `r20`, then returns `-ENOSYS`.

### Control Flow
The function is entered through compat syscall table holes and immediately reports the missing syscall before failing.

### State, Persistence, And Dependencies
No state is persisted. It depends on `current`, printk, and syscall table dispatch convention passing the syscall number as the final argument.

### Integration Points
Used by generated or hand-wired compat syscall tables for unsupported entries.

### Risks
Repeated unsupported calls can spam logs. The function assumes PA-RISC argument register ordering.

### Test Signals
Invoke an intentionally unimplemented compat syscall and confirm `-ENOSYS` plus a single understandable kernel log line.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/sys_parisc32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/syscall.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/syscall.S

### Purpose
`syscall.S` implements the PA-RISC Linux gateway page, regular syscall entry, ptrace-aware syscall dispatch, light-weight syscalls, syscall tables, and gateway-page lock table.

### Important APIs, Types, And Functions
Important labels include `linux_gateway_page`, `lws_entry`, `set_thread_pointer`, `linux_gateway_entry`, `syscall_nosys`, `tracesys`, `tracesys_exit`, `lws_start`, `lws_compare_and_swap32/64`, `lws_compare_and_swap_2`, `lws_atomic_xchg`, `lws_atomic_store`, `lws_table`, `sys_call_table`, `sys_call_table64`, and `lws_lock_start`.

### Control Flow
Userland enters the gateway page at fixed offsets. The syscall entry promotes privilege, switches space registers, handles 64-bit wide-mode/compat argument clipping, saves syscall state into `task->thread.regs`, saves FP/SAR state, chooses native or compat syscall tables, and branches to the syscall with a return pointer to `syscall_exit` or `syscall_exit_rfi`. The trace path saves a fuller register image, calls `do_syscall_trace_enter()`, dispatches or skips, then calls `do_syscall_trace_exit()`. LWS operations run on the gateway page without switching address spaces, validate arguments, hash the user address to an aligned lock, disable interrupts and page faults for critical sections, use exception table entries for user faults, and return errno/retry reason in PA-RISC ABI registers.

### State, Persistence, And Dependencies
Persistent state includes saved task registers, `cr27` thread pointer, generated syscall tables, and the 256-entry LWS lock table. Dependencies include `entry.S` return paths, ptrace/seccomp C helpers, generated syscall headers, exception table offsets relative to `linux_gateway_page`, and PA-RISC gateway privilege semantics.

### Integration Points
This is the central interface between userspace and the kernel, glibc fixed gateway offsets, VDSO trampolines, signal restart, ptrace, and atomic user helpers.

### Risks
Fixed offsets at `0xb0`, `0xe0`, and `0x100` are ABI. Register save/restore must match `pt_regs`, signal, ptrace, and syscall restart code. LWS critical sections must not sleep and must always release locks/pagefault disable state on every fault path.

### Test Signals
Run native and compat syscall suites, ptrace/seccomp/audit tracing, `rt_sigreturn` from syscall and interrupt contexts, glibc thread-pointer setup, LWS CAS/exchange/store success and EFAULT/EAGAIN paths, and syscall table generation checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/syscall.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/syscalls/Makefile -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/syscalls/Makefile

### Purpose
This Makefile generates PA-RISC UAPI syscall number headers and kernel syscall table headers from `syscall.tbl`.

### Important APIs, Types, And Functions
It defines `uapi`, `kapi`, `syscall`, `syshdr`, `systbl`, `quiet_cmd_syshdr`, `quiet_cmd_systbl`, `uapisyshdr-y`, `kapisyshdr-y`, `targets`, and the `all` phony target.

### Control Flow
The Makefile creates generated include directories, invokes `scripts/syscallhdr.sh` with `--emit-nr --abis common,$*`, invokes `scripts/syscalltbl.sh` with the same ABI selection, and builds 32-bit and 64-bit UAPI and kernel table headers.

### State, Persistence, And Dependencies
Generated files persist under `arch/$(SRCARCH)/include/generated/...`. Dependencies are Kbuild, `syscall.tbl`, and the shared syscall header/table scripts.

### Integration Points
`syscall.S` includes the generated `syscall_table_32.h` and `syscall_table_64.h`; userspace-facing headers include the generated `unistd_*.h`.

### Risks
ABI filtering must match PA-RISC table tags. Generated path prefixing with `../../../../` is Kbuild-sensitive.

### Test Signals
Build both 32-bit and 64-bit syscall headers, verify generated table sizes match `__NR_Linux_syscalls`, and confirm syscall.S includes resolve in native and compat builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/syscalls/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/time.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/time.c

### Purpose
`time.c` provides PA-RISC timer interrupt handling, clockevent/clocksource setup, sched_clock from CR16, persistent clock access, profile PC adjustment, and optional generic RTC support.

### Important APIs, Types, And Functions
Important state includes `cr16_clock_freq`, `clocktick`, `time_keeper_id`, and per-cpu `parisc_clockevent_device`. Main functions are `timer_interrupt()`, `parisc_timer_next_event()`, `parisc_clockevent_init()`, `profile_pc()`, `read_persistent_clock64()`, `read_cr16_sched_clock()`, `read_cr16()`, and `time_init()`.

### Control Flow
Timer interrupts reprogram periodic events and call the clockevent handler. Clockevent init configures per-CPU oneshot/periodic devices backed by CR16. `time_init()` derives CR16 frequency from PAGE0's 10ms calibration, registers sched_clock, clockevents, optional PAT 64-bit counter discovery, and the CR16 clocksource. RTC support proxies PDC TOD read/set through a platform `rtc-generic` device.

### State, Persistence, And Dependencies
Clock frequency, tick delta, timekeeper CPU, per-CPU clockevent devices, clocksource registration, and optional RTC platform device persist. Dependencies include PDC TOD/PAT calls, PAGE0, generic clockevents/clocksources, RTC core, and SMP CPU IDs.

### Integration Points
Used by IRQ timer handling, scheduler clock, profiling, CPU hotplug, and persistent clock initialization.

### Risks
CR16 is per-CPU, so hotplug and migration-sensitive timing need care. PDC TOD set has a 32-bit seconds limitation. `parisc_find_64bit_counter()` only logs discovery and does not register that counter.

### Test Signals
Boot clocksource selection, periodic and oneshot timer interrupts, high-resolution timers, CPU hotplug timer init, RTC read/set including invalid dates, and profiling around nullified instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/toc.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/toc.c

### Purpose
`toc.c` handles PA-RISC Transfer of Control events by converting firmware PIM data into `pt_regs`, printing diagnostics, optionally entering KGDB, and rebooting.

### Important APIs, Types, And Functions
It defines `toc_lock`, per-cpu `toc_stack`, `toc20_to_pt_regs()`, `toc11_to_pt_regs()`, `toc_intr()`, and early init `setup_toc()`.

### Control Flow
The assembly handler enters `toc_intr()` with a per-CPU stack-backed `pt_regs`. C code verifies the stack, fetches TOC PIM data through PDC depending on CPU generation, fills `pt_regs`, enters KGDB if configured, serializes `show_regs()` output, parks nonzero CPUs, waits for other CPUs to print, and restarts with reason `TOC`. Setup writes the physical TOC handler address and checksum into PAGE0.

### State, Persistence, And Dependencies
Persistent state includes PAGE0 TOC vector fields, handler checksum, per-CPU TOC stacks, and the output serialization lock. Dependencies include PDC PIM calls, KGDB, `show_regs()`, machine restart, and TOC assembly symbols.

### Integration Points
Installed as an early firmware-visible TOC vector; used for crash/debug transfer events.

### Risks
TOC runs in exceptional conditions with limited stack assumptions. The checksum and physical vector fields must match firmware rules. Secondary CPUs intentionally spin forever after printing.

### Test Signals
Firmware TOC injection, KGDB over TOC, multi-CPU backtrace serialization, PAGE0 vector checksum validation, and restart after monarch delay are the useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/toc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/toc_asm.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/toc_asm.S

### Purpose
`toc_asm.S` is the low-level firmware TOC handler that saves enough CPU state and switches to virtual kernel execution before calling `toc_intr()`.

### Important APIs, Types, And Functions
It exports `toc_handler`, `toc_handler_csum`, and `toc_handler_size`, and imports `toc_intr` and per-cpu `toc_stack`.

### Control Flow
The handler selects the per-CPU TOC stack on SMP, lays out and clears a `pt_regs`, saves FP registers, installs `swapper_pg_dir` into control registers, clears upper space registers, converts stack and argument pointers to virtual addresses, enables kernel virtual mapping, loads GP, and branches to `toc_intr()`.

### State, Persistence, And Dependencies
The handler's code bytes and checksum are consumed by firmware through PAGE0 fields set in `toc.c`. It depends on task CPU offsets, per-cpu offsets, page-table symbols, `virt_map`, and PA-RISC calling convention.

### Integration Points
Directly paired with `toc.c`; firmware enters this code on TOC.

### Risks
The checksum word is included in the firmware checksum span. Per-CPU stack selection depends on `cr30` still identifying the current task. Register save omissions limit what C can report.

### Test Signals
TOC injection on UP and SMP, FP register visibility in dumps, checksum acceptance by firmware, and successful transition from physical to virtual mode validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/toc_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/topology.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/topology.c

### Purpose
`topology.c` registers CPU devices and constructs PA-RISC package/core topology records.

### Important APIs, Types, And Functions
It defines per-cpu `cpu_devices`, `store_cpu_topology()`, and `init_cpu_topology()`.

### Control Flow
On first topology storage for a CPU, it marks the CPU hotpluggable when supported, registers the CPU device, initializes thread/core IDs, compares firmware `cpu_loc` values with online CPUs, assigns package IDs, updates sibling masks, and logs the resulting core/socket pair. Init resets all CPU topology state.

### State, Persistence, And Dependencies
Persistent state is `cpu_topology[]`, registered CPU devices, and sibling masks. Dependencies include per-cpu `cpu_data`, CPU hotplug locking assumptions, generic topology helpers, and firmware location values.

### Integration Points
Called from CPU probing and early boot topology initialization; `show_cpuinfo()` later reads generic topology values.

### Risks
Package/core inference is heuristic around `cpu_loc`, especially when firmware reports zero. Registration failures are warnings rather than fatal.

### Test Signals
SMP boot with multiple sockets/cores, CPU hotplug device registration, sibling masks, and `/proc/cpuinfo` physical/core IDs should be checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/traps.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/traps.c

### Purpose
`traps.c` handles PA-RISC hardware interruptions after low-level save code, producing signals, page faults, oops/panic diagnostics, breakpoints, FP emulation, and IVT initialization.

### Important APIs, Types, And Functions
Major routines include `show_regs()`, `show_stack()`, `die_if_kernel()`, `handle_break()`, `parisc_terminate()`, `handle_interruption()`, `initialize_ivt()`, and `early_trap_init()`.

### Control Flow
Register dump helpers print PSW/GPR/SR/IAOQ/IIR/ISR/IOR and unwind kernel stacks. `handle_interruption()` re-enables interrupts when appropriate, handles user-space space-ID abuse, dispatches machine checks, breakpoints, recovery/taken-branch traps, illegal/privileged instructions, FP assist, TLB/page faults, unaligned references, protection faults, and default SIGBUS/panic cases. It calls `do_page_fault()` for valid memory faults, `handle_unaligned()` for unaligned traps, `handle_fpe()` for assist exceptions, and exception fixups for kernel faults when allowed. Early trap init validates fault vectors and writes HPMC checksum fields.

### State, Persistence, And Dependencies
State includes ratelimiters, per-thread death flags, chassis status, IVT checksum words, and task signal/oops state. Dependencies include PDC/chassis, unwind, unaligned handler, math emulator, kprobes, KGDB, kfence, perf events, and page fault code.

### Integration Points
Central exception path for assembly trap vectors, page fault handling, debugging, oops reporting, and signal delivery.

### Risks
Trap code runs under hostile CPU state. Space/register checks protect gateway-page privilege transitions. Misclassifying kernel faults can panic instead of fix up, or vice versa. Early IVT checksum must satisfy firmware.

### Test Signals
Illegal instruction, breakpoints, kprobes, KGDB breaks, FP assist, page faults, unaligned access, HPMC/LPMC paths, kernel exception-table fixups, and early boot IVT validation are high-value tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/traps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/unaligned.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/unaligned.c

### Purpose
`unaligned.c` emulates supported unaligned PA-RISC load/store instructions or signals/fixes up failures.

### Important APIs, Types, And Functions
Public state and functions are `unaligned_enabled`, `no_unaligned_warning`, `handle_unaligned()`, and `check_unaligned()`. Internal helpers emulate halfword, word, doubleword, and floating load/store forms.

### Control Flow
The handler counts and reports alignment faults, honors per-thread user alignment-control flags, optionally rejects user unaligned access, decodes the trapped instruction to determine base modification and operation type, emulates memory access using space-register-aware inline assembly with exception table fixups, updates base registers for modifying forms, and nullifies the trapped instruction on success. Failures either use kernel exception fixups, send SIGSEGV/SIGBUS, or call `die_if_kernel()`.

### State, Persistence, And Dependencies
Global policy flags and per-thread flags control warnings and SIGBUS behavior. Dependencies include `pt_regs`, PA-RISC instruction encoding, exception table macros, perf alignment fault events, user access fault handling, and trap code.

### Integration Points
Called from `traps.c` for unaligned data reference traps and PCXS access-rights checks.

### Risks
Instruction decoding is complex and architecture-specific. 64-bit integer doubleword emulation is unavailable on 32-bit builds except FP paths. Emulation must preserve memory ordering and avoid sleeping in fault-sensitive contexts.

### Test Signals
User and kernel unaligned half/word/doubleword, FP load/store, modifying loads/stores, disabled unaligned policy, exception-table fixups, and ratelimited warnings should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/unaligned.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/unaligned.h -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/unaligned.h

### Purpose
`unaligned.h` declares the local PA-RISC unaligned-access handler interface.

### Important APIs, Types, And Functions
It forward-declares `struct pt_regs` and declares `handle_unaligned()` and `check_unaligned()`.

### Control Flow
No runtime control flow is present; it allows trap code to call the unaligned implementation without exposing internals.

### State, Persistence, And Dependencies
No state is defined. The declarations depend only on `struct pt_regs`.

### Integration Points
Included by `traps.c` and implemented by `unaligned.c`.

### Risks
The header is intentionally tiny; signature mismatches would be caught at compile time.

### Test Signals
Build coverage of `traps.c` plus runtime unaligned trap tests validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/unaligned.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/unwind.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/unwind.c

### Purpose
`unwind.c` implements PA-RISC kernel stack unwinding using `.PARISC.unwind` tables, module unwind tables, and special frame handling.

### Important APIs, Types, And Functions
Core APIs are `unwind_table_add()`, `unwind_table_remove()`, `unwind_init()`, `unwind_frame_init()`, `unwind_frame_init_from_blocked_task()`, `unwind_frame_init_task()`, `unwind_once()`, `unwind_to_user()`, and `return_address()`.

### Control Flow
Unwind tables are sorted and initialized with relocated region bounds. Lookup binary-searches the kernel table or scans module tables under a spinlock, moving hits to the front. Frame unwinding uses unwind entries to scan function prologues for frame growth and return-pointer saves, handles special frames such as interruption, syscall exit, interrupt return, context switch, and IRQ stack calls, and falls back to conservative stack scanning when no unwind entry exists.

### State, Persistence, And Dependencies
The kernel unwind table is static `__ro_after_init`; module tables are dynamically allocated in a locked list. Dependencies include linker-provided unwind sections, PA-RISC function descriptors, stack/task layout, ftrace, switch code symbols, and exception frame layouts.

### Integration Points
Used by stacktrace, oops printing, `__get_wchan()`, return-address helpers, and module load/unload unwind registration.

### Risks
Forced unwinding without metadata can miss modules or produce unreliable frames. Prologue instruction recognition must match compiler output. Blocked-task initialization allocates a temporary `pt_regs` with `GFP_ATOMIC`.

### Test Signals
Backtraces through interrupts, syscalls, context switches, modules, ftrace, and functions without unwind data should be compared against expected call chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/unwind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso.c

### Purpose
`vdso.c` maps the PA-RISC vDSO into new processes and initializes special mapping page lists for 32-bit and 64-bit vDSO images.

### Important APIs, Types, And Functions
Key items are `vdso32_start/end`, `vdso64_start/end`, `vdso_mremap()`, `vdso32_mapping`, `vdso64_mapping`, `arch_setup_additional_pages()`, `vdso_setup_pages()`, and `vdso_init()`.

### Control Flow
During exec, the code locks the mm, chooses 64-bit or compat vDSO image, randomizes the base near `mmap_base`, finds an unmapped area, installs a read/exec special mapping with may-write for debugger COW breakpoints, records `mm->context.vdso_base`, and unlocks. Init converts embedded image ranges into NULL-terminated `struct page **` arrays for special mappings.

### State, Persistence, And Dependencies
Persistent state includes per-mm `vdso_base` and static special mapping page arrays. Dependencies include ELF exec, mm locks, randomization, `get_unmapped_area()`, time namespaces includes, and wrapper-embedded VDSO images.

### Integration Points
Signal delivery uses VDSO symbol offsets relative to `vdso_base`; exec uses `arch_setup_additional_pages()`.

### Risks
Mapping failure cleanup currently calls `do_munmap()` for one page regardless of full vDSO length. Randomization is small. Incorrect image selection breaks compat signal and restart trampolines.

### Test Signals
Exec native and compat binaries, inspect `[vdso]` mapping permissions/base randomization, mremap vDSO, set debugger breakpoints, and deliver signals requiring VDSO trampolines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/Makefile -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/Makefile

### Purpose
This Makefile builds the 32-bit PA-RISC vDSO shared object, wrapper, and generated symbol-offset header.

### Important APIs, Types, And Functions
It defines `obj-vdso32`, `obj-cvdso32`, `VDSO_CFLAGS_REMOVE`, 32-bit compiler/linker flags, `VDSO_LIBGCC`, wrapper dependency on `vdso32.so`, and `include/generated/vdso32-offsets.h`.

### Control Flow
Kbuild assembles note/sigtramp/restart files, compiles `vdso32_generic.c` with VDSO-safe flags, links `vdso32.so` through `CROSS32CC` and `vdso32.lds`, builds `vdso32_wrapper.o` that incbins the shared object, and extracts `__kernel_*` offsets via `gen_vdso_offsets.sh`.

### State, Persistence, And Dependencies
Generated artifacts persist in the build tree. Dependencies include `lib/vdso/Makefile.include`, a working 32-bit cross compiler, libgcc, linker script, and Kbuild generated offsets.

### Integration Points
The wrapper contributes `vdso32_start/end` for `vdso.c`, and generated offsets feed signal code macros.

### Risks
Toolchain flags must avoid instrumentation and unsupported call models. Missing `CROSS32CC` breaks compat VDSO builds. Offset extraction only captures matching `__kernel_` symbols.

### Test Signals
Build with compat enabled, inspect exported symbol versions, verify offsets header, run VDSO signal/restart paths, and ensure no sanitizer/ftrace instrumentation appears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/gen_vdso_offsets.sh -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/gen_vdso_offsets.sh

### Purpose
This script converts `nm` output for the 32-bit vDSO into C preprocessor defines for vDSO symbol offsets.

### Important APIs, Types, And Functions
It uses a single `sed` expression to emit `#define vdso32_offset_<name> 0x<addr>` for symbols matching `__kernel_*`.

### Control Flow
The Makefile pipes `$(NM) vdso32.so` into the script, then sorts the output. The script sets `LC_ALL=C` and filters matching symbol lines.

### State, Persistence, And Dependencies
The generated header persists under `include/generated`. Dependencies are POSIX shell, sed, stable nm output, and vDSO symbol naming.

### Integration Points
Offsets are consumed by `VDSO32_SYMBOL()` users such as signal delivery.

### Risks
Only lowercase hexadecimal addresses and symbol type `.` lines match. Renaming trampoline symbols or changing nm output format silently drops defines.

### Test Signals
Run the Makefile rule and verify defines for sigtramp and restart syscall offsets are present and sorted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/gen_vdso_offsets.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/note.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/note.S

### Purpose
`note.S` emits ELF note metadata into the vDSO, currently including the kernel version.

### Important APIs, Types, And Functions
Macros `ASM_ELF_NOTE_BEGIN` and `ASM_ELF_NOTE_END` build a `.note.kernel-version` section with vendor `UTS_SYSNAME`, type 0, and `LINUX_VERSION_CODE`.

### Control Flow
Assembly emits note header sizes, vendor string, aligned payload, and restores the previous section.

### State, Persistence, And Dependencies
The note persists in the vDSO PT_NOTE segment. Dependencies include Linux version and uts headers plus linker script note placement.

### Integration Points
Included directly in the 32-bit vDSO and reused by the 64-bit note source.

### Risks
Alignment and size fields must match ELF note format or userland note parsing fails.

### Test Signals
Inspect `readelf -n` output for the 32-bit and 64-bit vDSO images and verify the kernel-version note.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/note.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/restart_syscall.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/restart_syscall.S

### Purpose
`restart_syscall.S` provides the vDSO trampoline used to restart interrupted syscalls.

### Important APIs, Types, And Functions
It exports `__kernel_restart_syscall`, compiled as either `__VDSO32__` or `__VDSO64__` through build flags.

### Control Flow
The trampoline loads the saved original return pointer from the user stack with 32-bit or 64-bit width, branches to the fixed gateway syscall entry at `0x100(%sr2,%r0)`, and loads `__NR_restart_syscall` into `%r20` in the delay slot.

### State, Persistence, And Dependencies
It consumes the saved return address planted by `insert_restart_trampoline()` in `signal.c`. Dependencies include syscall gateway fixed offset, stack layout, and generated syscall numbers.

### Integration Points
Used by both 32-bit and 64-bit vDSO builds and by signal restart handling.

### Risks
Stack layout must match signal.c for native and compat cases. The gateway offset is ABI-fixed.

### Test Signals
Interrupted syscalls returning `ERESTART_RESTARTBLOCK` should resume through this trampoline on both 32-bit and 64-bit tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/restart_syscall.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/sigtramp.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/sigtramp.S

### Purpose
`sigtramp.S` implements the 32-bit vDSO realtime signal-return trampoline and unwind metadata for debuggers.

### Important APIs, Types, And Functions
It exports `__kernel_sigtramp_rt`, embeds `SIGFRAME_CONTEXT_REGS32`, and emits `.eh_frame` CIE/FDE records with register save offsets.

### Control Flow
The trampoline contains two entry sequences: one for signals delivered outside syscalls and one for in-syscall delivery. Each loads `in_syscall` into `%r25`, loads `__NR_rt_sigreturn` into `%r20`, and branches to the fixed gateway entry. The unwind metadata describes where the 32-bit signal context registers live relative to `%sp`.

### State, Persistence, And Dependencies
The code lives in the mapped vDSO. It depends on exact offsets expected by GDB, `generated/asm-offsets.h`, the upward-growing PA-RISC signal frame, and syscall gateway ABI.

### Integration Points
`signal.c` selects this trampoline for compat or 32-bit tasks and may skip the first four instructions for in-syscall delivery.

### Risks
Comments warn GDB depends on exact instruction sequences and 64-byte alignment. Offset drift in signal frame structs breaks unwinding and sigreturn.

### Test Signals
Deliver signals to 32-bit tasks, run GDB backtraces through handlers, test in-syscall and interrupt-context returns, and inspect `.eh_frame`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/sigtramp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/vdso32.lds.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/vdso32.lds.S

### Purpose
`vdso32.lds.S` defines the ELF32 PA-RISC vDSO link layout, program headers, discarded sections, and exported symbol version set.

### Important APIs, Types, And Functions
It sets `OUTPUT_FORMAT("elf32-hppa-linux")`, `OUTPUT_ARCH(hppa)`, base address `VDSO_LBASE`, PT_LOAD/PT_NOTE/PT_DYNAMIC/PT_GNU_EH_FRAME program headers, and version exports for sigtramp, restart, gettimeofday, clock_gettime, and clock_gettime64.

### Control Flow
The linker places hash/dynamic symbol sections, note, text, rodata, unwind frames, dynamic/PLT/GOT, debug-only zero-address sections, and discards writable/bss/stack-note inputs.

### State, Persistence, And Dependencies
The linked shared object layout persists in `vdso32.so`. Dependencies include `asm/vdso.h`, page constants, Kbuild compile flags, and vDSO source symbol names.

### Integration Points
Used by the vDSO32 Makefile and consumed by the wrapper object and user dynamic linker.

### Risks
Export names include suffixed aliases expected by `VDSO32_SYMBOL()`/offset generation. Accidentally retaining writable data would violate vDSO mapping assumptions.

### Test Signals
Use `readelf -l -s -V` on `vdso32.so`, verify exported symbol versions and no writable load segment or bss/data payload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/vdso32.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/vdso32_generic.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/vdso32_generic.c

### Purpose
`vdso32_generic.c` provides 32-bit vDSO time symbols as syscall fallbacks.

### Important APIs, Types, And Functions
It defines `__vdso_gettimeofday()`, `__vdso_clock_gettime()`, and `__vdso_clock_gettime64()`, each using `syscall2()`.

### Control Flow
Each function directly invokes the matching syscall number with casted pointer arguments and returns the syscall result.

### State, Persistence, And Dependencies
No state is persisted. Dependencies include PA-RISC vDSO syscall helpers, UAPI syscall numbers, and time structure forward declarations.

### Integration Points
Exported from `vdso32.so` through the linker script for libc fast-path lookup, though these implementations still trap to the kernel.

### Risks
These are not true userspace time reads, so performance is syscall-bound. Type declarations must match the 32-bit ABI, especially `clock_gettime64`.

### Test Signals
Call all vDSO time symbols from 32-bit userspace and compare return values/errors with direct syscalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/vdso32_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/vdso32_wrapper.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/vdso32_wrapper.S

### Purpose
`vdso32_wrapper.S` embeds the built 32-bit vDSO shared object into the kernel image.

### Important APIs, Types, And Functions
It exports page-aligned `vdso32_start` and `vdso32_end` symbols and `.incbin`s `arch/parisc/kernel/vdso32/vdso32.so`.

### Control Flow
Assembly emits page alignment, includes the binary vDSO, aligns the end to a page, and returns to the previous section.

### State, Persistence, And Dependencies
The embedded vDSO bytes persist in kernel data. Dependencies include `vdso32.so` build ordering and page alignment.

### Integration Points
`vdso.c` uses `vdso32_start/end` to build special mapping page lists.

### Risks
The incbin path is build-tree sensitive and requires the Makefile dependency to avoid stale objects. Page alignment controls mapping size.

### Test Signals
Build dependency checks, symbol addresses, page-aligned size, and successful mapping in 32-bit processes validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso32/vdso32_wrapper.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/Makefile -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/Makefile

### Purpose
This Makefile builds the 64-bit PA-RISC vDSO shared object, wrapper, and generated symbol-offset header.

### Important APIs, Types, And Functions
It defines `obj-vdso64`, `obj-cvdso64`, instrumentation-disabling flags, `VDSO_LIBGCC` from `$(CC)`, wrapper dependency, linker/assembler/compiler commands, and `include/generated/vdso64-offsets.h`.

### Control Flow
Kbuild assembles note/sigtramp/restart objects, compiles `vdso64_generic.c`, links `vdso64.so` with `vdso64.lds`, builds the incbin wrapper, and extracts sorted offsets for `__kernel_*` symbols.

### State, Persistence, And Dependencies
Generated artifacts persist in the build tree. Dependencies include the native 64-bit compiler, linker script, `lib/vdso/Makefile.include`, and `gen_vdso_offsets.sh`.

### Integration Points
The wrapper supplies `vdso64_start/end` to `vdso.c`; generated offsets support native signal/restart trampoline lookup.

### Risks
Instrumentation must stay disabled for vDSO code. `CPPFLAGS_vdso64.lds` undefines `$(ARCH)`, so preprocessing assumptions matter. Offset generation depends on symbol naming.

### Test Signals
Native 64-bit builds should verify `vdso64.so`, offsets header contents, exported symbol versions, and absence of ftrace/sanitizer instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/gen_vdso_offsets.sh -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/gen_vdso_offsets.sh

### Purpose
This script converts 64-bit vDSO `nm` output into offset defines.

### Important APIs, Types, And Functions
Its sed rule emits `#define vdso64_offset_<name> 0x<addr>` for matching `__kernel_*` symbols.

### Control Flow
The Makefile pipes `NM` output into the script and sorts the result under `LC_ALL=C`.

### State, Persistence, And Dependencies
The output header persists in `include/generated`. Dependencies are shell, sed, nm symbol format, and `__kernel_` symbol names.

### Integration Points
Used by native VDSO symbol lookup macros in signal and restart paths.

### Risks
The matching pattern is narrow; symbol type or address formatting changes can drop needed defines.

### Test Signals
Generated header should include sigtramp and restart syscall offsets after a 64-bit vDSO build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/gen_vdso_offsets.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/note.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/note.S

### Purpose
`vdso64/note.S` reuses the 32-bit vDSO note implementation for the 64-bit vDSO.

### Important APIs, Types, And Functions
It includes `../vdso32/note.S`, thereby emitting the same kernel-version ELF note macros and data.

### Control Flow
All assembly emission is delegated to the included source.

### State, Persistence, And Dependencies
The note persists in `vdso64.so`. Dependencies are the relative include path and the shared note implementation.

### Integration Points
Built by the vDSO64 Makefile and placed by `vdso64.lds.S`.

### Risks
Changes to the 32-bit note source affect both vDSOs. Relative include path must remain valid.

### Test Signals
`readelf -n vdso64.so` should show the same kernel-version note as the 32-bit vDSO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/note.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/restart_syscall.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/restart_syscall.S

### Purpose
`vdso64/restart_syscall.S` reuses the common restart-syscall trampoline for the 64-bit vDSO.

### Important APIs, Types, And Functions
It includes `../vdso32/restart_syscall.S`, compiled with `__VDSO64__` to select 64-bit load width.

### Control Flow
Runtime control is the included trampoline: load saved return pointer and branch through gateway offset `0x100` with `__NR_restart_syscall`.

### State, Persistence, And Dependencies
Consumes the saved return pointer planted by signal restart code. Depends on the shared source and 64-bit vDSO build flags.

### Integration Points
Exported from `vdso64.so` and used by `signal.c` for native restart-block syscalls.

### Risks
Correctness depends on `__VDSO64__` being defined and native stack layout matching `signal.c`.

### Test Signals
Native 64-bit interrupted syscall restart tests should pass through this trampoline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/restart_syscall.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/sigtramp.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/sigtramp.S

### Purpose
`sigtramp.S` implements the 64-bit vDSO realtime signal-return trampoline and debugger unwind metadata.

### Important APIs, Types, And Functions
It exports `__kernel_sigtramp_rt`, embeds `SIGFRAME_CONTEXT_REGS`, and emits `.eh_frame` entries with 64-bit data alignment and register save offsets.

### Control Flow
Two instruction sequences load `in_syscall` as 0 or 1, set `%r20` to `__NR_rt_sigreturn`, and branch to the fixed syscall gateway. The FDE describes where GPRs, FP registers, SAR, and IAOQ are saved in the 64-bit signal frame.

### State, Persistence, And Dependencies
The trampoline and `.eh_frame` live in `vdso64.so`. Dependencies include exact signal frame offsets, GDB expectations, PA-RISC gateway ABI, and generated asm offsets.

### Integration Points
Selected by `signal.c` for native 64-bit handlers through `VDSO64_SYMBOL(current, sigtramp_rt)`.

### Risks
Instruction order and alignment are ABI/debugger-sensitive. Frame offset drift will break unwinding and possibly sigreturn.

### Test Signals
Native 64-bit signal delivery, GDB unwinding through handlers, syscall-interrupted handlers, and `readelf --debug-dump=frames` are useful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/sigtramp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/vdso64.lds.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/vdso64.lds.S

### Purpose
`vdso64.lds.S` defines the ELF64 PA-RISC vDSO link layout, program headers, discarded sections, and symbol version exports.

### Important APIs, Types, And Functions
It sets `OUTPUT_FORMAT("elf64-hppa-linux")`, `OUTPUT_ARCH(hppa:hppa2.0w)`, VDSO base placement, PT_LOAD/PT_NOTE/PT_DYNAMIC/PT_GNU_EH_FRAME headers, and exports sigtramp, restart, gettimeofday, and clock_gettime symbols.

### Control Flow
The linker places dynamic symbol/hash sections, note, text, rodata, unwind frames, dynamic/PLT/GOT, debug sections, and discards writable data/BSS/stack notes.

### State, Persistence, And Dependencies
The resulting layout persists in `vdso64.so`. Dependencies include `asm/vdso.h`, vDSO source symbol names, and the 64-bit PA-RISC ABI.

### Integration Points
Used by the vDSO64 Makefile and user dynamic linking of the `[vdso]` image.

### Risks
Writable sections must remain discarded. Exported names with `64` suffixes must match offset generation and kernel lookup macros.

### Test Signals
Inspect program headers, symbol versions, exported symbols, and absence of writable LOAD data with `readelf`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/vdso64.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/vdso64_generic.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/vdso64_generic.c

### Purpose
`vdso64_generic.c` provides native 64-bit vDSO time symbols as syscall fallbacks.

### Important APIs, Types, And Functions
It defines `__vdso_gettimeofday()` and `__vdso_clock_gettime()`, both implemented with `syscall2()`.

### Control Flow
Each exported function casts pointer arguments to `long`, invokes the corresponding syscall number, and returns the result.

### State, Persistence, And Dependencies
No state is persisted. Dependencies include PA-RISC vDSO syscall helpers, syscall numbers, and kernel time structure ABI declarations.

### Integration Points
Exported from `vdso64.so` for libc resolver use; execution still enters the kernel gateway.

### Risks
These are syscall wrappers rather than true data-page time fast paths. ABI type mismatch would surface in libc time calls.

### Test Signals
Compare vDSO gettimeofday/clock_gettime results and errno behavior with direct syscalls on native 64-bit tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/vdso64_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/vdso64_wrapper.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/vdso64_wrapper.S

### Purpose
`vdso64_wrapper.S` embeds the built 64-bit vDSO shared object into the kernel image.

### Important APIs, Types, And Functions
It exports page-aligned `vdso64_start` and `vdso64_end` symbols and `.incbin`s `arch/parisc/kernel/vdso64/vdso64.so`.

### Control Flow
Assembly aligns the start, includes the vDSO binary, aligns the end to a page, and restores the previous section.

### State, Persistence, And Dependencies
The embedded image persists in kernel data. Dependencies include Makefile build ordering, incbin path, and page alignment.

### Integration Points
`vdso.c` turns this range into special mapping pages for native 64-bit processes.

### Risks
Stale or missing `vdso64.so` would embed wrong bytes. Alignment controls mapping length.

### Test Signals
Check wrapper dependencies, `vdso64_start/end` page alignment, and successful `[vdso]` mapping in native processes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/vdso64_wrapper.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vmlinux.lds.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vmlinux.lds.S

### Purpose
`vmlinux.lds.S` defines the PA-RISC kernel image link layout, including init sections, text/data/BSS, GP/linkage tables, unwind tables, alignment constraints, and discarded sections.

### Important APIs, Types, And Functions
It sets output format/architecture, entry `parisc_kernel_start`, `jiffies` aliasing, `BSS_FIRST_SECTIONS`, long-call keep/discard macros, `_text/_stext/_etext`, `_sdata/_edata/_end`, `__start___unwind`, `__stop___unwind`, and 64-bit `.opd/.plt/.dlt` placement with `__gp`.

### Control Flow
The linker starts at `KERNEL_BINARY_TEXT_START`, emits init text/data/percpu/alternatives, aligns to huge pages, emits main text and RO data, places GP-sensitive linkage tables before RO data on 64-bit, emits `.PARISC.unwind`, writable data, lock-aligned data, BSS with page tables first, debug/modinfo/ELF details, notes, and architecture-specific discards.

### State, Persistence, And Dependencies
All kernel section addresses and linker-provided symbols persist in the final image. Dependencies include generic `vmlinux.lds.h`, PA-RISC cache/page/thread constants, unwind code, boot code, and binutils behavior.

### Integration Points
Consumed by boot, unwind initialization, alternatives, percpu setup, BSS/page-table assumptions, and module/debug metadata.

### Risks
`swapper_pg_dir` must remain first in BSS. `__gp` must stay below architectural limits. Section alignment impacts hugepage mapping, cache behavior, and early boot reachability.

### Test Signals
Link both 32-bit and 64-bit kernels, inspect section addresses, verify unwind symbols, boot with alternatives/percpu/BSS, and check no unwanted dynamic sections in static 64-bit images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/Makefile -->
## sources/distributed-fs/ceph-client/arch/parisc/lib/Makefile

### Purpose
This Makefile selects PA-RISC architecture library objects for built-in archive and object linkage.

### Important APIs, Types, And Functions
`lib-y` includes `lusercopy.o`, `bitops.o`, `io.o`, `memset.o`, `memcpy.o`, `ucmpdi2.o`, and `delay.o`; `obj-y` includes `iomap.o`.

### Control Flow
Kbuild compiles listed library sources into the architecture library or built-in objects according to `lib-y`/`obj-y`.

### State, Persistence, And Dependencies
No runtime state. Build output persists in the kernel build tree. Dependencies are Kbuild object classification and source availability.

### Integration Points
These objects provide low-level copy, memory, atomic, I/O, compare, delay, and iomap helpers used throughout the PA-RISC kernel.

### Risks
Moving helpers between `lib-y` and `obj-y` can affect link order/export availability. Missing objects cause architecture-wide build failures.

### Test Signals
Full PA-RISC build and symbol resolution for atomic, delay, memcpy/usercopy, and I/O helper references validate this Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/bitops.c -->
## sources/distributed-fs/ceph-client/arch/parisc/lib/bitops.c

### Purpose
`bitops.c` implements out-of-line atomic exchange and compare-exchange helpers for PA-RISC.

### Important APIs, Types, And Functions
On SMP it defines aligned `__atomic_hash`. It implements `__xchg64()` on 64-bit builds, `__xchg32()`, `__xchg8()`, and macro-generated `__cmpxchg_u64/u32/u16/u8()`.

### Control Flow
Each helper hashes/locks through `_atomic_spin_lock_irqsave(ptr, flags)`, reads the previous value, optionally writes the new value, unlocks with IRQ restore, and returns the previous value.

### State, Persistence, And Dependencies
The SMP hash lock table persists globally. Dependencies include PA-RISC atomic spinlock helpers, IRQ flag save/restore, and architecture inline atomic APIs that call these out-of-line functions.

### Integration Points
Used by generic atomics and synchronization primitives when operations are too large to inline or require hashed locking.

### Risks
`__xchg32()` and `__xchg8()` sign-extend through `long temp`, noted in comments. Hash-lock granularity can serialize unrelated addresses. Correct 16-byte lock alignment is required by PA-RISC locking instructions.

### Test Signals
Atomic exchange/cmpxchg tests for all widths, SMP contention, IRQ-disabled callers, and sign/zero extension expectations should be run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/bitops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/delay.c -->
## sources/distributed-fs/ceph-client/arch/parisc/lib/delay.c

### Purpose
`delay.c` implements precise busy-wait microsecond delays using PA-RISC CR16.

### Important APIs, Types, And Functions
`__cr16_delay()` performs cycle-based waiting and `__udelay()` converts microseconds using `boot_cpu_data.cpu_hz`; `__udelay` is exported.

### Control Flow
The delay loop disables preemption, records CR16 and CPU ID, polls until elapsed cycles exceed the requested loop count, periodically enables preemption to allow RT tasks, and compensates if migration to a different CPU occurs by subtracting elapsed cycles and restarting from the new CPU's CR16. `__udelay()` multiplies microseconds by CPU Hz per microsecond.

### State, Persistence, And Dependencies
No persistent mutable state. It depends on per-CPU CR16 counters, `boot_cpu_data.cpu_hz`, preemption control, and `smp_processor_id()`.

### Integration Points
Used by generic delay APIs and firmware/driver timing paths.

### Risks
CR16 is per-CPU and may differ between CPUs, so migration compensation is necessary but can extend delays. Large delays on 32-bit builds risk rollover, bounded by generic maximum delay settings.

### Test Signals
Delay calibration, RT preemption behavior, CPU migration during delay, and measured minimum delay length under SMP validate the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/delay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/io.c -->
## sources/distributed-fs/ceph-client/arch/parisc/lib/io.c

### Purpose
`io.c` provides non-inlined PA-RISC port I/O string helpers for byte, word, and long transfers.

### Important APIs, Types, And Functions
It implements and exports `insb()`, `insw()`, `insl()`, `outsb()`, `outsw()`, and `outsl()`.

### Control Flow
Input helpers read repeated port values with `inb/inw/inl`, pack little-endian data, and store into destination buffers while handling 8-, 16-, and 32-bit alignments. Output helpers unpack source buffers according to alignment and write repeated values with `outb/outw/outl`. Word and long helpers use special cases to avoid unaligned stores/loads and improve IDE-sector transfer performance.

### State, Persistence, And Dependencies
No state is persisted. Dependencies include `asm/io.h`, endian conversion helpers, exported symbol infrastructure, and caller-provided port/buffer/count contracts.

### Integration Points
Used by drivers needing port string I/O on PA-RISC, especially legacy IDE-style transfers where inline accessors were insufficient.

### Risks
Alignment case logic is intricate and manually packs bytes. Some paths decrement `count` after checking nonzero; callers must pass counts matching element width. Endianness conversions must preserve device-visible little-endian ordering.

### Test Signals
Port I/O loopback or emulated device tests should cover every source/destination alignment, odd counts, zero counts, byte/word/long transfers, and exported module use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/lib/io.c -->
