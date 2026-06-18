# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_close_kvm_test.c

Purpose: Verifies that closing a KVM VM/process while a nested guest is active and has open file descriptors does not crash or corrupt kernel state.

Important APIs/types/functions: `l2_guest_code()` exits to L0 through port I/O; `l1_vmx_code()` and `l1_svm_code()` launch L2; `l1_guest_code()` selects VMX or SVM; `main()` drives the vCPU until the L0 exit point. It uses nested VMX/SVM setup and `PORT_L0_EXIT`.

Control flow: L1 launches L2. L2 performs port I/O intended to exit all the way to userspace/L0. The host observes the exit and then allows process teardown with nested state still present.

State and persistence behavior: Nested VMCS/VMCB state exists at process close time. The test's value is in cleanup behavior, not persisted data.

Dependencies and integration points: Requires VMX or SVM nested virtualization and KVM cleanup paths for active nested guests.

Risks and maintenance notes: The test is intentionally small and may not catch all teardown races, but it is a focused regression for file-descriptor/VM destruction cleanup. Exit path must continue to reach L0 as expected.

Test signals: Passing means KVM handles VM destruction with active nested state without kernel errors. Failures can be crashes, unexpected exits, or nested teardown assertions.
