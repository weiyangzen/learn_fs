# sources/distributed-fs/ceph-client/arch/sh/kernel/perf_callchain.c

Purpose: records SH kernel perf callchains.

Important APIs and control flow: `callchain_address()` stores only reliable addresses into the perf callchain entry. `perf_callchain_kernel()` records the interrupted PC, then calls `unwind_stack()` with callchain callbacks to append reliable frames.

State, dependencies, and risks: state is the perf callchain entry supplied by the perf core. Dependencies include `pt_regs`, active SH unwinder, and reliability classification. Risks are shallow callchains when the DWARF unwinder is unavailable or marks frames unreliable. Test signals are `perf record -g` kernel callchains, function-graph tracer interaction, and oops/unwinder reliability comparisons.
