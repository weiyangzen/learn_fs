<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pvclock-abi.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pvclock-abi.h

Purpose: defines the KVM/Xen paravirtual clock ABI shared between hypervisor and guest. Important types are packed `pvclock_vcpu_time_info` and `pvclock_wall_clock`; important flags are `PVCLOCK_TSC_STABLE_BIT`, `PVCLOCK_GUEST_STOPPED`, and the deprecated `PVCLOCK_COUNTS_FROM_ZERO`.

Control flow: guests read a versioned time structure using an odd/even update protocol to avoid torn hypervisor updates, then scale TSC deltas against `system_time`. State is hypervisor-shared memory, not kernel-owned persistence. Dependencies include exact packing and shared ABI knowledge from Xen/KVM.

Risks: these structures must not change because layout is a hypervisor ABI. Version handling, flag interpretation, and field widths affect guest time monotonicity. Test signals include KVM/Xen boot, pvclock wallclock reads, live migration/resume, guest-stop flag handling, and timekeeping stability tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pvclock-abi.h -->
