# sources/distributed-fs/ceph-client/arch/loongarch/kvm/vm.c

Purpose: implements LoongArch VM-level KVM lifecycle, feature discovery, capability reporting, IRQ line handling, and VM statistics.

Important APIs, types, and functions: `kvm_arch_init_vm()`, `kvm_arch_destroy_vm()`, `kvm_vm_ioctl_check_extension()`, `kvm_arch_vm_ioctl()`, `kvm_vm_ioctl_irq_line()`, `kvm_arch_irqchip_in_kernel()`, stats descriptors, and internal `kvm_vm_init_features()`.

Control flow: VM init allocates the GPA shadow PGD, allocates the physical CPUID map, initializes VMCS pointer and feature bitmaps, computes GPA size from `cpu_vabits`, and initializes page-table metadata. VM ioctl reports common LoongArch KVM capabilities and handles `KVM_CREATE_IRQCHIP` as a no-op plus feature attribute probing. IRQ line ioctls route through generic KVM IRQ routing when in-kernel irqchips are present.

State and persistence: per-VM state includes `arch.pgd`, `phyid_map`, feature masks, PV features, GPA size, page-table levels/shifts, invalid PTE tables, and stats counters.

Dependencies and integration points: relies on `mmu.c` for PGD allocation, `main.c` for VMCS initialization, CPU feature probes, generic KVM caps/ioctls, IRQ routing, and in-kernel IPI/EIOINTC/PCH-PIC devices.

Risks: capability reporting must match implemented behavior. GPA size derived from user VA bits constrains memslot creation. Destroy path must release vCPUs before page tables and CPUID map.

Test signals: VM create/destroy, KVM_CHECK_EXTENSION, feature attributes, memslot bounds tests, IRQCHIP creation order, and stats reading.
