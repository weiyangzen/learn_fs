# sources/distributed-fs/ceph-client/arch/loongarch/kvm/irqfd.c

Purpose: implements architecture-specific KVM IRQ routing and irqfd/MSI injection hooks for LoongArch.

Important APIs, types, and functions: `kvm_set_msi()`, `kvm_set_routing_entry()`, `kvm_arch_set_irq_inatomic()`, `kvm_arch_intc_initialized()`, and internal `kvm_set_pic_irq()`.

Control flow: userspace IRQCHIP routes are converted to PCH-PIC pin callbacks after bounds checking; MSI routes copy address/data and dispatch through `pch_msi_set_irq()`. Atomic injection supports asserted IRQCHIP and MSI routes, returning `-EWOULDBLOCK` for deassertion or unsupported routes.

State and persistence: does not own state; it reads `kvm->arch.pch_pic` and routes into PCH-PIC/EIOINTC/DMSINTC state.

Dependencies and integration points: used by generic KVM irq routing, irqfd, ioeventfd-style injections, and `KVM_IRQ_LINE`. Requires in-kernel irqchip presence from `vm.c`.

Risks: deasserted MSI returns failure by design; callers must tolerate edge-only MSI. Invalid routing pins must be rejected to avoid corrupting PCH state.

Test signals: irqfd tests, userspace `KVM_SET_GSI_ROUTING`, MSI injection, in-atomic injection paths, and `kvm_arch_intc_initialized()` before/after irqchip creation.
