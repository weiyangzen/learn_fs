<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/insn.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/insn.h

## Purpose
Defines instruction bitfield masks, opcodes, immediate extraction/insertion helpers, and instruction-class predicates.

## Important APIs, Types, And Functions
functions/prototypes `riscv_insn_is_system`, `riscv_insn_is_branch`, `riscv_insn_is_c_jr`, `riscv_insn_is_c_jalr`, `riscv_insn_extract_jtype_imm`, `riscv_insn_insert_jtype_imm`, `riscv_insn_extract_utype_itype_imm`, `riscv_insn_insert_utype_itype_imm`; macros/constants `_ASM_RISCV_INSN_H`, `RV_INSN_FUNCT3_MASK`, `RV_INSN_FUNCT3_OPOFF`, `RV_INSN_OPCODE_MASK`, `RV_INSN_OPCODE_OPOFF`, `RV_INSN_FUNCT12_OPOFF`, `RV_ENCODE_FUNCT3(f_) (RVG_FUNCT3_##f_ << RV_INSN_FUNCT3_OPOFF)`, `RV_ENCODE_FUNCT12(f_) (RVG_FUNCT12_##f_ << RV_INSN_FUNCT12_OPOFF)`, `RV_I_IMM_SIGN_OPOFF`, `RV_I_IMM_11_0_OPOFF`, `RV_I_IMM_SIGN_OFF`, `RV_I_IMM_11_0_OFF`, `RV_I_IMM_11_0_MASK`, `RV_J_IMM_SIGN_OPOFF`, plus 314 more.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Special attention: the immediate extraction and insertion helpers are consumed by instruction patching, probes, and ftrace-style call rewriting, so bitfield definitions are executable correctness data.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `linux/bits.h`. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 603 lines, 20987 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/insn.h -->
