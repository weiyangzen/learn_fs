<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub6.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub6.S

Purpose: Tests `R_RISCV_SET6` plus `R_RISCV_SUB6` relocation behavior for a six-bit field.

Important APIs/types/functions: Defines global `test_sub6`.

Control flow: The relocation sequence writes a six-bit difference between labels spaced by 32 bytes; the function subtracts 32 and returns zero.

State and persistence: Contains byte data label `sub6` patched by paired relocations.

Dependencies and integration points: RISC-V module relocation handler for narrow subtraction forms.

Risks: Narrow relocation ranges and sign extension are fragile.

Test signals: `run_test_sub()` expects zero from `test_sub6()`.

Source read size: 20 lines, 271 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_sub6.S -->
