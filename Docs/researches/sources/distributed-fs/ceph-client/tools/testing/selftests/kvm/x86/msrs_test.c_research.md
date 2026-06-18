# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/msrs_test.c

Purpose: Provides broad MSR ABI coverage for common x86 MSRs, including supported/unsupported access, reserved-value rejection, reset values, host ioctl visibility, save/restore list consistency, and optional `KVM_{GET,SET}_ONE_REG` paths.

Important APIs/types/functions: `struct kvm_msr` describes feature dependency, reset/write/reserved values, MSR index, and whether it is KVM-defined. Macros such as `MSR_TEST`, `MSR_TEST_CANONICAL`, and `MSR_TEST_KVM` build the matrix. Guest helpers `__rdmsr()`, `__wrmsr()`, `guest_test_supported_msr()`, `guest_test_unsupported_msr()`, and `guest_test_reserved_val()` validate in-guest behavior. Host helpers `host_test_kvm_reg()`, `host_test_msr()`, `do_vcpu_run()`, and `test_msrs()` validate ioctl behavior.

Control flow: The host creates three vCPUs: two with normal features and one with selected CPUID features cleared. For every MSR descriptor, it checks save/restore list consistency, syncs the index to the guest, and runs all vCPUs twice to validate state reset and context switching. If `KVM_CAP_ONE_REG` exists, the entire matrix is repeated using one-reg access where possible.

State and persistence behavior: MSR values are per-vCPU architectural state. The test intentionally runs multiple vCPUs on one host thread without CPU pinning to exercise KVM context switching across host CPUs. Global `idx` and descriptor arrays are shared with the guest.

Dependencies and integration points: Depends on x86 MSR definitions, CPUID feature filtering, KVM MSR ioctls, `KVM_GET_MSR_INDEX_LIST`, `KVM_CAP_ONE_REG`, and KVM's `ignore_msrs` behavior.

Risks and maintenance notes: MSR behavior is highly feature-dependent. AMD truncation of some SYSENTER/TSC_AUX values is handled by `fixup_rdmsr_val()`. `ignore_msrs` weakens negative checks by necessity. New MSRs or new one-reg entries require updating the matrix and maximum reg-list assumptions.

Test signals: Passing means KVM guest MSR access, host MSR ioctls, reset behavior, reserved-bit checks, unsupported-feature faults, and one-reg access are consistent. Failures point to MSR emulation, CPUID gating, save/restore, or context-switch bugs.
