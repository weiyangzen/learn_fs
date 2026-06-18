# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/userfaultfd_util.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/userfaultfd_util.h

Purpose: shared userfaultfd helper interface for KVM demand-paging and memory-fault selftests.

Important APIs/types/functions: declarations for creating/configuring userfaultfd, registering memory ranges, spawning fault-handler threads, resolving page faults, and collecting handler statistics.

Control flow and state: host registers guest memory ranges with userfaultfd, starts a handler thread, runs vCPUs that fault on demand, and the handler resolves faults by copying/zeroing pages or coordinating with test policy. Persistent state includes uffd fd, registered ranges, thread state, and counters.

Dependencies and integration: depends on Linux userfaultfd ioctls, pthreads, `kvm_util.h`, `test_util.h`, and memory stress helpers. It integrates with demand paging, dirty logging, private memory, and memslot tests.

Risks: userfaultfd availability is kernel-config and permission dependent. Races between vCPU faults, handler shutdown, and memory unregistration can be subtle. Tests must skip when unprivileged userfaultfd is unavailable.

Test signals: demand-paging KVM selftests validate successful registration, fault resolution, statistics, and clean handler shutdown.
