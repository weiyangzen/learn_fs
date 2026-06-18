# sources/distributed-fs/ceph-client/arch/loongarch/kvm/intc/dmsintc.c

Purpose: emulates the LoongArch direct MSI interrupt controller used with message-signaled interrupts and AVEC delivery.

Important APIs, types, and functions: `dmsintc_inject_irq()`, `dmsintc_deliver_msi_to_vcpu()`, `dmsintc_set_irq()`, device ops `kvm_dmsintc_create()`, `kvm_dmsintc_destroy()`, `kvm_dmsintc_set_attr()`, and registration `kvm_loongarch_register_dmsintc_device()`.

Control flow: MSI address/data decode chooses a target CPU and vector. Delivery sets the vector bit in the target vCPU `dmsintc_state.vector_map`, injects `INT_AVEC`, and kicks the vCPU. On guest interrupt delivery, `dmsintc_inject_irq()` atomically drains vector maps into guest ISR0-ISR3 CSRs. Device attributes initialize the message address base and size once, deriving the CPU mask from the base address encoding.

State and persistence: per-VM state is `struct loongarch_dmsintc` with message base, size, CPU mask, and KVM pointer. Per-vCPU vector bitmap state is stored atomically in `vcpu->arch.dmsintc_state`.

Dependencies and integration points: used by PCH-PIC MSI routing when `cpu_has_msgint` and the MSI address falls inside the DMSINTC window; registered as a KVM device type during KVM environment initialization; integrated with `interrupt.c` AVEC injection.

Risks: `dmsintc_inject_irq()` declares `vector[4]` without explicit zero initialization before conditional writes, so empty vector slots must be handled carefully. Duplicate attribute setting returns errors. CPU and vector decoding must match the ABI used by userspace VMMs.

Test signals: KVM device create/set-attr tests, MSI injection to all vectors, AVEC interrupt visibility in guest ISR CSRs, invalid CPU/vector rejection, and migration save/restore through attributes.
