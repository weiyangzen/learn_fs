# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/kvm_util_arch.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/kvm_util_arch.h

Purpose: RISC-V architecture placeholder types for the common KVM utility layer.

Important APIs/types/functions: defines `struct kvm_vm_arch` and `struct kvm_mmu_arch` for RISC-V builds, currently minimal/empty.

Control flow and state: no runtime behavior. The types reserve architecture slots inside `struct kvm_vm` and `struct kvm_mmu`.

Dependencies and integration: included by `kvm_util.h`; RISC-V-specific implementation files provide the actual VM and page-table hook behavior.

Risks: future RISC-V state such as SATP mode, extension capability caches, or page-table metadata may need to be added here. Empty arch structs require the generic layer to avoid assumptions about state availability.

Test signals: RISC-V KVM selftest compilation and VM/page-table creation tests are the validation path.
