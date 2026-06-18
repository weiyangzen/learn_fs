<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set16.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set16.S

Purpose: Tests `R_RISCV_SET16` module relocation handling.

Important APIs/types/functions: Defines global `test_set16`.

Control flow: Loads a relocated 16-bit value from data, computes the low 16 bits of the symbol address, subtracts, and returns zero on correct relocation.

State and persistence: Contains one data word labeled `set16` with a `.reloc` directive.

Dependencies and integration points: Used by the module-linking KUnit harness and RISC-V module loader relocation code.

Risks: RV32/RV64 masking differs; incorrect sign/zero extension can hide relocation errors.

Test signals: `run_test_set()` expects zero from `test_set16()`.

Source read size: 23 lines, 325 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set16.S -->
