<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_module_linking_main.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_module_linking_main.c

Purpose: Provides the KUnit harness for RISC-V module relocation/linking tests.

Important APIs/types/functions: Declares relocation test functions, defines `run_test_set()`, `run_test_sub()`, optional `run_test_uleb()`, and suite `riscv_checksum`.

Control flow: Each KUnit case calls assembly helpers that return zero only when the module loader applied the tested relocation correctly, then asserts equality with zero.

State and persistence: The module has no persistent state beyond KUnit registration.

Dependencies and integration points: Integrates architecture relocation assembly with KUnit and module loader relocation code.

Risks: The suite name is generic, and failures map to relocation class only through the helper function name. Optional ULEB coverage depends on assembler capability.

Test signals: KUnit pass/fail per SET, SUB, and ULEB relocation family on RV32/RV64 module loads.

Source read size: 88 lines, 1890 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_module_linking_main.c -->
