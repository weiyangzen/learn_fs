# sources/distributed-fs/ceph-client/arch/csky/kernel/probes/simulate-insn.c

Purpose: simulation of C-SKY control-flow and literal-load instructions that cannot safely run out of line.

Important APIs/types/functions: functions: `csky_insn_reg_get_val`, `csky_insn_reg_set_val`, `simulate_br16`, `simulate_br32`, `simulate_bt16`, `simulate_bt32`, `simulate_bf16`, `simulate_bf32`, `simulate_jmp16`, `simulate_jmp32`, `simulate_jsr16`, `simulate_jsr32`, `simulate_lrw16`, `simulate_lrw32`, `simulate_pop16`, `simulate_pop32`, `simulate_bez32`, `simulate_bnez32`

Control flow: Runtime flow is organized around `csky_insn_reg_get_val`, `csky_insn_reg_set_val`, `simulate_br16`, `simulate_br32`, `simulate_bt16`, `simulate_bt32`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/bitops.h`, `linux/kernel.h`, `linux/kprobes.h`, `decode-insn.h`, `simulate-insn.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Instruction encoding, alignment, text patching, simulated control flow, and cache coherency are high-risk and can misdirect execution or crash CPUs.

Test signals: C-SKY cross-build; ftrace, kprobes, uprobes, and jump-label selftests.
