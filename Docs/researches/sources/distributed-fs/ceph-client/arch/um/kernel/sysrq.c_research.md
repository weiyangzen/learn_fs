# sources/distributed-fs/ceph-client/arch/um/kernel/sysrq.c

## Purpose
Provides UML's `show_stack()` implementation for sysrq, oops, and scheduler debugging paths.

## Important APIs, Types, and Functions
`show_stack()` prints a short raw stack window and then emits a call trace using `dump_trace()`. `_print_addr()` formats each address with symbol resolution and reliability marker. `stackops` wires the callback into the stacktrace walker.

## Control Flow, State, and Persistence
No persistent state. The function uses the supplied stack pointer or derives one from task/segv register state, prints up to three stack lines, then delegates symbolic trace printing.

## Dependencies and Integration Points
Depends on `stacktrace.c`, `kallsyms`, task stack helpers, and current thread fault register tracking. Called by generic debug paths and panic/oops reporting.

## Risks and Test Signals
Risks are bad stack pointer selection after nested faults and misleading unreliable markers. Test SysRq task dumps, kernel oops, fatal SIGSEGV, and non-current task stack printing.
