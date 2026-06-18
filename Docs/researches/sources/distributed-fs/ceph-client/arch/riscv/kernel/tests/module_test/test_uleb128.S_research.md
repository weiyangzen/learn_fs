<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_uleb128.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_uleb128.S

Purpose: Tests RISC-V ULEB128 relocation pairs in modules.

Important APIs/types/functions: Defines `test_uleb_basic()` and `test_uleb_large()`.

Control flow: Two data labels use `R_RISCV_SET_ULEB128` and `R_RISCV_SUB_ULEB128` to encode label distances of 127 and 0x7e8; functions subtract those expected distances and return zero.

State and persistence: Contains relocation-patched data words and padding regions that establish known distances.

Dependencies and integration points: Included only when `CONFIG_AS_HAS_ULEB128` is true and validates module loader ULEB relocation support.

Risks: Variable-length encodings can overflow or be applied with wrong byte counts; assembler support gating is required.

Test signals: Optional `run_test_uleb()` KUnit case passing both basic and large distances.

Source read size: 31 lines, 504 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/test_uleb128.S -->
