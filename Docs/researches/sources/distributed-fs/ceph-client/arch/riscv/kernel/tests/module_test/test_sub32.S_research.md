<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub32.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub32.S

Purpose: Tests paired `R_RISCV_ADD32` and `R_RISCV_SUB32` relocations.

Important APIs/types/functions: Defines global `test_sub32`.

Control flow: Relocation data should become the 32-byte distance between `second` and `first`; the function subtracts 32 and returns zero.

State and persistence: Contains word data patched by ADD32/SUB32 relocations.

Dependencies and integration points: Module loader relocation arithmetic.

Risks: Incorrect add/sub ordering or width truncation produces non-zero return.

Test signals: `run_test_sub()` zero-return assertion.

Source read size: 20 lines, 279 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub32.S -->
