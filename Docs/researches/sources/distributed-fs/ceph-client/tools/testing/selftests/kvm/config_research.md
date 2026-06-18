<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/config

Purpose: this kselftest config fragment declares kernel configuration options expected for KVM selftests in this tree.

Important entries: `CONFIG_KVM=y` enables core KVM support. `CONFIG_KVM_INTEL=y` and `CONFIG_KVM_AMD=y` enable x86 vendor modules. `CONFIG_EVENTFD=y` supports irqfd/eventfd-based tests. `CONFIG_USERFAULTFD=y` supports demand paging tests. `CONFIG_IDLE_PAGE_TRACKING=y` supports memory tracking scenarios elsewhere in the KVM selftests.

Control flow and state: this file is declarative data consumed by kselftest configuration tooling; it has no runtime control flow and writes no state.

Dependencies and integration: it integrates with kernel build/config checking for `tools/testing/selftests/kvm`. Individual tests still perform runtime `TEST_REQUIRE()` capability checks because kernel config alone does not guarantee host hardware or KVM module support.

Risks and test signals: the fragment is generic and x86-heavy despite the directory containing multi-architecture tests. Missing options can cause build or runtime skips; extra options do not force tests to run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/config -->
