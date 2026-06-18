<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vm.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vm.c

## Purpose
`vm.c` implements RISC-V architecture-specific KVM VM lifecycle, VM capabilities, IRQ routing, and selected VM ioctls.

## Important APIs, Types, And Functions
`kvm_arch_init_vm()` allocates G-stage page tables, initializes VMID, AIA, and guest timer. `kvm_arch_destroy_vm()` destroys vCPUs and AIA state. IRQ APIs include `kvm_vm_ioctl_irq_line()`, `kvm_set_msi()`, `kvm_riscv_setup_default_irq_routing()`, `kvm_set_routing_entry()`, and `kvm_arch_set_irq_inatomic()`. Capability paths are `kvm_vm_ioctl_check_extension()` and `kvm_vm_ioctl_enable_cap()`.

## Control Flow
VM init unwinds page-table allocation if VMID init fails. IRQ routing converts user routing entries to in-kernel callbacks for AIA IRQ or MSI injection. Capability queries return booleans or numeric limits. Enabling GPA bits validates requested G-stage levels, then under `kvm->lock` and `slots_lock` rejects changes after vCPU creation or memslot population.

## State And Persistence
VM state includes G-stage PGD, VMID metadata, AIA state, timer conversion state, MP reset mode, and configured G-stage page-table levels. All state is in-memory and VMM-managed through KVM APIs.

## Dependencies And Integration Points
It integrates KVM common VM lifecycle, RISC-V MMU/G-stage, VMID allocator, AIA irqchip/MSI, memory slots, and capability ABI exposed to userspace VMMs.

## Risks
Capability values are ABI. GPA-bit changes must be locked and denied once memory/vCPUs exist. MSI injection ignores deasserted level. VM destroy relies on common KVM vCPU destruction before AIA cleanup.

## Test Signals
KVM selftests for capability probing, VM GPA bits, irqchip routing/MSI delivery, memory-slot ordering, and VM lifecycle failure unwind are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vm.c -->
