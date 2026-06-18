<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub64.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub64.S

Purpose: Tests paired `R_RISCV_ADD64` and `R_RISCV_SUB64` relocations.

Important APIs/types/functions: Defines global `test_sub64`.

Control flow: Loads a relocated 64-bit value on RV64 or low word on RV32, subtracts the known 32-byte label distance, and returns zero on correct relocation.

State and persistence: Data label `sub64` is two words patched by ADD64/SUB64.

Dependencies and integration points: Module loader 64-bit relocation arithmetic.

Risks: RV32 handling of a 64-bit relocation test must match what the loader emits and what the test loads.

Test signals: `run_test_sub()` zero-return assertion on both XLEN variants.

Source read size: 25 lines, 336 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub64.S -->
