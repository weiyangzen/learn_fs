# sources/distributed-fs/ceph-client/arch/alpha/kernel/signal.c

## Purpose
`signal.c` implements Alpha signal ABI support: OSF/1-compatible signal syscalls, RT signal action, signal frame creation/restoration, signal-return syscalls, syscall restart handling, ptrace single-step interaction, and pending user-mode work processing.

## Important APIs, Types, And Functions
- `_BLOCKABLE` masks out `SIGKILL` and `SIGSTOP`.
- `osf_sigprocmask`, `osf_sigaction`, and `rt_sigaction` implement Alpha/OSF ABI signal mask/action variants.
- `struct sigframe` and `struct rt_sigframe` define user stack frame layouts; a compile-time assertion protects `rt_sigframe` offset ABI.
- Instruction constants encode an inline return stub: move stack pointer to argument, load syscall number, and `callsys`.
- `restore_sigcontext()` restores PC, integer registers, switch-stack saved registers, user stack pointer, FP registers, FPCR, restart block, and FPU restore status.
- `do_sigreturn()` and `do_rt_sigreturn()` validate user frames, restore blocked masks, restore context, and generate `SIGTRAP` if single-stepping.
- `get_sigframe()` chooses altstack/current stack and aligns the frame to 32 bytes.
- `setup_sigcontext()`, `setup_frame()`, and `setup_rt_frame()` build non-RT and RT signal frames.
- `handle_signal()` selects frame type and calls `signal_setup_done()`.
- `syscall_restart()` implements Alpha syscall restart register/PC adjustments.
- `do_signal()` coordinates signal selection, restart behavior, saved mask restoration, and ptrace breakpoint reset.
- `do_work_pending()` loops over reschedule, signal, notify, and resume-user-mode work before returning to userspace.

## Control Flow
Signal delivery starts from `do_work_pending()` when `_TIF_SIGPENDING` or `_TIF_NOTIFY_SIGNAL` is present. It enables interrupts, saves FPU state, and calls `do_signal()`. `do_signal()` cancels pending single-step breakpoints before inspecting signals. If a signal is available, it optionally rewinds/restarts a syscall, builds a frame via `handle_signal()`, and arranges user registers to enter the handler. If no signal is delivered, it handles syscall restart cases and restores saved signal mask. Finally it reinstalls single-step breakpoints when needed.

Signal return validates the user-provided `sigcontext` or `ucontext`, restores blocked signal mask, restores register state through `restore_sigcontext()`, and reports a breakpoint trap if a single-step breakpoint had been active.

## State And Persistence
State moves between kernel register frames and user stack frames. The file mutates current signal mask, restart block, FPU restore flags, FP save area, user stack pointer, and syscall result registers. User-space signal frames persist until the handler returns or user code overwrites them.

## Dependencies And Integration Points
This code depends on Alpha ABI structs (`sigcontext`, `ucontext`), syscall numbers, `pt_regs`/`switch_stack` layout, ptrace breakpoint helpers from `ptrace.c`, FPU save/restore conventions, generic signal APIs, altstack helpers, and user-mode resume work.

## Risks
- Signal frame layout is ABI-sensitive; offsets and `siginfo_t` sizing cannot change without breaking userland unwinders and signal return.
- Inline return stubs require executable user stack or supplied restorer behavior consistent with Alpha ABI expectations.
- Register restore reads many user fields; partial faults must reliably force `SIGSEGV`.
- Syscall restart depends on Alpha `r0`, `r19`, and PC rewind semantics.
- Ptrace single-step state must be canceled and restored around signal delivery to avoid stale breakpoints.

## Test Signals
- OSF and RT signal action/mask ABI tests.
- Signal delivery and return for normal and `SA_SIGINFO` handlers, including altstack.
- Syscall restart tests for `ERESTARTSYS`, `ERESTARTNOHAND`, `ERESTARTNOINTR`, and `ERESTART_RESTARTBLOCK`.
- Ptrace single-step across signal delivery should produce expected `SIGTRAP`.
- Fault injection with invalid signal frames should force `SIGSEGV`.
