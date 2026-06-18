# sources/distributed-fs/ceph-client/arch/x86/kernel/smp.c

## Purpose
`smp.c` supplies x86 SMP interrupt handlers and CPU stopping operations. It implements reschedule/call-function vectors, reboot stop vectors, NMI fallback stopping, exported `smp_ops`, and dead SMT sibling rescanning.

## Important APIs, Types, And Functions
Core functions are `native_stop_other_cpus()`, `sysvec_reboot`, `sysvec_reschedule_ipi`, `sysvec_call_function`, `sysvec_call_function_single`, and `arch_cpu_rescan_dead_smt_siblings()`. Important state includes `stopping_cpu`, `smp_no_nmi_ipi`, `cpus_stop_mask`, and `struct smp_ops smp_ops`.

## Control Flow
Stopping elects one CPU, kicks offline MWAIT CPUs for kexec, sends `REBOOT_VECTOR` IPIs, waits, then optionally sends NMI IPIs to CPUs that did not stop. It disables local APIC/MCE state and clears the stop mask. IPI handlers EOI the APIC, emit tracepoints, increment IRQ stats, and call scheduler or generic SMP callback handlers.

## State, Persistence, Dependencies, Integration
Persistent state is the SMP operations table and `nonmi_ipi` boot option. Runtime state includes stop ownership, online/stop masks, interrupt stats, tracing, virtualization emergency-disable state, and APIC state. Generic SMP and CPU hotplug use `smp_ops` entries from this file and `smpboot.c`.

## Risks And Test Signals
Shutdown is best-effort and races with locks/NMIs. NMI fallback must avoid the stopping CPU. Missing APIC EOI or trace pairing skews interrupt state. Test reboot, panic, kexec, crash dump, `nonmi_ipi`, MWAIT offline CPUs, IPI storms, SMT hotplug, virtualized systems, and trace/IRQ counters.
