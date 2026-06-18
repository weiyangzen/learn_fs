<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/ioapic.c -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/ioapic.c

### Purpose
`ioapic.c` emulates the x86 I/O APIC for KVM's in-kernel irqchip. It owns MMIO register emulation, redirection table state, IRQ assertion and LAPIC delivery, level-triggered remote-IRR/EOI handling, RTC EOI coalescing tracking, mask notifier lists, migration get/set, and I/O APIC creation/destruction.

### Important APIs, Types, And Functions
Public entry points include `kvm_ioapic_init()`, `kvm_ioapic_destroy()`, `kvm_ioapic_set_irq()`, `kvm_ioapic_update_eoi()`, `kvm_ioapic_scan_entry()`, `kvm_get_ioapic()`, `kvm_set_ioapic()`, `kvm_register_irq_mask_notifier()`, `kvm_unregister_irq_mask_notifier()`, `kvm_fire_mask_notifiers()`, and `kvm_rtc_eoi_tracking_restore_one()`. Internal helpers include `ioapic_read_indirect()`, `ioapic_write_indirect()`, `ioapic_set_irq()`, `ioapic_service()`, `ioapic_lazy_update_eoi()`, `kvm_ioapic_eoi_inject_work()`, and RTC tracking helpers.

### Control Flow
MMIO reads/writes access the select register and indirect window. Redirection-table writes preserve read-only fields, clear remote IRR for edge mode, fire mask notifiers on mask changes, and may re-inject pending level interrupts when unmasked. IRQ assertion updates per-source line state, coalesces already-pending edge/RTC interrupts, sets IRR, and calls `ioapic_service()`. Service builds a `struct kvm_lapic_irq`, delivers it to matching LAPICs, records edge delivery, and sets remote IRR for delivered level interrupts. EOI updates clear RTC tracking, notify ack listeners outside the lock, clear remote IRR, and reinject still-asserted level IRQs; repeated immediate EOIs are delayed through workqueue throttling.

### State, Persistence, And Dependencies
`struct kvm_ioapic` persists base address, selected register, ID, IRR, redirection table, per-pin source states, spinlock, RTC status bitmap/vector array, delayed EOI work, per-pin EOI storm counters, delivered-edge IRR mask, and mask notifier hlist. Dependencies include LAPIC destination matching and delivery, KVM MMIO bus registration, SRCU-protected IRQ routing, irqfd resampler notification, workqueues, tracepoints, and APICv pending-EOI checks.

### Integration Points
`irq.c` routes IOAPIC pins to `kvm_ioapic_set_irq()` and scans IOAPIC/MSI routes for EOI exit bitmaps. LAPIC EOI paths call `kvm_ioapic_update_eoi()`. PIT and other legacy routes target IOAPIC pins through default routing. Userspace migrates IOAPIC state through `KVM_GET_IRQCHIP` and `KVM_SET_IRQCHIP`.

### Risks
Level-triggered correctness depends on remote IRR, IRR, EOI, and mask-notifier ordering. Unmasking a level interrupt can inject stale IRR unless irqfd resampling is used correctly. RTC interrupt coalescing is special and guest-visible for Windows timekeeping. The code drops the IOAPIC lock around ack notifiers, so state must be updated before callbacks re-enter. Migration intentionally clears internal delivered IRR state and reinjects saved IRR, which can affect pending edge semantics.

### Test Signals
Exercise MMIO access sizes, redirection-table high/low writes, invalid register indices, mask/unmask with irqfd resampler, edge and level delivery, remote IRR clearing on EOI, EOI storm delay, RTC coalescing and pending EOI restore, APIC destination changes and EOI bitmap scanning, migration get/set, and APICv lazy EOI update paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/ioapic.c -->
