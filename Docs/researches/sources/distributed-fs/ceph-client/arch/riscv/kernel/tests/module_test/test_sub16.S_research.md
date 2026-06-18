<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub16.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub16.S

Purpose: Tests paired `R_RISCV_ADD16` and `R_RISCV_SUB16` relocations.

Important APIs/types/functions: Defines global `test_sub16`.

Control flow: Two text labels are separated by 32 bytes; the data halfword is relocated as `second - first`. The function subtracts 32 and returns zero on correct relocation.

State and persistence: Contains relocation-patched data label `sub16`.

Dependencies and integration points: Exercises module loader arithmetic relocation handling.

Risks: Signed halfword loads and relocation overflow/truncation can affect results.

Test signals: `run_test_sub()` expects zero from `test_sub16()`.

Source read size: 20 lines, 279 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub16.S -->
