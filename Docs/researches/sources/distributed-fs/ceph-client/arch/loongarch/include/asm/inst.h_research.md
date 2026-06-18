# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/inst.h

## Purpose

`inst.h` models LoongArch instruction encodings and instruction patch/generation helpers. It is part of the LoongArch architecture support in the Ceph client kernel source snapshot and is compiled into low-level kernel code rather than into Ceph-specific distributed filesystem logic. The header has 809 source lines, so its role is mostly to publish constants, inline helpers, ABI-shaped types, or external entry points to the rest of the architecture tree.

## Important APIs And Types

Important exported surface: opcode enums, format structs, union loongarch_instruction, loongarch_gpr, is_branch/break/pc/stack/ra helpers, simu_pc/branch, larch_insn_* read/write/patch/generate, emit_* helpers, unaligned access emulation. Symbol extraction from the file shows representative defines `_ASM_INST_H`, `INSN_NOP`, `INSN_BREAK`, `INSN_HVCL`, `ADDR_IMMMASK_LU52ID`, `ADDR_IMMMASK_LU32ID`, `ADDR_IMMMASK_LU12IW`, `ADDR_IMMMASK_ORI`, `ADDR_IMMMASK_ADDU16ID`, `ADDR_IMMSHIFT_LU52ID`, `ADDR_IMMSBIDX_LU52ID`, `ADDR_IMMSHIFT_LU32ID`, representative callable declarations or inline helpers `is_imm_negative`, `is_break_ins`, `is_pc_ins`, `is_branch_ins`, `is_ra_save_ins`, `is_stack_alloc_ins`, `is_self_loop_ins`, `simu_pc`, `simu_branch`, `insns_not_supported`, `insns_need_simulation`, `arch_simulate_insn`, and representative local types `reg0i15_op`, `reg0i26_op`, `reg1i20_op`, `reg1i21_op`, `reg2_op`, `reg2i5_op`, `reg2i6_op`, `reg2i12_op`, `reg2i14_op`, `reg2i16_op`. Direct includes seen in the header are `asm/asm.h`, `asm/ptrace.h`, `linux/bitops.h`, `linux/types.h`. These names are the practical API because other LoongArch files include this header rather than constructing the register encodings, memory-management details, or low-level calling conventions themselves.

## Control Flow, State, And Persistence

Control flow is mostly compile-time inclusion plus inline execution at architecture call sites. Where the file declares assembly or C entry points, runtime control enters from exception, MMU, KVM, IRQ, tracing, module-loading, or boot code and returns through the generic Linux subsystem that requested the operation. Persistent state is not stored in the header itself, but the interfaces frequently describe persistent kernel state such as per-CPU feature data, task FPU/LBT ownership, page-table roots, KVM vCPU/VM fields, firmware boot data, interrupt-controller domains, or hardware CSR state.

## Dependencies And Integration Points

This header central to alternatives, ftrace, kprobes, BPF, module PLT, KVM emulation and unaligned access traps. Its immediate dependencies are the included Linux and `asm/` headers listed above, while its broader integration is with generic kernel subsystems that expect an architecture implementation of the same names. For the Ceph client source tree, these headers matter because networking, memory allocation, atomics, scheduling, module loading, tracing, and block/network drivers all rely on the architecture layer underneath filesystem code.

## Risks And Test Signals

Primary risks: bitfield layout, immediate sign extension and text patch synchronization are critical; test with tracing, probes and branch-range cases. Because most of these headers are ABI-like architecture contracts, small numeric changes can compile cleanly but fail at boot, during context switch, under interrupt load, or when userspace observes ELF, ptrace, signal, KVM, or perf behavior. Useful test signals are LoongArch defconfig/allmodconfig builds, sparse/objtool where enabled, boot tests under QEMU or real Loongson hardware, and subsystem-specific selftests that exercise the exported contract. For this specific file, also watch compile coverage of every extracted symbol category above and runtime logs around the subsystem named in the integration section.
