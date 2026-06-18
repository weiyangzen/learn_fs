<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/wild_bctr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/wild_bctr.c

Purpose: Tests register preservation and signal behavior when branching through a wild count register target. It intentionally executes an invalid indirect branch.

Important APIs and types: Defines `BAD_NIP`, context save/handlers, register poisoning/checking helpers, OPD handling for ELFv1, `test_wild_bctr()`, and `main()`.

Control flow: `test_wild_bctr()` poisons GPRs, attempts a branch to a bad target (`bctr` path), handles SIGSEGV/SIGUSR2, saves ucontext registers, and checks the kernel did not corrupt preserved registers while reporting the bad NIP.

State and persistence: Global register snapshots and signal status are process-local. No persistent state.

Dependencies and integration points: Depends on powerpc64 ABI differences, ucontext register layout, signals, and inline assembly.

Risks: Highly ABI-sensitive: ELFv1 function descriptors and ELFv2 direct code pointers differ. Compiler register allocation must not defeat the poison/check assumptions.

Test signals: Pass indicates wild indirect branch faults preserve expected userspace register state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/wild_bctr.c -->
