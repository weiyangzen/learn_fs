# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/ucall.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/ucall.h

Purpose: RISC-V architecture adapter for common ucall notifications.

Important APIs/types/functions: defines RISC-V `UCALL_EXIT_REASON` and `ucall_arch_do_ucall(gva_t uc)`, using the architecture's supported guest-to-host exit path.

Control flow and state: common ucall code places a payload in guest memory and calls the RISC-V adapter, which triggers an exit that host userspace decodes as a ucall. The state is the guest payload address and KVM exit metadata.

Dependencies and integration: includes `kvm_util.h` and is pulled into `ucall_common.h`. It integrates with all RISC-V guest assertions, sync points, and completion notifications.

Risks: an incorrect exit reason or payload transport convention breaks all common guest communication. Tests must keep host-side ucall decoding synchronized with this adapter.

Test signals: any RISC-V selftest using `GUEST_SYNC`, `GUEST_DONE`, or `GUEST_ASSERT` validates this header.
