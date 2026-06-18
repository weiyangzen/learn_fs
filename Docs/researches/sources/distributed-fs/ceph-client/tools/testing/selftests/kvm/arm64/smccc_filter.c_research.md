<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/smccc_filter.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/smccc_filter.c

Purpose: this arm64 selftest validates the VM-level SMCCC filter UAPI. It verifies argument validation, reserved-range protection, overlap rejection, and runtime behavior for denied versus userspace-forwarded SMCCC calls.

Important APIs, types, and functions: `enum smccc_conduit` selects HVC or SMC. `guest_main()` issues `smccc_hvc()` or `smccc_smc()` and reports `res.a0`. `__set_smccc_filter()` and `set_smccc_filter()` wrap `KVM_ARM_VM_SMCCC_CTRL`/`KVM_ARM_VM_SMCCC_FILTER` device attributes using `struct kvm_smccc_filter`. `setup_vm()` creates a PSCI-enabled vCPU. Test functions cover nonzero `pad`, zero or overflowing ranges, reserved action values, Arm Architecture reserved SMCCC ranges, overlapping filter ranges, `KVM_SMCCC_FILTER_DENY`, and `KVM_SMCCC_FILTER_FWD_TO_USER`.

Control flow: `main()` first checks `kvm_supports_smccc_filter()`, then runs UAPI validation tests followed by runtime action tests. Runtime tests iterate conduits with `for_each_conduit()`, using SMC only when the vCPU can run at EL2 and otherwise HVC plus SMC. Denied calls must return `SMCCC_RET_NOT_SUPPORTED` through the guest ucall path; forwarded calls must exit to userspace with `KVM_EXIT_HYPERCALL`, the expected function number, and the SMC flag set only for SMC.

State, persistence, and dependencies: all filter state is VM-local KVM state; each test uses a fresh VM and frees it. Dependencies include `<linux/arm-smccc.h>`, `<linux/psci.h>`, KVM arm64 vCPU target setup, PSCI feature bits, and selftest ucall helpers.

Risks and edge cases: reserved Arm Architecture calls must not be filterable, because KVM owns mitigation and discovery semantics there. The conduit loop depends on whether the guest has EL2. Overlap and overflow checks protect interval arithmetic. Test failures indicate either too-permissive UAPI acceptance or incorrect exit/return-code behavior.

Test signals: expected `EINVAL` for bad padding, zero range, overflow, and reserved actions; expected `EEXIST` for reserved/overlapping ranges; `SMCCC_RET_NOT_SUPPORTED` for denied calls; and `KVM_EXIT_HYPERCALL` plus correct flags for forwarded calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/smccc_filter.c -->
