## sources/distributed-fs/ceph-client/arch/loongarch/kernel/paravirt.c

### Purpose
`paravirt.c` enables LoongArch KVM paravirtual features: optimized IPI delivery, steal-time accounting, virtual preemption hints, and paravirtual spinlock static keys. It detects KVM by CPUCFG signature and switches architecture hooks when advertised features are present.

### Important APIs, Types, And Functions
Global keys are `virt_preempt_key`, `virt_spin_lock_key`, and `paravirt_steal_enabled` integration via generic code. Per-CPU state is `struct kvm_steal_time steal_time`. Important functions include `kvm_para_available`, `kvm_arch_para_features`, `pv_ipi_init`, `pv_time_init`, `pv_spinlock_init`, `paravt_steal_clock`, `pv_send_ipi_single`, `pv_send_ipi_mask`, and `pv_ipi_interrupt`.

### Control Flow
Feature detection reads CPUCFG signature and feature bits. If KVM IPI is available, `pv_ipi_init` saves native `mp_ops` and replaces init/send hooks; boot-CPU IPIs still go through native delivery. PV IPI sends coalesce action bits in per-CPU `irq_stat.message` and use KVM hypercalls, while SWI0 interrupt handling drains message bits and calls scheduler, call-function, irq-work, or IRQ migration handlers. Steal-time init registers the per-CPU physical address with KVM, installs CPU hotplug and reboot callbacks, updates the `pv_steal_clock` static call, and enables accounting static keys.

### State, Persistence, And Dependencies
Paravirt state persists in static keys, static calls, `mp_ops`, per-CPU steal-time pages, and hypervisor registration. It depends on KVM hypercall ABI, LoongArch CPUCFG feature bits, SWI0 IRQ mapping, SMP `irq_stat`, cpuhp, and reboot notifier infrastructure.

### Integration Points
SMP setup calls `pv_ipi_init`; boot CPU preparation calls `pv_spinlock_init`; `time_init` calls `pv_time_init`. Scheduler accounting reads steal time through the updated static call, and queued IPI actions use the same generic handlers as native IPI delivery.

### Risks
The steal-time structure must not cross a page boundary, and failure disables the feature. PV IPI bitmap clustering uses a 128-bit bitmap and physical CPU IDs; incorrect CPU map assumptions could miss CPUs. Replacing `mp_ops` must preserve native boot CPU behavior. The `no-steal-acc` early param disables runqueue accounting but not steal clock registration.

### Test Signals
Boot under KVM with and without advertised IPI, steal-time, preempt, and spinlock features. Check dmesg feature messages, `/proc/stat` steal accounting, CPU hotplug registration/unregistration hypercalls, IPI counters, and reboot notifier cleanup. Compare scheduler behavior with `no-steal-acc`.
