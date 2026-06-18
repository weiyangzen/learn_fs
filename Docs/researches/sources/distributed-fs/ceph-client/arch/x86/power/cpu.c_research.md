<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/cpu.c -->
# sources/distributed-fs/ceph-client/arch/x86/power/cpu.c

## Purpose
Saves and restores x86 processor state across suspend/hibernate, handles hibernate CPU hotplug constraints, and registers quirks for MSRs that must survive firmware sleep.

## Important APIs, Types, And Functions
Exports `save_processor_state()` and `restore_processor_state()` on 32-bit. `__save_processor_state()` records descriptor tables, segments, control registers, MSRs, MTRRs, FPU state, and scheduler clock state. `__restore_processor_state()` restores CRs/segments/MSRs/FRED/TSS/LDT/FPU/debug/perf/cache/microcode state. `hibernate_resume_nonboot_cpu_disable()` forces nonboot CPUs into safe halt paths.

## Control Flow
Save enters kernel FPU context, records architectural state, and calls platform clock save. Restore reverses control-register and descriptor setup, restores percpu access before complex exception/FRED work, reloads TSS/LDT, restores user segment bases, ends FPU context, verifies TSC adjust, restores platform/debug/perf/cache state, updates microcode, then restores saved MSRs. Init registers a PM notifier requiring CPU0 online and builds MSR save lists from DMI, CPU family, and speculation-control features.

## State And Persistence
Global `saved_context` holds the resume image. Dynamic saved-MSR arrays persist after device init. PM notifier state persists for sleep transitions.

## Dependencies And Integration Points
Depends on x86 descriptor/MSR/FPU/MTRR/microcode/FRED/TLB APIs, PM notifier core, CPU hotplug, tboot, DMI, and platform clock hooks.

## Risks And Edge Cases
Restore ordering is critical, especially `%gs`, FRED, CR3/CR4, and MSRs emulated by microcode. CPU0 must be online. Nonboot SMT siblings must not resume from stale page tables via MWAIT.

## Test Signals
Suspend/resume and hibernate/resume on 32/64-bit systems, DMI/CPU MSR quirk logs, CPU0-offline rejection, and no segment/percpu faults after resume validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/cpu.c -->
