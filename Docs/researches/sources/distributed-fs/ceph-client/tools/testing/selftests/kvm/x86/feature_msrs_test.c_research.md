# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/feature_msrs_test.c

Purpose: Validates KVM's feature MSR index list and access semantics. It checks that KVM-controlled feature MSRs are visible through the expected APIs, hidden VMX MSRs stay hidden when appropriate, and unsupported or quirked MSRs behave consistently.

Important APIs/types/functions: `is_kvm_controlled_msr()`, `is_hidden_vmx_msr()`, `is_quirked_msr()`, and `test_feature_msr()` classify and test each MSR. The program uses `KVM_GET_MSR_FEATURE_INDEX_LIST`, `KVM_GET_MSRS`, `KVM_SET_MSRS`, and x86 feature MSR constants.

Control flow: `main()` obtains KVM's feature MSR list and iterates every entry. For each MSR, host-side ioctls validate read behavior, classification exceptions, and write rejection/acceptance as appropriate.

State and persistence behavior: Feature MSRs are host/KVM capability state, not per-VM durable state. The test creates temporary structures for ioctl lists and results only.

Dependencies and integration points: Integrates with KVM's global MSR feature enumeration ABI and x86 VMX/feature MSR filtering logic.

Risks and maintenance notes: New feature MSRs, hidden MSR rules, or compatibility quirks require updating the classifier helpers. The test is intentionally ABI-facing and should not encode transient implementation details except documented quirks.

Test signals: Passing means feature MSR enumeration and access behavior match KVM's public ABI. Failures indicate stale MSR lists, incorrect hidden MSR exposure, or broken feature MSR ioctl handling.
