# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_vmsave_vmload_test.c

Purpose: Tests nested SVM `VMSAVE` and `VMLOAD` handling for L2 VMCB state, including access through multiple VMCB GPAs.

Important APIs/types/functions: Memory constants define two test VMCB pages; `l2_guest_code_vmsave()`, `l2_guest_code_vmload()`, and `l2_guest_code_vmcb*()` execute the SVM instructions; `l1_guest_code()` sets up nested SVM and validates saved/loaded state. It uses SVM utilities and guest memory slots.

Control flow: The host creates a nested SVM VM with a test memory slot. L1 launches L2 payloads that perform `VMSAVE` or `VMLOAD` against selected VMCB addresses and checks that state is saved to or loaded from the expected guest physical memory.

State and persistence behavior: VMCB save areas in guest memory are the main state. The test intentionally uses two pages to ensure operations target the requested VMCB, not stale cached state.

Dependencies and integration points: Requires SVM nested virtualization and KVM support for virtualizing `VMSAVE`/`VMLOAD`.

Risks and maintenance notes: AMD-only coverage. The VMCB memory layout must match the helper structures. If KVM changes which state fields are virtualized for these instructions, assertions may need updates.

Test signals: Passing means nested `VMSAVE`/`VMLOAD` read and write the correct guest VMCB memory. Failures indicate SVM nested state serialization or GPA targeting bugs.
