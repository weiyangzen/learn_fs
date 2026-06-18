<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/simulate-insn.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/simulate-insn.c

Purpose: Simulates selected RISC-V branch and PC-relative instructions when kprobes single-step cannot execute the original instruction in place. It updates `pt_regs` as if the probed instruction ran, allowing probes on control-flow instructions.

Important APIs/types/functions: Implements `simulate_jal()`, `simulate_jalr()`, `simulate_auipc()`, `simulate_branch()`, `simulate_c_j()`, `simulate_c_jr()`, `simulate_c_jalr()`, `simulate_c_bnez()`, and `simulate_c_beqz()`. Internal helpers `rv_insn_reg_get_val()` and `rv_insn_reg_set_val()` bridge decoded register numbers to `pt_regs`.

Control flow: Each simulator decodes immediates and register operands with `riscv_insn_*` helpers, validates source/destination registers, writes link or AUIPC results when required, and advances or redirects `regs->epc`. Conditional branches compare decoded register values and choose `addr + offset` or the next instruction length.

State and persistence: The only persistent state is the interrupted register file. The code mutates `regs->epc`, optional destination GPRs, and link registers; it has no global state and returns false when an instruction form or register access is rejected.

Dependencies and integration points: Used by RISC-V kprobe decode tables through `simulate-insn.h`; depends on `<asm/insn.h>`, probe `decode-insn.h`, and the architecture `pt_regs` layout. KUnit kprobe assembly in this subset provides direct behavior coverage for these simulators.

Risks: Wrong immediate sign extension, compressed instruction length, or x0 handling can corrupt the probed control flow. JALR target masking, link address selection, and branch compare signedness are ABI-visible under probes.

Test signals: Probe `jal`, `jalr`, `auipc`, all conditional branch variants, compressed jump/register/branch instructions, x0 destinations, and rejected forms under `CONFIG_RISCV_KPROBES_KUNIT`.

Source read size: 239 lines, 6033 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/simulate-insn.c -->
