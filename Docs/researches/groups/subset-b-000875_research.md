# Research: subset-b-000875

Grouped source research for x86 Ceph client kernel headers. Each section is source-tree aligned and delimited for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/topology.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/topology.h

Purpose: x86 topology declarations for NUMA, SMT/core/package hierarchy, scheduler capacity, PCI root-bus locality, and hybrid CPU classification. It bridges generic Linux topology helpers with x86 CPU metadata in `cpu_data(cpu).topo`.

Important APIs/types/functions: `enum x86_topology_domains`, `enum x86_topology_cpu_type`, `struct x86_topology_system`, `x86_topo_system`, `topology_get_domain_size()`, `topology_get_domain_shift()`, `cpu_coregroup_mask()`, `cpu_clustergroup_mask()`, topology access macros for package/die/core IDs, `topology_get_logical_id()`, `topology_is_primary_thread()`, `topology_get_primary_thread()`, `topology_is_core_online()`, `x86_pci_root_bus_node()`, ITMT scheduler hooks, and frequency/capacity scaling hooks.

Control flow: the header is mostly inline dispatch and configuration gating. NUMA builds use early per-CPU CPU-to-node maps and node cpumasks; non-NUMA builds collapse everything to node 0. SMP builds expose sibling/core/cluster/die masks, SMT counts, and AMD node data; uniprocessor builds return conservative constants. Local APIC builds can map APIC topology IDs; otherwise logical IDs collapse to zero.

State/persistence: state is boot-discovered and held in extern globals/per-CPU maps: `x86_topo_system`, max package/die/thread counters, node cpumasks, `__cpu_primary_thread_mask`, ITMT priorities, and scheduler capacity/frequency values. The header does not persist data itself, but exposes long-lived topology state consumed by scheduler, NUMA, PCI, and CPU hotplug paths.

Dependencies/integration: depends on `linux/numa.h`, `linux/cpumask.h`, `asm/mpspec.h`, per-CPU support, APIC, scheduler MC priority, static keys, and generic topology. It integrates with sched domains, CPU capacity scaling, PCI resource discovery, and architecture-specific CPU enumeration.

Risks/test signals: wrong domain shifts or cpumasks can misplace scheduler domains, NUMA locality, PCI locality, and hybrid capacity decisions. Test via x86 boot on NUMA/non-NUMA, SMT on/off, CPU hotplug, hybrid Intel systems, AMD multi-node packages, `lscpu` topology checks, scheduler tracepoints, and PCI root-bus NUMA node validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/trace/fpu.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/trace/fpu.h

Purpose: defines x86 FPU tracepoints for observing FPU save/load/register activation and xstate validation events.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(x86_fpu)` and events `x86_fpu_before_save`, `x86_fpu_after_save`, `x86_fpu_regs_activated`, `x86_fpu_regs_deactivated`, `x86_fpu_dropped`, `x86_fpu_copy_dst`, and `x86_fpu_xstate_check_failed`.

Control flow: each event accepts `struct fpu *`, records the current `TIF_NEED_FPU_LOAD` state, and, when `X86_FEATURE_OSXSAVE` is available, reads `xfeatures` and `xcomp_bv` from the task fpstate xsave header. The trace include macros route generated code through `trace/define_trace.h`.

State/persistence: no persistent state is owned here. The trace payload snapshots FPU pointer, lazy-load flag, and xsave header fields at event emission time.

Dependencies/integration: depends on Linux tracepoint infrastructure, thread flags, CPU feature checks, and FPU/xstate internals. Integrated by FPU management code around save/restore and error paths.

Risks/test signals: instrumentation must not dereference xsave fields unless OSXSAVE exists. Trace output should be checked with ftrace/perf while exercising FPU-heavy workloads, fork/exec, signal delivery, lazy FPU load, and xstate corruption/error handling paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/trace/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/trace/hyperv.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/trace/hyperv.h

Purpose: Hyper-V tracepoint definitions for TLB flush, nested guest mapping flush, and IPI send operations on x86 guests.

Important APIs/types/functions: `hyperv_mmu_flush_tlb_multi`, `hyperv_nested_flush_guest_mapping`, `hyperv_nested_flush_guest_mapping_range`, `hyperv_send_ipi_mask`, and `hyperv_send_ipi_one`.

Control flow: tracepoints are compiled only when `CONFIG_HYPERV` is enabled. TLB flush tracing records CPU mask weight plus `flush_tlb_info` memory range and mm pointer. Nested flush events record address space and return code. IPI events record target CPU count or single CPU plus vector.

State/persistence: no owned state; events snapshot arguments from Hyper-V MMU and interrupt calls. Return codes are captured for diagnosing hypercall failures.

Dependencies/integration: depends on `linux/tracepoint.h`, `cpumask`, `flush_tlb_info`, Hyper-V MMU and IPI implementation files, and the generated trace header path `asm/trace/hyperv`.

Risks/test signals: incorrect trace fields would mislead virtualization debugging but should not alter behavior. Test by enabling tracepoints on Hyper-V guests under TLB shootdown, nested virtualization mapping flush, and synthetic IPI traffic; verify CPU counts, ranges, vectors, and return codes match the caller paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/trace/hyperv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/trace/irq_vectors.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/trace/irq_vectors.h

Purpose: tracepoint definitions for x86 local APIC vector handlers and IRQ vector allocation/lifecycle operations.

Important APIs/types/functions: `DECLARE_EVENT_CLASS(x86_irq_vector)`, `DEFINE_IRQ_VECTOR_EVENT()`, entry/exit events for local timer, spurious APIC, error APIC, platform IPI, IRQ work, reschedule, call-function vectors, MCE/thermal vectors, plus `vector_config`, `vector_update`, `vector_clear`, reserve/alloc/activate/deactivate/teardown/setup/free-moved events.

Control flow: when `CONFIG_X86_LOCAL_APIC` is enabled, shared event classes capture vector numbers and IRQ/vector/cpu/apic destination transitions. Optional blocks follow IRQ work, SMP, MCE, AMD deferred error, and thermal-vector configs. `irq_work_exit` denies sampling perf events to prevent recursive irq_work generation.

State/persistence: no persistent state; the payload records the live vector allocator and interrupt-handler state passed by IRQ/APIC code.

Dependencies/integration: depends on Linux tracepoints, APIC vector management, SMP IPI code, perf sampling permission hooks, and generated trace include conventions.

Risks/test signals: the main risk is tracing recursion or stale event schemas for IRQ allocation debugging. Test with ftrace/perf enabled during IRQ affinity changes, managed IRQ allocation, CPU hotplug, timer/IPI interrupts, irq_work, and APIC error/spurious paths; verify the perf sampling permission on `irq_work_exit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/trace/irq_vectors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/trace_clock.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/trace_clock.h

Purpose: exposes an architecture trace clock backed by the x86 TSC when TSC support is configured.

Important APIs/types/functions: `trace_clock_x86_tsc()` and `ARCH_TRACE_CLOCKS`.

Control flow: `CONFIG_X86_TSC` builds register `{ trace_clock_x86_tsc, "x86-tsc", .in_ns = 0 }` with generic trace clock infrastructure. Non-TSC builds define no x86-specific trace clocks.

State/persistence: no owned state. The clock reads TSC-derived time from the implementation declared elsewhere.

Dependencies/integration: depends on compiler/types headers and the trace clock registry. It integrates with ftrace/perf timestamp selection.

Risks/test signals: TSC reliability and cross-CPU synchronization determine trace ordering quality. Test by selecting the `x86-tsc` trace clock, running multi-CPU tracing, and comparing event ordering against stable clocks on systems with stable and unstable TSCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/trace_clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/trap_pf.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/trap_pf.h

Purpose: names x86 page-fault error-code bits used by fault handlers and diagnostics.

Important APIs/types/functions: `enum x86_pf_error_code` with `X86_PF_PROT`, `WRITE`, `USER`, `RSVD`, `INSTR`, `PK`, `SHSTK`, `SGX`, and `RMP`.

Control flow: none; this is a constants header. Fault handlers decode hardware-provided error code bits using these masks.

State/persistence: no state.

Dependencies/integration: depends on `linux/bits.h`. Integrated with page fault, signal, KVM/TDX/SEV, SGX, protection-key, and control-flow enforcement paths.

Risks/test signals: wrong bit assignments would misclassify protection, user/kernel, instruction-fetch, shadow-stack, SGX, or RMP faults. Test via page-fault selftests, pkeys, CET/shadow stack tests, SGX/SEV-SNP paths where available, and fault log decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/trap_pf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/trapnr.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/trapnr.h

Purpose: defines x86 event-type codes and exception/trap vector numbers.

Important APIs/types/functions: `EVENT_TYPE_*` constants and `X86_TRAP_*` values for divide error, debug, NMI, breakpoint, overflow, invalid opcode, device-not-available, double fault, TSS, segment, general protection, page fault, machine check, SIMD FP, virtualization/control-protection/VC, and IRET exception.

Control flow: none; hardware and virtualization entry/exit code use these constants to classify events.

State/persistence: no state.

Dependencies/integration: used by IDT/FRED, Intel VT-x, AMD SVM, trap handlers, signal delivery, tracing, and exception fixup paths.

Risks/test signals: constants are ABI-like architecture facts; changes would break exception dispatch and virtualization injection. Test through exception selftests, KVM event injection, FRED/legacy IDT builds, debug/breakpoint handling, and page-fault/machine-check smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/trapnr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/traps.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/traps.h

Purpose: declares x86 trap helper entry points and small inline helpers for signal codes and IRQ restoration around trap handling.

Important APIs/types/functions: `sync_regs()`, `fixup_bad_iret()`, `vc_switch_off_ist()`, `ibt_selftest()`, `handle_invalid_op()`, `handle_bug()`, `get_si_code()`, `math_emulate()`, `fault_in_kernel_space()`, `handle_stack_overflow()`, `cond_local_irq_enable()`, and `cond_local_irq_disable()`.

Control flow: trap code calls architecture helpers to synchronize register frames, fix bad IRET frames, switch off IST for #VC, run IBT selftests, emulate legacy math, handle stack overflow, and conditionally restore interrupt state based on saved `X86_EFLAGS_IF`. `get_si_code()` maps debug register condition bits to ptrace/signal trap codes.

State/persistence: no owned persistent state. It operates on `pt_regs`, debug register condition bits, and stack metadata passed by trap handlers.

Dependencies/integration: depends on context tracking, kprobes, debugreg, IDT entry annotations, siginfo constants, and page-fault masks. Integrated with exception entry assembly/C handlers, KASAN/vmap stack handling, signal delivery, and kprobe/BUG handling.

Risks/test signals: interrupt-state restoration and register-frame fixups are correctness-critical for traps returning to user or kernel mode. Test with x86 exception selftests, kprobes, BUG/UD2 handling, bad IRET tests, VMAP stack overflow tests, #VC on encrypted guests, and debug register signal-code checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/traps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tsc.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/tsc.h

Purpose: declares and inlines x86 timestamp counter access, calibration, reliability, synchronization, and scheduler-clock helpers.

Important APIs/types/functions: `rdtsc()`, `rdtsc_ordered()`, `cycles_t`, `get_cycles()`, `cpu_khz`, `tsc_khz`, `disable_TSC()`, `tsc_early_init()`, `tsc_init()`, `mark_tsc_unstable()`, `unsynchronized_tsc()`, `check_tsc_unstable()`, `native_calibrate_cpu_early()`, `native_calibrate_tsc()`, `native_sched_clock_from_tsc()`, TSC adjust verification helpers, suspend/resume sched-clock state helpers, and `cpu_khz_from_msr()`.

Control flow: `rdtsc()` emits raw unordered RDTSC. `rdtsc_ordered()` uses alternatives to prefer `lfence; rdtsc` or `rdtscp` based on CPU features. `get_cycles()` returns 0 if TSC is unavailable in non-TSC builds, otherwise raw cycles. Boot and resume code use the extern initialization/synchronization helpers.

State/persistence: timing state lives in extern frequency globals, reliability flags, and TSC adjust/async-reset state. The header itself only declares accessors and low-level inline assembly reads.

Dependencies/integration: depends on asm alternative/cpufeature/MSR/processor support. Integrated with clocksource, sched_clock, delay calibration, tracing, and CPU synchronization checks.

Risks/test signals: ordering, feature alternatives, and TSC synchronization affect time monotonicity and scheduler/trace timestamps. Test on CPUs with/without RDTSCP/LFENCE_RDTSC, multi-socket systems, suspend/resume, CPU hotplug, `notsc`, clocksource watchdog, and sched_clock monotonicity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/uaccess.h

Purpose: central x86 user-memory access interface for scalar `get_user`/`put_user`, unsafe access regions, kernel nofault access, user cmpxchg, NMI copy, string helpers, machine-check copy, and nontemporal copy support.

Important APIs/types/functions: `get_user()`, `__get_user()`, `put_user()`, `__put_user()`, `user_access_begin()`, `user_access_end()`, `arch_unsafe_get_user()`, `arch_unsafe_put_user()`, `unsafe_try_cmpxchg_user()`, `__try_cmpxchg_user()`, `unsafe_copy_to_user()`, `arch_get_kernel_nofault()`, `arch_put_kernel_nofault()`, `copy_from_user_nmi()`, `strncpy_from_user()`, `strnlen_user()`, and optional `copy_mc_to_kernel()/copy_mc_to_user()`.

Control flow: public scalar accessors run `might_fault()` and call size-specialized assembly thunks or inline asm. Access windows use `stac()`/`clac()` with `barrier_nospec()` after `access_ok()`. Faulting load/store/cmpxchg instructions are paired with exception-table fixups to branch to error labels or produce `-EFAULT`. Compile-time branches handle asm-goto output capabilities and 32-bit/64-bit 8-byte operations.

State/persistence: no persistent state is owned. It temporarily changes SMAP AC state, records instrumentation hooks, updates caller-provided output variables, and may update old-value pointers for failed cmpxchg.

Dependencies/integration: depends on compiler instrumentation, KASAN, MM types, SMAP, exception tables, TLB/user address helpers, `uaccess_32.h` or `uaccess_64.h`, and generic `access_ok`. It is used by syscalls, ptrace, signal handling, procfs, filesystems, BPF, and most kernel/user copy boundaries.

Risks/test signals: this is security-critical. Risks include missing `access_ok()`, unbalanced `stac/clac`, wrong exception-table type, speculative bypass, bad register constraints, missing instrumentation, and width/sign-extension bugs. Test with LKDTM/usercopy, fault-injection, KASAN/KMSAN, hardened usercopy, 32-bit compat, pagefault-disabled paths, `copy_from_user_nmi`, cmpxchg futex-style paths, and compiler matrix with/without asm-goto output support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uaccess_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/uaccess_32.h

Purpose: 32-bit x86 raw user-copy declarations and wrappers used by the common uaccess layer.

Important APIs/types/functions: `__copy_user_ll()`, `__copy_from_user_ll_nocache_nozero()`, `raw_copy_to_user()`, `raw_copy_from_user()`, `copy_from_user_inatomic_nontemporal()`, `clear_user()`, and `__clear_user()`.

Control flow: raw copy wrappers force-cast user pointers and delegate to low-level assembly copy routines. Clearing and nontemporal copy are declared for architecture implementations.

State/persistence: no state; functions return the number of uncopied bytes.

Dependencies/integration: depends on string/page/asm helpers and is included only under `CONFIG_X86_32` by `uaccess.h`.

Risks/test signals: 32-bit copy semantics must match generic usercopy expectations, especially returned residual counts and nozero behavior. Test i386 builds, compat-heavy usercopy tests, page fault during copy, clear_user partial faults, and nontemporal inatomic copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uaccess_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uaccess_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/uaccess_64.h

Purpose: 64-bit x86 raw user-copy, address-validation, tagged-address masking, and clear-user implementation.

Important APIs/types/functions: `USER_PTR_MAX`, `__untagged_addr()`, `untagged_addr()`, `untagged_addr_remote()`, `valid_user_address()`, `mask_user_address()`, `masked_user_access_begin()`, `__access_ok()`, `rep_movs_alternative()`, `copy_user_generic()`, `raw_copy_from_user()`, `raw_copy_to_user()`, `copy_to_nontemporal()`, `copy_user_flushcache()`, `copy_from_user_inatomic_nontemporal()`, `copy_from_user_flushcache()`, `rep_stos_alternative()`, `__clear_user()`, and `clear_user()`.

Control flow: access checks compare pointers/ranges against runtime-constant `USER_PTR_MAX`, with special handling for small constant sizes. LAM-enabled builds mask tag bits via alternative instructions and per-CPU `tlbstate_untag_mask`. Copies open SMAP, execute `rep movsb` or call `rep_movs_alternative` if FSRM is absent, and use exception-table fixups to return residual length. Clear-user similarly uses `rep stosb` or an alternative routine.

State/persistence: reads runtime constants, per-CPU tag masks, CPU feature alternatives, and KASAN instrumentation state. It does not persist data beyond destination writes and residual return values.

Dependencies/integration: depends on lockdep, KASAN, alternatives, cpufeatures, page/percpu, runtime constants, SMAP, exception tables, and cache-flush/nontemporal copy implementations. Integrated by generic copy_to/from_user and memory-management code.

Risks/test signals: risks include range overflow, incorrect LAM/tag masking, missing SMAP close on exception, wrong residual count, and cache/nontemporal copy corruption. Test x86_64 usercopy, LAM/address masking, KASAN, FSRM/FSRS alternatives, machine-check tolerant copy users, page-boundary faults, and `clear_user` partial fault behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uaccess_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/umip.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/umip.h

Purpose: declares x86 UMIP exception fixup support.

Important APIs/types/functions: `fixup_umip_exception(struct pt_regs *regs)`.

Control flow: `CONFIG_X86_UMIP` builds call into the real fixup implementation; non-UMIP builds inline-return `false`.

State/persistence: no state in the header; the implementation operates on trap register state.

Dependencies/integration: depends on `pt_regs` and UMIP trap handling for privileged instruction emulation or signal delivery.

Risks/test signals: wrong return value can cause incorrect handling of user-mode SGDT/SIDT/SLDT/SMSW/STR faults. Test with UMIP enabled/disabled, user-space privileged instruction probes, signal delivery, and virtualization/compat mode coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/umip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/unaccepted_memory.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/unaccepted_memory.h

Purpose: architecture hook for accepting confidential-computing memory ranges and finding the EFI unaccepted-memory table.

Important APIs/types/functions: `arch_accept_memory(phys_addr_t start, phys_addr_t end)` and `efi_get_unaccepted_table()`.

Control flow: acceptance dispatches to TDX when `X86_FEATURE_TDX_GUEST` is present, to SEV-SNP when `CC_ATTR_GUEST_SEV_SNP` is set, and panics for unknown platforms. TDX failure also panics. EFI table lookup returns NULL if the firmware address is invalid, otherwise maps it with `__va()`.

State/persistence: reads EFI global table address and CPU/platform confidential-computing feature state. Memory acceptance changes platform-managed page state outside normal kernel RAM metadata.

Dependencies/integration: depends on EFI, TDX, SEV/SNP, CPU feature checks, and early memory initialization accepting pages before use.

Risks/test signals: accepting the wrong range or failing to accept before use can crash encrypted guests; silently accepting on unknown platforms would be unsafe. Test TDX and SEV-SNP boot paths, EFI unaccepted-memory table parsing, partial range acceptance, and failure/panic injection where practical.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/unaccepted_memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/unistd.h

Purpose: selects x86 syscall number tables and architecture compatibility `__ARCH_WANT_*` feature flags.

Important APIs/types/functions: includes UAPI syscall numbers plus `unistd_32.h`, `unistd_64.h`, `unistd_64_x32.h`, `unistd_32_ia32.h`; defines `NR_syscalls`, `IA32_NR_syscalls`, and `X32_NR_syscalls`.

Control flow: 32-bit builds include native i386 syscalls and legacy wants. 64-bit builds include native, x32, and ia32 compat tables and define compat syscall feature requests.

State/persistence: no runtime state; this is a compile-time ABI selection point.

Dependencies/integration: used by syscall table generation, compat syscall handlers, seccomp/audit ABI metadata, and architecture build logic.

Risks/test signals: wrong table or count breaks syscall dispatch and compat ABI. Test native x86_64, i386, ia32 compat, x32 if enabled, seccomp syscall numbering, strace smoke tests, and syscall ABI selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/unwind.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/unwind.h

Purpose: public x86 stack unwinder state and helpers for ORC, frame-pointer, and fallback unwinders.

Important APIs/types/functions: `struct unwind_state`, `__unwind_start()`, `unwind_start()`, `unwind_next_frame()`, `unwind_get_return_address()`, `unwind_get_return_address_ptr()`, `unwind_done()`, `unwind_error()`, `unwind_get_entry_regs()`, `unwind_init()`, `unwind_module_init()`, `unwind_recover_rethook()`, `unwind_recover_ret_addr()`, `READ_ONCE_TASK_STACK()`, and `task_on_another_cpu()`.

Control flow: callers initialize with task/regs/first frame, then iterate `unwind_next_frame()` until `STACK_TYPE_UNKNOWN`. ORC and frame-pointer builds store different cursor fields. Return-address recovery first accounts for ftrace graph rewriting, then rethook trampoline rewriting. Entry-reg access exposes full or partial interrupt/exception frames depending on unwinder state.

State/persistence: unwind cursor state is per-call stack data. Persistent inputs include task stacks, ORC metadata, module ORC tables, ftrace graph state, and rethook lists.

Dependencies/integration: depends on scheduler tasks, ftrace, rethook, ptrace, stacktrace, module metadata, and KASAN-safe stack reads. Integrated with stack traces, livepatch/debugging, lockdep, oops reporting, perf, and BPF stack walkers.

Risks/test signals: unwinding across interrupts, rethooks, ftrace, modules, and remote running tasks is fragile. Test ORC and frame-pointer configs, module load/unload with ORC data, ftrace graph tracer, kretprobe/rethook users, NMI/oops stack traces, and KASAN remote stack-read behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/unwind.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/unwind_hints.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/unwind_hints.h

Purpose: assembler and C macros that emit ORC/objtool unwind hints for hand-written x86 assembly.

Important APIs/types/functions: assembler macros `UNWIND_HINT_END_OF_STACK`, `UNWIND_HINT_UNDEFINED`, `UNWIND_HINT_ENTRY`, `UNWIND_HINT_REGS`, `UNWIND_HINT_IRET_REGS`, `UNWIND_HINT_IRET_ENTRY`, `UNWIND_HINT_FUNC`, `UNWIND_HINT_SAVE`, `UNWIND_HINT_RESTORE`, and C-side `UNWIND_HINT_*` macro forms.

Control flow: assembler macros validate base registers, calculate ORC stack register/offset/type fields, distinguish full vs partial register frames, mark signal frames, and pair entry hints with unret validation. C-side macros provide equivalent static annotations for objtool-visible code.

State/persistence: no runtime state. Hints are persisted into object metadata consumed by objtool and the ORC unwinder.

Dependencies/integration: depends on `linux/objtool.h` and x86 `orc_types.h`. Used by entry code, interrupt/exception assembly, context switch code, and any hand-coded stack manipulation.

Risks/test signals: incorrect hints lead to broken stack traces or objtool warnings, especially around interrupt frames and special stacks. Test with `objtool` validation, ORC unwinder enabled, all entry/exit paths, NMI/IST frames, retbleed/unret validation, and oops stack traces through annotated assembly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/unwind_hints.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/unwind_user.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/unwind_user.h

Purpose: x86-specific helpers for user-space stack unwinding.

Important APIs/types/functions: `unwind_user_word_size()`, `ARCH_INIT_USER_FP_FRAME`, `ARCH_INIT_USER_FP_ENTRY_FRAME`, and `unwind_user_at_function_start()`.

Control flow: when user unwinding is enabled, word size is derived from `pt_regs`: VM86 stacks return 0 because they are unsupported, 64-bit user mode returns 8, and other user modes return 4. Frame-pointer initialization macros encode CFA, return-address, and frame-pointer offsets. Function-start detection delegates to uprobes.

State/persistence: no state. It reads register mode bits and uprobe state.

Dependencies/integration: depends on ptrace mode helpers and `asm/uprobes.h`. Integrated with generic user unwinding, perf, BPF/profile stack collection, and uprobe-aware unwinding.

Risks/test signals: wrong word size or frame layout corrupts user stack traces, especially compat processes. Test 64-bit, 32-bit compat, VM86 rejection, frame-pointer unwinding at normal call sites and function entries with uprobes installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/unwind_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uprobes.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/uprobes.h

Purpose: x86 architecture definitions for user-space probes, including breakpoint instruction details and per-probe decoded instruction storage.

Important APIs/types/functions: `uprobe_opcode_t`, `MAX_UINSN_BYTES`, `UPROBE_XOL_SLOT_BYTES`, `UPROBE_SWBP_INSN`, `UPROBE_SWBP_INSN_SIZE`, `ARCH_UPROBE_FLAG_CAN_OPTIMIZE`, `ARCH_UPROBE_FLAG_OPTIMIZE_FAIL`, `struct arch_uprobe`, `struct arch_uprobe_task`, and `is_uprobe_at_func_entry()`.

Control flow: uprobes patch user code with `int3` (`0xcc`), copy/decode original instructions into execute-out-of-line slots, and use per-instruction operation metadata for branches, default fixups, or push register fixups. Per-task state preserves trap number, TF, and on x86_64 a scratch register.

State/persistence: persistent probe state lives in `struct arch_uprobe`; per-thread execution state lives in `struct arch_uprobe_task`. The header defines layout, not storage ownership.

Dependencies/integration: depends on notifier infrastructure and `pt_regs`. Integrated with kernel uprobes, perf, tracing, and user unwinding function-entry detection.

Risks/test signals: instruction length, branch displacement, TF restoration, and optimized-probe flags are correctness-critical. Test uprobes on 32/64-bit processes, branches, pushes, optimized and non-optimized probes, single-step behavior, signal interaction, and unwind-at-function-entry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/user.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/user.h

Purpose: common x86 user ABI header selecting 32-bit or 64-bit legacy `struct user` layouts and defining extended xstate structures for ptrace/core dump consumers.

Important APIs/types/functions: includes `user_32.h` or `user_64.h`; defines `struct user_ymmh_regs`, `struct user_xstate_header`, `USER_XSTATE_FX_SW_WORDS`, `USER_XSTATE_XCR0_WORD`, and `struct user_xstateregs`.

Control flow: compile-time selection chooses native `struct user` ABI layout. Extended xstate layout mirrors processor XSAVE layout for NT_X86_XSTATE notes and ptrace, with software words carrying OS-enabled xstate mask.

State/persistence: no kernel runtime state. The structures describe serialized register state visible to debuggers and core dump readers.

Dependencies/integration: depends on arch integer types and native user layout headers. Integrated with ptrace, ELF core notes, debuggers, crash tools, and xsave feature enumeration.

Risks/test signals: layout drift breaks user-space debuggers and core dump parsing. Test ptrace GET/SETREGSET for xstate, core dump NT_X86_XSTATE notes, AVX/YMM state visibility, and CPUID-reported xsave size compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/user32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/user32.h

Purpose: IA32-compatible user register/FPU/core-dump structures for 64-bit kernels handling 32-bit tasks and 32-bit core dumps.

Important APIs/types/functions: `struct user_i387_ia32_struct`, `struct user32_fxsr_struct`, `struct user_regs_struct32`, and IA32 `struct user`.

Control flow: no runtime flow; compat ptrace/core dump code fills or reads these fixed layouts for 32-bit tasks.

State/persistence: serialized task register/FPU/core metadata layout. Fields include general registers, segment selectors, eflags, stack/ip, FP state, sizes, start addresses, signal, `u_ar0`, `u_fpstate`, magic, command, and debug registers.

Dependencies/integration: relies on fixed-width `u32`/`__u32` style types from included architecture context. Integrated with compat ptrace, ELF core dumping, and debugger ABI compatibility.

Risks/test signals: padding and field size mistakes break IA32 debuggers and core files. Test 32-bit process ptrace on x86_64, compat core dumps, FP/FXSR register access, debug register export, and gdb/strace compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/user32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/user_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/user_32.h

Purpose: native i386 legacy `struct user`, register, and FPU layouts used by ptrace and traditional core dumps.

Important APIs/types/functions: `struct user_i387_struct`, `struct user_fxsr_struct`, `struct user_regs_struct`, and `struct user`.

Control flow: no executable flow; core dump and ptrace code serialize/deserialize these structures.

State/persistence: describes one-page UPAGE-style core metadata plus data/stack sizing information, legacy and FXSR FPU state, segment registers, debug registers, process command, signal, and register pointer metadata.

Dependencies/integration: depends on page definitions. Integrated with i386 ptrace requests, GDB legacy core format expectations, and FPU register access.

Risks/test signals: this is ABI-stable historical layout. Test native i386 builds, GDB core reading, PTRACE_GETREGS/SETREGS, PTRACE_GETFPREGS/GETFPXREGS, debug registers, and segment register round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/user_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/user_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/user_64.h

Purpose: native x86_64 legacy `struct user`, register, and FPU layouts for ptrace and core dumps.

Important APIs/types/functions: `struct user_i387_struct`, `struct user_regs_struct`, and `struct user`.

Control flow: no runtime flow; layouts are consumed by ptrace/core dump paths.

State/persistence: serialized state includes 64-bit FXSAVE-compatible FPU fields, all general-purpose registers including r8-r15, segment/base fields, data/stack/text sizes, start addresses, signal, debug registers, error code, and fault address.

Dependencies/integration: depends on arch types and page definitions. Integrated with native x86_64 ptrace, ELF core dumping, GDB/crash tooling, and register note generation.

Risks/test signals: field order and width are ABI-sensitive. Test native ptrace register access, x86_64 core dumps under GDB, FP/SSE register notes, debug registers, and faulting process core metadata for `error_code` and `fault_address`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/user_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/bios.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/bios.h

Purpose: SGI/HPE UV BIOS runtime interface definitions, UV system table format, GAM/architecture metadata, firmware command IDs, status codes, and exported BIOS wrapper prototypes.

Important APIs/types/functions: `enum uv_bios_cmd`, `UV_BIOS_EXTRA*` commands, BIOS status constants, `struct uv_gam_parameters`, `struct uv_gam_range_entry`, `struct uv_arch_type_entry`, `struct uv_systab`, `uv_systab`, `struct uv_bios_hub_info`, `struct uv_bios_port_info`, `union partition_info_u`, `enum uv_memprotect`, UV BIOS call wrappers, `uv_bios_init()`, `get_uv_systab_phys()`, UV identity globals, `uv_get_archtype()`, `uv_get_hubless_system()`, `sgi_uv_kobj`, and `__efi_uv_runtime_lock`.

Control flow: UV initialization locates `uv_systab`, validates signature/revision, uses the EFI runtime function pointer for commands, and exposes typed wrappers for serial/partition info, frequency base, watchlists, memory protection, heap/object enumeration, geoinfo, PCI topology, and VGA target operations.

State/persistence: persistent firmware-derived state includes the UV system table pointer, architecture type, partition/coherency/region identifiers, serial number, RTC cycles, UV type, sysfs kobject, and EFI runtime lock.

Dependencies/integration: depends on EFI and RTC headers. Integrated with UV platform bring-up, MMR/GAM setup, sysfs firmware exposure, PCI topology, NMI/watchlist support, and protected memory operations.

Risks/test signals: EFI runtime calling conventions, table revision parsing, and buffer copy-in/out sizes are sensitive. Test UV boot on supported generations, missing/invalid systab handling, each BIOS wrapper return status, sysfs firmware nodes, PCI topology discovery, geoinfo parsing, and EFI runtime lock coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/bios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv.h

Purpose: top-level UV platform detection and initialization interface.

Important APIs/types/functions: `enum uv_system_type`, `UV_PROC_NODE`, `uv()`, `uv_systab_phys`, `get_uv_system_type()`, `is_early_uv_system()`, `is_uv_system()`, `is_uv_hubbed()`, `uv_cpu_init()`, `uv_nmi_init()`, and `uv_system_init()`.

Control flow: `CONFIG_X86_UV` builds expose real detection/init functions and early detection from a valid UV system table physical address. Non-UV builds inline to `UV_NONE`, false, or no-op.

State/persistence: UV detection state includes `uv_systab_phys` and runtime platform classification maintained by implementation files.

Dependencies/integration: depends on EFI when UV is enabled. Integrated with x86 platform setup, per-CPU UV initialization, NMI setup, and `/proc/sgi_uv` naming.

Risks/test signals: false UV detection can route normal x86 systems into UV-specific paths; missed detection disables UV platform support. Test UV and non-UV boots, early EFI systab detection, hubbed/hubless UV variants, CPU bring-up, and NMI initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv_geo.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv_geo.h

Purpose: UV hardware geolocation ID structures and helpers for rack/slot/blade naming.

Important APIs/types/functions: `GEOID_SIZE`, `struct geo_common_s`, `struct geo_node_s`, `struct geo_rtr_s`, `struct geo_iocntl_s`, `struct geo_pcicard_s`, `struct geo_cpu_s`, `struct geo_mem_s`, `union geoid_u`, `GEO_TYPE_*`, `geo_rack()`, `geo_slot()`, and `geo_blade()`.

Control flow: helper functions return `-1` for invalid geo IDs and otherwise derive rack, upos slot, and blade number (`blade * 2 + slot`) from common fields.

State/persistence: no runtime state. The union is a compact 8-byte firmware-provided hardware location encoding used in diagnostics.

Dependencies/integration: used with UV BIOS geoinfo enumeration, sysfs/diagnostics, and platform topology reporting.

Risks/test signals: incorrect packing or blade calculation mislabels physical hardware. Test by enumerating UV geoinfo, comparing rack/slot/blade labels with firmware/service-processor data, and validating invalid geoid handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv_geo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv_hub.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv_hub.h

Purpose: SGI/HPE UV hub architecture definitions for global physical addressing, NASID/GNODE/PNODE conversion, GAM ranges, MMR access, blade/node/cpu mapping, TSC/NMI hub flags, and per-CPU/per-hub metadata.

Important APIs/types/functions: `struct uv_gam_range_s`, `struct uv_hub_info_s`, `struct uv_cpu_info_s`, per-CPU `__uv_cpu_info`, `uv_hub_info_list()`, `uv_hub_info`, hub type predicates (`is_uv2_hub()` etc.), `UV_NASID_TO_PNODE()`, `UV_PNODE_TO_GNODE()`, MMR base/size macros, GPA conversion helpers (`uv_gpa_shift()`, `uv_gam_range()`, `uv_soc_phys_ram_to_gpa()`, `uv_gpa_to_soc_phys_ram()`, `uv_gpa_to_gnode()`, `uv_gpa_to_pnode()`, `uv_gpa_to_offset()`), socket/pnode/node conversion helpers, MMR read/write helpers, blade CPU/node helpers, `uv_possible_blades`, NMI structs, and UV NMI state constants.

Control flow: most routines are inline transforms over boot-populated `uv_hub_info`. Address conversion handles UV4+/GAM table formats, low-memory remap, m/n bit layouts, pnode/socket translation tables, and MMIO address construction. MMR helpers create local/global virtual addresses and issue `readq/writeq/readb/writeb`. Blade helpers map CPUs, nodes, sockets, pnodes, and memory NIDs. `uv_gam_range()` scans the GAM range table and `BUG()`s if no range matches.

State/persistence: long-lived state is per-hub and per-CPU: hub type/revision, MMR/GRU base/shift values, masks, translation tables, GAM ranges, pnode/socket/node IDs, memory node, possible/online CPU counts, NMI hub state, and global `uv_possible_blades`. This metadata is established during UV platform initialization and then treated mostly read-only.

Dependencies/integration: only active for `CONFIG_X86_64`; depends on NUMA, per-CPU, timers, I/O accessors, topology, UV BIOS/MMR definitions, IRQ vectors, and IO-APIC. Integrated with UV memory addressing, GRU, NMI, IRQ routing, CPU/node topology, firmware tables, and platform diagnostics.

Risks/test signals: address translation and MMR access are platform-critical. Wrong masks/shifts/tables can corrupt memory, hit wrong MMRs, or panic via `BUG()`. Test on UV2/UV3/UV4/UV4A/UV5 and hubless variants, GAM table edge ranges, lowmem remap, pnode/socket/node mapping with sub-NUMA clustering, local/global MMR reads, blade CPU counts during hotplug, NMI MMR handling, and non-UV build exclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv_hub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv_irq.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv_irq.h

Purpose: UV-specific IRQ route entry layout and setup/teardown declarations.

Important APIs/types/functions: `struct uv_IO_APIC_route_entry`, affinity enum values `UV_AFFINITY_ALL`, `UV_AFFINITY_NODE`, `UV_AFFINITY_CPU`, `uv_setup_irq()`, and `uv_teardown_irq()`.

Control flow: implementation code uses the route-entry bitfield to program UV IO-APIC style destinations and uses affinity mode to target all CPUs, a node, or a specific CPU. Teardown releases the IRQ by number.

State/persistence: no state in the header. Runtime IRQ state is owned by the UV IRQ implementation and generic IRQ core.

Dependencies/integration: integrated with UV hub interrupt routing, IO-APIC semantics, Linux IRQ allocation, and platform device drivers needing UV affinity.

Risks/test signals: bitfield layout and destination semantics must match hardware. Test UV IRQ setup for all affinity modes, interrupt delivery under CPU/node hotplug, teardown leak checks, and route-entry programming against firmware/hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv_irq.h -->
