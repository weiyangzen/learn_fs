<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/pmae_handling_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/pmae_handling_test.c

Purpose: Tests PMAE/PMEO handling around syscalls from within an EBB handler. It verifies reset logic when EBBs occur near syscall boundaries.

Important APIs and types: Defines custom `syscall_ebb_callee`, `test_body`, `pmae_handling`, and `main()`.

Control flow: The handler performs a syscall or syscall-like operation while servicing an EBB, then resets EBB state. The body drives events and checks PMAE/PMEO bits are handled so counting continues correctly.

State and persistence: Uses global EBB stats and hardware BESCR/MMCR0 state.

Dependencies and integration points: Depends on `ebb.h`, syscall behavior from handler context, and PMU SPR semantics.

Risks: Calling into C/syscall paths from an exception handler is delicate and can expose ABI ordering issues.

Test signals: Pass means PMAE handling remains correct across handler/syscall interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/pmae_handling_test.c -->
