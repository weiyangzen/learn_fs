# subset-b-000780 grouped research

This grouped report covers the PowerPC kernel files requested by `subset-b-000780`. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/signal_64.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/signal_64.c

## Purpose
Implements 64-bit PowerPC signal delivery, `rt_sigreturn`, and `swapcontext` handling. The file builds/restores user `ucontext`/`sigcontext` frames, including FP, AltiVec/VMX, VSX, endian state, signal masks, alternate stack state, and the special two-context layout needed when a signal interrupts transactional memory.

## Important APIs, Types, and Functions
- `struct rt_sigframe` is the ABI-visible stack frame: `ucontext` first for `sys_rt_sigreturn`, optional transactional `ucontext`, trampoline words, `siginfo`, and the ELFv2 redzone gap.
- `get_min_sigframe_size_64()` reports minimum stack usage to common signal code.
- `prepare_setup_sigcontext()` flushes lazy FP/VMX/VSX state into `thread_struct` before copying to userspace.
- `__unsafe_setup_sigcontext()` writes a normal `sigcontext`, including GPRs, FPRs, VMX/VRSAVE, VSX low halves, `signal`, `handler`, and optional old mask.
- `setup_tm_sigcontexts()` and `restore_tm_sigcontexts()` save/restore checkpointed and transactional register state for TM-aware signal frames.
- `setup_trampoline()` emits an on-stack fallback `bctrl; addi r1; li r0; sc` trampoline when no VDSO signal trampoline exists.
- `SYSCALL_DEFINE3(swapcontext)` saves the old user context and restores a new one, validating whether VSX state is present in the supplied size.
- `SYSCALL_DEFINE0(rt_sigreturn)` restores state from the user frame, including TM cleanup/recheckpointing, altstack restore, and `_TIF_RESTOREALL`.
- `handle_rt_signal64()` allocates and fills the signal frame, sets the return address to VDSO or stack trampoline, and rewrites `pt_regs` so userspace enters the handler.

## Control Flow and State
Signal delivery begins with `get_sigframe()`, optional `prepare_setup_sigcontext()`, an unsafe user write window to populate `rt_sigframe`, a later `copy_siginfo_to_user()`, and finally register edits that arrange handler arguments and the return path. Return flow begins at `rt_sigreturn`, reads `uc_sigmask`, handles any suspended TM state, selects normal or TM restore, restores altstack state, and marks the thread to restore all user registers. `swapcontext` has a two-phase flow: write old context first, then fault-in/read the new context and kill with `SIGSEGV` if a late partial restore fault corrupts register state.

## State and Persistence Behavior
The code persists architectural register state into user memory and restores from it later. It mutates `current->blocked`, `current->restart_block`, `thread_struct` FP/VMX/VSX/TM fields, `pt_regs`, VRSAVE, and `_TIF_RESTOREALL`. TM restore disables preemption around MSR[TS] recheckpointing because page faults or rescheduling with transactional state half-restored can cause a TM bad thing.

## Dependencies and Integration Points
Depends on common signal helpers in `signal.h`, `uaccess`, VDSO symbols, `asm/switch_to.h`, `asm/tm.h`, FP/VMX/VSX save helpers, and syscall table wiring. It is tightly coupled to PowerPC ABI stack layout, ELFv1 function descriptors versus ELFv2 entry points, MSR bits, and the transactional memory assembly in `tm.S`.

## Risks
User-provided frames are trusted only through explicit `access_ok`, `fault_in_readable`, and unsafe access windows; any missing check can corrupt kernel return state. TM paths are fragile because no user access may occur after MSR[TS] is restored. ABI regressions in frame layout, VSX sizing, endian MSR handling, or handler descriptor setup would break signal delivery, debuggers, runtimes, and checkpoint/restore. Trampoline patching requires cache flushing and is sensitive on no-VDSO systems.

## Test Signals
Exercise `rt_sigreturn`, nested signals, `sigaltstack`, VDSO and no-VDSO paths, ELFv1/ELFv2 handlers, `swapcontext` with old and new context sizes, 32-byte VSX extensions, endian switching, FP/VMX/VSX register preservation, bad user frames, and TM-active signals followed by normal return, modified context return, and invalid reserved TM modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/signal_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/smp-tbsync.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/smp-tbsync.c

## Purpose
Provides a generic software timebase synchronization algorithm for SMP PowerPC systems whose platform code supplies `take_timebase` and `give_timebase` operations. It aligns a secondary CPU timebase against the boot CPU by repeated timed contests.

## Important APIs, Types, and Functions
- `tbsync` is a shared cacheline-spaced control block with `tb`, `mark`, `cmd`, `handshake`, `ack`, and `race_result`.
- `smp_generic_take_timebase()` runs on the secondary CPU with interrupts disabled, waiting for commands, optionally setting the timebase, and entering contests.
- `smp_generic_give_timebase()` allocates state, starts the secondary, binary-searches an offset, validates it, sends exit, then frees state.
- `start_contest()` coordinates one batch of contests and scores which CPU crossed the mark first.

## Control Flow and State
The primary sets `running`, waits for secondary `ack`, then repeats `kSetAndTest` contests with varying offsets. Each contest posts target timebase and mark, opens `handshake`, waits until the local timebase reaches the start point, clears handshake, and records a race result. The secondary mirrors the handshake, sets its timebase for `kSetAndTest`, and races to write `race_result`. The chosen offset minimizes absolute score, with a guard loop to handle inaccurate `mttb`.

## State and Persistence Behavior
State is transient and global. Interrupts are disabled on both sides during contests. The only persistent effect is the secondary CPU's hardware timebase being set closer to the primary.

## Dependencies and Integration Points
Uses `get_tb()`, `set_tb()`, SMP bring-up hooks, barriers, and early CPU startup sequencing. It is called from platform `smp_ops` during secondary CPU bring-up.

## Risks
Busy waits can hang boot if the secondary never acknowledges. The volatile protocol depends on precise memory barriers and interrupt-disabled execution. Timebase writes are platform-sensitive, and poor firmware/hardware behavior can leave skew.

## Test Signals
Boot SMP systems requiring generic sync, stress CPU hotplug where platform reuses the hooks, check monotonic timebase deltas across CPUs, and instrument debug scores for convergence rather than oscillation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/smp-tbsync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/smp.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/smp.c

## Purpose
Implements common PowerPC SMP support: IPI dispatch, NMI-style IPIs, crash/stop IPIs, CPU bring-up and hotplug, per-CPU topology masks, big-core/thread-group parsing, scheduler topology, and secondary CPU initialization.

## Important APIs, Types, and Functions
- Global topology state includes `cpu_sibling_map`, `cpu_smallcore_map`, `cpu_l2_cache_map`, `cpu_core_map`, `cpu_coregroup_map`, `has_big_cores`, `coregroup_enabled`, and `shared_caches`.
- `struct smp_ops_t *smp_ops` is the platform integration table for probing, kicking, IPI delivery, timebase handoff, CPU setup, and CPU offline.
- IPI handlers: `call_function_action()`, `reschedule_action()`, `tick_broadcast_ipi_action()`, `nmi_ipi_action()`, `smp_request_message_ipi()`, muxed `smp_ipi_demux[_relaxed]()`, and `arch_*_ipi()` send helpers.
- NMI IPI helpers: `smp_handle_nmi_ipi()`, `smp_send_nmi_ipi()`, `smp_send_safe_nmi_ipi()`.
- CPU lifecycle: `smp_prepare_cpus()`, `smp_prepare_boot_cpu()`, `__cpu_up()`, `start_secondary()`, `__cpu_disable()`, `__cpu_die()`, `arch_cpu_idle_dead()`, and generic hotplug state helpers.
- Topology helpers: `parse_thread_groups()`, `init_thread_group_cache_map()`, `cpu_die_mask()`, `cpu_die_id()`, `cpu_to_core_id()`, `add_cpu_to_masks()`, `remove_cpu_from_masks()`, and `build_sched_topology()`.

## Control Flow and State
Early boot initializes per-CPU masks, boot CPU data, NUMA mappings, optional chip lookup tables, and platform probing. `__cpu_up()` prepares the idle thread, invokes platform preparation and kick, then waits for `cpu_callin_map` and `cpu_online()`. The secondary runs `start_secondary()`, sets up MM context, decrementer, platform CPU setup, timebase sync, NUMA state, topology masks, ftrace enablement, and then enters the CPU hotplug idle state. Hotplug disable removes a CPU from online state, migrates IRQs, drains pending interrupts, removes topology masks, and calls platform death/offline operations.

## State and Persistence Behavior
Persistent state is mostly per-CPU masks, `cpu_callin_map`, `current_set`, `secondary_current`, optional `cpu_state`, systemcfg processor count, PACA current/kstack on PPC64, and scheduler topology. The NMI IPI path uses a global atomic lock, pending mask, busy flag, and callback pointer. Muxed IPIs use per-CPU byte slots in `ipi_message.messages`.

## Dependencies and Integration Points
Integrates with `linux/smp`, scheduler domains, CPU hotplug, interrupt controllers, KVM HV, crash dump/kexec, debugger, NUMA, VDSO getcpu, time/decrementer init, ftrace, firmware/device tree CPU properties, and platform-specific `smp_ops`.

## Risks
CPU bring-up and hotplug are race-prone: incorrect barriers around `cpu_callin_map`, `secondary_current`, or PACA updates can leave CPUs stuck or using the wrong stack/current. NMI IPIs are not truly non-maskable on all platforms and timeouts can race with late handlers. Topology construction depends on firmware properties; bad thread-group/cache data can degrade scheduling or produce inconsistent masks. Crash-stop paths deliberately spin CPUs forever.

## Test Signals
Boot with SMT on/off limits, CPU hotplug loops, crash/kdump stop paths, debugger backtraces, muxed and direct IPI controllers, KVM HV active mode, pseries shared processor topology, big-core systems with `ibm,thread-groups`, NUMA CPU maps, and scheduler domain dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/stacktrace.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/stacktrace.c

## Purpose
Provides PowerPC stack walking for generic stacktrace users, reliable stacktrace validation, and NMI-IPI based remote CPU backtraces on Book3S 64-bit systems.

## Important APIs, Types, and Functions
- `arch_stack_walk()` walks frame backchains from `pt_regs`, current stack, or `task->thread.ksp`.
- `arch_stack_walk_reliable()` validates alignment, monotonic stack growth, stack bounds, exception frames, kernel text return addresses, ftrace graph rewriting, and rethook trampoline presence.
- `arch_trigger_cpumask_backtrace()` uses `nmi_trigger_cpumask_backtrace()` with `raise_backtrace_ipi()` when supported.
- `raise_backtrace_ipi()` sends safe NMI IPIs and falls back to PACA inspection if a CPU does not respond.

## Control Flow and State
Simple walking repeatedly validates SP, reads backlink and saved LR, and calls the consumer. Reliable walking stops at the computed stack end and rejects any ambiguity. Remote backtrace sends an NMI IPI per target, waits up to five seconds for the CPU to clear itself from the mask, and prints PACA state and possibly stale `saved_r1` stack if it times out.

## State and Persistence Behavior
Mostly read-only against task stacks and PACA. The remote path mutates the cpumask passed by the NMI framework and emits diagnostic logs.

## Dependencies and Integration Points
Depends on PowerPC stack frame layout constants, `validate_sp()`, ftrace graph return address repair, rethook, `paca_ptrs`, and SMP NMI IPI functions.

## Risks
Reliable unwinding intentionally rejects exception frames and rethooks, which may reduce coverage but avoids false reliability. Remote fallback PACA stack traces can be stale or corrupt; diagnostics are guarded by `virt_addr_valid()` but still diagnostic-only.

## Test Signals
Run `stack_trace_save*`, livepatch/ftrace graph enabled traces, kretprobe/rethook stacks, blocked CPU backtraces, invalid task stack simulations, and lockup/NMI backtrace paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/static_call.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/static_call.c

## Purpose
Implements PowerPC runtime patching for Linux static calls, converting call sites and trampolines between NOP/return, direct branches, and long trampoline dispatch.

## Important APIs, Types, and Functions
- `arch_static_call_transform(site, tramp, func, tail)` is the exported architecture hook.
- Uses `patch_instruction()`, `patch_branch()`, `patch_ulong()`, `text_mutex`, `PPC_SCT_RET0`, and `PPC_SCT_DATA`.

## Control Flow and State
The function serializes on `text_mutex`, classifies the requested target as NULL, `__static_call_return0`, short branch range, or trampoline-backed long target, then patches either a call site, tail-call site, or trampoline. For long trampoline targets it stores the real function pointer in trampoline data before patching trampoline code.

## State and Persistence Behavior
Persists changes directly in kernel text/trampoline memory. Failures panic because static-call text patching must not leave inconsistent executable code.

## Dependencies and Integration Points
Integrates with generic `static_call` infrastructure and PowerPC text patching. Branch range checks must match instruction encoding limits.

## Risks
Wrong branch-range decisions or partial patch failure can redirect kernel execution. Concurrency is protected by `text_mutex`, but callers rely on instruction patching to handle cache coherency.

## Test Signals
Boot with static calls enabled, toggle static keys using return0 and NULL targets, test long out-of-range call targets, and run under ftrace/livepatch text-patching stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/static_call.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/suspend.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/suspend.c

## Purpose
Defines PowerPC hibernation/suspend memory exclusion for the kernel `__nosave` section.

## Important APIs, Types, and Functions
- `pfn_is_nosave(pfn)` computes physical PFN bounds for `__nosave_begin` to aligned `__nosave_end`.

## Control Flow and State
The function is a pure range test used by suspend image code when deciding which PFNs not to save.

## State and Persistence Behavior
No mutable state. It reflects linker section addresses into PFN ranges.

## Dependencies and Integration Points
Depends on `asm/sections.h`, `__pa()`, `PAGE_SHIFT`, and suspend core `pfn_is_nosave` hooks.

## Risks
Incorrect section boundaries or alignment would cause hibernation to save volatile memory or omit required memory.

## Test Signals
Validate hibernation image creation, inspect nosave PFN bounds, and test linker changes that move `__nosave` symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/suspend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/switch.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/switch.S

## Purpose
Implements the low-level PowerPC context switch routine `_switch` plus Book3S 64-bit branch predictor/cache flush helpers and stack SLB pinning needed while switching kernel stacks.

## Important APIs, Types, and Functions
- `flush_branch_caches` is a patchable Book3S 64 helper for link stack/count cache flushing.
- `pin_stack_slb` bolts the next task stack SLB entry on hash MMU systems before switching SP.
- `do_switch_32` and `do_switch_64` macros update current/thread/PACA state and stack pointers.
- `_switch(prev_thread, next_thread)` saves nonvolatile GPRs, CCR, LR/NIP, old KSP, switches to the next stack/current, restores the next saved state, and returns previous task.

## Control Flow and State
On entry interrupts are disabled. `_switch` creates a switch frame on the old stack, saves nonvolatile state, updates architecture current pointers, optionally flushes branch prediction structures and user streams, pins the next stack mapping, then pivots `r1` to the new stack and restores the new task's saved frame.

## State and Persistence Behavior
Persists each task's kernel SP in `thread_struct.KSP` and updates PPC64 PACA fields for `current`, stack canary, and `PACAKSAVE`. The routine is the ordering point for task migration and relies on scheduler lock barriers for MMIO ordering.

## Dependencies and Integration Points
Depends on offsets generated in `asm-offsets.h`, PACA layout, KUAP checks, feature fixup patch sites, hash MMU SLB shadow structures, and `copy_thread()` creating frames compatible with `_switch`.

## Risks
Any offset/layout mismatch corrupts task stacks. Stack SLB handling is sensitive to hash versus radix MMU. Branch-cache flush patch sites mitigate speculation vulnerabilities and must stay aligned and correctly patched.

## Test Signals
Boot with stack protector, KUAP, hash/radix MMU, speculation mitigations, and heavy context-switch workloads. Verify forked tasks return through compatible frames and CPU migration preserves MMIO ordering assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/switch.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp.c

## Purpose
Provides common PowerPC processor-state save/restore hooks for software suspend.

## Important APIs, Types, and Functions
- `save_processor_state()` flushes lazy special register state from the current task and hard-disables IRQs on PPC64.
- `restore_processor_state()` restores the MMU context on PPC32.

## Control Flow and State
Called by hibernation core before and after image creation/copyback. Save flushes all lazy FP/vector/etc. state into `current->thread`; restore reselects the active MM on 32-bit.

## State and Persistence Behavior
Mutates current task thread state by forcing lazy register materialization. IRQ state is changed on PPC64.

## Dependencies and Integration Points
Uses `flush_all_to_thread()`, `hard_irq_disable()`, and `switch_mmu_context()`. Pairs with assembly resume/suspend routines in `swsusp_*.S`.

## Risks
Missing lazy state flush would produce corrupted hibernation images. IRQ/MMU state assumptions must match the low-level assembly resume path.

## Test Signals
Hibernate/resume with FP, VMX, VSX, and active user state; PPC32 MM context restoration; PPC64 interrupt state during suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp_32.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp_32.S

## Purpose
Implements 32-bit classic PowerPC hibernation suspend/resume assembly for saving CPU registers, copying restored pages back, restoring timebase/MMU-related registers, flushing caches/TLBs, and returning to the restored kernel.

## Important APIs, Types, and Functions
- `swsusp_save_area` stores SP, LR/CR, MSR, SDR1, SPRGs, BATs, timebase, r2, and r12-r31.
- `swsusp_arch_suspend()` saves state and calls `swsusp_save`.
- `swsusp_arch_resume()` copies pages from `restore_pblist`, flushes/invalidate caches, restores saved control state, TLBs, timebase, decrementer, and callee-saved registers.
- `turn_on_mmu` uses SRR0/SRR1 and `rfi` to restore MSR/MMU state.

## Control Flow and State
Suspend saves register and MMU state, calls the generic hibernation save function, restores LR, and returns. Resume disables data translation to avoid hash/TLB misses while copying pages, iterates the page backup list, flushes L1 cache and TLBs, restores SPRG/SDR1/timebase, restarts decrementer, restores GPRs, and returns 0.

## State and Persistence Behavior
Uses a static save area in `.data` that survives until the restored image takes over. It directly writes BAT/SDR1/SPRG/timebase/decrementer state and physical memory pages.

## Dependencies and Integration Points
Depends on hibernation `restore_pblist`/`pbe_*` offsets, 32-bit MMU/BAT features, `swsusp_save`, `__nosave` layout, and cache/TLB assembly helpers.

## Risks
The file itself notes limitations around G5/750 MMU handling. Running with translation partially disabled and copying physical pages is highly sensitive to mappings, cache coherency, and identical loader/restored kernels.

## Test Signals
Hibernate/resume on classic 32-bit Book3S with and without high BATs, large memory, AltiVec users, and page lists spanning kernel/data text. Verify timebase and decrementer continue after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp_64.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp_64.c

## Purpose
Provides the C post-copyback hook for 64-bit PowerPC hibernation resume.

## Important APIs, Types, and Functions
- `do_after_copyback()` restores IOMMU state, touches the softlockup watchdog, and issues a memory barrier.

## Control Flow and State
Called from `swsusp_asm64.S` after restored pages are copied and architectural registers are partly restored.

## State and Persistence Behavior
Restores global IOMMU programming and updates watchdog activity timestamp. The barrier orders copyback and IOMMU/watchdog side effects.

## Dependencies and Integration Points
Depends on `iommu_restore()`, watchdog infrastructure, and 64-bit hibernation assembly.

## Risks
If omitted or misordered, devices may DMA against stale IOMMU state after resume, or the watchdog may fire during long resume copyback.

## Test Signals
Hibernate/resume with active IOMMU/DMA devices and softlockup watchdog enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp_85xx.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp_85xx.S

## Purpose
Implements hibernation suspend/resume for Freescale BookE/e500-class 85xx systems.

## Important APIs, Types, and Functions
- `swsusp_save_area` stores SP, LR/CR, MSR, TCR, SPRG0-7, timebase, r2, and r12-r31.
- `swsusp_arch_suspend()` saves register/control state and calls `swsusp_save`.
- `swsusp_arch_resume()` copies pages, flushes data/instruction caches, invalidates TLBs, restores SPRGs/MSR/timebase/TCR, clears TSR pending bits, kicks decrementer, and returns.

## Control Flow and State
The resume path copies each `pbe` page using virtual addresses suitable for this BookE path, flushes caches via platform helpers, invalidates all TLBs because mappings may differ, restores special-purpose registers, restarts timer state, and restores saved nonvolatile registers.

## State and Persistence Behavior
Uses static `.data` save area and directly rewrites hardware SPRs and restored memory pages. It changes timer state by restoring TCR and clearing TSR bits.

## Dependencies and Integration Points
Depends on BookE SPR names, `_tlbil_all`, `flush_dcache_L1`, `flush_instruction_cache`, hibernation page backup structures, and generic `swsusp_save`.

## Risks
Incorrect TLB/cache flush ordering can execute stale instructions or use old translations. TCR/TSR restore must avoid pending timer/watchdog surprises after resume.

## Test Signals
Hibernate/resume on e500/e6500-class hardware, with timer interrupts enabled, large page-copy lists, and different MMU mappings after restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp_85xx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp_asm64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp_asm64.S

## Purpose
Implements 64-bit PowerPC hibernation suspend/resume assembly for Book3S and non-Book3S 64-bit variants.

## Important APIs, Types, and Functions
- `swsusp_save_area` stores r1/r2/r12-r31/r13, LR/CR/XER/MSR, timebase, SDR1 or TCR/SPRG1, and control state.
- `swsusp_arch_suspend()` saves state, makes a small temporary stack adjustment, calls `swsusp_save`, then restores LR.
- `swsusp_arch_resume()` copies restored pages, flushes caches/TLBs where needed, restores timebase and registers, restores MSR/SDR1 or TCR/SPRG1, calls `slb_flush_and_restore_bolted()` on Book3S, then `do_after_copyback()`.

## Control Flow and State
Resume first stops AltiVec streams, copies all pages in `restore_pblist` 8 bytes at a time, performs Book3S cache flush and `tlbia`, restores the saved timebase and GPRs, restores MMU/timer control, optionally invalidates all TLBs on non-Book3S, calls post-copyback C code, restores LR, and returns 0.

## State and Persistence Behavior
The static save area persists CPU state across the restore transition. The routine mutates architectural registers, timebase, MMU state, cache/TLB state, memory image pages, and IOMMU state through `do_after_copyback()`.

## Dependencies and Integration Points
Integrates with generic hibernation page backup lists, Book3S firmware feature checks, SLB restore helpers, `do_after_copyback()` in `swsusp_64.c`, and feature fixups for AltiVec.

## Risks
Ordering is critical: memory copy, cache flush, TLB invalidation, MSR restoration, SLB restore, and IOMMU restore must happen in a valid sequence. The code uses low-level register assumptions and depends on `asm-offsets.h` matching C structures.

## Test Signals
Hibernate/resume on pseries/Book3S hash and radix systems, non-Book3S 64 systems, with IOMMU devices, AltiVec workloads, watchdog enabled, and large restored page lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp_asm64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/sys_ppc32.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/sys_ppc32.c

## Purpose
Implements 32-bit PowerPC syscall wrappers whose 64-bit arguments are split across constrained register pairs. This supports both native PPC32 and compat calls on PPC64.

## Important APIs, Types, and Functions
- `PPC32_SYSCALL_DEFINE*` maps to native `SYSCALL_DEFINE*` or compat `COMPAT_SYSCALL_DEFINE*`.
- Wrappers include `ppc_pread64`, `ppc_pwrite64`, `ppc_readahead`, `ppc_truncate64`, `ppc_ftruncate64`, `ppc32_fadvise64`, `ppc_sync_file_range2`, and native PPC32 `ppc_fallocate`.
- `merge_64(high, low)` reconstructs 64-bit offsets/lengths.

## Control Flow and State
Each syscall wrapper decodes split arguments, discards ABI padding registers where needed, and calls the generic `ksys_*` implementation.

## State and Persistence Behavior
No local persistent state. Effects are those of the delegated filesystem/memory syscalls.

## Dependencies and Integration Points
Depends on syscall ABI tables, `asm/syscalls.h`, compat syscall infrastructure, and generic kernel syscall helpers.

## Risks
Wrong register pairing silently targets the wrong file offset or length. Compat/native macro differences must match `ARCH_HAS_SYSCALL_WRAPPER` and table generation.

## Test Signals
Run 32-bit userspace on 32-bit and 64-bit kernels for large-file pread/pwrite, truncate/ftruncate, fallocate, fadvise, readahead, and sync_file_range2 with offsets above 4 GiB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/sys_ppc32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/syscall.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/syscall.c

## Purpose
Implements the C-level PowerPC system call exception path from user mode into the syscall table.

## Important APIs, Types, and Functions
- `system_call_exception(struct pt_regs *regs, unsigned long r0)` is the central syscall dispatcher.
- Handles KUAP/KUEP/pkey register capture, context tracking, random kstack offset, tracing entry, TM syscall abort, syscall trace hooks, compat table dispatch, and nospec bounds barrier.

## Control Flow and State
The path locks KUAP, reconciles irq trace state, exits user context, randomizes kernel stack offset, validates user-mode entry assumptions, saves AMR/IAMR when pkeys are active, restores debug registers, accounts user/stolen time, prepares soft mask state, handles transactional-memory syscalls, enables IRQs, processes ptrace/seccomp tracing, validates syscall number, applies a speculation barrier, then calls the native or compat syscall table entry.

## State and Persistence Behavior
Mutates `pt_regs` saved pkey fields, thread flags (`_TIF_RESTOREALL` for TM), context tracking state, CPU accounting, IRQ soft-mask metadata, and potentially returns modified `regs->gpr[3]` when tracing rejects a syscall. TM transactional syscalls are doomed with `tabort` and return `-ENOSYS` internally.

## Dependencies and Integration Points
Integrates with entry assembly, KUAP/KUEP, context tracking, ptrace/seccomp syscall trace, compat syscall tables in `systbl.c`, transactional memory support in `tm.S`, BookE debug restoration, and syscall wrappers.

## Risks
This is a security-critical entry path. Incorrect AMR/IAMR handling can expose user access; wrong IRQ/context tracking state breaks lockdep/RCU; missing nospec barrier can expose syscall table speculation; TM handling must avoid returning via RFSCV to transactional state.

## Test Signals
Native and compat syscall smoke tests, ptrace/seccomp tracing, invalid syscall numbers, unsupported `scv` vector SIGILL, pkey/KUAP configurations, transactional-memory active syscalls, lockdep/RCU context tracking, and syscall fuzzers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/syscalls.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/syscalls.c

## Purpose
Contains miscellaneous PowerPC syscall implementations with nonstandard ABI behavior: mmap variants, PPC64 personality translation, 64-bit fadvise splitting, and endian switching.

## Important APIs, Types, and Functions
- `do_mmap2()` validates protection with `arch_validate_prot()`, checks offset alignment, and calls `ksys_mmap_pgoff()`.
- `mmap2`, compat `mmap2`, and `mmap` translate 4 KiB or page-size offsets.
- `ppc64_personality` preserves/normalizes `PER_LINUX32` behavior for 32-bit tasks on PPC64.
- `ppc_fadvise64_64` merges split offset/length arguments.
- `switch_endian` toggles the return MSR little-endian bit and sets `_TIF_RESTOREALL`.

## Control Flow and State
Most functions validate ABI-specific arguments and delegate to generic kernel helpers. `switch_endian` directly edits the saved user MSR in `current->thread.regs`, then forces a full register restore so r3/nonvolatile registers are preserved on return.

## State and Persistence Behavior
Persistent effects are from mmap/personality/fadvise syscalls. `switch_endian` persists an endian-mode change in the user return frame and thread flags.

## Dependencies and Integration Points
Depends on syscall table generation, generic `ksys_*` helpers, PowerPC memory protection validation, and MSR return helpers.

## Risks
Offset alignment shifts must match ABI expectations. Endian switching is unusual and can break if return path clobbers registers or fails to restore full state.

## Test Signals
Test `mmap`, `mmap2`, compat `mmap2`, protection-key validation, PPC64 32-bit personality behavior, `ppc_fadvise64_64` with large offsets/lengths, and userspace `switch_endian` round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/syscalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/syscalls/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/syscalls/Makefile

## Purpose
Builds generated PowerPC syscall UAPI headers and kernel syscall table headers from `syscall.tbl`.

## Important APIs, Types, and Functions
- Defines output directories `arch/$(SRCARCH)/include/generated/uapi/asm` and `.../generated/asm`.
- Uses `scripts/syscallhdr.sh` and `scripts/syscalltbl.sh`.
- Generates `unistd_32.h`, `unistd_64.h`, `syscall_table_32.h`, `syscall_table_64.h`, and `syscall_table_spu.h` with ABI filters.

## Control Flow and State
The Makefile creates generated include directories, wires `if_changed` commands per target, and exposes `all` to build both UAPI and kernel generated headers.

## State and Persistence Behavior
Persists generated headers under the architecture generated include tree. It has no runtime state.

## Dependencies and Integration Points
Consumes `arch/powerpc/kernel/syscalls/syscall.tbl` and generic scripts. Outputs are included by `systbl.c` and userspace-facing unistd headers.

## Risks
Wrong ABI filters would expose wrong syscall numbers or table entries for 32-bit, 64-bit, nospu, or SPU ABIs. Directory creation via `$(shell mkdir -p ...)` happens at parse time.

## Test Signals
Run architecture header generation, compare generated syscall numbers/tables after `syscall.tbl` changes, and build 32-bit, 64-bit, compat, and SPU configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/syscalls/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/sysfs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/sysfs.c

## Purpose
Creates and manages PowerPC CPU sysfs files for topology, physical IDs, CPU hotplug registration, PMU and SPR access, DSCR defaults, pseries idle counters, SVM status, and selected e500 power-management controls.

## Important APIs, Types, and Functions
- `DEFINE_PER_CPU(struct cpu, cpu_devices)` backs CPU device registration.
- SPR/PMC macros generate `read_*`, `write_*`, `show_*`, and `store_*` functions that run on the target CPU via `smp_call_function_single()`.
- DSCR support: `dscr_default`, `show/store_dscr`, `show/store_dscr_default`, `sysfs_create_dscr_default()`.
- e500 controls: PW20 and AltiVec idle state/wait-time attributes manipulate `SPRN_PWRMGTCR0`.
- `ppc_enable_pmcs()` enables PMCs once per CPU and marks PMU in use.
- `register_cpu_online()` creates per-CPU attributes according to CPU features and `cur_cpu_spec->pmc_type`; `unregister_cpu_online()` removes them.
- Exported helpers `cpu_add_dev_attr[_group]()` and `cpu_remove_dev_attr[_group]()` add/remove attributes across possible CPUs.
- `topology_init()` registers CPU devices, physical ID files, CPUHP callbacks, DSCR default, and SVM file.

## Control Flow and State
At `subsys_initcall`, the code registers present/hotpluggable CPU devices and installs a CPU hotplug state. On CPU online, it obtains the OF CPU node, creates SMT snooze, PMU, PURR/SPURR/PIR/TSCR, DSCR, pseries idle, and e500 idle files depending on config and feature bits, then calls cacheinfo online. Offline removes the same files, cacheinfo state, and OF node reference.

## State and Persistence Behavior
Persistent kernel state includes per-CPU device objects, sysfs files, `dscr_default`, per-PACA DSCR defaults, per-CPU `pmcs_enabled`, e500 idle wait globals, and OF node references. Sysfs writes can directly modify hardware SPRs on target CPUs.

## Dependencies and Integration Points
Integrates with CPU subsystem, CPU hotplug, OF CPU nodes, cacheinfo, PMU/PMC definitions, PACA/LPPACA, firmware features, pseries idle accounting, secure virtual machine status, and platform CPU probe/release hooks.

## Risks
Sysfs SPR writes are privileged but dangerous: wrong values can affect performance counters, power management, or CPU behavior. Attribute add/remove must mirror exactly across hotplug to avoid stale sysfs files. `smp_call_function_single()` assumes target CPUs are online and responsive. DSCR updates across all CPUs must respect task inheritance semantics.

## Test Signals
CPU online/offline loops with sysfs scanning, read/write DSCR and PMU attributes, pseries idle PURR/SPURR exposure, e6500 PW20/AltiVec idle controls, secure guest `svm` file, NUMA node symlinks, and dynamic `cpu_add_dev_attr_group()` users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/systbl.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/systbl.c

## Purpose
Defines PowerPC native and compat syscall function tables from generated syscall table headers.

## Important APIs, Types, and Functions
- `sys_call_table[]` includes either `syscall_table_64.h` or `syscall_table_32.h`.
- `compat_sys_call_table[]` includes 32-bit table entries with compat handlers when `CONFIG_COMPAT` is enabled.
- `__SYSCALL` macro casts handlers to common `syscall_fn` when syscall wrappers are not used.

## Control Flow and State
This is static table initialization at build time; runtime syscall dispatch indexes these arrays in `system_call_exception()`.

## State and Persistence Behavior
Exports read-only syscall dispatch tables in kernel memory.

## Dependencies and Integration Points
Depends on generated headers from `kernel/syscalls/Makefile`, `asm/syscalls.h`, and `CONFIG_ARCH_HAS_SYSCALL_WRAPPER` calling convention.

## Risks
Mismatched generated headers or wrong compat macro expansion can dispatch to native handlers with compat arguments or vice versa. Casts are intentional but hide type mismatches when wrappers are disabled.

## Test Signals
Build native 32-bit, native 64-bit, and compat configs; run syscall ABI tests; verify unknown syscall bounds in `system_call_exception()` and table size match `NR_syscalls`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/systbl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/tau_6xx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/tau_6xx.c

## Purpose
Implements thermal monitoring for 6xx/750-class CPUs with Thermal Assist Units (TAU), maintaining low/high temperature thresholds and optionally handling TAU interrupts.

## Important APIs, Types, and Functions
- `struct tau_temp tau[NR_CPUS]` stores interrupt count, low/high thresholds, and whether the window grew.
- `set_thresholds()` writes THRM1/THRM2 threshold SPRs.
- `TAUupdate()` reads THRM1/THRM2, adjusts thresholds when low/high trips, and clears threshold registers.
- `TAUException()` handles TAU interrupts when `CONFIG_TAU_INT`.
- `tau_timeout()` periodically polls/updates thresholds, shrinks the window, and restarts THRM3 sampling.
- `TAU_init()` initializes all CPUs, starts an ordered workqueue, and exposes `tau_initialized`.
- `cpu_temp_both()`, `cpu_temp()`, and `tau_interrupts()` expose readings/counters.

## Control Flow and State
Initialization checks `CPU_FTR_TAU`, decides whether interrupts are usable for ppc750, allocates an ordered workqueue, initializes thresholds on each CPU, then queues recurring work. The work sleeps for `shrink_timer`, runs `tau_timeout()` on each CPU, and requeues itself. Interrupt mode updates thresholds immediately in `TAUException`.

## State and Persistence Behavior
Per-CPU threshold state persists in `tau[]` and hardware THRM SPRs. The workqueue is long-lived. `tau_int_enable` and `tau_initialized` are global mode indicators.

## Dependencies and Integration Points
Depends on CPU feature/spec detection, THRM SPR definitions, interrupt entry macros, `on_each_cpu()`, workqueues, and consumers of exported temperature helper functions.

## Risks
Threshold adjustments are heuristic and uncalibrated. Workqueue recursion has no teardown path here. Incorrect TAU interrupt enablement or SPR writes can cause interrupt storms or stale temperature windows.

## Test Signals
Boot on TAU-capable and non-TAU CPUs, observe threshold movement under thermal load, test interrupt and polling configs, CPU hotplug/SMP behavior, and helper return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/tau_6xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/time.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/time.c

## Purpose
Provides common PowerPC timebase, clocksource, decrementer clockevent, delay, virtual CPU accounting, timer interrupt, persistent clock, RTC, suspend IRQ, and scheduler clock logic.

## Important APIs, Types, and Functions
- `clocksource_timebase` exposes `get_tb()` as a continuous clocksource.
- `decrementer_clockevent`, per-CPU `decrementers`, and `decrementers_next_tb` implement one-shot timer events.
- Time globals include `tb_ticks_per_jiffy`, `tb_ticks_per_usec`, `tb_ticks_per_sec`, `ppc_proc_freq`, `ppc_tb_freq`, `decrementer_max`, `boot_tb`, and conversion scale/shift.
- Vtime functions account kernel, idle, hardirq, softirq, guest, steal, and scaled cputime.
- `__delay()`/`udelay()` spin on timebase unless `tb_invalid`.
- `arch_irq_work_raise()` marks pending irq work and programs decrementer.
- `timer_interrupt()` handles decrementer interrupts, irq work, machine-check irq-context handlers, and clockevent dispatch/rearm.
- `time_init()` calibrates frequencies, computes `tb_to_ns` scale, initializes VDSO/systemcfg data, decrementer, clocksource, broadcast ticks, OF clocks, and sched-clock irqtime.
- Persistent clock helpers read/write RTC through `ppc_md`; optional `rtc-generic` device is registered.

## Control Flow and State
Boot calls platform or generic calibration from device tree, computes timebase conversion, registers clocksource and the boot CPU decrementer, and initializes clock infrastructure. Secondary CPUs call `secondary_cpu_time_init()`. Timer interrupts optionally hard-enable IRQs after parking the decrementer, run irq work, compare `get_tb()` to `decrementers_next_tb`, invoke the event handler or reprogram the decrementer.

## State and Persistence Behavior
Maintains global frequency/conversion state, per-CPU next decrementer deadlines, per-task/per-CPU accounting accumulators, RTC timezone offset, boot timebase, and `tb_invalid` recovery behavior. Persistent clock updates go to platform RTC.

## Dependencies and Integration Points
Integrates with clocksource/clockevents, VDSO data page, pseries SPLPAR stolen time, KVM host decrementer rearm, irq_work, machine-check handlers, suspend hooks, RTC platform hooks, OF clock init, and scheduler/accounting code.

## Risks
Frequency calibration errors affect all timekeeping. Decrementer max/large decrementer setup must match CPU features and firmware `ibm,dec-bits`. Timer interrupt ordering with hard IRQ enable, irq work, and watchdog is subtle. Vtime accounting assumes interrupts disabled and correct SPURR/PURR behavior.

## Test Signals
Clocksource stability tests, high-resolution timers, CPU hotplug timer init, KVM HV decrementer paths, pseries stolen time, suspend/resume IRQ disable/enable, RTC read/write, `udelay` under TB error injection, and cputime accounting validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/tm.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/tm.S

## Purpose
Implements low-level PowerPC transactional memory helpers for enabling/disabling TM, saving/restoring TM SPRs, aborting transactions, reclaiming transactional state at context switch/signal paths, and recheckpointing saved state.

## Important APIs, Types, and Functions
- `tm_enable()`, `tm_disable()`, and `tm_abort(cause)` are exported helpers.
- `tm_save_sprs()`/`tm_restore_sprs()` move TFHAR/TEXASR/TFIAR between SPRs and `thread_struct`.
- `tm_reclaim(thread, cause)` aborts/reclaims a suspended transaction and saves checkpointed GPR/FPR/VMX/VSX/TAR/DSCR/AMR/PPR/TM SPR state into `thread_struct`.
- `__tm_recheckpoint(thread)` reloads checkpointed state and executes `TRECHKPT` so the task can resume with transactional state.

## Control Flow and State
`tm_reclaim` builds a special stack frame, enables FP/VMX/VSX with IRQs hard-off, verifies suspended state, clears recoverability while using scratch SPR/PACA-only accesses, executes `TRECLAIM`, reconstructs kernel PACA/SP, saves user checkpointed registers into `thread_struct`, saves FP/vector/TM SPR state, restores kernel AMR/MSR, and returns. `__tm_recheckpoint` loads checkpointed FP/vector/GPR/special state, performs sanity checks on TEXASR and MSR, temporarily stores user r1/r5/r13 on stack, clears RI, executes `TRECHKPT`, restores PACA/kernel state, and returns.

## State and Persistence Behavior
Mutates MSR TM/RI/FP/VEC/VSX bits, PACA scratch fields, `thread_struct` checkpointed and live TM fields, DSCR/PPR/AMR/TAR, and hardware TM SPRs. It must run with IRQs off and carefully avoids faults while RI is clear.

## Dependencies and Integration Points
Coupled to signal TM handling in `signal_64.c`, context switch code, `thread_struct` offsets, PACA layout, FPU/VMX/VSX save macros, TM opcodes, feature fixups, and exported helpers used by modules/kernel code.

## Risks
Extremely sensitive to register clobbering, stack layout, recoverability, and fault avoidance. Bugs can corrupt user transactions, kernel PACA state, or make unrecoverable exceptions. Requires matching C structure offsets and CPU TM feature behavior.

## Test Signals
TM userspace stress with signals, preemption, context switches, ptrace, FP/VMX/VSX inside transactions, syscall aborts, suspended transactions, and invalid CPU feature configs. Add lockdep/RCU/watchdog coverage for IRQ-off reclaim/recheckpoint durations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/tm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/Makefile

## Purpose
Selects and builds PowerPC tracing objects, particularly ftrace C/assembly variants and the trace clock.

## Important APIs, Types, and Functions
- Builds `ftrace.o`/`ftrace_entry.o` for PPC32 and for PPC64 when mprofile/patchable entry is used.
- Builds `ftrace_64_pg.o`/`ftrace_64_pg_entry.o` for older PPC64 profiling ABI cases.
- Builds `trace_clock.o` under `CONFIG_TRACING`.
- Removes ftrace instrumentation from ftrace implementation files and disables GCOV/KCOV/KCSAN/UBSAN on sensitive text-patching files.

## Control Flow and State
Pure build logic based on `CONFIG_FUNCTION_TRACER`, `CONFIG_MPROFILE_KERNEL`, `CONFIG_ARCH_USING_PATCHABLE_FUNCTION_ENTRY`, `CONFIG_PPC64`, and `CONFIG_PPC32`.

## State and Persistence Behavior
No runtime state. It controls which object files enter the kernel and which instrumentation is suppressed.

## Dependencies and Integration Points
Integrates with Kbuild, tracing/ftrace config options, sanitizer/gcov/kcov build flags, and architecture-specific ftrace variants.

## Risks
Selecting the wrong ftrace implementation for an ABI/compiler mode breaks dynamic ftrace patching. Instrumenting ftrace text-patching code can recurse or perturb sensitive code.

## Test Signals
Build matrix across PPC32/PPC64, mprofile, patchable function entry, function graph tracer, dynamic ftrace with regs/direct/call-ops, and sanitizer/kcov/gcov configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/ftrace.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/ftrace.c

## Purpose
Implements the modern/common PowerPC dynamic ftrace text-patching backend for PPC32 and PPC64 mprofile/patchable-entry modes, including out-of-line stubs, call-ops, direct calls, module trampolines, init trampolines, and function graph tracing.

## Important APIs, Types, and Functions
- `ftrace_call_adjust()` maps compiler-recorded addresses to actual patch sites, including Clang PPC64 local-entry correction.
- `ftrace_read_inst()`, `ftrace_validate_inst()`, and `ftrace_modify_code()` safely verify and patch instructions.
- `ftrace_get_call_inst()` chooses direct branch, kernel ftrace trampoline, module trampoline, or fallback target.
- `ftrace_init_ool_stub()` allocates and patches an out-of-line stub when `CONFIG_PPC_FTRACE_OUT_OF_LINE`.
- `ftrace_replace_code()` overrides generic patching to update records in-place without stop_machine.
- `ftrace_init_nop()`, `ftrace_make_call()`, `ftrace_update_ftrace_func()`, `arch_ftrace_update_code()`, `ftrace_dyn_arch_init()`, and `ftrace_free_init_tramp()` provide ftrace arch hooks.
- `ftrace_graph_func()` redirects return addresses for function graph tracing.

## Control Flow and State
Initialization builds text/init trampolines to `FTRACE_REGS_ADDR` or ftrace caller using TOC or PC-relative code. Each ftrace record is initialized by validating the compiler sequence, possibly patching mflr/std instructions, creating out-of-line stubs, and setting call-ops storage. Runtime updates iterate records, compute old/new ftrace targets, patch the call instruction or out-of-line stub, update call-ops pointers, and toggle original function patch sites for out-of-line mode.

## State and Persistence Behavior
Persists mutable instruction text at ftrace sites, trampoline areas, module trampolines/stubs, out-of-line stub reservations, and optional per-record ftrace ops pointers. `ftrace_tramps[]` tracks reachable kernel trampolines.

## Dependencies and Integration Points
Integrates with generic dynamic ftrace, modules, livepatch/direct calls through assembly entry code, PowerPC text patching/cache flush, TOC/PACATOC, section boundaries, compiler profiling sequences, and function graph tracer.

## Risks
Text patching must validate exact old instructions or it can corrupt arbitrary code. Branch-range limits require trampolines; missing reachable trampolines disables tracing. Compiler ABI changes, especially local/global entry behavior, can move patch sites. Out-of-line stubs must remain in branch range and their sequence must match `ftrace_entry.S` decoding.

## Test Signals
Enable/disable dynamic ftrace repeatedly, load/unload modules, run with Clang and GCC, patchable function entry, out-of-line stubs, call-ops, direct calls, livepatch, function graph tracer, inittext freeing, and records near branch range limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/ftrace_64_pg.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/ftrace_64_pg.c

## Purpose
Implements the older PPC64 profiling ABI dynamic ftrace backend used when not building with mprofile/patchable function entry. It patches `bl _mcount` call sites, handles TOC restore sequences, module trampolines, compiler long-branch trampolines, and function graph tracing.

## Important APIs, Types, and Functions
- `ftrace_call_adjust()` returns recorded addresses unchanged for this ABI.
- `ftrace_call_replace()`, `ftrace_modify_code()`, `test_24bit_addr()`, `is_bl_op()`, `is_b_op()`, and `find_bl_target()` build/validate branches.
- `setup_mcount_compiler_tramp()` rewrites compiler long-branch trampolines from `_mcount` to `ftrace_caller`/`ftrace_regs_caller`.
- `ftrace_make_nop()`, `ftrace_make_call()`, and `ftrace_modify_call()` patch direct, kernel trampoline, or module trampoline calls.
- `ftrace_update_ftrace_func()`, `ftrace_dyn_arch_init()`, and `ftrace_free_init_tramp()` manage global ftrace call target and kernel trampolines.
- Function graph helpers patch `ftrace_graph_call` and replace LR through `prepare_ftrace_return()`/`ftrace_graph_func()`.

## Control Flow and State
NOP conversion either patches a within-range branch to `nop`, rewrites kernel compiler trampolines then nops the call, or validates module trampoline target and patches a `b +8` over TOC restore. Call conversion validates the expected NOP/TOC sequence, selects a reachable trampoline, and patches a branch-link. Runtime callback updates patch `ftrace_call` and optionally `ftrace_regs_call`.

## State and Persistence Behavior
Mutates kernel/module text, compiler trampolines, and ftrace trampoline arrays. Module state includes `mod->arch.tramp` and `tramp_regs`.

## Dependencies and Integration Points
Depends on PPC64 ABI v1/v2 function entry rules, module trampoline target decoding, PowerPC text patching, dynamic ftrace core, function graph tracer, and assembly symbols in `ftrace_64_pg_entry.S`.

## Risks
The legacy ABI includes TOC restore hazards: a plain NOP can corrupt r2 if a task was preempted in a tracing call, hence the branch-over-load sequence. Wrong trampoline target validation or branch range handling can break modules or kernel text.

## Test Signals
PPC64 non-mprofile builds, dynamic ftrace toggles, module tracing, function graph tracing, regs and non-regs variants, long-branch trampolines, ABI v1 function descriptor cases, and TOC corruption stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/ftrace_64_pg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/ftrace_64_pg_entry.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/ftrace_64_pg_entry.S

## Purpose
Provides PPC64 legacy profiling ftrace assembly entry points for `ftrace_caller`, `_mcount`, graph caller stubs, return handler, and reserved trampolines.

## Important APIs, Types, and Functions
- `ftrace_caller` checks `PACA_FTRACE_ENABLED`, saves LR/stack state, computes traced IP and parent IP, calls patched `ftrace_call`, optionally branches to graph caller, and restores state.
- `ftrace_stub` and `ftrace_graph_stub` are no-op branch targets.
- `ftrace_graph_caller` calls `prepare_ftrace_return()` and rewrites caller LR in the stack frame.
- `_mcount`/`mcount` return through LR/CTR and export `_mcount`.
- `return_to_handler` saves return values/TOC, calls `ftrace_return_to_handler`, and returns to the real address.
- `ftrace_tramp_text` and `ftrace_tramp_init` reserve trampoline storage.

## Control Flow and State
An instrumented function branches here before its normal body has fully executed. The caller saves enough state to call C tracing code while preserving ABI TOC and LR semantics, then restores stack and LR. Function graph tracing diverts the saved return address to `return_to_handler`.

## State and Persistence Behavior
Uses stack frames and PACA ftrace enable state. Trampolines are patched by `ftrace_64_pg.c`.

## Dependencies and Integration Points
Coupled to `ftrace_64_pg.c` patch targets, PPC64 TOC ABI, `prepare_ftrace_return()`, `ftrace_return_to_handler`, PACA layout, and module TOC switching.

## Risks
Incorrect stack offsets or TOC restoration corrupts traced functions. Graph return rewriting must identify the caller frame correctly. Trampoline storage must be sized for generated stubs.

## Test Signals
Legacy PPC64 ftrace, graph tracing, module tracing, nested traced calls, tracing disabled/enabled per CPU, and return-value preservation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/ftrace_64_pg_entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/ftrace_entry.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/ftrace_entry.S

## Purpose
Provides the common PowerPC ftrace assembly entry points for modern dynamic ftrace, including regs/non-regs callers, direct calls, out-of-line stubs, livepatch redirection, `_mcount`, function graph return handling, and reserved out-of-line/trampoline storage.

## Important APIs, Types, and Functions
- `ftrace_regs_entry`/`ftrace_regs_exit` macros build and tear down synthetic stack frames and `pt_regs`.
- `ftrace_regs_caller` saves all registers for regs-capable tracing; `ftrace_caller` saves the minimal set.
- `ftrace_call` and `ftrace_regs_call` are patch sites for the C callback.
- Direct-call labels bypass normal ftrace when `FTRACE_OPS_DIRECT_CALL` is present.
- `livepatch_handler` redirects execution to patched replacement functions while preserving a livepatch stack.
- `_mcount`/`mcount` are exported when patchable function entry is not used.
- `return_to_handler` calls `ftrace_return_to_handler` for function graph tracing.
- `ftrace_ool_stub_text` reserves out-of-line stub slots.

## Control Flow and State
Entry creates a minimal frame for the traced callee plus a switch frame containing `pt_regs`, extracts the call-site IP from LR or out-of-line stub decoding, saves parent LR, loads ftrace ops/callback, calls it, then restores registers and returns past the call site. Exit can route to direct-call target, livepatch handler, out-of-line return, or normal branch-through-CTR.

## State and Persistence Behavior
Uses per-call stack frames, optional livepatch per-thread stack pointer, PACA TOC/ftrace enable flag, and mutable NIP/LR in `pt_regs`. Reserved out-of-line stub text is patched by `ftrace.c`.

## Dependencies and Integration Points
Coupled to `ftrace.c` instruction sequence assumptions, `asm-offsets.h`, livepatch thread-info fields, `function_trace_op`, dynamic ftrace call-ops/direct-call layouts, ftrace graph infrastructure, and PPC32/PPC64 ABI differences.

## Risks
This code runs between function prologue stages, so stack/LR/TOC assumptions are narrow. Out-of-line decoding must match stub layout. Livepatch handler cannot allocate a normal frame and must preserve only allowed volatile state. Direct-call and graph paths must not corrupt return values.

## Test Signals
Dynamic ftrace with regs/non-regs, direct calls, call-ops, out-of-line stubs, livepatch transitions, function graph tracer, PPC32 and PPC64 builds, modules, and stack unwinder reliability while tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/ftrace_entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/trace_clock.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/trace_clock.c

## Purpose
Provides a PowerPC trace clock backed directly by the architecture timebase.

## Important APIs, Types, and Functions
- `trace_clock_ppc_tb()` returns `get_tb()` and is marked `notrace`.

## Control Flow and State
The function is a single read of the timebase register through `get_tb()`.

## State and Persistence Behavior
No mutable state. It exposes raw monotonically increasing timebase ticks to tracing.

## Dependencies and Integration Points
Depends on `asm/trace_clock.h` declarations and `asm/time.h` timebase access. Used by tracing clock selection.

## Risks
The value is not nanoseconds and assumes synchronized, valid timebase behavior. It must remain `notrace` to avoid tracing recursion.

## Test Signals
Select the PowerPC trace clock, verify monotonically increasing trace timestamps across CPUs, and test with timebase synchronization/error scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/trace_clock.c -->
