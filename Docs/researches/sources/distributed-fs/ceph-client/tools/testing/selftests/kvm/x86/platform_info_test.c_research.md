# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/platform_info_test.c

Purpose: Tests x86 `KVM_CAP_MSR_PLATFORM_INFO` handling, specifically guest read visibility and userspace configuration of `MSR_PLATFORM_INFO`.

Important APIs/types/functions: `MSR_PLATFORM_INFO_MAX_TURBO_RATIO` identifies the tested field; `guest_code()` reads `MSR_PLATFORM_INFO` and asserts expected behavior; `main()` checks/enables the capability and writes test MSR values through KVM ioctls.

Control flow: The host verifies the capability, creates a VM/vCPU, configures platform-info MSR state, and runs the guest. The guest reads the MSR and validates that the exposed max turbo ratio/state matches what userspace configured.

State and persistence behavior: Platform-info MSR state is vCPU/VM configuration state. No data is persisted externally.

Dependencies and integration points: Depends on `KVM_CAP_MSR_PLATFORM_INFO`, MSR emulation, and x86 processor helpers.

Risks and maintenance notes: The test focuses on a specific platform-info field; future KVM support for additional fields may need expanded assertions. Feature availability is host/KVM dependent.

Test signals: Passing means userspace can configure platform-info MSR exposure and the guest observes the expected value. Failures point to capability gating or MSR emulation regressions.
