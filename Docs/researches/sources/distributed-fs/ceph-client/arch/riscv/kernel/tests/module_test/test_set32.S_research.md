<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set32.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set32.S

Purpose: Tests `R_RISCV_SET32` module relocation handling.

Important APIs/types/functions: Defines global `test_set32`.

Control flow: Reads the relocated word, masks the symbol address to 32 bits on RV64, subtracts, and returns zero if relocation was applied correctly.

State and persistence: Contains data label `set32` patched by `.reloc set32, R_RISCV_SET32, set32`.

Dependencies and integration points: Linked into the module relocation KUnit test.

Risks: Width handling must match ELF relocation semantics on RV32 and RV64.

Test signals: `run_test_set()` zero-return assertion.

Source read size: 20 lines, 286 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set32.S -->
