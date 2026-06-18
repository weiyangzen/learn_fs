# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/ucall.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/ucall.h

Purpose: arm64 architecture adapter for the common selftest ucall mechanism. It defines ucalls as MMIO exits and performs the guest-side write that causes KVM to exit to userspace.

Important APIs/types/functions: `UCALL_EXIT_REASON` is `KVM_EXIT_MMIO`, `ucall_exit_mmio_addr` is the shared target address, and `ucall_arch_do_ucall(gva_t uc)` stores the ucall payload pointer through the MMIO address.

Control flow and state: common ucall code builds a `struct ucall` in guest memory and calls `ucall_arch_do_ucall`; the arm64 helper writes the guest virtual address of the payload to a configured MMIO page. Userspace observes the MMIO exit and decodes the pointer through common helpers.

Dependencies and integration: includes `kvm_util.h` and is included by `ucall_common.h`. It depends on VM setup mapping `ucall_exit_mmio_addr` to an exit-producing MMIO region.

Risks: if the MMIO address is not initialized or not mapped as expected, guest notification will either fault or not reach userspace. Pointer-size and endian assumptions must remain aligned with arm64 guest code.

Test signals: any arm64 selftest using `GUEST_SYNC`, `GUEST_DONE`, `GUEST_ASSERT`, or guest printf exercises this adapter.
