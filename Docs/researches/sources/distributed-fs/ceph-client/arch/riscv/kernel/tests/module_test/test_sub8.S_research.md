<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub8.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub8.S

Purpose: Tests paired `R_RISCV_ADD8` and `R_RISCV_SUB8` relocations.

Important APIs/types/functions: Defines global `test_sub8`.

Control flow: Relocates a byte with `second - first`, subtracts 32 in the function, and returns zero when relocation is correct.

State and persistence: Contains byte data label `sub8`.

Dependencies and integration points: Module loader support for byte-sized arithmetic relocations.

Risks: Sign extension from `lb` and byte overflow can expose relocation mistakes.

Test signals: `run_test_sub()` expects zero from `test_sub8()`.

Source read size: 20 lines, 271 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub8.S -->
