<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/smp_hvm.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/smp_hvm.c

## Purpose
Adapts native x86 SMP operations for Xen HVM/PVHVM guests. It sets up Xen vCPU info placement, Xen time operations, spinlock paravirt alternatives, Xen IPI handlers, and CPU hotplug cleanup when Xen vector callbacks are available.

## Important APIs, Types, And Functions
Key functions are `xen_hvm_smp_prepare_boot_cpu`, `xen_hvm_smp_prepare_cpus`, `xen_hvm_cleanup_dead_cpu`, and `xen_hvm_smp_init`.

## Control Flow
Initialization overwrites selected members of the existing `smp_ops`. Boot CPU preparation calls native setup, installs vCPU info for CPU0, retries Xen HVM time initialization for high vCPU IDs, and initializes PV spinlocks. CPU preparation delegates to native SMP setup, then binds Xen IPI/lock IRQs for CPU0 only if vector callbacks exist and marks secondary vCPU IDs invalid until Xen CPU-up code assigns them. Without vector callbacks, PV spinlocks are disabled and IPI send hooks remain native.

## State And Persistence
Persistent state is the modified `smp_ops`, per-CPU `xen_vcpu_id` defaults, and event-channel IRQ state allocated by common SMP and spinlock code.

## Dependencies And Integration Points
Depends on native x86 SMP setup, Xen vector callback support, HVM vCPU setup, Xen time initialization, common Xen SMP IPI code, and paravirt spinlock globals.

## Risks And Edge Cases
The vector-callback gate is central: enabling Xen IPI hooks without callback delivery would break secondary CPU interrupts, while disabling them loses PV spinlock benefits. Booting on vCPU IDs outside embedded shared-info slots requires delayed time init. Hotplug cleanup without `CONFIG_HOTPLUG_CPU` intentionally bugs.

## Test Signals
Use HVM/PVHVM boots with and without vector callbacks, CPU hotplug, SMP function-call IPI stress, PV spinlock enable/disable logs, and timer setup on boot CPU and secondary CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/smp_hvm.c -->
