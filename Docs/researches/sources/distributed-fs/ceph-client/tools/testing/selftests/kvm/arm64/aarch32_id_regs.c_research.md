# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/aarch32_id_regs.c

Purpose: this arm64 KVM selftest verifies AArch64-only vCPUs expose the AArch32 ID register views as read-as-zero, with correct write-ignore or invariant-write rejection semantics.

Important APIs and functions: guest `guest_main()` reads many AArch32 ID and media feature sysregs and asserts zero. Host helpers `test_guest_raz()`, `test_user_raz_wi()`, `test_user_raz_invariant()`, and `vcpu_aarch64_only()` exercise `KVM_GET_ONE_REG` / `KVM_SET_ONE_REG` through `vcpu_get_reg()`, `vcpu_set_reg()`, and `__vcpu_set_reg()`. Register arrays classify writable-ignore versus invariant registers.

Control flow: `main()` creates one vCPU, requires an AArch64-only EL0 profile by reading `ID_AA64PFR0_EL1`, tests userspace read/write behavior on the register arrays, then runs the guest to verify in-guest RAZ behavior.

State and persistence: no persistent state exists. Host state is the VM/vCPU and temporary register values. Guest state is only assertion progress.

Dependencies and integration points: depends on arm64 sysreg encodings, KVM one-reg UAPI, libkvm VM creation, `linux/bitfield.h`, and guest ucall assertion reporting.

Risks: the test is intentionally skipped on systems that support AArch32 at EL0. Register classification must track KVM ABI behavior: some zero registers accept writes with no effect, while invariant registers must reject nonzero writes with `EINVAL`.

Test signals: failures identify a nonzero guest read, nonzero userspace read, unexpected write acceptance/rejection, or unexpected ucall. Passing indicates both guest and userspace views conform.
