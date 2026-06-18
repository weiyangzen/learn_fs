<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/stacktrace.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/stacktrace.h

Purpose: declares x86 stacktrace, unwind, and stack-type helpers. Important APIs/types include stack type enums, stack metadata, `get_stack_info()`, `unwind_start()`, `unwind_next_frame()`-adjacent declarations, reliable stacktrace helpers, and checks for entry/exception/IRQ stacks.

Control flow: oops, perf, ftrace, livepatch, lockdep, and proc stack readers classify an address into task, IRQ, exception, entry, or unknown stacks, then unwind frames using ORC/frame-pointer/guess unwinders. State is stack memory and unwinder cursor state.

Dependencies include thread/IRQ stack layout, ORC unwinder, frame pointers, entry stacks, per-CPU stacks, and KASAN/KMSAN constraints. Risks include unreliable unwinds, stack-boundary misclassification, false livepatch safety, and unsafe reads from corrupted stacks. Test signals include oops backtraces, perf callchains, livepatch reliable stacktrace tests, NMI/IRQ stack unwinds, and frame-pointer/ORC build variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/stacktrace.h -->
