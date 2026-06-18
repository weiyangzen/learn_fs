<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/Makefile

Purpose: Builds the RISC-V kprobes KUnit module from C and assembly test objects.

Important APIs/types/functions: Defines `kprobes_riscv_kunit-objs := test-kprobes.o test-kprobes-asm.o`.

Control flow: Kbuild links the C test harness and assembly probe target functions when `CONFIG_RISCV_KPROBES_KUNIT` is enabled.

State and persistence: No runtime state in the Makefile itself.

Dependencies and integration points: Ties the kprobes simulator tests to KUnit and the architecture test build.

Risks: Object list drift can produce a test module without probe targets or without the harness.

Test signals: Build and run `kprobes_riscv` KUnit suite.

Source read size: 3 lines, 122 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/Makefile -->
