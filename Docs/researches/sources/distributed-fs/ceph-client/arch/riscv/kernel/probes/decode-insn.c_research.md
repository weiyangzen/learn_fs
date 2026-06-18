# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/decode-insn.c

Purpose: Classifies RISC-V instructions for kprobe single-step or simulation handling.

Important APIs/types/functions: Implements `riscv_probe_decode_insn()` returning `enum probe_insn` values.

Control flow: Kprobe preparation passes an instruction and address to the decoder. The decoder rejects unsupported or unsafe instructions, marks simulatable control-flow forms for software simulation, and allows normal single-step slot preparation for other probeable instructions.

State and persistence: No persistent state; classification is per instruction.

Dependencies and integration points: Used by `kprobes.c`, instruction simulation helpers, RISC-V instruction predicates, and probe blacklists.

Risks and test signals: Misclassification can probe unsafe instructions or single-step instructions that cannot be executed out of line. Test kprobe placement on compressed/normal branches, jumps, breakpoints, illegal instructions, and exception-generating instructions.
