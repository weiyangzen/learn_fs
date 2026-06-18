<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/suspend.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/suspend.c

## Purpose
Provides architecture-level Xen suspend/resume coordination common to PV and HVM x86 guests. It saves and restores Xen time-memory areas, delegates PV/HVM domain-specific suspend hooks, preserves SPEC_CTRL state for PV, suspends/resumes local ticks, and restarts PMU state around suspend.

## Important APIs, Types, And Functions
Entry points are `xen_arch_pre_suspend`, `xen_arch_post_suspend`, `xen_arch_suspend`, and `xen_arch_resume`. Per-CPU state is `spec_ctrl`. Internal cross-CPU callbacks are `xen_vcpu_notify_suspend` and `xen_vcpu_notify_restore`.

## Control Flow
Pre-suspend saves Xen secondary time info and calls PV pre-suspend when needed. The suspend phase finishes PMU for all online CPUs, then runs a blocking callback on each CPU to suspend local ticks and, for PV SPEC_CTRL-capable CPUs, save and clear `MSR_IA32_SPEC_CTRL`. Post-suspend calls either PV or HVM restoration, restores Xen time-memory areas, then resume callbacks restore SPEC_CTRL and resume local ticks on non-boot CPUs. PMU pages are reinitialized after resume.

## State And Persistence
State is per-CPU saved `SPEC_CTRL`, Xen PMU registration state, tick state, and time-memory registration state. Effects are transient across Xen save/restore or migration.

## Dependencies And Integration Points
Depends on PV and HVM suspend helpers, Xen PMU init/finish, Xen time save/restore, Linux tick suspend/resume, CPU feature flags, and MSR accessors.

## Risks And Edge Cases
SPEC_CTRL clearing is PV-only and conditional on CPU feature support. Boot CPU tick handling is left to generic timekeeping resume. PMU finish/init ordering must match event-channel and CPU online state. Missing time restore can break sched_clock continuity.

## Test Signals
Exercise Xen save/restore and migration for PV and HVM guests with multiple CPUs, PMU enabled, SPEC_CTRL-capable CPUs, and active timers; verify monotonic time, no lost ticks, and no PMU registration leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/suspend.c -->
