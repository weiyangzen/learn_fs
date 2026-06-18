# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/max_vcpuid_cap_test.c

Purpose: Tests the `KVM_CAP_MAX_VCPU_ID` limit by attempting to create vCPUs at and around the reported maximum vCPU ID.

Important APIs/types/functions: `MAX_VCPU_ID` is a small requested ID used in the test; `main()` queries KVM caps and creates a VM/vCPUs. It uses `kvm_check_cap(KVM_CAP_MAX_VCPU_ID)` and vCPU creation helpers.

Control flow: The host checks the maximum supported vCPU ID and verifies KVM accepts legal IDs and rejects IDs beyond the cap. The test is host-only and does not need guest execution.

State and persistence behavior: Only VM/vCPU file descriptors are created. No guest or external persistence exists.

Dependencies and integration points: Depends on KVM vCPU creation ioctl semantics and capability reporting.

Risks and maintenance notes: This is a narrow ABI test. If KVM changes whether the cap is inclusive or exclusive, the expected boundary must remain aligned with documentation.

Test signals: Passing means max-vCPU-ID capability reporting and enforcement agree. Failures indicate vCPU ID bound-checking or cap-reporting bugs.
