# sources/distributed-fs/ceph-client/arch/x86/kernel/process.c

## Purpose
Implements architecture-common x86 task lifecycle, clone/fork register setup, thread teardown, TLS and I/O bitmap handling, CPUID/TSC prctl modes, speculation mitigation context switch work, CPU idle selection, CPU stop behavior, stack/brk randomization, and `arch_prctl` dispatch.

## APIs, Types, And Functions
Important state includes per-CPU `cpu_tss_rw`, `__tss_limit_invalid`, `cache_state_incoherent`, `msr_misc_features_shadow`, per-CPU `ssb_state`, `boot_option_idle_override`, and `cpus_stop_mask`. Core functions include `arch_dup_task_struct()`, `arch_release_task_struct()`, `exit_thread()`, `copy_thread()`, `ret_from_fork()`, `flush_thread()`, `set_tsc_mode()`, CPUID faulting helpers, `arch_setup_new_exec()`, `native_tss_update_io_bitmap()`, `__switch_to_xtra()`, idle functions, `stop_this_cpu()`, `select_idle_routine()`, `arch_post_acpi_subsys_init()`, `arch_align_stack()`, `arch_randomize_brk()`, `__get_wchan()`, and syscall handlers for `arch_prctl`/`ni_syscall`.

## Control Flow
Fork setup builds a `fork_frame`, copies user registers, handles kernel-thread vs user-thread paths, allocates shadow stack state, clones FPU state, applies `CLONE_SETTLS`, and shares I/O bitmaps when needed. Exec cleanup re-enables CPUID if disabled, clears no-exec SSBD state, and resets tagged-address masks. Context switches call `__switch_to_xtra()` only when thread flags require extra work; it invalidates/copies I/O bitmaps, propagates return notifiers, toggles blockstep, TSC disable, CPUID faulting, and speculation MSRs. Idle setup chooses polling, MWAIT, TDX-aware halt, or safe halt based on command line and CPU quirks.

## State And Persistence
Per-task thread fields preserve TLS, PKRU, I/O bitmap, debug breakpoints, CPUID/TSC flags, and speculation flags. Per-CPU TSS and SSBD sibling state persist across context switches and CPU hotplug. Boot parameters such as `idle=` and prctl calls persist as global or per-task policy.

## Dependencies And Integration
Integrates with scheduler, entry code, FPU/xstate, shadow stacks, ptrace breakpoints, TSS/descriptor handling, APIC/tick idle, machine check, TDX, seccomp/prctl speculation controls, unwind/proc, and process_32/process_64 switch implementations.

## Risks And Test Signals
Risks are high because this code touches context switch correctness, security mitigations, user ABI, idle behavior, and CPU shutdown. Watch for stale I/O bitmaps, wrong PKRU/FPU/shstk state, CPUID/TSC policy mismatch, speculation MSR races across HT siblings, and idle regressions. Test signals include fork/clone/exec suites, prctl tests, ptrace/hw-breakpoint tests, kexec/cache-incoherent paths, idle boot options, CPU hotplug, and speculation mitigation selftests.
