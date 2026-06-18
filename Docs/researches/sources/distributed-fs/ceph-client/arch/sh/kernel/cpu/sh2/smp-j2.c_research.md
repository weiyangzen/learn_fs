<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/smp-j2.c -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/smp-j2.c

Purpose: implements J2 device-tree based SMP/IPI support.

Important APIs/types/functions: `j2_prepare_cpus()`, `j2_start_cpu()`, `j2_smp_processor_id()`, `j2_send_ipi()`, IPI handler, `CPU_METHOD_OF_DECLARE`.

Control flow: maps IPI controller and cpuid MMIO from DT, requests per-CPU IPI IRQ, disables unavailable CPUs, writes release/initpc addresses for secondary boot, and sends messages through per-CPU bitmasks plus MMIO trigger.

State and persistence: state includes per-CPU `j2_ipi_messages`, mapped MMIO pointers, IRQ number, and CPU possible/present masks.

Dependencies/integration: integrates OF CPU spin-table binding, generic SMP message handling, and native CPU hotplug hooks.

Risks: missing DT resources silently limits to one CPU; IPI bitmask races rely on cmpxchg correctness.

Test signals: boot SMP J2 DT, send reschedule/call-function IPIs, and test CPU hotplug paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/smp-j2.c -->
