<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/Makefile

Purpose: Builds the RISC-V module-linking KUnit test module from relocation-specific assembly objects and a C KUnit harness.

Important APIs/types/functions: Defines `test_sub` and `test_set` object groups, optional `test_uleb128.o`, and `test_module_linking-objs`.

Control flow: Kbuild links relocation test objects into one loadable module; ULEB128 tests are included only when assembler support is available.

State and persistence: No runtime state in the Makefile.

Dependencies and integration points: Exercises module loader relocation support for RISC-V-specific relocations.

Risks: Config or object-list errors reduce relocation coverage without obvious runtime failures.

Test signals: Build/load the test module with `CONFIG_RISCV_MODULE_LINKING_KUNIT` and `CONFIG_AS_HAS_ULEB128` variations.

Source read size: 15 lines, 392 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/module_test/Makefile -->
