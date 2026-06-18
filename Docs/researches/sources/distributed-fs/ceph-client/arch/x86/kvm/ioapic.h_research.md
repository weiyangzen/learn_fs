<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/ioapic.h -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/ioapic.h

### Purpose
`ioapic.h` defines KVM's internal I/O APIC data structures, register constants, redirection entry layout, RTC EOI tracking state, mask notifier API, and helper prototypes.

### Important APIs, Types, And Functions
Important definitions include `IOAPIC_NUM_PINS`, `IOAPIC_DEFAULT_BASE_ADDRESS`, MMIO register offsets, indirect register numbers, delivery modes, trigger modes, and `RTC_GSI`. Key types are `struct rtc_status`, `union kvm_ioapic_redirect_entry`, `struct kvm_ioapic`, and `struct kvm_irq_mask_notifier`. Declared APIs include IOAPIC init/destroy, set irq, get/set state, update EOI, scan redirection entries, register/unregister/fire mask notifiers, and route scanning helpers. `ioapic_in_kernel()` maps to full in-kernel irqchip mode.

### Control Flow
The header provides declarations and one mode helper; behavior is implemented in `ioapic.c` and `irq.c`. The redirection entry bitfield defines how MMIO writes map to vector, delivery mode, destination mode, polarity, remote IRR, trigger mode, mask, and destination ID.

### State, Persistence, And Dependencies
`struct kvm_ioapic` persists guest-visible state plus internal delivery bookkeeping. The mask notifier list is documented as read under `irq_srcu` and written under `irq_lock`. Dependencies include KVM host state, KVM I/O devices, and `irq.h`.

### Integration Points
This header is shared by IOAPIC emulation, IRQ routing, PIT, PIC, irqfd resampling, LAPIC EOI scanning, and VM irqchip ioctls. It also gives non-IOAPIC code a stable way to test whether a full in-kernel IOAPIC exists.

### Risks
Bitfield layout in `union kvm_ioapic_redirect_entry` is guest ABI sensitive because it is copied to/from UAPI state. The notifier locking contract must be preserved to avoid use-after-free or missed mask transitions. `ioapic_in_kernel()` means full irqchip only; using it for split irqchip would incorrectly enable PIT/IOAPIC assumptions.

### Test Signals
Compile both `CONFIG_KVM_IOAPIC` modes, validate IOAPIC UAPI state layout through migration tests, exercise mask notifier registration/removal under IRQ routing changes, and verify full/split/none irqchip mode decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/ioapic.h -->
