<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_arch_timer.h -->
# sources/distributed-fs/ceph-client/include/kvm/arm_arch_timer.h

## Purpose
`arm_arch_timer.h` declares ARM/arm64 KVM architectural timer state, timer register accessors, VM/VCPU lifecycle hooks, and helpers for mapping virtual and physical guest timers to emulated or direct hardware paths.

## Important APIs, types, and functions
Important enums are `kvm_arch_timers` and `kvm_arch_timer_regs`. Key structs are `arch_timer_offset`, `arch_timer_vm_data`, `arch_timer_context`, `timer_map`, and `arch_timer_cpu`. APIs include `kvm_timer_hyp_init()`, `kvm_timer_enable()`, VCPU init/reset/load/put/terminate functions, user attribute accessors, `kvm_phys_timer_read()`, `kvm_arm_timer_read_sysreg()`, `kvm_arm_timer_write_sysreg()`, trace helpers, and CPU hotplug callbacks.

## Control flow
KVM initializes VM-wide offsets and PPIs, initializes each VCPU's timer contexts, loads timer state when a VCPU enters the guest, puts it on exit, and uses background hrtimers for non-running guests. `get_timer_map()` selects direct versus emulated timer contexts. Sysreg helpers read/write CNT/CVAL/TVAL/CTL/VOFF state.

## State and persistence behavior
VM timer state includes virtual/physical offsets and PPI numbers. VCPU state includes per-timer hrtimers, fractional nanosecond accounting, loaded flags, IRQ output level, and host timer IRQ. Offsets can be VM-wide or per-VCPU, and `timer_set_offset()` writes only VM-backed offsets.

## Dependencies and integration points
The header depends on hrtimers, clocksource logic, GICv5 IRQ encoding, static keys, CPU capability helpers, and `struct kvm_vcpu` architecture fields. It integrates with VGIC interrupt injection, userspace KVM device attributes, tracing, hyp initialization, and CPU hotplug.

## Risks and test signals
Risks include stale loaded state across VCPU switches, incorrect offset handling on broken CNTVOFF or ECV/CNTPOFF systems, wrong PPI encoding for GICv5, and timer IRQ level drift. Test signals include KVM timer selftests, migration/user attribute tests, nested timer synchronization, CPU hotplug testing, and guest clock/interrupt accuracy checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kvm/arm_arch_timer.h -->
