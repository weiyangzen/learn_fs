<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/test-kprobes.h -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/test-kprobes.h

Purpose: Declares shared constants and symbols for the RISC-V kprobes KUnit assembly and C harness.

Important APIs/types/functions: Defines `KPROBE_TEST_MAGIC`, lower/upper halves, and extern arrays `test_kprobes_addresses` and `test_kprobes_functions`.

Control flow: No runtime flow; it synchronizes constants between assembly targets and C assertions.

State and persistence: No state.

Dependencies and integration points: Included by both `test-kprobes-asm.S` and `test-kprobes.c`.

Risks: Constant mismatches or missing externs break deterministic test validation.

Test signals: Successful assembly/C compile and KUnit magic-value assertions.

Source read size: 24 lines, 704 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/test-kprobes.h -->
