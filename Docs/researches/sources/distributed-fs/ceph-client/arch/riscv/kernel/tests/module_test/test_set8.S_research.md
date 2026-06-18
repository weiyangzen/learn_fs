<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set8.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set8.S

Purpose: Tests `R_RISCV_SET8` module relocation handling.

Important APIs/types/functions: Defines global `test_set8`.

Control flow: Reads the relocated data, masks the symbol address to eight bits, subtracts, and returns zero if the loader wrote the expected value.

State and persistence: Data label `set8` carries an `R_RISCV_SET8` relocation.

Dependencies and integration points: Used by the module-linking KUnit suite.

Risks: Byte-width relocation truncation must not sign-extend unexpectedly.

Test signals: `run_test_set()` zero-return assertion.

Source read size: 23 lines, 317 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_set8.S -->
