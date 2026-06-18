# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_tsc_adjust_test.c

Purpose: Tests `IA32_TSC_ADJUST` behavior when L1 and L2 write `IA32_TSC`, including the unusual case where L2 writes TSC without L1 intercepting and thereby changes L1's TSC adjust accounting.

Important APIs/types/functions: Constants `TSC_ADJUST_VALUE` and `TSC_OFFSET_VALUE` define expected offsets; `check_ia32_tsc_adjust()` reads and reports adjust; `l2_guest_code()` writes TSC from L2; `l1_guest_code()` writes TSC in L1 and launches L2 through VMX or SVM with a TSC offset; `report()` logs observed values.

Control flow: L1 first writes TSC so `TSC_ADJUST` becomes negative one unit. It then launches L2 with a TSC offset. L2 computes L1-relative TSC, writes TSC again, and asserts adjust is now about negative two units. After L2 exits, L1 checks the final adjust value and reports done.

State and persistence behavior: `IA32_TSC` and `IA32_TSC_ADJUST` are vCPU MSR state. Nested TSC offset is VMCS/VMCB state. No persistent external state exists.

Dependencies and integration points: Requires nested VMX/SVM, TSC adjust MSR support, and correct interaction between nested TSC offsetting and non-intercepted MSR writes.

Risks and maintenance notes: TSC behavior can be host-sensitive, but the test compares large adjust deltas rather than exact TSC values. Intercept policy changes could alter which level's TSC is affected.

Test signals: Passing means KVM accounts TSC writes into `IA32_TSC_ADJUST` correctly across L1 and L2 with offsets. Failures implicate nested TSC offset or adjust emulation.
