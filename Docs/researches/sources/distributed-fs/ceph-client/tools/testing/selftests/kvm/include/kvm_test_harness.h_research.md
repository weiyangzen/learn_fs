# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_test_harness.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/kvm_test_harness.h

Purpose: convenience macros that bind kselftest harness tests to common one-vCPU KVM VM setup and cleanup.

Important APIs/types/functions: `KVM_ONE_VCPU_TEST_SUITE(name)` defines fixture setup/teardown and `KVM_ONE_VCPU_TEST(suite, test, guestcode)` defines a harness test body receiving a prepared `struct kvm_vcpu *`.

Control flow and state: the fixture creates a VM with one vCPU running the supplied guest code before each test and frees it afterward. The macro-generated test invokes an internal `__suite_test(struct kvm_vcpu *)` helper so test authors can focus on vCPU behavior.

Dependencies and integration: includes `kselftest_harness.h` and uses common KVM VM creation from `kvm_util.h` through the fixture implementation.

Risks: the abstraction is intentionally narrow: one VM, one vCPU, default shape. Tests needing custom memory, protected VM types, multiple vCPUs, or custom setup should not force-fit into these macros.

Test signals: compile-time macro expansion and harness execution of one-vCPU tests validate fixture lifecycle and cleanup.
