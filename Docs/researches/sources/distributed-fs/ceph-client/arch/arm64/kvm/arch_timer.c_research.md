## sources/distributed-fs/ceph-client/arch/arm64/kvm/arch_timer.c

### Purpose
`arch_timer.c` implements ARM64 KVM virtual and physical architected timer emulation/direct injection for guests, including VHE/nVHE differences, nested virtualization timers, userspace irqchip support, background hrtimers, IRQ-domain wrapping, counter offsets, and timer device attributes.

### Important APIs, Types, And Functions
Important APIs include `timer_get_ctl`, `timer_get_cval`, `kvm_phys_timer_read`, `get_timer_map`, `kvm_cpu_has_pending_timer`, `kvm_timer_update_run`, `kvm_timer_vcpu_load`, `kvm_timer_should_notify_user`, `kvm_timer_vcpu_put`, `kvm_timer_sync_nested`, `kvm_timer_sync_user`, `kvm_timer_vcpu_reset`, `kvm_timer_vcpu_init`, `kvm_timer_init_vm`, `kvm_timer_cpu_up/down`, `kvm_arm_timer_read_sysreg`, `kvm_arm_timer_write_sysreg`, `kvm_timer_hyp_init`, `kvm_timer_vcpu_terminate`, `kvm_timer_enable`, `kvm_timer_init_vhe`, `kvm_arm_timer_set_attr/get_attr/has_attr`, and `kvm_vm_ioctl_set_counter_offset`.

### Control Flow
Initialization obtains architected timer info, records the timecounter and host PPIs, wraps IRQ domains when active-state handling or GICv5 requires it, requests per-CPU virtual/physical timer IRQs, sets vcpu affinity, and enables erratum handling for broken CNTVOFF when needed. Each VCPU initializes four timer contexts, maps guest timer roles depending on VHE/nVHE/nested state, and sets default PPIs. On VCPU load, KVM updates IRQ output, manages physical active state or userspace irq masking, maps/unmaps direct timer PPIs for nested switches, restores direct hardware timer registers and offsets, and emulates non-direct timers with hrtimers. On put, it saves direct hardware state, cancels hrtimers, updates userspace notification state, and emulates timers whose backing registers may have changed. Blocking VCPUs get a background hrtimer for the earliest guest expiration or WFIT deadline. Sysreg reads/writes either operate on emulated context or temporarily save/restore loaded hardware state.

### State, Persistence, And Dependencies
Global state includes `timecounter`, host virtual/physical timer IRQ numbers and flags, `has_gic_active_state`, and `broken_cntvoff_key`. Per-VM state includes timer PPI assignments, virtual and physical counter offsets, immutable-PPI and counter-offset flags. Per-VCPU state includes `arch_timer_cpu`, four `arch_timer_context` structures, hrtimers, loaded/enabled flags, IRQ level, host timer IRQ, `ns_frac`, and vcpu offset pointers. State is in memory only but is ABI-visible through KVM device attributes and run structure fields.

### Integration Points
The file connects KVM run/put/load, VGIC IRQ injection and physical IRQ mapping, GICv5 direct injection, irqchip-in-kernel and userspace irqchip modes, architected timer clocksource data, hrtimer core, nested virtualization, protected VM restrictions, WFIT, ECV/CNTPOFF, Qualcomm CNTVOFF erratum handling, CPU hotplug, and KVM device ioctls.

### Risks
Timer correctness is highly timing-sensitive. Offset mistakes break guest time. Loaded-state save/restore must be preemption/IRQ safe. Userspace irqchip masking can lose or storm interrupts if active state is wrong. Nested timer mapping changes can inject on the wrong PPI. Broken CNTVOFF mitigation trades performance for correctness and depends on feature detection. Timer PPI configuration becomes immutable after first validation.

### Test Signals
Run KVM selftests for arch timers, timer migration, userspace irqchip, in-kernel VGIC, GICv5 if available, VHE/nVHE, nested virtualization, WFIT, counter-offset ioctl, CPU hotplug, live migration style sysreg save/restore, timer interrupt latency, and erratum-enabled builds.
