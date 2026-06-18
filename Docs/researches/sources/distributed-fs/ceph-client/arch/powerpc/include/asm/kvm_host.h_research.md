# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_host.h

Purpose: defines the architecture-specific KVM host data model for PowerPC: VM/vCPU stats, exit reasons, memory slots, HPT/rmap structures, vcore states, PAPR TCE tables, interrupt-controller state, BookE debug/MMU fields, nestedv2 IO buffers, and the large `struct kvm_vcpu_arch`.

Important APIs/types/functions: key definitions include `KVM_MAX_VCPUS`, `KVM_MAX_VCPU_IDS`, `KVM_REQ_*`, HPTE cache sizes, `struct kvm_vm_stat`, `struct kvm_vcpu_stat`, `enum kvm_exit_types`, `struct kvmppc_exit_timing`, `struct kvm_arch_memory_slot`, `struct kvm_hpt_info`, `struct kvm_arch`, `struct kvmppc_vpa`, `struct kvmppc_pte`, `struct kvmppc_mmu`, `struct kvmppc_slb`, passthrough IRQ maps, MMIO register encodings, and `struct kvm_vcpu_arch`.

Control flow: this header is mostly declarative, but its fields are walked by KVM core operations during VM creation, vcpu run, memory-slot changes, interrupt routing, dirty logging, MMIO emulation, HPT/radix page faults, and guest entry/exit accounting. Stub hooks such as `kvm_arch_memslots_updated()` are intentionally empty for generic KVM integration.

State and persistence: persistent VM state includes LPID/MMU mode, HPT/radix roots, memory-slot arch data, TCE tables, RTAS tokens, XICS/XIVE/MPIC devices, secure-VM state, nested guest arrays, vcore lists, and dirty/rmap metadata. Per-vcpu state includes registers, timers, interrupt pending bits, BookE TLB/debug state, FPU/VMX/VSX state, MMIO emulation state, VPA/DTL/SLB shadows, and statistics.

Dependencies and integration points: integrates Linux KVM core, PPC MMU headers, XICS/XIVE/MPIC devices, PAPR TCE/IOMMU, pSeries RTAS, nested-HV, BookE, and generic module/device infrastructure.

Risks: structure layout and field semantics are consumed throughout KVM and sometimes by assembly/generated offsets. Mis-sizing ID limits breaks userspace ABI for vcpu IDs. Rmap and memory-slot fields are concurrency-sensitive. Interrupt-controller pointers may be NULL depending on selected irqchip mode.

Test signals: KVM selftests for vcpu creation, one-reg access, dirty logging, memory-slot add/delete, irqchip creation, TCE/IOMMU ioctls, BookE TLB ioctls, nested virtualization, secure VM transitions, and statistics/debugfs visibility.
