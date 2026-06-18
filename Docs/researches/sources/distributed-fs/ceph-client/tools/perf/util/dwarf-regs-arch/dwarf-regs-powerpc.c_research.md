# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-powerpc.c

Purpose: Provides PowerPC DWARF register mapping and a helper to decode register operands from raw PowerPC instructions for annotation. `get_powerpc_regs(raw_insn, is_source, op_loc)` fills an `annotated_op_loc` with source/target register, optional second register, and memory offset for D/DS-form instructions. `__get_dwarf_regnum_for_perf_regnum_powerpc(perf_regnum)` maps perf register enums to DWARF numbers for GPRs and selected special registers.

Control flow and state: Stateless bitfield extraction macros decode opcode and operand fields. Register mapping uses a sparse static table where unsupported entries remain zero, with a special case preserving valid register zero.

Dependencies and integration: Depends on PowerPC perf uapi, `dwarf-regs.h`, and `annotated_op_loc`. The generic dispatcher selects it for `EM_PPC` and `EM_PPC64`.

Risks: The sparse table uses zero as unsupported sentinel, requiring special handling for register 0; this pattern is easy to break on future valid zero-like entries. X-form offset handling is still TODO. Several perf registers are intentionally unmapped.

Test signals: Instruction decode tests for D, DS, and X forms; mapping tests for R0/R31, MSR, CTR, LINK, XER, unsupported NIP/CCR; annotation tests for PowerPC load/store operands.
