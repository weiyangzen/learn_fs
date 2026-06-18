## sources/distributed-fs/ceph-client/arch/mips/kernel/stacktrace.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/stacktrace.c` implements the MIPS `save_stack_trace()` API. It records kernel return addresses either by raw stack scanning or by the MIPS unwinder when kallsyms and valid kernel PCs are available.

### Important APIs, Types, And Functions
Core helpers are `save_raw_context_stack()`, `save_context_stack()`, `save_stack_trace()`, and `save_stack_trace_tsk()`. It uses `struct stack_trace`, `struct pt_regs`, `prepare_frametrace()`, `unwind_stack()`, `__kernel_text_address()`, and `in_sched_functions()`.

### Control Flow
For the current task, `save_stack_trace_tsk()` synthesizes pt_regs through `prepare_frametrace()`. For another task, it reads saved stack pointer and return address from `task_struct.thread`. `save_context_stack()` either raw-scans stack words for kernel text addresses or walks frames with `unwind_stack()`, honoring `trace->skip`, `trace->max_entries`, and the `savesched` filtering flag.

### State, Persistence, And Dependencies
No durable state is changed. Output is the caller-provided `stack_trace` buffer. Dependencies include MIPS stack unwinder state, `raw_show_trace` from `traps.c`, task stack layout, `THREAD_SIZE`, and scheduler-function filtering.

### Integration Points
This file supports generic stacktrace users such as lockdep, tracing, debugging, and profiling. It shares unwind behavior with `traps.c` register dumps and respects the same raw trace mode.

### Risks
Raw scanning can miss frames or include false positives. Saved context for non-current tasks may be stale. The function warns if the caller provides a non-empty or zero-sized trace. Stack bounds checks are essential before raw scanning a task stack.

### Test Signals
Collect stack traces from current and sleeping tasks, with and without kallsyms, with `raw_show_trace`, with scheduler-frame filtering, and with shallow `max_entries` plus nonzero `skip`.
