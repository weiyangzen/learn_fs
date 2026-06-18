# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_set_state_test.c

Purpose: Tests integrity and validation of `KVM_SET_NESTED_STATE` for VMX and SVM. It covers valid default state, malformed sizes, bad flags, bad addresses, revision mismatches, eVMCS-specific cases, and SVM enable/disable transitions.

Important APIs/types/functions: `test_nested_state*()` wrappers assert success or errno; `set_revision_id_for_vmcs12()`, `set_default_state()`, `set_default_vmx_state()`, and `set_default_svm_state()` build test structures; `test_vmx_nested_state()` and `test_svm_nested_state()` contain the validation matrices; `vcpu_efer_enable_svm()` and `vcpu_efer_disable_svm()` manipulate SVM enablement.

Control flow: `main()` creates a VM/vCPU, detects VMX/SVM/eVMCS support, and runs the relevant nested-state tests. Each matrix mutates one field at a time from a known-good nested-state structure and verifies KVM accepts or rejects it with the expected errno.

State and persistence behavior: Nested state is userspace-provided serialized vCPU state. The test repeatedly overwrites it through ioctls and checks validation behavior; no external persistence exists.

Dependencies and integration points: Depends on `KVM_CAP_NESTED_STATE`, VMX/SVM support, eVMCS support where available, Linux `struct kvm_nested_state`, and KVM's ioctl validation paths.

Risks and maintenance notes: Structure layout, `VMCS12_REVISION`, and accepted flag combinations are tightly coupled to KVM internals exposed through UAPI. Updates to nested-state UAPI require synchronized test changes.

Test signals: Passing means KVM accepts valid nested serialized state and rejects malformed VMX/SVM state with stable errno values. Failures identify UAPI validation regressions.
