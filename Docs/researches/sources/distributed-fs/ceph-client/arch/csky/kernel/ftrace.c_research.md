# sources/distributed-fs/ceph-client/arch/csky/kernel/ftrace.c

Purpose: dynamic ftrace patching, ftrace-call replacement, function graph return rewriting, and SMP instruction-cache synchronization.

Important APIs/types/functions: functions: `make_jbsr`, `ftrace_check_current_nop`, `ftrace_modify_code`, `ftrace_make_call`, `ftrace_make_nop`, `ftrace_update_ftrace_func`, `ftrace_modify_call`, `prepare_ftrace_return`, `ftrace_enable_ftrace_graph_caller`, `ftrace_disable_ftrace_graph_caller`, `__ftrace_modify_code`, `arch_ftrace_update_code`; types: `ftrace_modify_param`; macros: `NOP`, `NOP32_HI`, `NOP32_LO`, `PUSH_LR`, `MOVIH_LINK`, `ORI_LINK`, `JSR_LINK`, `BSR_LINK`; exports: `_mcount`

Control flow: Runtime flow is organized around `make_jbsr`, `ftrace_check_current_nop`, `ftrace_modify_code`, `ftrace_make_call`, `ftrace_make_nop`, `ftrace_update_ftrace_func`, called by generic kernel subsystems through architecture hooks.

State and persistence: Persistent effect is executable text or relocation patching; cache synchronization is required so all CPUs execute the updated instruction stream.

Dependencies and integration: Depends on `linux/ftrace.h`, `linux/uaccess.h`, `linux/stop_machine.h`, `asm/cacheflush.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Instruction encoding, alignment, text patching, simulated control flow, and cache coherency are high-risk and can misdirect execution or crash CPUs.

Test signals: C-SKY cross-build; ftrace, kprobes, uprobes, and jump-label selftests.
