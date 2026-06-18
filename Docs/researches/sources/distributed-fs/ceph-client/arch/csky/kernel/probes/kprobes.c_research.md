# sources/distributed-fs/ceph-client/arch/csky/kernel/probes/kprobes.c

Purpose: kprobe breakpoint planting, single-step/simulation, reentry, fault, and kretprobe trampoline handling.

Important APIs/types/functions: functions: `patch_text_cb`, `patch_text`, `arch_prepare_ss_slot`, `arch_prepare_simulate`, `arch_simulate_insn`, `arch_prepare_kprobe`, `arch_arm_kprobe`, `arch_disarm_kprobe`, `arch_remove_kprobe`, `save_previous_kprobe`, `restore_previous_kprobe`, `set_current_kprobe`, `kprobes_save_local_irqflag`, `kprobes_restore_local_irqflag`, `set_ss_context`, `clear_ss_context`, `setup_singlestep`, `reenter_kprobe`; types: `csky_insn_patch`, `kprobe_ctlblk`, `pt_regs`, `kprobe`; macros: `pr_fmt(fmt)`, `TRACE_MODE_SI`, `TRACE_MODE_MASK`, `TRACE_MODE_RUN`

Control flow: Preparation decodes and copies the probed instruction, patching text with a breakpoint. Trap handling runs pre-handlers, single-steps or simulates the instruction, restores PC/status, handles faults/reentry, and then invokes post-handlers.

State and persistence: Persistent effect is executable text or relocation patching; cache synchronization is required so all CPUs execute the updated instruction stream.

Dependencies and integration: Depends on `linux/kprobes.h`, `linux/extable.h`, `linux/slab.h`, `linux/stop_machine.h`, `asm/ptrace.h`, `linux/uaccess.h`, `asm/sections.h`, `asm/cacheflush.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Instruction encoding, alignment, text patching, simulated control flow, and cache coherency are high-risk and can misdirect execution or crash CPUs.

Test signals: C-SKY cross-build; ftrace, kprobes, uprobes, and jump-label selftests.
