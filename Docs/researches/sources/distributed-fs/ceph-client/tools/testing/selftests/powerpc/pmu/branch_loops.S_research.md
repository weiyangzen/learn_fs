<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/branch_loops.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/branch_loops.S

Purpose: Assembly loop for PMU branch event testing. It repeatedly performs an indirect branch via CTR for a large iteration count.

Important APIs and types: Exports `indirect_branch_loop` and defines `ITER_SHIFT` to set loop count to `1 << 31`.

Control flow: The function initializes a counter, decrements it, loads the address of a local branch target through the TOC/GOT, moves it into CTR, and executes `bctr` until the count reaches zero.

State and persistence: No persistent state. It consumes CPU and branch predictor/PMU resources.

Dependencies and integration points: Depends on powerpc assembly macros from `ppc-asm.h` and PMU tests that call it.

Risks: Long loops are intentionally expensive. ABI/TOC addressing must match the link mode.

Test signals: PMU branch counter tests use this routine to produce repeatable indirect branch traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/branch_loops.S -->
