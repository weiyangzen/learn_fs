# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/kvm_util_arch.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/kvm_util_arch.h

Purpose: x86 architecture state definitions for the common KVM utility layer. It stores x86-specific VM/MMU metadata needed by page-table and protected-memory helpers.

Important APIs/types/functions: defines x86 `struct kvm_vm_arch`, `struct kvm_mmu_arch`, PTE mask storage, and arch-specific fields used by `kvm_util.h` and `x86/processor.h`.

Control flow and state: no direct runtime control flow. The structs persist page-table mode, PTE masks, encryption/shared-bit metadata, and other x86-only state across VM setup and mapping operations.

Dependencies and integration: included by `kvm_util.h` for x86 builds and consumed by x86 page-table helpers, SEV/SNP code, TDP/EPT mapping, and VM creation hooks.

Risks: PTE mask correctness is critical for guest page-table and EPT predicates. SEV/SNP state must align with encryption C-bit and shared-bit handling or protected-memory tests can map pages incorrectly.

Test signals: x86 memory-management, EPT/TDP, SEV/SNP, and page-table inspection tests validate the struct fields indirectly.
