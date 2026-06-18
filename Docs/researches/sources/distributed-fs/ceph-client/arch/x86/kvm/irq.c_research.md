<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/irq.c -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/irq.c

### Purpose
`irq.c` is the x86 KVM interrupt-controller coordination layer. It queries and consumes pending external interrupts, timer interrupts, and LAPIC interrupts; validates and installs IRQ routing entries; handles MSI delivery and fast in-atomic routes; coordinates IOAPIC route scanning; supports posted-interrupt IRQ bypass; and implements default PIC/IOAPIC routing plus irqchip state ioctls.

### Important APIs, Types, And Functions
Important functions include `kvm_cpu_has_pending_timer()`, `kvm_cpu_has_extint()`, `kvm_cpu_has_injectable_intr()`, `kvm_cpu_has_interrupt()`, `kvm_cpu_get_extint()`, `kvm_cpu_get_interrupt()`, `kvm_inject_pending_timer_irqs()`, `__kvm_migrate_timers()`, `kvm_set_msi()`, `kvm_arch_set_irq_inatomic()`, `kvm_vm_ioctl_irq_line()`, `kvm_set_routing_entry()`, `kvm_scan_ioapic_irq()`, `kvm_scan_ioapic_routes()`, `kvm_arch_irq_routing_update()`, IRQ bypass add/delete/update hooks, `kvm_setup_default_ioapic_and_pic_routing()`, `kvm_vm_ioctl_get_irqchip()`, and `kvm_vm_ioctl_set_irqchip()`.

### Control Flow
Interrupt queries first consider non-APIC external sources: userspace pending vector, Xen upcall, and PIC output when LAPIC accepts PIC interrupts. Injectable checks then account for APICv, protected APIC, and LAPIC pending vectors. MSI routing converts KVM route fields into `struct kvm_lapic_irq` using x86 MSI decoding, validates x2APIC address-high bits, and delivers through LAPIC helpers. Routing entry setup maps IRQCHIP routes to PIC or IOAPIC callbacks, MSI routes to `kvm_set_msi()`, Hyper-V SINT routes to SynIC, and Xen event channels to Xen helpers. IOAPIC scans build EOI interception bitmaps for level-triggered MSI/IOAPIC vectors and stale pending EOIs.

### State, Persistence, And Dependencies
The file manipulates vCPU pending external vector state, KVM IRQ routing tables under SRCU, irqfd bypass state, irqchip mode, PIC/IOAPIC state, LAPIC interrupt state, Xen timer/upcall state, Hyper-V SINT routing, and posted-interrupt IRTE state. Dependencies include `hyperv.h`, `ioapic.h`, `irq.h`, Xen hooks, x86 MSI helpers, irqfd/irq bypass infrastructure, APICv/posted interrupt x86 ops, and tracepoints.

### Integration Points
This is the bridge between userspace irq ioctls, irqfd, in-kernel PIC/IOAPIC, LAPIC, Hyper-V, Xen, MSI routing, and hardware posted interrupts. It is used by the vCPU run loop to decide whether to inject, acknowledge, or migrate interrupt/timer events.

### Risks
Pending interrupt semantics differ between userspace LAPIC, in-kernel LAPIC, APICv, nested guests, PIC extints, and Xen upcalls. Route validation must reject unsupported split irqchip PIC routes and invalid x2APIC MSI encodings. Posted-interrupt bypass must safely fall back for multicast, non-postable delivery modes, or producer removal. IOAPIC EOI scanning must include stale pending EOIs for routes that changed destination.

### Test Signals
Test full/split/no irqchip modes, IRQ_LINE ioctls, default PIC/IOAPIC routes, MSI and x2APIC MSI routing, in-atomic MSI fast path, Hyper-V SINT and Xen event channel routes, APICv active/inactive injectable checks, userspace external interrupt delivery, IOAPIC EOI bitmap scans after route changes, IRQ bypass producer add/delete/update, and irqchip get/set migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/irq.c -->
