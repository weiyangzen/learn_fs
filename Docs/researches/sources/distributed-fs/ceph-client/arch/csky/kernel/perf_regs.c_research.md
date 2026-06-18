# sources/distributed-fs/ceph-client/arch/csky/kernel/perf_regs.c

Purpose: perf register mask validation and pt_regs register-value extraction.

Important APIs/types/functions: functions: `perf_reg_value`, `perf_reg_validate`, `perf_reg_abi`, `perf_get_regs_user`; types: `pt_regs`; macros: `REG_RESERVED`

Control flow: Runtime flow is organized around `perf_reg_value`, `perf_reg_validate`, `perf_reg_abi`, `perf_get_regs_user`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/errno.h`, `linux/kernel.h`, `linux/perf_event.h`, `linux/bug.h`, `asm/perf_regs.h`, `asm/ptrace.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; perf stat/record, callchain, and overflow tests.
