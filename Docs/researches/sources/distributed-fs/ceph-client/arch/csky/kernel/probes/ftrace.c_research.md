# sources/distributed-fs/ceph-client/arch/csky/kernel/probes/ftrace.c

Purpose: dynamic ftrace patching, ftrace-call replacement, function graph return rewriting, and SMP instruction-cache synchronization.

Important APIs/types/functions: functions: `kprobe_ftrace_handler`, `arch_prepare_kprobe_ftrace`; types: `ftrace_ops`, `kprobe`, `kprobe_ctlblk`, `pt_regs`

Control flow: Runtime flow is organized around `kprobe_ftrace_handler`, `arch_prepare_kprobe_ftrace`, called by generic kernel subsystems through architecture hooks.

State and persistence: Persistent effect is executable text or relocation patching; cache synchronization is required so all CPUs execute the updated instruction stream.

Dependencies and integration: Depends on `linux/kprobes.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Instruction encoding, alignment, text patching, simulated control flow, and cache coherency are high-risk and can misdirect execution or crash CPUs.

Test signals: C-SKY cross-build; ftrace, kprobes, uprobes, and jump-label selftests.
