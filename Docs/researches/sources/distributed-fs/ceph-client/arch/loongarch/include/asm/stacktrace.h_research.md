<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/stacktrace.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/stacktrace.h

Purpose: declares LoongArch stacktrace helpers and stack-frame validation interfaces.
Important APIs and types: defines frame record structures/helpers and declares `arch_stack_walk`, `arch_stack_walk_reliable`, and user stack-walk helpers through generic stacktrace integration.
Control flow: unwinder code walks frames from `pt_regs` or task stacks and feeds return addresses to generic consumers.
State and persistence: no persistent state; it interprets stack contents and saved frame pointers.
Dependencies and integration: consumed by `kernel/stacktrace.c`, `unwind.h`, ftrace, livepatch reliable-stack checks, perf, lockdep, and panic backtraces.
Risks and test signals: weak validation can emit bogus traces or mark unreliable stacks reliable. Signals include unwinder selftests, livepatch reliable-stack checks, NMI/panic backtraces, and user stack walking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/stacktrace.h -->
