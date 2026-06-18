# sources/distributed-fs/ceph-client/arch/x86/include/asm/unwind_user.h

Purpose: x86-specific helpers for user-space stack unwinding.

Important APIs/types/functions: `unwind_user_word_size()`, `ARCH_INIT_USER_FP_FRAME`, `ARCH_INIT_USER_FP_ENTRY_FRAME`, and `unwind_user_at_function_start()`.

Control flow: when user unwinding is enabled, word size is derived from `pt_regs`: VM86 stacks return 0 because they are unsupported, 64-bit user mode returns 8, and other user modes return 4. Frame-pointer initialization macros encode CFA, return-address, and frame-pointer offsets. Function-start detection delegates to uprobes.

State/persistence: no state. It reads register mode bits and uprobe state.

Dependencies/integration: depends on ptrace mode helpers and `asm/uprobes.h`. Integrated with generic user unwinding, perf, BPF/profile stack collection, and uprobe-aware unwinding.

Risks/test signals: wrong word size or frame layout corrupts user stack traces, especially compat processes. Test 64-bit, 32-bit compat, VM86 rejection, frame-pointer unwinding at normal call sites and function entries with uprobes installed.
