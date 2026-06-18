<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/simulate-insn.h -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/simulate-insn.h

Purpose: Declares the RISC-V probe instruction simulation interface and macros used to bind decoded instruction patterns to simulator callbacks or explicit rejections.

Important APIs/types/functions: Defines `RISCV_INSN_REJECTED()` and `RISCV_INSN_SET_SIMULATE()` initializer macros, and prototypes for `simulate_auipc()`, `simulate_branch()`, `simulate_jal()`, `simulate_jalr()`, `simulate_c_j()`, `simulate_c_jr()`, `simulate_c_jalr()`, `simulate_c_bnez()`, and `simulate_c_beqz()`.

Control flow: This header has no runtime flow. Its macros generate decode-table entries whose `handler` points to a simulation function and whose `type` marks the instruction as rejected or simulated.

State and persistence: It owns no state; consumers provide opcode, instruction address, and `pt_regs` state to the declared simulator functions.

Dependencies and integration points: Included by RISC-V kprobe decode logic and the simulator C file. It depends on `struct pt_regs`, `struct riscv_probe_insn`, and `INSN_*` probe type constants from neighboring probe headers.

Risks: Macro field names must stay synchronized with the decode-table structure. Missing prototypes or wrong signatures break kprobe simulation at build time.

Test signals: Compile kprobes with compressed and non-compressed ISA configs and run RISC-V kprobe KUnit coverage for every simulator declared here.

Source read size: 33 lines, 1238 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/simulate-insn.h -->
