## sources/distributed-fs/ceph-client/arch/loongarch/kernel/mcount_dyn.S

### Purpose
`mcount_dyn.S` implements the dynamic ftrace trampoline path for LoongArch patchable function entries. It builds partial or full `pt_regs`, invokes the selected ftrace operation, supports function graph tracing, and includes the direct-call trampoline used by dynamic ftrace direct calls.

### Important APIs, Types, And Functions
It defines `ftrace_stub`, `ftrace_common`, `ftrace_call`, `ftrace_graph_call`, `ftrace_caller`, `ftrace_regs_caller`, `ftrace_graph_caller`, `return_to_handler`, and `ftrace_stub_direct_tramp`. The `ftrace_regs_entry` macro saves argument registers, frame pointer, return addresses, and optionally all GPRs into a `PT_SIZE` frame matching `struct pt_regs`.

### Control Flow
Patchable function entry branches arrive with `t0` holding parent `ra`. The caller wrapper saves registers, computes `ip = ra - 8`, loads `function_trace_op`, and calls the patched `ftrace_call` site. If graph tracing is patched in, `ftrace_graph_caller` calls `prepare_ftrace_return` using the saved parent return slot. The common return path restores live ABI registers and either returns to the original function continuation or, when direct-call state is present in `PT_R13`, jumps to a direct target.

### State, Persistence, And Dependencies
Persistent state lives in generic ftrace static globals and dynamically patched branch sites, not in this file. The assembly depends on `-fpatchable-function-entry=2`, LoongArch module trampolines, `asm/ftrace.h` address constants, `asm/stackframe.h` pt_regs offsets, and graph/direct ftrace configuration.

### Integration Points
`ftrace_dyn.c` patches callsites and module trampolines to these entry points. Generic ftrace and graph tracer code supply callbacks, direct-call targets, and return handlers. The generated `pt_regs` shape is consumed by `CONFIG_DYNAMIC_FTRACE_WITH_REGS` callbacks.

### Risks
The entry contract is tight: compiler patchable-entry layout, module trampoline layout, and `ra - 8` callsite math must remain in sync. Incorrect saved register layout breaks ftrace-with-regs consumers. Direct-call return routing through `PT_R13` is subtle and can redirect control flow incorrectly if not initialized exactly.

### Test Signals
Run dynamic ftrace selftests, ftrace-with-regs probes, graph tracing, module tracing, and direct-call tracing. Inspect patched instructions in core kernel and modules and verify callbacks see correct `ip`, `parent_ip`, `op`, and register values.
