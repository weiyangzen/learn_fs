<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/ftrace.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/ftrace.c

### Purpose
`ftrace.c` implements MIPS dynamic ftrace code patching, function graph return-address hijacking, and syscall address lookup for ftrace syscall tracing. It rewrites `_mcount` call sites between NOP/branch sequences and calls into `ftrace_caller`.

### Important APIs, Types, And Functions
Key APIs include `arch_ftrace_update_code()`, `ftrace_make_nop()`, `ftrace_make_call()`, `ftrace_update_ftrace_func()`, `ftrace_dyn_arch_init()`, `ftrace_enable_ftrace_graph_caller()`, `ftrace_disable_ftrace_graph_caller()`, `prepare_ftrace_return()`, and `arch_syscall_addr()`. Internal instruction helpers generate JAL, branch, NOP, and long-call sequences using `uasm`.

### Control Flow
Dynamic ftrace boot initialization precomputes patch instructions and removes the boot-time branch around `ftrace_caller`. Later, ftrace core calls `ftrace_make_call()` or `ftrace_make_nop()` per callsite. Kernel text can use direct JAL, while modules use an address-load sequence when `_mcount` is outside direct jump range. Function graph tracing locates or receives the caller's saved return address, replaces it with `return_to_handler`, and calls `function_graph_enter()`.

### State, Persistence, And Dependencies
Patch templates are stored in read-mostly globals such as `insn_jal_ftrace_caller`, `insn_la_mcount`, and `insn_j_ftrace_graph_caller`. Runtime state is in text memory and the current task's graph tracing state. The file depends on safe text load/store helpers, icache flushing, `core_kernel_text()`, syscall tables, `mcount.S` symbols, and `CONFIG_DYNAMIC_FTRACE`/`CONFIG_FUNCTION_GRAPH_TRACER`.

### Integration Points
It integrates with Linux ftrace core, function graph tracer, syscall tracing, MIPS module callsite layout, and architecture-specific `_mcount` assembly. The code must match the exact instruction sequences emitted by GCC and represented in `mcount.S`.

### Risks
Risks are instruction patch atomicity, icache coherency, jump-range limits, module long-call encoding, and stack return-address discovery. The 32-bit path patches two instructions and uses different write ordering for call enablement, so partial patching bugs can execute malformed code.

### Test Signals
Useful tests are booting with dynamic ftrace, enabling/disabling function tracing repeatedly, tracing module functions, enabling function graph tracing with and without `KBUILD_MCOUNT_RA_ADDRESS`, and checking syscall tracepoints on O32/N32/64-bit ABI builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/ftrace.c -->
