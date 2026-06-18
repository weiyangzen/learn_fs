<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/kvm_util_arch.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/kvm_util_arch.h

Purpose: this small architecture-specific header defines arm64 extensions to the shared KVM selftest utility VM structures.

Important APIs, types, and functions: `struct kvm_mmu_arch` is currently empty for arm64. `struct kvm_vm_arch` stores whether a VM has a GIC (`has_gic`) and the associated GIC device fd (`gic_fd`).

Control flow: no executable code; the structures are embedded by shared selftest infrastructure.

State, persistence, and dependencies: `has_gic` and `gic_fd` persist for the lifetime of the in-process `struct kvm_vm` and let helpers avoid creating duplicate VGIC devices or find the existing fd.

Risks and edge cases: the fd must be closed by VM teardown paths that understand arm64 VGIC ownership. Empty `kvm_mmu_arch` signals that generic MMU helper state is sufficient for arm64 today, but future arm64 MMU metadata would be added here.

Test signals: downstream tests indirectly validate this state through `vgic_v3_setup()`, `test_disable_default_vgic()`, and other KVM utility helpers that create or reuse VGIC devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/kvm_util_arch.h -->
