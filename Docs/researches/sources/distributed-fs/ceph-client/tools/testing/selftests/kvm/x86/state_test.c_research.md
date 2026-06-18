<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/state_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/state_test.c

## Purpose
This broad save/restore test validates `KVM_GET/SET_*` vCPU state, XSAVE restoration, and nested VMX/SVM state preservation. It is a migration-style regression test for regular and nested guest execution.

## Important APIs, Types, and Functions
Important functions are `guest_code()`, `svm_l1_guest_code()`, `svm_l2_guest_code()`, `vmx_l1_guest_code()`, `vmx_l2_guest_code()`, `svm_check_nested_state()`, and `check_nested_state()`. Host logic uses `vcpu_save_state()`, `kvm_vm_release()`, `vm_recreate_with_one_vcpu()`, `vcpu_load_state()`, `vcpu_xsave_set()`, `vcpu_init_cpuid()`, and nested allocation helpers.

## Control Flow, State, and Persistence
The guest first dirties XSAVE-managed state for x87, SSE, AVX, AVX-512, MPX, and PKRU when available. If nested state is available, it then runs either SVM or VMX L1 code. SVM validates VGIF and next-RIP preservation; VMX validates VMCS launch state, `vmptrst`, VMRESUME/VMLAUNCH behavior, and shadow VMCS interaction. On every `GUEST_SYNC`, the host saves full x86 state, releases and recreates the VM, reloads the state, verifies register equality, and separately attempts XSAVE loading into dummy vCPUs with and without CPUID.

## Dependencies and Integration Points
This integrates with x86 state ioctls, nested-state capability, VMX/SVM selftests helpers, XSAVE ABI rules, CPUID/XCR0 feature state, and VM recreation as a migration proxy.

## Risks and Test Signals
Risks include lost launched VMCS state, incorrect shadow-VMCS pointer state, SVM VGIF/nRIP mismatch, XSAVE rejection based on guest CPUID, and register drift after restore. Signals are guest assertions across staged syncs, host nested-state checks, successful dummy XSAVE loads, and identical pre/post-restore general registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/state_test.c -->
