<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/irq.h -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/irq.h

### Purpose
`irq.h` defines x86 KVM in-kernel interrupt-controller structures and shared helpers for PIC, irqchip mode checks, timer injection, and timer migration.

### Important APIs, Types, And Functions
Under `CONFIG_KVM_IOAPIC`, it defines `PIC_NUM_PINS`, `SELECT_PIC()`, `struct kvm_kpic_state`, and `struct kvm_pic`, plus prototypes for PIC init/destroy, set/read/update IRQ, default routing, and irqchip get/set ioctls. Common helpers include `irqchip_full()`, `pic_in_kernel()`, `irqchip_split()`, and `irqchip_in_kernel()`. It declares timer-related functions such as `kvm_inject_pending_timer_irqs()`, `kvm_inject_apic_timer_irqs()`, `kvm_apic_nmi_wd_deliver()`, `__kvm_migrate_apic_timer()`, `__kvm_migrate_pit_timer()`, `__kvm_migrate_timers()`, and `apic_has_pending_timer()`.

### Control Flow
The mode helpers read `kvm->arch.irqchip_mode` with an `smp_rmb()` paired with irqchip mode publication. `SELECT_PIC()` maps global legacy IRQ numbers to master or slave PIC identifiers. Other control flow is implemented in the corresponding `.c` files.

### State, Persistence, And Dependencies
PIC state includes edge detection, request/mask/service registers, priority rotation, vector base, read/poll modes, initialization state, AutoEOI, special fully nested mode, ELCR, and top-level output/wakeup/IRQ source arrays. Dependencies include KVM host state, hrtimer declarations, spinlocks, KVM I/O devices, and LAPIC declarations.

### Integration Points
Included by PIC, PIT, IOAPIC, IRQ routing, and vCPU interrupt injection paths. Its irqchip mode helpers gate whether in-kernel PIC/IOAPIC/PIT behavior is available and whether userspace IRQ injection is legal.

### Risks
The irqchip mode helpers are small but widely used; a stale or incorrectly ordered mode read can send callers down full, split, or none irqchip paths incorrectly. PIC structure layout is copied to UAPI irqchip state, so incompatible changes affect migration. `__kvm_migrate_pit_timer()` is declared unconditionally but implemented only with IOAPIC support, so config guards matter.

### Test Signals
Build all irqchip configurations, validate full/split/none mode behavior, migrate PIC state through irqchip ioctls, and exercise callers that compile against PIT migration and APIC timer declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/irq.h -->
