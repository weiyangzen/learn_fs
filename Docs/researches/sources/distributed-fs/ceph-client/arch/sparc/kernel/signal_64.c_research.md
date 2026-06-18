# sources/distributed-fs/ceph-client/arch/sparc/kernel/signal_64.c

Purpose: implements native SPARC64 signal and user-context handling, including `getcontext`/`setcontext`, RT signal frame setup/return, 32-bit compat delegation, syscall restart, uprobe/notify resume, FPU/register-window preservation, and siginfo ABI assertions.

Important APIs/functions: entry points are `sparc64_set_context()`, `sparc64_get_context()`, `do_rt_sigreturn()`, and `do_notify_resume()`. Internal helpers include `invalid_frame_pointer()`, `get_sigframe()`, `setup_rt_frame()`, `syscall_restart()`, and `do_signal()`.

Control flow: `set_context` validates user context, optionally restores signal mask, applies PC/NPC alignment and 32-bit truncation, restores safe TSTATE bits, selected globals/outs, register-window FP/I7 slots, and optional FPU state. `get_context` clears a user context, advances past the trap instruction, writes mask/register/window/FPU metadata, and signals on faults. RT sigreturn validates the biased frame, restores PC/NPC, Y, safe TSTATE bits, all user regs, optional FPU/window state, mask and altstack, clears syscall state, then returns. Signal delivery delegates to `do_signal32()` for `TIF_32BIT`; otherwise it saves windows/FPU, builds an aligned RT frame, saves regs/mask/altstack/siginfo/window state, sets handler arguments according to the SPARC64 libc sigcontext convention, and uses the user-provided restorer.

State and persistence: mutates current `pt_regs`, signal mask, altstack state, FPU/VIS saved state, register-window buffers, and user ucontext/signal-frame memory. No persistent storage.

Dependencies and integration points: depends on generic signal/uprobes/resume-user-mode work, context tracking, compat signal32 code, SPARC64 ucontext ABI, stack-bias rules, `save_fpu_state()`/`restore_fpu_state()`, register-window helpers, and syscall restart conventions.

Risks: native SPARC64 requires a user restorer for signal return. `set_context` deliberately skips `%g7` because it is the user thread register. Safe TSTATE masking is critical to avoid privilege-state corruption. Bias handling for frame and saved FP values is error-prone, especially when dispatching compat tasks.

Test signals: 64-bit signal delivery/rt_sigreturn, libc `getcontext`/`setcontext`, signal masks and altstack restoration, FPU/VIS state preservation, saved register windows, syscall restart behavior, uprobe notify resume, compat 32-bit signal delegation, and malformed biased frame tests.
