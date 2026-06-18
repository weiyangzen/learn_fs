## sources/distributed-fs/ceph-client/arch/s390/kernel/stacktrace.c

Purpose: Provides s390 stack walking for generic stacktrace and perf callchain users, including reliable kernel unwinds and user-space stack walks that understand s390 ABI frames and special vDSO wrapper frames.

Important APIs and functions: `arch_stack_walk()`, `arch_stack_walk_reliable()`, `arch_stack_walk_user_common()`, and `arch_stack_walk_user()`. Helpers store entries either through `perf_callchain_store()` or a generic consumer, reject invalid user IPs, and detect IPs within the vDSO text range.

Control flow: Kernel walks use `unwind_for_each_frame()` and consume `unwind_get_return_address()`. Reliable walks reject non-task stacks, trap-frame frames, missing return addresses, rethook trampolines, and any unwind error. User walks start with the register IP, then follow the user backchain with page faults disabled. If a frame has no backchain while executing inside vDSO, the vDSO wrapper frame layout is decoded to recover the saved return address.

State and persistence: No persistent state is owned here. The walker observes current task `mm`, `vdso_base`, register state, stack contents, and unwind state.

Dependencies and integration: Depends on `unwind_bc.c`, s390 ABI stack-frame definitions, `mmap_min_addr`, mm context ASCE limit, vDSO sizing, perf events, rethook/kprobes, and generic stacktrace consumers.

Risks and test signals: Risks are false reliable stack traces, user memory faults while pagefaults are disabled, and vDSO wrapper layout changes. Test signals include perf callchains, livepatch/reliable-stacktrace validation, user stack unwinds across vDSO calls, bad stack pointer/IP rejection, and rethook-enabled traces being marked unreliable.
