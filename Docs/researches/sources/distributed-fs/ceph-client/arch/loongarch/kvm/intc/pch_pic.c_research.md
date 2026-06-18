# sources/distributed-fs/ceph-client/arch/loongarch/kvm/intc/pch_pic.c

Purpose: emulates the LoongArch PCH PIC, routes legacy IRQ pins and MSI vectors toward EIOINTC or DMSINTC, and exposes MMIO/KVM-device state.

Important APIs, types, and functions: external IRQ APIs are `pch_pic_set_irq()` and `pch_msi_set_irq()`. Device paths include `kvm_pch_pic_create()`, `kvm_pch_pic_destroy()`, `kvm_pch_pic_get_attr()`, `kvm_pch_pic_set_attr()`, `kvm_pch_pic_init()`, and `kvm_loongarch_register_pch_pic_device()`.

Control flow: line assertion updates IRR, honors edge-triggered behavior, and calls `pch_pic_update_irq()` to move unmasked requests into ISR and route through `htmsi_vector` to EIOINTC. Deassertion clears level-triggered IRR/ISR. Mask writes raise newly unmasked pending IRQs and lower newly masked active IRQs. MSI delivery uses DMSINTC when the message address falls inside its window on message-interrupt hardware, otherwise it injects into EIOINTC using MSI data as vector.

State and persistence: per-VM `loongarch_pch_pic` stores masks, edge, polarity, IRR/ISR, route entries, HTMSI vectors/enables, base address, device object, and lock. Default IRQ routing maps each GSI to the same PCH-PIC pin.

Dependencies and integration points: registered on `KVM_MMIO_BUS` after userspace initializes the base address; integrates with KVM IRQ routing, irqfd/MSI, EIOINTC, optional DMSINTC, and userspace migration attrs.

Risks: edge-triggered clear semantics differ from level lines. Attribute writes directly copy state and may bypass side effects, so migration ordering matters. The model implements fixed routing only for some route registers.

Test signals: guest legacy IRQs, MSI routing, irqfd injection, mask/clear/polarity behavior, MMIO width accesses, migration restore, and default IRQ routing validation.
