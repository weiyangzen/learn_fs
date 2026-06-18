# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/ucall.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/ucall.h

Purpose: LoongArch adapter for common ucall guest-to-userspace notifications.

Important APIs/types/functions: defines the LoongArch `UCALL_EXIT_REASON` and `ucall_arch_do_ucall(gva_t uc)` implementation used by `ucall_common.h`.

Control flow and state: common guest code prepares a ucall record and invokes the architecture adapter. The adapter triggers a KVM exit in the LoongArch-supported way so host userspace can retrieve the ucall payload.

Dependencies and integration: includes `kvm_util.h` and participates in `ucall_common.h`. It integrates with all LoongArch tests using `GUEST_SYNC`, `GUEST_DONE`, assertions, or guest printf.

Risks: ucall transport is architecture-specific; incorrect exit reason or payload register/address convention will make every guest notification fail. The common side must agree with the host-side decoder.

Test signals: any LoongArch selftest using guest assertions validates this adapter. Failures usually manifest as unexpected exit reason or missing ucall payload.
