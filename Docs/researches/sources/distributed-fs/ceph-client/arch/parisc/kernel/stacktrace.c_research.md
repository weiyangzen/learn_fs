<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/stacktrace.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/stacktrace.c

### Purpose
`stacktrace.c` adapts PA-RISC unwind support to the generic stacktrace API.

### Important APIs, Types, And Functions
`walk_stackframe()` drives `unwind_once()` and filters entries through `__kernel_text_address()`. `arch_stack_walk()` and `arch_stack_walk_reliable()` are the exported generic hooks.

### Control Flow
The walker initializes unwind state for the target task, repeatedly unwinds one frame, and invokes the consumer callback for kernel text addresses until unwind failure, zero IP, or consumer rejection. The "reliable" variant currently always returns success after walking.

### State, Persistence, And Dependencies
No state is persisted. It depends entirely on `arch/parisc/kernel/unwind.c`, `task_struct`, and kernel text address validation.

### Integration Points
Used by stack dumping, livepatch/reliability consumers, tracing, and generic kernel stacktrace helpers.

### Risks
Reliability reporting is optimistic because it returns `1` even though unwind can fall back to forced stack scanning. User stack tracing is explicitly not implemented.

### Test Signals
Stacktrace collection for current tasks, blocked tasks, interrupt frames, and functions without unwind entries should be compared with expected symbol chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/stacktrace.c -->
