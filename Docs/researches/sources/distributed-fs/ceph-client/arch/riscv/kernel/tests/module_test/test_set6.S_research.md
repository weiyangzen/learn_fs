<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set6.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set6.S

Purpose: Tests `R_RISCV_SET6` relocation handling for small encoded fields.

Important APIs/types/functions: Defines global `test_set6`.

Control flow: Reads the relocated byte/word value, masks the symbol address down to six bits, subtracts, and returns zero on correct relocation.

State and persistence: Data label `set6` is patched with `R_RISCV_SET6`.

Dependencies and integration points: Exercises module loader support for narrow RISC-V relocation fields.

Risks: Six-bit masking is easy to mishandle across XLEN sizes.

Test signals: `run_test_set()` expects `test_set6()` to return zero.

Source read size: 23 lines, 317 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set6.S -->
