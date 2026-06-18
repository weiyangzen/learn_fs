<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vcpu_width_config.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vcpu_width_config.c

Purpose: this test verifies arm64 KVM's `KVM_ARM_VCPU_INIT` width consistency rule. Homogeneous 64-bit EL1 vCPUs and homogeneous 32-bit EL1 vCPUs must be accepted, while mixed-width vCPUs in the same VM must be rejected.

Important APIs, types, and functions: `add_init_2vcpus()` creates and initializes vCPU0 before creating and initializing vCPU1. `add_2vcpus_init_2vcpus()` creates both vCPUs first and then initializes them. Both use barebones VMs, `__vm_vcpu_add()`, and `__vcpu_ioctl(..., KVM_ARM_VCPU_INIT, ...)`. `main()` obtains `KVM_ARM_PREFERRED_TARGET`, toggles `KVM_ARM_VCPU_EL1_32BIT`, and requires `KVM_CAP_ARM_EL1_32BIT`.

Control flow: the test runs two ordering variants for all-64-bit, all-32-bit, and mixed 64/32-bit configurations. Accepted cases assert return value zero; mixed cases assert a nonzero return value.

State, persistence, and dependencies: VM state is transient. Dependencies are arm64 KVM vCPU initialization, preferred target discovery, and capability reporting. There is no guest code because the test only validates creation/init policy.

Risks and edge cases: the same rule must hold regardless of whether both vCPUs already exist before initialization. The test does not inspect exact errno for mixed-width rejection, only that initialization fails.

Test signals: skip when `KVM_CAP_ARM_EL1_32BIT` is absent; pass when homogeneous cases succeed and both mixed-ordering cases fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vcpu_width_config.c -->
