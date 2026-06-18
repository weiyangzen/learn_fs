# sources/distributed-fs/ceph-client/arch/s390/kernel/kprobes.c

Purpose: s390 architecture implementation of kprobes, including instruction slot allocation, breakpoint patching, PER-based single stepping, reentrancy handling, and exception notifier integration.

Important APIs and state: per-CPU `current_kprobe` and `kprobe_ctlblk` hold active probe state. Hooks include `alloc_insn_page()`, `arch_prepare_kprobe()`, `arch_arm_kprobe()`, `arch_disarm_kprobe()`, `arch_remove_kprobe()`, `kprobe_fault_handler()`, `kprobe_exceptions_notify()`, `arch_populate_kprobe_blacklist()`, and `arch_trampoline_kprobe()`.

Control flow: preparation verifies instruction boundaries with symbol-size decoding, rejects prohibited opcodes, allocates executable instruction slots, and copies/adjusts relative-long instructions. Arm/disarm writes a breakpoint or original opcode using `s390_kernel_write()` and either `text_poke_sync()` or `stop_machine_cpuslocked()`. Breakpoint notification disables preemption, pushes probe state, runs pre-handlers, enables PER single-step on the copied instruction, resumes/fixes PSW/registers after the single-step trap, then runs post-handlers. Fault paths restore state or try exception fixups.

Dependencies and integration: depends on disassembler helpers, extable fixups, text patching, executable memory, stop_machine, ftrace/kdebug notifier events, PER control registers, and irqentry blacklist sections.

Risks and test signals: instruction decoding, relative displacement fixup, PER mask restore, and reentrant probe BUG paths are critical. Test probes on branches, modules, faulting instructions, nested handlers, remove races, irqentry blacklist rejection, and systems without sequential instruction patching.
