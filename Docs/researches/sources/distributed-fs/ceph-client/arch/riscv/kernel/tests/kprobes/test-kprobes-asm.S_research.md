<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/test-kprobes-asm.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/test-kprobes-asm.S

Purpose: Provides assembly functions and address tables used to verify that RISC-V kprobes can instrument control-flow and arithmetic instructions without changing architectural results.

Important APIs/types/functions: Defines test functions for add, `jal`, `jalr`, `auipc`, conditional branches, and compressed `c.j`, `c.jr`, `c.jalr`, `c.bnez`, `c.beqz`; also exports address arrays consumed by the KUnit C harness.

Control flow: Each function computes `KPROBE_TEST_MAGIC` only if probed instructions execute or are simulated correctly. Labeled instruction addresses identify probe sites; compressed tests are built only under `CONFIG_RISCV_ISA_C`.

State and persistence: No persistent state; functions return deterministic values in registers.

Dependencies and integration points: Exercises `simulate-insn.c`, kprobe registration, instruction decoding, and compressed instruction support.

Risks: Label drift or assembler relaxation could move probe sites away from intended instructions; `.option norvc` sections guard full-width instruction tests.

Test signals: `kprobes_riscv` KUnit pass across ISA_C on/off, RV32/RV64, and with kprobes placed at every exported address.

Source read size: 231 lines, 4761 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/test-kprobes-asm.S -->
