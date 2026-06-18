# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/ucall.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/s390/ucall.h

Purpose: s390 adapter for common KVM selftest ucalls.

Important APIs/types/functions: defines s390 `UCALL_EXIT_REASON` and `ucall_arch_do_ucall(gva_t uc)` to transport guest notifications to host userspace.

Control flow and state: common guest code writes a ucall payload and invokes the s390 architecture adapter. The adapter triggers the architecture-specific KVM exit used by host-side ucall decoding.

Dependencies and integration: includes `kvm_util.h` and participates in `ucall_common.h`. All s390 tests using guest sync, done, abort, or printf depend on it.

Risks: the exit reason and payload convention must match host decoding. A broken adapter causes broad test failures with unexpected exits or missing ucall data.

Test signals: s390 guest assertion and synchronization tests are the primary validation path.
