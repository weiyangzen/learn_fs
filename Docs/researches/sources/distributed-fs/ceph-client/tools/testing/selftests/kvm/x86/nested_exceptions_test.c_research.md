# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_exceptions_test.c

Purpose: Tests pending versus injected exception handling for L2, especially a queued `#SS` that becomes `#GP`, `#DF`, or nested shutdown/triple fault depending on L1 intercepts.

Important APIs/types/functions: Defines expected error-code constants for AMD and Intel, intercept masks, `l2_ss_*` sync functions, `svm_run_l2()`, `vmx_run_l2()`, `l1_svm_code()`, `l1_vmx_code()`, `assert_ucall_vector()`, and `queue_ss_exception()`. It uses `KVM_CAP_EXCEPTION_PAYLOAD` and `KVM_GET/SET_VCPU_EVENTS`.

Control flow: L2 first syncs asking the host to queue `#SS`. The host tests a pending `#SS` with immediate exit, verifies event payload round trip, then runs and observes L1 intercepting `#SS`. It repeats with injected `#SS` cases where vectoring through an empty IDT causes `#GP`, then `#DF`, then final shutdown/triple fault as L1 disables intercepts.

State and persistence behavior: Pending/injected exception state is vCPU event state manipulated by userspace. Nested intercept bitmaps are L1 VMCS/VMCB state. Error payloads must survive get/set events.

Dependencies and integration points: Requires nested VMX or SVM, exception payload capability, event ioctls, and precise x86 exception-vectoring semantics.

Risks and maintenance notes: Intel and AMD differ in `#GP` error-code external-bit semantics, and the test encodes both. Injected versus pending semantics are subtle and easy to regress in nested event handling.

Test signals: Passing means KVM preserves event payloads, honors L1 intercepts, and morphs nested exceptions into `#GP`, `#DF`, and triple fault correctly. Failures identify nested exception delivery or event-ioctl bugs.
