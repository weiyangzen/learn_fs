# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_pkvm.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_pkvm.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_pkvm.h

### Purpose
`kvm_pkvm.h` declares protected KVM constants and helpers for memory ownership, host/guest hyp mappings, pKVM initialization, and protected VM lifecycle.

### Important APIs, Types, And Functions
The header defines pKVM memory protection constants, hyp/host memory helpers, handle types, protected VM setup/finalization/teardown declarations, host donation/share/unshare operations, and conditional stubs for non-pKVM builds.

### Control Flow
pKVM initialization reserves hyp memory and transitions the host into a protected mode. VM creation allocates a protected handle, donates pages to hyp/guest ownership, maps required ranges, and later tears them down through protected hypercalls.

### State, Persistence, And Dependencies
State lives in hyp-owned metadata, `struct kvm_protected_vm`, memory ownership annotations, and host/hyp page tables. It depends on `kvm_host.h`, `kvm_pgtable.h`, SMCCC/hyp calls, and protected-mode static keys.

### Integration Points
Connects KVM VM lifecycle, hyp memory management, page-table annotation, and host deprivileging.

### Risks
Ownership transition bugs can violate host/guest isolation or leak pages. Handle lifetime and teardown ordering must prevent reuse while vCPUs run. Stub behavior must keep non-pKVM builds correct.

### Test Signals
Boot pKVM-enabled kernels, create/destroy protected VMs, stress page donation/reclaim/share paths, and run isolation/security regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_pkvm.h -->
