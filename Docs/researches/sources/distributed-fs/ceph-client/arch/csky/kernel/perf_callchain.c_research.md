# sources/distributed-fs/ceph-client/arch/csky/kernel/perf_callchain.c

Purpose: perf user and kernel callchain unwinding from frame records.

Important APIs/types/functions: functions: `unwind_frame_kernel`, `walk_stackframe`, `user_backtrace`, `perf_callchain_user`, `perf_callchain_kernel`; types: `stackframe`, `perf_callchain_entry_ctx`, `pt_regs`

Control flow: Runtime flow is organized around `unwind_frame_kernel`, `walk_stackframe`, `user_backtrace`, `perf_callchain_user`, `perf_callchain_kernel`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/perf_event.h`, `linux/uaccess.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build; perf stat/record, callchain, and overflow tests.
