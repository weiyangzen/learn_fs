# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/kvm_util_arch.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/kvm_util_arch.h

Purpose: s390 architecture placeholder/state definitions for the common KVM utility layer.

Important APIs/types/functions: defines `struct kvm_vm_arch` and `struct kvm_mmu_arch` for s390 builds, currently minimal.

Control flow and state: no runtime control flow; the header shapes `struct kvm_vm` and `struct kvm_mmu` for s390 compilation.

Dependencies and integration: included by `kvm_util.h` and paired with s390-specific implementation files for VM setup, page tables, and vCPU initialization.

Risks: s390 has distinct memory-management and CPU-model behavior; if common utilities need cached arch state, this header must evolve in lockstep with implementations.

Test signals: s390 selftest compilation and VM creation/page mapping tests validate that the common layer has enough arch state.
