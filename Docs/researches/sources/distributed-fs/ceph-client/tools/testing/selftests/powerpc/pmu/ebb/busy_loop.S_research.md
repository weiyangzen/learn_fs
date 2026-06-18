<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/busy_loop.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/busy_loop.S

Purpose: Assembly CPU burner used by EBB tests to generate PMU events predictably.

Important APIs and types: Exports `core_busy_loop` and contains long loops of arithmetic/branch work with EBB-safe return behavior.

Control flow: Callers invoke it repeatedly while PMCs count cycles/instructions. It returns control for C-side checks after loop completion or interruption.

State and persistence: No persistent state; only CPU/PMU activity is generated.

Dependencies and integration points: Linked into all EBB tests by the EBB Makefile.

Risks: Instruction mix and loop length affect event rates and test timing. Assembly must remain compatible with the EBB handler ABI.

Test signals: Tests pass when this loop reliably causes configured PMU overflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/busy_loop.S -->
