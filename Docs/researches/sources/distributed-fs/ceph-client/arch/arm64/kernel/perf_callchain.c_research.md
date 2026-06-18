# sources/distributed-fs/ceph-client/arch/arm64/kernel/perf_callchain.c

Purpose: Implements arm64 perf user and kernel callchain collection.

Important APIs: `perf_callchain_user()` and `perf_callchain_kernel()` call the architecture stack walkers with `callchain_trace()`, which stores PCs through `perf_callchain_store()`.

Control flow and state: if `perf_guest_state()` is active, both paths return without recording guest callchains. Otherwise user callchains use `arch_stack_walk_user()` with current regs, while kernel callchains use `arch_stack_walk()` for `current`.

Dependencies and integration: depends on perf callchain core, arm64 stacktrace unwinding, user access safety, and pointer authentication stripping behavior in stack walkers.

Risks and test signals: risks are missing guest support, bad unwinding across PAC-signed frames, user memory faults, and truncated callchains. Test with perf record/report in user and kernel mode, PAC-enabled kernels, frame-pointer unwinding, and guest execution samples.
