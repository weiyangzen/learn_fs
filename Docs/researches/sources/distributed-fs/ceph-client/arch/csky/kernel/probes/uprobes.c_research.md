# sources/distributed-fs/ceph-client/arch/csky/kernel/probes/uprobes.c

Purpose: C-SKY user-space probe breakpoint, xol slot, cache flush, and resume handling.

Important APIs/types/functions: functions: `is_swbp_insn`, `uprobe_get_swbp_addr`, `arch_uprobe_analyze_insn`, `arch_uprobe_pre_xol`, `arch_uprobe_post_xol`, `arch_uprobe_xol_was_trapped`, `arch_uprobe_skip_sstep`, `arch_uprobe_abort_xol`, `arch_uretprobe_is_alive`, `arch_uretprobe_hijack_return_addr`, `arch_uprobe_exception_notify`, `uprobe_breakpoint_handler`, `uprobe_single_step_handler`; types: `uprobe_task`, `pt_regs`; macros: `UPROBE_TRAP_NR`

Control flow: Runtime flow is organized around `is_swbp_insn`, `uprobe_get_swbp_addr`, `arch_uprobe_analyze_insn`, `arch_uprobe_pre_xol`, `arch_uprobe_post_xol`, `arch_uprobe_xol_was_trapped`, called by generic kernel subsystems through architecture hooks.

State and persistence: Persistent effect is executable text or relocation patching; cache synchronization is required so all CPUs execute the updated instruction stream.

Dependencies and integration: Depends on `linux/highmem.h`, `linux/ptrace.h`, `linux/uprobes.h`, `asm/cacheflush.h`, `decode-insn.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Instruction encoding, alignment, text patching, simulated control flow, and cache coherency are high-risk and can misdirect execution or crash CPUs.

Test signals: C-SKY cross-build; ftrace, kprobes, uprobes, and jump-label selftests.
