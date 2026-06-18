<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/large_vm_gpr_corruption.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/large_vm_gpr_corruption.c

Purpose: Stress test for general-purpose register corruption during faults on large virtual-memory mappings. It targets SLB/high-address exception paths.

Important APIs and types: Defines high-address mapping constants, `signal_handler`, `CHECK_REG` macro, `touch_mappings()`, `test()`, and `main()`.

Control flow: `test()` maps many high-address regions, installs a signal handler, poisons/checks GPR values around loads/stores that fault or touch mappings, and verifies registers retain expected values after exception handling.

State and persistence: Transient mappings plus register snapshots are the only state. No files are persisted.

Dependencies and integration points: Depends on 64-bit powerpc, signal delivery, high virtual address support, and inline assembly/register constraints.

Risks: Register-specific inline assembly is fragile across compiler options. The test is meaningful only on configurations that exercise large VM/SLB paths.

Test signals: Pass indicates exception handling around high-address VM activity preserves user GPR state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/large_vm_gpr_corruption.c -->
