# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_extended_hypercalls.c

Purpose: Tests userspace handling of Hyper-V extended hypercall `HV_EXT_CALL_QUERY_CAPABILITIES`. It verifies that KVM exits to userspace and that a userspace-supplied result is visible to the guest.

Important APIs/types/functions: `EXT_CAPABILITIES` is the expected output token; `guest_code()` enables Hyper-V, executes the extended hypercall, and checks the output page; `main()` allocates input/output pages and handles the KVM Hyper-V exit. It uses `KVM_CAP_HYPERV_CPUID`, `HV_ENABLE_EXTENDED_HYPERCALLS`, `KVM_EXIT_HYPERV`, and `hyperv_hypercall()`.

Control flow: The host skips if extended hypercalls are unsupported. The guest sets guest OS ID and hypercall MSR, then invokes `HV_EXT_CALL_QUERY_CAPABILITIES`. KVM exits to userspace; the host validates call metadata, writes `EXT_CAPABILITIES` into the output page, resumes the vCPU, and the guest asserts the value.

State and persistence behavior: Hypercall input/output pages are guest memory. Output content is written by userspace and read by the guest in the same VM lifetime.

Dependencies and integration points: Integrates with KVM Hyper-V hypercall exit ABI and the guest/host shared-memory contract for extended hypercalls.

Risks and maintenance notes: Only the positive path is covered here; negative cases are in `hyperv_features.c`. Hypercall exit structure changes or TLFS output-size changes would require updates.

Test signals: Passing means KVM exposes extended hypercalls to userspace and the guest receives userspace-completed results. Failures indicate Hyper-V hypercall exit ABI or page-translation regressions.
