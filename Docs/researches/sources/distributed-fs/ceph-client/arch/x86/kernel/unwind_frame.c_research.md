# sources/distributed-fs/ceph-client/arch/x86/kernel/unwind_frame.c

Purpose: implements the frame-pointer based x86 stack unwinder. It walks saved base-pointer chains, validates stack transitions, handles encoded `pt_regs` frames, and exposes return-address iteration to generic stacktrace code.

Important APIs/functions: `unwind_get_return_address()`, `unwind_get_return_address_ptr()`, `unwind_next_frame()`, and `__unwind_start()`. Internal helpers validate final task frames, aligned GCC prologue frames, ftrace frames, encoded frame pointers, and stack bounds.

Control flow: `__unwind_start()` initializes state from task/register inputs, rejects user-mode start states, handles the special IP==0 incomplete-frame case, seeds stack metadata, and advances until the requested first frame. `unwind_next_frame()` stops on user regs or known last task frames, obtains the next frame pointer from saved regs/current BP/queued BP, then calls `update_stack_state()` to validate the new frame and recover the return address. Bad addresses set `state->error` and may dump the current stack once.

State and persistence: state is per-unwind in `struct unwind_state`. Persistent behavior is limited to one-shot dump suppression via static booleans. The unwinder reads task stacks using `READ_ONCE_TASK_STACK` and does not modify task state.

Dependencies and integration: integrates with stack metadata from `get_stack_info()`, task stack layout, entry text boundaries, ftrace graph return recovery, KMSAN annotations, `task_pt_regs()`, and exported stacktrace APIs.

Risks: frame-pointer corruption, stack switching, entry-code interrupts before a frame is established, 32-bit objtool gaps, and concurrent unwinding of running non-current tasks can produce incomplete traces or warnings. Validation must avoid reading outside legitimate task/exception stacks.

Test signals: reliable stack traces from current and sleeping tasks, warnings for intentionally corrupted frame pointers, ftrace graph traces, syscall/interrupt frames, and IP==0 crash scenarios. 32-bit builds intentionally suppress some warnings.
