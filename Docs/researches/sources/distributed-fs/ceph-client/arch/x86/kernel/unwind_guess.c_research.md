# sources/distributed-fs/ceph-client/arch/x86/kernel/unwind_guess.c

Purpose: provides a fallback heuristic unwinder that scans stack words for values that look like kernel text addresses when reliable ORC or frame-pointer unwind data is unavailable.

Important APIs/functions: implements the same unwinder surface: `unwind_get_return_address()`, `unwind_get_return_address_ptr()`, `unwind_next_frame()`, and `__unwind_start()`.

Control flow: unwind start aligns the supplied first frame, records stack metadata, and optionally advances until the first plausible text address. Each `unwind_next_frame()` increments the stack pointer through the current stack range, returns when it sees a word passing `__kernel_text_address()`, and follows `stack_info.next_sp` to additional stacks until no valid stack remains.

State and persistence: all active state lives in `struct unwind_state`: task, stack pointer, stack info, and visited stack mask. It reads stack memory without modifying task or global state.

Dependencies and integration: depends on stack bounds from `get_stack_info()`, text-address validation, ftrace/rethook return address recovery, and generic unwind callers expecting the normal unwind API.

Risks: this is intentionally imprecise. It can report false positives from data words that resemble code addresses, miss frames with nonstandard layouts, and cannot provide return-address pointers for patching. It is useful for diagnostics, not correctness-sensitive call-chain reconstruction.

Test signals: stack dumps should contain plausible call chains when other unwinders are disabled. False-positive tolerance and graceful termination on stack boundaries are more important than exact frame counts.
