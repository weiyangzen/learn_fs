## sources/distributed-fs/ceph-client/arch/loongarch/kernel/mcount.S

### Purpose
`mcount.S` is the classic LoongArch `_mcount` implementation for function tracing and function graph tracing when dynamic patchable ftrace is not the active entry path. It calls the registered trace function with callsite and parent return addresses, and optionally rewrites function returns through the graph tracer.

### Important APIs, Types, And Functions
The main exported symbol is `_mcount`. It also defines `ftrace_stub`, `ftrace_graph_func`, `ftrace_graph_caller`, and `return_to_handler` when graph tracing is enabled. It calls `ftrace_trace_function`, `prepare_ftrace_return`, and `ftrace_return_to_handler`, while saving only `s0` and `ra` in a small local frame.

### Control Flow
At function entry, `_mcount` loads `ftrace_trace_function`; if it differs from `ftrace_stub`, it saves registers and calls the tracer with `ra` and the parent return address. It then checks graph tracing callbacks and either returns through `ftrace_stub` or calls `ftrace_graph_caller`, which asks `prepare_ftrace_return` to replace the parent return address. `return_to_handler` saves return-value registers, asks generic graph tracing for the real parent address, restores return values, and jumps there.

### State, Persistence, And Dependencies
State is controlled by global ftrace function pointers patched by generic tracing. The assembly depends on LoongArch ABI conventions, stack-frame offsets, and the compiler's mcount call sequence. No persistent storage is owned locally.

### Integration Points
This file integrates with `kernel/trace/ftrace.c`, graph tracer core, and LoongArch build flags that emit mcount calls. It is parallel to `mcount_dyn.S`, which handles patchable-function-entry/dynamic ftrace.

### Risks
The code relies on precise return-address interpretation; off-by-one-instruction callsite math would corrupt call graph output. Saving too few registers is safe only because psABI caller/callee rules are honored. Graph tracing must preserve return-value registers or traced functions will misbehave.

### Test Signals
Enable function tracer and function graph tracer, trace simple kernel functions, verify callsite and parent symbols, and run with modules if classic mcount is used. Stress with nested tracing and functions returning values in `a0/a1`.
