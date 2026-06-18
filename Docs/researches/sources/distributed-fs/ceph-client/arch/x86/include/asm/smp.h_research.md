<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/smp.h

Purpose: declares x86 SMP topology maps, CPU startup/shutdown operations, IPI helpers, cache writeback helpers, and boot-control flags. Important APIs/types include per-CPU sibling/core/die/cache masks, early APIC/ACPI IDs, `struct smp_ops`, native SMP callbacks, stop/reschedule/call-function IPI wrappers, CPU hotplug functions, `raw_smp_processor_id()`, shared-cache mask helpers, `smpboot_control`, and startup flags.

Control flow: generic SMP and hotplug code dispatch through `smp_ops` to prepare CPUs, kick APs, send IPIs, disable/die CPUs, and enter dead states. Cache writeback helpers run WBINVD/WBNOINVD locally or on masks. !SMP builds collapse many helpers to local operations.

State and persistence: per-CPU topology masks and APIC/ACPI IDs describe runtime CPU layout; boot-control flags coordinate AP startup. Dependencies include cpumasks, APIC, CPU hotplug, scheduler IPIs, topology discovery, and cache flush instructions.

Risks: wrong topology masks affect scheduler/cache locality; IPI failures break rescheduling and TLB shootdowns; CPU hotplug races are severe. Test signals include SMP boot, parallel AP startup, CPU online/offline, scheduler IPI tests, cache flush operations, topology sysfs, and UP build stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/smp.h -->
