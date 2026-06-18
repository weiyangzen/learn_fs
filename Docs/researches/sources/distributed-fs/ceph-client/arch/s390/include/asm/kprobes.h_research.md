# sources/distributed-fs/ceph-client/arch/s390/include/asm/kprobes.h

Purpose: This header defines s390 kprobes instruction and per-CPU control-block contracts.

Important APIs/types/functions: `BREAKPOINT_INSTRUCTION`, fixup flags, `probe_is_prohibited_opcode()`, `probe_get_fixup_type()`, `probe_is_insn_relative_long()`, `kprobe_opcode_t`, `MAX_INSN_SIZE`, `MAX_STACK_SIZE`, `struct arch_specific_insn`, `struct prev_kprobe`, `struct kprobe_ctlblk`, `arch_remove_kprobe()`, and `kprobe_fault_handler()` are the public pieces.

Control flow: Kprobes copies the original s390 instruction into an insn slot, replaces the target with the breakpoint instruction, and uses fixup classification to emulate or adjust PSW/register state after single-stepping or trap handling. The per-CPU control block saves probe status, interrupt mask, selected control registers, and nested probe state.

State and persistence: Persistent state includes per-probe copied instructions and per-CPU kprobe control blocks while probes are armed. Instruction slots need no cache flush according to this header.

Dependencies and integration points: It depends on `ctlreg.h`, generic kprobes, ptrace, per-CPU storage, and task stack helpers.

Risks and test signals: Probing prohibited opcodes, relative-long branches, or stack-sensitive code can corrupt execution. Tests should include kprobe and kretprobe selftests, prohibited opcode rejection, relative branch fixups, nested probe faults, and CONFIG_KPROBES=n builds.
