# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/kvm_util_arch.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/kvm_util_arch.h

Purpose: LoongArch architecture extension point for `kvm_util.h`. This small header supplies the arch-specific struct definitions required by the common VM/MMU structs.

Important APIs/types/functions: defines `struct kvm_vm_arch` and `struct kvm_mmu_arch` for LoongArch builds, currently as minimal/empty architecture state placeholders.

Control flow and state: no runtime control flow. It fixes the shape of common KVM utility structures for LoongArch compilation.

Dependencies and integration: included by `kvm_util.h` when building LoongArch selftests. Architecture-specific implementation files fill behavior through hooks declared in `kvm_util.h`.

Risks: if LoongArch gains common per-VM or per-MMU state, these placeholders need to expand without breaking existing utility code. Empty structs can hide assumptions that the generic code does not require arch metadata.

Test signals: successful LoongArch selftest compilation and VM/page-table tests validate that no missing arch state is required.
