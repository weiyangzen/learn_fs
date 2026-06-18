# sources/distributed-fs/ceph-client/arch/arc/kernel/unaligned.c

Purpose: emulates selected user-mode unaligned ARC load/store instructions when `CONFIG_ARC_EMUL_UNALIGNED` is enabled.

Important APIs/functions: `misaligned_fixup()` is called by trap handling. `fixup_load()` and `fixup_store()` perform register writeback and byte-wise memory access. Inline assembly macros implement exception-table guarded unaligned 8/16/32-bit loads and stores, with endian-specific byte ordering.

Control flow: `misaligned_fixup()` rejects kernel-mode faults and disabled emulation, logs according to sysctl knobs, disassembles the faulting instruction with `disasm_instr()`, rejects unsupported byte/invalid forms, then dispatches to load or store fixup. On success it advances `regs->ret`, handles delay-slot state and zero-overhead-loop wraparound, and emits a perf alignment fault event.

State and persistence: global `unaligned_enabled` and `no_unaligned_warning` are read-mostly sysctl-controlled policy state. Per-fault state lives in `struct disasm_state`, `pt_regs`, and optional `callee_regs`; register and instruction pointer state are modified to make the emulated instruction appear complete.

Dependencies and integration: integrates with trap code, ARC disassembler/register access helpers, exception tables, perf software events, uaccess-style fixups, and endian/ISA configuration.

Risks: instruction decoding must exactly match hardware semantics, especially address writeback, delay slots, sign extension, and loop registers. Store fixup writeback has a suspicious branch where `state->aa == 2` is checked before a nested `state->aa == 3` case, so maintenance should be careful around writeback modes. Emulation hides user bugs and can degrade performance.

Test signals: userspace unaligned halfword/word load/store tests across endian builds, sysctl enable/disable behavior, delay-slot and zero-overhead-loop cases, perf alignment fault counters, and faulting user pages during emulation.
