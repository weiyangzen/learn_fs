# subset-b-000889 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/setup_percpu.c -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/setup_percpu.c

### Purpose
`setup_percpu.c` initializes x86 per-CPU storage during early boot. It exports the core per-CPU variables `cpu_number`, `this_cpu_off`, and `__per_cpu_offset`, chooses the first-chunk allocator strategy, wires x86 CPU-to-node/APIC early maps into the allocated per-CPU areas, and makes the per-CPU base usable by the boot CPU and AP startup code.

### Important APIs, Types, And Functions
The public initialization entry is `setup_per_cpu_areas()`. `pcpu_populate_pte()` delegates extra page-table population to `populate_extra_pte()`. `pcpu_cpu_distance()` and `pcpu_cpu_to_node()` provide NUMA callbacks to the generic percpu allocator. On 32-bit, `pcpu_need_numa()` decides whether sparse NUMA placement requires the page allocator and `setup_percpu_segment()` installs `GDT_ENTRY_PERCPU`.

### Control Flow
Boot logs topology sizes, chooses embedded first-chunk allocation unless 32-bit NUMA pressure forces page chunks, and falls back from `pcpu_embed_first_chunk()` to `pcpu_page_first_chunk()` before panicking on total failure. It computes the delta from `__per_cpu_start` to `pcpu_base_addr`, fills every possible CPU's offset, CPU number, APIC/ACPI IDs, and NUMA node map, then switches CPU0 from early init data to the real per-CPU base. It clears early map pointers, builds node cpumasks, initializes CPU local masks, and syncs initial page tables for SMP boot assembly.

### State, Persistence, And Dependencies
Persistent state is the final per-CPU offset table, the per-CPU exported variables, CPU-to-APIC/ACPI/node maps, and 32-bit GDT descriptors. It depends on memblock-era percpu allocation, early CPU-to-node data, APIC and NUMA early arrays, GDT helpers, and page-table synchronization.

### Integration Points
This file bridges generic percpu allocation with x86 GDT/percpu-base setup and later SMP boot. `setup_cpu_local_masks()` and `setup_node_to_cpumask_map()` prepare topology data consumed by `smpboot.c`. `switch_gdt_and_percpu_base()` is called for CPU0 once the permanent per-CPU region exists.

### Risks
Allocator fallback and NUMA decisions are boot-critical. Wrong offsets corrupt every per-CPU access. Clearing early maps too early would break later CPU bringup; clearing them too late can hide use-after-init bugs. On 32-bit, descriptor base mistakes break `%fs/%gs` style per-CPU addressing.

### Test Signals
Useful signals include boot on 32-bit and 64-bit, NUMA and non-NUMA, large `NR_CPUS`, APIC and non-APIC configurations, kdump/crash-dump boots, CPU hotplug after boot, and checking that per-CPU variables, APIC IDs, NUMA nodes, and SMP startup all remain coherent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/setup_percpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/sev_verify_cbit.S -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/sev_verify_cbit.S

### Purpose
`sev_verify_cbit.S` verifies at early boot that the SEV C-bit position reported by the hypervisor is correct before switching to a new long-mode page table. It protects encrypted guests from continuing with page tables that would misinterpret encrypted memory.

### Important APIs, Types, And Functions
The sole entry point is `sev_verify_cbit(new_cr3)` with the new page-table pointer in `%rdi`; it returns that pointer in `%rax`. It reads `sme_me_mask`, `sev_status`, and writes/reads the global `sev_check_data`.

### Control Flow
When AMD memory encryption is not configured, or SME/SEV are not active, the function returns immediately. Under SEV it saves CR4, disables PGE, obtains a random value with `RDRAND`, writes it through the current mapping, saves CR3, switches to the candidate CR3, compares the same address, restores CR3 and CR4, and returns on match. On mismatch it invalidates the stack pointer and loops on `hlt`.

### State, Persistence, And Dependencies
The only temporary memory state is `sev_check_data`; CR3 and CR4 are restored on success. The code depends on early identity/kernel mappings containing `sev_check_data`, mandatory SEV `RDRAND`, and the C-bit mask/status setup performed before this verification.

### Integration Points
This assembly is part of SEV early page-table transition code. It complements the SME/SEV setup code that discovers `sme_me_mask` and `sev_status`, and it runs before the kernel trusts the new long-mode page tables.

### Risks
The failure path intentionally halts forever because continuing could expose encrypted memory or enable ROP-style recovery after a hostile mapping. The loop around `RDRAND` can also block progress rather than using a weak value. Mapping assumptions are fragile because stack availability may change after CR3 is switched.

### Test Signals
Boot SEV guests with valid and deliberately wrong C-bit configuration, non-SEV SME systems, and non-encrypted systems. Check that CR4.PGE is restored on success, that the function returns the input page-table pointer, and that invalid C-bit tests halt before proceeding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/sev_verify_cbit.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/shstk.c -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/shstk.c

### Purpose
`shstk.c` implements Intel CET user shadow-stack support for x86. It owns shadow-stack allocation, enable/disable policy, signal-frame shadow-stack tokens, clone/vfork handling, `map_shadow_stack`, and `ARCH_SHSTK_*` `arch_prctl` operations.

### Important APIs, Types, And Functions
Important exported/integrated functions include `reset_thread_features()`, `shstk_alloc_thread_stack()`, `shstk_pop()`, `shstk_push()`, `setup_signal_shadow_stack()`, `restore_signal_shadow_stack()`, `shstk_free()`, `shstk_prctl()`, `shstk_update_last_frame()`, and `shstk_is_enabled()`. Internal helpers manage `thread.features`, `thread.features_locked`, `struct thread_shstk`, restore tokens, signal data markers, and CET MSRs `MSR_IA32_PL3_SSP` and `MSR_IA32_U_CET`.

### Control Flow
`shstk_setup()` rejects unsupported CPUs and IA32 syscalls, allocates a shadow-stack VMA sized from `RLIMIT_STACK` up to 4 GiB, writes PL3 SSP to the top, enables CET shadow stack, and records base/size. Clone handling allocates a separate stack for `CLONE_VM`, leaves non-`CLONE_VM` to copy semantics, and clears tracking for `CLONE_VFORK`. Signal delivery pushes a high-bit-marked restore token and restorer address, then updates SSP; sigreturn validates the VMA and token through mmap sequence checks before restoring SSP. Disable clears CET MSRs, frees the tracked stack, and clears SHSTK/WRSS feature bits.

### State, Persistence, And Dependencies
Persistent per-task state lives in `current->thread.features`, `features_locked`, and `thread.shstk`. Persistent memory is held in `VM_SHADOW_STACK` mappings with a guard-page model. The code depends on FPU register locking for CET MSR access, `vm_mmap_shadow_stack()`, `write_user_shstk_64()`, mmap locks/speculation sequence helpers, clone/signal code, and CPU feature `X86_FEATURE_USER_SHSTK`.

### Integration Points
Signal setup in `signal_64.c` calls `setup_signal_shadow_stack()` and sigreturn calls `restore_signal_shadow_stack()`. Thread creation and exit paths call stack allocation/free helpers. User policy arrives through `arch_prctl` and the `map_shadow_stack` syscall; ptrace/CRIU can unlock locked features only under checkpoint-restore support.

### Risks
Incorrect SSP token validation can let sigreturn pivot shadow stacks. VMA races are controlled with mmap sequence retry and `VM_SHADOW_STACK` checks. CET MSR updates require current fpregs ownership. `CLONE_VFORK` and failed `fork()` paths are easy to double-free or leak. Feature locking and one-feature-at-a-time rules are ABI/security sensitive.

### Test Signals
Exercise `ARCH_SHSTK_ENABLE/DISABLE/LOCK/UNLOCK/STATUS`, WRSS enablement without SHSTK, `map_shadow_stack` flags and overflow checks, signal delivery and nested signal return, invalid restorer/token/VMA cases, clone/vfork/fork/exec/exit paths, ptrace unlock under CRIU, and 32-bit syscall rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/shstk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/signal.c -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/signal.c

### Purpose
`signal.c` is the common x86 signal-delivery and syscall-restart layer shared by 32-bit, 64-bit, IA32 compat, and x32 signal-frame implementations. It selects the ABI-specific frame builder, computes frame sizing, handles alternate stacks and FPU state placement, adjusts syscall restart state, and validates dynamic sigaltstack size.

### Important APIs, Types, And Functions
Key functions are `get_sigframe()`, `get_sigframe_size()`, `arch_do_signal_or_restart()`, `signal_fault()`, and, under dynamic sigframes, `sigaltstack_size_valid()`. It dispatches to `ia32_setup_frame()`, `ia32_setup_rt_frame()`, `x32_setup_rt_frame()`, and `x64_setup_rt_frame()`. It uses `rseq_signal_deliver()`, `fpu__alloc_mathframe()`, `copy_fpstate_to_sigframe()`, and `fpu__clear_user_states()`.

### Control Flow
`get_sigframe()` starts from user SP, applies the x86-64 red zone when needed, switches to altstack when `SA_ONSTACK` allows it, supports legacy ia32 stack switching, allocates the FPU frame, aligns the ABI stack, checks altstack overflow, temporarily enables all pkeys through PKRU, and saves FP/xstate. `arch_do_signal_or_restart()` either delivers a pending signal through `handle_signal()` or rewinds/replaces syscall state for restart. `handle_signal()` handles vm86 save, restart errors, ptrace single-step clearing, frame setup, DF/RF/TF clearing, and signal completion.

### State, Persistence, And Dependencies
State touched includes `pt_regs`, saved signal masks, restart blocks, PKRU, FPU/xstate signal frames, rseq state, `thread.trap_nr/error_code` indirectly through ABI frame builders, and `max_frame_size` initialized at early boot. Dependencies include generic signal code, FPU signal helpers, pkeys, vDSO/vm86, rseq, and ABI-specific frame files.

### Integration Points
This file coordinates with `signal_32.c` and `signal_64.c` for actual frame layout. It exposes the maximum frame size to userspace-facing stack checks and validates dynamic xstate permissions against sigaltstack sizes. It also integrates syscall restart semantics with the x86 entry path by subtracting two bytes from IP for restartable syscall instructions.

### Risks
Stack alignment and red-zone handling are ABI-critical. PKRU is deliberately widened during frame creation and must be restored on failure. Dynamic xstate can make old `MINSIGSTKSZ` assumptions unsafe. Wrong restart rewinding breaks syscall semantics, and wrong single-step handling corrupts debugger-visible state.

### Test Signals
Test native 64-bit, IA32, and x32 signal delivery, altstack and `SS_AUTODISARM`, PKU-protected signal stacks, AVX512/dynamic xstate frame growth, syscall restart cases for every `ERESTART*`, vm86 signals, ptrace single-step into handlers, and bad frame faults reporting `SIGSEGV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/signal_32.c -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/signal_32.c

### Purpose
`signal_32.c` implements i386 and IA32-compat signal-frame setup and signal-return handling. It preserves the 32-bit ABI layouts for classic and realtime signal frames, handles 32-bit segment registers, and enforces `siginfo32_t` ABI size/offset invariants.

### Important APIs, Types, And Functions
Key paths are `ia32_setup_frame()`, `ia32_setup_rt_frame()`, `SYSCALL32_DEFINE0(sigreturn)`, `SYSCALL32_DEFINE0(rt_sigreturn)`, and `ia32_restore_sigcontext()`. Helpers include `fixup_rpl()`, `reload_segments()`, and `__unsafe_setup_sigcontext32()`. The file uses `struct sigframe_ia32`, `struct rt_sigframe_ia32`, `struct sigcontext_32`, `compat_sigset_t`, and `compat_siginfo_t`.

### Control Flow
Sigreturn locates the frame below the current 32-bit SP, validates access, restores blocked masks, restores registers and segments from sigcontext, restores FPU state, and restores altstack for realtime frames. Frame setup obtains a frame from `get_sigframe()`, chooses a vDSO or inline `int $0x80` restorer, writes sigcontext, masks, return code markers, `siginfo`, and `ucontext`, then sets handler registers according to i386 calling convention.

### State, Persistence, And Dependencies
The durable ABI state is the exact userspace frame and `siginfo32_t` layout. Runtime state includes pt_regs general registers, CS/SS/DS/ES/FS/GS selectors, FPU state pointer, signal masks, and altstack state. It depends on compat helpers, 32-bit vDSO symbols, segment load helpers, SMAP user access windows, and FPU signal restore.

### Integration Points
`signal.c` dispatches here for native x86-32 and x86-64 IA32 emulation. `signal_64.c` reuses `__copy_siginfo_to_user32()` for non-x32 compat. Debuggers also rely on the old `retcode` marker bytes even though vDSO restorers are normally used.

### Risks
Segment selector semantics are subtle: nonzero null selectors are preserved for FRED behavior, while non-null selectors get RPL forced to 3. Siginfo layout static assertions are ABI tripwires. Inline restorer bytes and vDSO symbol offsets must remain compatible with old userspace and debuggers.

### Test Signals
Run classic and realtime signals under native i386 and IA32 emulation, handlers with and without `SA_RESTORER`, vDSO absent/present fallback, segment selector changes in handlers, bad sigreturn frames, FPU restore failures, altstack restore, and static layout checks for new `si_code` fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/signal_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/signal_64.c -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/signal_64.c

### Purpose
`signal_64.c` implements native x86-64 and x32 realtime signal frames and sigreturn. It restores 64-bit register/FPU context, handles compatibility SS restore rules, integrates shadow stacks, and preserves native and x32 `siginfo` ABI layouts.

### Important APIs, Types, And Functions
Important functions are `x64_setup_rt_frame()`, `SYSCALL_DEFINE0(rt_sigreturn)`, `x32_setup_rt_frame()`, `COMPAT_SYSCALL_DEFINE0(x32_rt_sigreturn)`, `copy_siginfo_to_user32()`, and `sigaction_compat_abi()`. Internals include `force_valid_ss()`, `restore_sigcontext()`, `__unsafe_setup_sigcontext()`, `frame_uc_flags()`, and `x32_copy_siginfo_to_user()`.

### Control Flow
Setup requires `SA_RESTORER`, obtains a stack frame from `get_sigframe()`, writes ucontext, sigcontext, sigmask, optional siginfo, installs a shadow-stack signal record when enabled, and sets handler arguments in `di/si/dx`. Sigreturn validates the frame, restores mask and altstack, restores general registers and FPU state, restores shadow-stack state, and returns the restored `ax`. x32 follows the x32 calling convention and uses compat `siginfo`, with special SIGCHLD time fields.

### State, Persistence, And Dependencies
State includes pt_regs, ucontext flags, `UC_FP_XSTATE`, `UC_SIGCONTEXT_SS`, `UC_STRICT_RESTORE_SS`, FPU signal state, sigmask, altstack, and CET shadow-stack tokens. Dependencies include `signal.c`, FPU signal helpers, shadow-stack helpers from `shstk.c`, user access primitives, x32/compat types, and segment descriptor validation via `lar`.

### Integration Points
The common signal dispatcher calls this for native 64-bit and x32 frames. Shadow-stack setup/restore connects signal delivery to CET state. `sigaction_compat_abi()` tags compat sigactions with IA32 or x32 ABI flags so later delivery chooses the correct frame format.

### Risks
SS handling is compatibility-sensitive for DOSEMU and CRIU: strict restore is used for normal 64-bit contexts, while old contexts may be sanitized. `SA_RESTORER` is mandatory for x86-64. Shadow-stack setup must align with user restorer addresses. x32 siginfo conversion is easy to break for SIGCHLD time fields.

### Test Signals
Test native 64-bit and x32 realtime handlers, missing `SA_RESTORER`, strict and non-strict SS restore, bad SS values causing `force_valid_ss()`, shadow-stack signal/sigreturn paths, x32 SIGCHLD siginfo layout, bad frames, FPU restore errors, and compat sigaction ABI tagging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/signal_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/smp.c -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/smp.c

### Purpose
`smp.c` supplies x86 SMP interrupt handlers and CPU stopping operations. It implements reschedule and call-function vectors, the reboot stop vector, NMI fallback stopping, the global `smp_ops` table, and a hotplug helper to rescan dead SMT siblings.

### Important APIs, Types, And Functions
Core functions are `native_stop_other_cpus()`, `sysvec_reboot`, `sysvec_reschedule_ipi`, `sysvec_call_function`, `sysvec_call_function_single`, and `arch_cpu_rescan_dead_smt_siblings()`. State includes `stopping_cpu`, `smp_no_nmi_ipi`, `cpus_stop_mask`, and exported `struct smp_ops smp_ops`.

### Control Flow
Stopping first elects one stopping CPU, optionally wakes offline MWAIT CPUs for kexec, sends `REBOOT_VECTOR` IPIs to other online CPUs, waits up to one second, then optionally registers an NMI handler and sends NMI IPIs to remaining CPUs. It waits again, disables the local APIC, clears MCE state, and clears `cpus_stop_mask`. IPI handlers EOI the APIC, trace entry/exit, update IRQ stats, and call generic scheduler or SMP call-function handlers.

### State, Persistence, And Dependencies
Persistent state is the `smp_ops` dispatch table and boot parameter `nonmi_ipi` flag. Runtime state includes atomic stop ownership, online/stop masks, interrupt statistics, tracing hooks, virtualization emergency-disable state, and APIC state. Dependencies include APIC IPI delivery, NMI registration, kexec, MCE, scheduler IPIs, and generic SMP call-function infrastructure.

### Integration Points
`smp_ops` points to functions implemented here and in `smpboot.c`, making this the arch dispatch layer for generic SMP and CPU hotplug code. The reboot vector invokes `stop_this_cpu()`, which interacts with SME comments in stop-mask clearing and offline CPU handling.

### Risks
CPU stop is best-effort under severe failure conditions; locks may be held and NMIs can race with CPUs reaching halt. NMI fallback registration must not run on the stopping CPU spuriously. Missing APIC EOI or trace pairing would distort interrupt accounting. `nonmi_ipi` weakens shutdown recovery.

### Test Signals
Exercise reboot, panic, kexec, crash dump, `nonmi_ipi`, stopped CPUs in MWAIT, scheduler and call-function IPI storms, CPU hotplug with SMT disabled, virtualization guests, and tracepoints/IRQ stat consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/smpboot.c -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/smpboot.c

### Purpose
`smpboot.c` implements x86 secondary CPU startup, topology mask construction, scheduler topology setup, AP wakeup, CPU hotplug teardown, and offline CPU dead loops. It is the main x86 bridge between firmware/APIC CPU enumeration and the generic CPU hotplug state machine.

### Important APIs, Types, And Functions
Major entry points include `start_secondary()`, `set_cpu_sibling_map()`, `common_cpu_up()`, `native_kick_ap()`, `arch_cpuhp_kick_ap_alive()`, `native_smp_prepare_cpus()`, `native_smp_prepare_boot_cpu()`, `native_smp_cpus_done()`, `cpu_disable_common()`, `native_cpu_disable()`, `mwait_play_dead()`, `smp_kick_mwait_play_dead()`, and `native_play_dead()`. It exports per-CPU sibling/core/die masks and `__max_smt_threads`.

### Control Flow
AP startup initializes CR4, page tables on 32-bit, exception handling, microcode, hotplug alive synchronization, CPU/FPU/RCU/per-CPU clocks, APIC setup, topology, TSC sync, delay calibration, mitigations, vector allocator online state, local interrupts, clock events, and finally idle startup. Boot CPU preparation allocates topology masks and prepares interrupt mode/timers. AP wakeup validates APIC IDs, saves MTRRs, prepares idle stack/canary/IRQ stacks, sets trampoline state, optionally warm-reset vectors, and sends platform or INIT/SIPI wakeups.

### State, Persistence, And Dependencies
Persistent topology state includes sibling/core/die/LLC/L2 masks, `cpu_sibling_setup_mask`, booted core counts, SMT-active flags, scheduler topology levels, `__max_smt_threads`, and `x86_topology_update`. Hotplug state includes per-CPU `mwait_cpu_dead` control/status. Dependencies include APIC, real-mode trampoline, microcode, TSC sync, FPU, RCU, scheduler topology, NUMA SLIT data, MTRR, local APIC vectors, TBoot, cpuidle, and speculation mitigations.

### Integration Points
Generic CPU hotplug calls the arch kick, cleanup, disable, and play-dead hooks. Scheduler domains consume `cpu_coregroup_mask()` and `cpu_clustergroup_mask()`. `smp.c` invokes `smp_kick_mwait_play_dead()` during kexec shutdown. SEV-SNP can override secondary wakeup via `snp_set_wakeup_secondary_cpu()`.

### Risks
AP startup ordering is fragile; microcode, CPUID-derived topology, vector locks, and online state must happen in the documented order. Topology matching must avoid crossing NUMA nodes incorrectly while still supporting SNC/COD quirks. Warm reset vector reference counting and parallel bringup state are boot-critical. Hotplug dead loops need cache flush and kexec escape handling.

### Test Signals
Boot with one CPU, many CPUs, SMT on/off, NUMA, Intel SNC/COD, AMD TOPOEXT, APIC variants, parallel bringup, CPU hotplug stress, suspend/thaw of secondary CPUs, kexec with offline MWAIT CPUs, cpuidle play-dead failure fallback, and scheduler domain topology inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/smpboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/stacktrace.c -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/stacktrace.c

### Purpose
`stacktrace.c` provides x86 implementations of kernel, reliable kernel, and userspace stack walking for the generic stacktrace API.

### Important APIs, Types, And Functions
The exported arch hooks are `arch_stack_walk()`, `arch_stack_walk_reliable()`, and `arch_stack_walk_user()`. Internal `copy_stack_frame()` reads `struct stack_frame_user { next_fp, ret_addr }` with page faults disabled.

### Control Flow
Normal kernel walking optionally emits `regs->ip`, starts the unwinder with task/regs, and feeds return addresses to the consumer until the consumer stops or unwinding ends. Reliable walking rejects kernel exception/interrupt register frames when frame pointers are enabled, rejects null return addresses and unwind errors, and returns `-EINVAL` on uncertainty. User walking emits current IP, then follows frame pointers from `bp` while addresses are accessible, not below SP, and have nonzero return addresses.

### State, Persistence, And Dependencies
No persistent state is modified. The code depends on the selected x86 unwinder, task stacks, `pt_regs`, user access checks, and generic stacktrace consumer callbacks.

### Integration Points
Generic stacktrace, livepatch reliability checks, tracing, profiling, and debugging code call these hooks. Reliable walking is especially relevant for code that must avoid patching or reporting from ambiguous stacks.

### Risks
Reliable unwinding deliberately fails on generated code unknown to `__kernel_text_address()` and on kernel-mode pt_regs frames with frame pointers. User walking is heuristic and frame-pointer-based, so optimized or corrupted userspace stacks truncate naturally.

### Test Signals
Check ORC/frame-pointer/guess unwind configurations, livepatch reliable-stack tests, interrupt and preemption frames, user stacks with good and bad frame pointers, inaccessible user memory, and consumer early-stop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/static_call.c -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/static_call.c

### Purpose
`static_call.c` implements x86 text transformations for Linux static calls and static-call trampolines. It patches call sites and trampolines between calls, NOPs, jumps, returns, and conditional branches while respecting retpoline/rethunk and special WARN/static-return cases.

### Important APIs, Types, And Functions
Public hooks are `arch_static_call_transform()`, `__static_call_update_early()`, and, under rethunk mitigation, `__static_call_fixup()`. Internals include `enum insn_type`, `__static_call_transform()`, `__static_call_validate()`, `__sc_insn()`, `__is_Jcc()`, `tramp_ud`, `xor5rax`, `retinsn`, and `warninsn`.

### Control Flow
Validation checks that a trampoline has the UD1 signature and that the current opcode matches the expected tail or non-tail form. Transform generation maps non-null normal calls to `CALL`, null calls to NOP, tail calls to `JMP`, null tail calls to `RET` or rethunk jump, and Jcc trampolines to conditional branches to the target/return thunk. During boot or module init it uses early patching; otherwise it uses `smp_text_poke_single()` under `text_mutex`, optionally with emulation bytes for special instructions.

### State, Persistence, And Dependencies
Persistent state is modified kernel text. The code depends on `text_mutex`, x86 text-patching helpers, callthunk destination translation, rethunk policy, static-call core state, and trampoline signatures chosen to avoid false positives.

### Integration Points
Static call users throughout the kernel rely on this arch backend. `traps.c` recognizes UD1 forms used by static calls and WARN traps. Rethunk alternatives call `__static_call_fixup()` to repair null trampolines after mitigation selection.

### Risks
Text corruption is fatal and guarded with BUGs. Instruction size mismatches, Jcc offset generation, or stale rethunk decisions could branch to the wrong target. Runtime patching must coordinate with CPUs executing the modified instruction stream.

### Test Signals
Test static calls during early boot, module init, runtime updates under load, null and non-null calls, tail calls, conditional tail calls, return0 optimization, WARN trap optimization, rethunk enabled/disabled, and objtool/static-call validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/static_call.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/step.c -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/step.c

### Purpose
`step.c` implements x86 ptrace single-step and block-step control. It manages TF, BTF, syscall-exit traps, LDT/vm86 linear IP conversion, and bookkeeping so debugger-forced TF does not permanently alter user TF state.

### Important APIs, Types, And Functions
Public functions are `convert_ip_to_linear()`, `set_task_blockstep()`, `user_enable_single_step()`, `user_enable_block_step()`, and `user_disable_single_step()`. Internals include `is_setting_trap_flag()`, `enable_single_step()`, and `enable_step()`.

### Control Flow
`convert_ip_to_linear()` handles vm86 segment arithmetic and LDT code segment bases, including 16-bit code masking. Enabling step sets `TIF_SINGLESTEP`, requests `SYSCALL_EXIT_TRAP`, sets TF in saved flags, and decides whether TF was debugger-forced by inspecting whether the next instruction is `popf`/`iret` and can modify TF itself. Block-step additionally sets `DEBUGCTLMSR_BTF` and `TIF_BLOCKSTEP`. Disable clears block-step, single-step work, and TF only if `TIF_FORCED_TF` says the kernel set it.

### State, Persistence, And Dependencies
State lives in `pt_regs->flags`, task thread flags `TIF_SINGLESTEP`, `TIF_FORCED_TF`, `TIF_BLOCKSTEP`, syscall work flags, and `MSR_IA32_DEBUGCTLMSR`. Dependencies include ptrace stop synchronization, debug registers, LDT locking, `access_process_vm()`, and syscall exit work.

### Integration Points
`traps.c` consumes debug exceptions generated by these settings. `signal.c` clears debugger stepping before entering handlers and reports setup completion. Ptrace uses these hooks for `PTRACE_SINGLESTEP` and `PTRACE_BLOCKSTEP`.

### Risks
Misclassifying user-owned TF as forced TF changes user-visible flags. Races are avoided only when ptrace has frozen the traced task or the task is current; the code documents this for block-step MSR changes. Instruction-prefix scanning is intentionally shallow and conservative.

### Test Signals
Test ptrace single-step and block-step across normal instructions, syscalls/sysenter, signal delivery, `popf`/`iret`, vm86, LDT 16-bit code, tasks with user TF already set, and concurrent ptrace freeze/unfreeze.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/step.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/sys_ia32.c -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/sys_ia32.c

### Purpose
`sys_ia32.c` provides IA32 compatibility syscall wrappers on x86-64. It converts 32-bit ABI arguments and structures into native kernel forms for large-file offsets, stat64, mmap, and clone.

### Important APIs, Types, And Functions
Wrappers include `ia32_truncate64`, `ia32_ftruncate64`, `ia32_pread64`, `ia32_pwrite64`, `ia32_fadvise64_64`, `ia32_readahead`, `ia32_sync_file_range`, `ia32_fadvise64`, and `ia32_fallocate`. Under IA32 emulation it defines `cp_stat64()`, `ia32_stat64`, `ia32_lstat64`, `ia32_fstat64`, `ia32_fstatat64`, `struct mmap_arg_struct32`, `ia32_mmap`, and `ia32_clone`.

### Control Flow
Most wrappers combine low/high 32-bit words into 64-bit offsets or lengths and call the native `ksys_*` helper. `cp_stat64()` translates `struct kstat` to the 32-bit `stat64` ABI using munged uid/gid and huge device encoding inside a user-write access window. `ia32_mmap()` copies the six-argument block from userspace, validates page-aligned offset, and calls `ksys_mmap_pgoff()`. `ia32_clone()` maps the backwards i386 clone ABI into `kernel_clone_args`.

### State, Persistence, And Dependencies
No persistent kernel state is owned here; it marshals userspace ABI data. Dependencies include compat syscall macros, VFS stat helpers, native `ksys_*` file operations, user namespace uid/gid munging, user access primitives, and clone internals.

### Integration Points
The IA32 syscall table targets these wrappers for syscalls whose 32-bit ABI does not match native x86-64 argument ordering or structure layout. VFS and process creation code receive normalized kernel arguments.

### Risks
Endian assumptions are explicit for split offsets. Incorrect high/low composition causes data corruption beyond 4 GiB. `stat64` layout must match the i386 ABI exactly. `ia32_clone()` must preserve parent/child TID and signal semantics of the backwards clone convention.

### Test Signals
Run IA32 binaries against large-file truncate, pread/pwrite beyond 4 GiB, fallocate/fadvise/sync ranges, stat64 on large inode/dev values, old mmap argument blocks with bad offsets, and clone variants with TLS and parent/child TID pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/sys_ia32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/sys_x86_64.c -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/sys_x86_64.c

### Purpose
`sys_x86_64.c` implements native x86 mmap syscall handling and x86-specific unmapped-area selection. It supports AMD F15h virtual-address alignment, `MAP_32BIT`, `MAP_ABOVE4G`, top-down fallback, huge-page alignment, and shadow-stack guard placement.

### Important APIs, Types, And Functions
Important functions are `SYSCALL_DEFINE6(mmap)`, `arch_get_unmapped_area()`, `arch_get_unmapped_area_topdown()`, `control_va_addr_alignment()`, `find_start_end()`, `get_align_mask()`, `get_align_bits()`, and `stack_guard_placement()`.

### Control Flow
The mmap syscall validates page-aligned file offsets and calls `ksys_mmap_pgoff()`. Bottom-up search computes an address window from `MAP_32BIT`, 32-bit syscall mode, and default task size, honors a valid hint if possible, then fills `vm_unmapped_area_info` with length, limits, file offset alignment, optional per-boot alignment bits, and a shadow-stack guard gap. Top-down search honors fixed mappings, validates hints, uses high limits from `get_mmap_base()`, expands beyond `DEFAULT_MAP_WINDOW` for high hints, and falls back to bottom-up on `-ENOMEM`.

### State, Persistence, And Dependencies
Persistent state is the boot/configured `va_align` policy and per-boot alignment bits. Runtime dependencies include current mm VMA tree, hugepage helpers, mmap base randomization, task-size helpers, `vm_unmapped_area()`, and VM flags such as `VM_SHADOW_STACK`.

### Integration Points
The generic mm uses these arch hooks for address selection. Shadow-stack mappings from `shstk.c` rely on the guard placement. `MAP_32BIT` supports old small-model and threading assumptions, while `MAP_ABOVE4G` supports shadow-stack allocation constraints.

### Risks
Address-window mistakes can break ASLR, x32/IA32 limits, or legacy `MAP_32BIT` applications. Alignment policy is CPU-family-specific and should not be accidentally enabled elsewhere. Shadow-stack guard gaps must be included in availability checks to prevent adjacency hazards.

### Test Signals
Test mmap with fixed/hinted/random addresses, native/x32/IA32 modes, `MAP_32BIT`, `MAP_ABOVE4G`, huge pages, AMD alignment on/off/32/64 boot options, large stack top-down fallback, and shadow-stack VM guard gaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/sys_x86_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/tboot.c -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/tboot.c

### Purpose
`tboot.c` provides Intel TXT/tboot measured-launch runtime support. It discovers the tboot shared page, builds executable identity mappings for tboot shutdown code, routes ACPI sleep/shutdown through tboot, coordinates AP wait-for-SIPI shutdown, exposes a debugfs tboot log, and supplies a DMA-protected DMAR table copy from the TXT heap.

### Important APIs, Types, And Functions
Key functions are `tboot_enabled()`, `tboot_probe()`, `tboot_shutdown()`, `tboot_get_dmar_table()`, and late init `tboot_late_init()`. Internals include `check_tboot_version()`, `map_tboot_page(s)()`, `tboot_create_trampoline()`, `tboot_setup_sleep()`, `tboot_sleep()`, `tboot_extended_sleep()`, `tboot_dying_cpu()`, and debugfs `tboot_log_read()`.

### Control Flow
Early probe validates `boot_params.tboot_addr` against E820 reserved memory, fixmaps the shared page, and checks UUID/version. Late init creates a separate page directory mapping tboot physical pages executable at identity addresses, registers a CPUHP dying callback, creates debugfs log access, and installs ACPI sleep callbacks. Shutdown optionally records S3 MAC regions from RAM E820 entries, fills ACPI sleep info, switches CR3 to the tboot page directory, jumps to `shutdown_entry`, and halts forever if it returns.

### State, Persistence, And Dependencies
Persistent state includes the global `tboot` pointer, tboot shared page fields, `tboot_pg_dir`, synthetic `tboot_mm`, AP wait counters, debugfs file, ACPI callback hooks, and a deliberately retained TXT heap mapping for DMAR use. Dependencies include boot params, E820, fixmap/ioremap, page-table allocation, ACPI FADT/FACS, real-mode wakeup vectors, CPU hotplug, debugfs, and TXT config registers.

### Integration Points
SMP hotplug invokes `tboot_dying_cpu()` as APs shut down. ACPI sleep code calls tboot prepare hooks. IOMMU/DMAR setup can call `tboot_get_dmar_table()` to prefer the SINIT-protected DMAR copy. `smpboot.c` calls `tboot_shutdown(TB_SHUTDOWN_WFS)` in CPU play-dead.

### Risks
Identity executable mappings and CR3 switching are high-risk and happen late in shutdown when recovery is limited. Incorrect MAC regions can break S3 integrity. The DMAR TXT heap walk assumes tboot heap layout. The debugfs log maps a fixed physical region and must validate UUID/size before copying.

### Test Signals
Boot with and without tboot, invalid UUID/version/E820 address, S3/S4/S5 shutdown, ACPI reduced-hardware sleep rejection, CPU offline wait-for-SIPI counts, debugfs log reads with valid/invalid UUID, and DMAR table retrieval from TXT heap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/tboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/time.c -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/time.c

### Purpose
`time.c` contains x86 legacy timer initialization glue, profiling PC extraction, late time initialization, and VDSO clocksource sanity checking.

### Important APIs, Types, And Functions
Public functions are `profile_pc()`, `hpet_time_init()`, `time_init()`, and `clocksource_arch_init()`. Internals include `timer_interrupt()`, `setup_default_timer_irq()`, and `x86_late_time_init()`.

### Control Flow
`time_init()` defers real timer setup by assigning `late_time_init`. Late init selects interrupt mode, calls the platform timer init, finalizes interrupt routing, initializes TSC, and enables TPAUSE delay when WAITPKG exists. HPET time init tries HPET first, falls back to PIT, and registers IRQ0 for legacy timer or HPET legacy replacement. The timer interrupt invokes the global clock event handler.

### State, Persistence, And Dependencies
State touched includes `late_time_init`, IRQ0 registration, `global_clock_event`, TSC/delay configuration, and clocksource VDSO mode. Dependencies include x86 init ops, HPET/PIT, clockevents, clocksource, interrupt routing, and CPU feature checks.

### Integration Points
Generic timekeeping calls these arch hooks during boot and clocksource registration. The VDSO path depends on `clocksource_arch_init()` rejecting non-64-bit masks for VDSO-capable clocks.

### Risks
Timer setup ordering matters because interrupt mode selection must precede PIT/HPET init and final interrupt mode must follow it. Registering IRQ0 is needed even without legacy PIT when HPET is in legacy replacement mode. Wrong VDSO mask acceptance can expose broken user time reads.

### Test Signals
Boot with HPET enabled/disabled, PIT fallback, IO-APIC/PIC interrupt modes, WAITPKG-capable CPUs, VDSO and non-VDSO clocksources, clocksource masks not equal to 64 bits, and timer interrupt delivery on IRQ0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/tls.c -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/tls.c

### Purpose
`tls.c` implements x86 `set_thread_area`/`get_thread_area` TLS descriptor management and TLS regset access for ptrace/core-dump interfaces. It validates user descriptors, updates GDT TLS entries, reloads affected segment registers, and serializes descriptor updates against preemption.

### Important APIs, Types, And Functions
Key functions are `do_set_thread_area()`, `SYSCALL_DEFINE1(set_thread_area)`, `do_get_thread_area()`, `SYSCALL_DEFINE1(get_thread_area)`, `regset_tls_active()`, `regset_tls_get()`, and `regset_tls_set()`. Internals include `get_free_idx()`, `tls_desc_okay()`, `set_tls_desc()`, and `fill_user_desc()`.

### Control Flow
Set copies a `user_desc`, accepts empty or historical zero descriptors, rejects 16-bit, non-data, and non-present TLS descriptors, optionally allocates a free TLS slot, validates index bounds, writes one or more descriptors under `get_cpu()`, reloads TLS for the current task, and refreshes DS/ES/FS/GS if they reference the changed selector. Get validates or reads the index, uses nospec masking, converts the descriptor back to `user_desc`, and copies it to userspace. Regset set validates alignment/count and all descriptors before bulk update.

### State, Persistence, And Dependencies
Persistent per-task state is `thread.tls_array`, and on x86-64 possibly `thread.fsbase`/`gsbase` when a non-current target's selector base changes. Dependencies include descriptor helpers, LDT semantics, segment load helpers, nospec array masking, regset/membuf infrastructure, and user access.

### Integration Points
IA32 TLS syscalls, `clone` TLS setup, ptrace regsets, and core dumping consume these helpers. `tls.h` declares the regset callbacks for local use.

### Risks
TLS descriptors are an attack surface for segmentation corner cases. Rejecting 16-bit and non-present DPL3 descriptors avoids espfix and sandbox hazards. Segment reloads are architecture-specific and especially important on x86-64 where returning to user mode does not reload all selectors automatically.

### Test Signals
Test allocation with `entry_number = -1`, empty and all-zero descriptors, invalid 16-bit/code/non-present descriptors, get/set bounds, current and non-current task updates, FS/GS base propagation, ptrace regset get/set, and IA32 clone TLS setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/tls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/tls.h -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/tls.h

### Purpose
`tls.h` is the internal declaration header for x86 TLS regset callbacks implemented in `tls.c`.

### Important APIs, Types, And Functions
It includes `<linux/regset.h>` and declares `regset_tls_active`, `regset_tls_get`, and `regset_tls_set` with the generic user-regset callback typedefs.

### Control Flow
There is no runtime control flow; this header supplies prototypes so other x86 kernel files can reference the TLS regset operations.

### State, Persistence, And Dependencies
No state is owned. Its only dependency is the regset API type definitions.

### Integration Points
The ptrace/user-regset registration code can include this header to connect TLS descriptor access to the generic regset layer while keeping the implementation private to `arch/x86/kernel`.

### Risks
The include guard is minimal but effective for this private header. Signature drift from `tls.c` or the regset API would produce build failures.

### Test Signals
Build coverage with TLS regset support enabled is sufficient; functional signals come from `tls.c` ptrace/regset tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/tls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/trace.c -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/trace.c

### Purpose
`trace.c` provides x86 OS noise tracer integration for local APIC and IPI vectors. When enabled, it registers architecture IRQ tracepoints so osnoise can attribute entry/exit time to specific x86 interrupt vectors.

### Important APIs, Types, And Functions
Public hooks are `osnoise_arch_register()` and `osnoise_arch_unregister()`. Internal callbacks are `trace_intel_irq_entry()` and `trace_intel_irq_exit()`, which call `osnoise_trace_irq_entry()` and `osnoise_trace_irq_exit()`.

### Control Flow
Registration installs tracepoint callbacks for local timer, optional thermal/deferred-error/threshold vectors, SMP call-function and reschedule IPIs, optional IRQ work, platform IPI, error APIC, and spurious APIC vectors. On any registration failure it unwinds previously registered callbacks in reverse order and returns `-EINVAL`. Unregister removes the full set under the same config guards.

### State, Persistence, And Dependencies
Persistent state is the tracepoint registration set. Dependencies include `CONFIG_OSNOISE_TRACER`, `CONFIG_X86_LOCAL_APIC`, generated `asm/trace/irq_vectors.h` tracepoints, and optional APIC/MCE/SMP/IRQ_WORK config symbols.

### Integration Points
The generic osnoise tracer calls these arch hooks to observe x86-specific interrupt noise. The tracepoint names correspond to vector handlers in APIC, SMP, timer, and MCE code.

### Risks
Registration unwind must remain exactly paired or later unregister can remove callbacks that were not installed. Config-guard asymmetry would create build or runtime tracepoint mismatches. Exit descriptions are user-visible tracer labels.

### Test Signals
Enable osnoise with local APIC and combinations of SMP, IRQ_WORK, MCE threshold/deferred error, and thermal vectors. Test registration failure injection, unregister after partial and full registration, and osnoise reports for timer/IPI/APIC vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/trace_clock.c -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/trace_clock.c

### Purpose
`trace_clock.c` implements the x86 TSC trace clock. It exposes a fast ordered cycle counter for tracing contexts that want raw cycles rather than nanoseconds.

### Important APIs, Types, And Functions
The sole function is `u64 notrace trace_clock_x86_tsc(void)`, which returns `rdtsc_ordered()`.

### Control Flow
There is no branching; the trace clock reads the ordered TSC and returns it.

### State, Persistence, And Dependencies
No state is modified. It depends on x86 TSC helpers and ordering semantics from `rdtsc_ordered()`.

### Integration Points
The tracing subsystem can select this clock through x86 trace-clock registration elsewhere. Consumers must know the unit is cycles, not nanoseconds.

### Risks
TSC stability and cross-CPU synchronization affect interpretability. The `notrace` annotation avoids recursive tracing. Mislabeling this as nanoseconds would break trace analysis.

### Test Signals
Verify tracing can select the x86 TSC clock, timestamps are monotonic enough on intended systems, no tracing recursion occurs, and documentation/UI shows cycle units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/trace_clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/traps.c -->
## sources/distributed-fs/ceph-client/arch/x86/kernel/traps.c

### Purpose
`traps.c` is the central x86 synchronous exception handler implementation. It decodes BUG/WARN trap encodings, routes architectural exceptions to signals or kernel oops paths, handles debug and breakpoint traps, coordinates special virtualization/fault cases, and initializes trap entry infrastructure.

### Important APIs, Types, And Functions
Important visible functions include `is_valid_bugaddr()`, `decode_bug()`, `__warn_args()`, `handle_bug()`, `sync_regs()`, `vc_switch_off_ist()`, `fixup_bad_iret()`, many `DEFINE_IDTENTRY*` handlers, and `trap_init()`. Major helpers include `do_trap_no_signal()`, `do_trap()`, `do_error_trap()`, `get_kernel_gp_address()`, `fixup_iopl_exception()`, `try_fixup_enqcmd_gp()`, `gp_try_fixup_and_notify()`, `do_int3()`, `debug_read_reset_dr6()`, `exc_debug_kernel()`, `exc_debug_user()`, `math_error()`, `handle_xfd_event()`, and `ve_raise_fault()`.

### Control Flow
Common trap handling first tries vm86, exception-table, vDSO, kprobe, notifier, or other fixups, then records `thread.error_code/trap_nr` and sends the appropriate signal or dies in kernel mode. Invalid-op runs `handle_bug()` before full exception entry so WARN/BUG/UBSAN/CFI trap encodings can be consumed safely. #GP handles ENQCMD PASID activation, vm86, IOPL CLI/STI emulation, UMIP/vsyscall/vDSO fixups, user SIGSEGV, and kernel address hints before `die_addr()`. #DB splits user and kernel paths, resets DR6 early, disables local breakpoints for kernel handling, and sends SIGTRAP for user step/watchpoint/ICEBP. #DF detects espfix and stack-overflow cases before panic.

### State, Persistence, And Dependencies
State includes `current->thread.error_code`, `trap_nr`, `cr2`, `virtual_dr6`, DR6/DR7/debugctl state, PASID activation, XFD MSRs, FPU/xstate, IDT/FRED entry setup, and per-CPU exception stacks. Dependencies include entry code, notifiers, kprobes/kgdb, BUG/UBSAN/CFI reporting, FPU, TDX/SEV-ES, UMIP, vsyscall emulation, vm86, MCE/NMI entry discipline, and text patching.

### Integration Points
Signal files consume saved trap numbers/error codes in sigcontexts. Static call and WARN encodings are coordinated with `static_call.c` and bug reporting. Ptrace stepping from `step.c` is completed by #DB handling. TDX and SEV-ES entry code depend on safe stack switching and #VE/#VC handling. `trap_init()` sets up CPU entry areas, GHCB handling, TSS/IST state, IDT traps, and CPU exception state.

### Risks
This file sits on privilege-boundary and noinstr paths. Entry ordering, RCU/IRQ state, and instrumentation boundaries are critical. BUG decoding reads kernel text directly. #VE cannot occur in syscall gaps or early NMI entry without severe security risk. #DB recursion is controlled by DR7 save/restore. Incorrect #GP fixups can hide real kernel faults or send wrong user signals.

### Test Signals
Test divide/overflow/UD/BUG/WARN/UBSAN/CFI traps, #BP with kprobes/kgdb/text poking, ptrace #DB watchpoints and single-step, vm86 traps, bad IRET, espfix double-fault recovery, stack guard overflow, ENQCMD PASID #GP fixup, UMIP/vsyscall/vDSO fixups, FPU/SIMD exceptions, XFD dynamic feature faults, TDX #VE, SEV-ES #VC stack switching, and FRED vs IDT configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/traps.c -->
