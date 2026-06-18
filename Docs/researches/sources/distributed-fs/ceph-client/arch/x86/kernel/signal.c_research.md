# sources/distributed-fs/ceph-client/arch/x86/kernel/signal.c

## Purpose
`signal.c` is the common x86 signal-delivery and syscall-restart layer. It chooses the ABI-specific frame builder, computes signal-frame sizing, handles altstack and FPU frame placement, manages syscall restart rewinds, and validates dynamic sigaltstack size.

## Important APIs, Types, And Functions
Important functions are `get_sigframe()`, `get_sigframe_size()`, `arch_do_signal_or_restart()`, `signal_fault()`, and `sigaltstack_size_valid()`. It dispatches to IA32, x32, and x64 setup functions, and uses `rseq_signal_deliver()`, `fpu__alloc_mathframe()`, `copy_fpstate_to_sigframe()`, and `fpu__clear_user_states()`.

## Control Flow
`get_sigframe()` applies the x86-64 red zone, switches to an altstack when requested, supports legacy ia32 stack switching, allocates the FPU frame, aligns the ABI stack, checks altstack overflow, temporarily opens PKRU access, and saves FP/xstate. `arch_do_signal_or_restart()` either delivers a pending signal or rewinds/replaces syscall state. `handle_signal()` handles vm86 state, restart errors, ptrace single-step cleanup, frame setup, DF/RF/TF clearing, and completion.

## State, Persistence, Dependencies, Integration
State touched includes `pt_regs`, saved masks, restart blocks, PKRU, FPU/xstate frames, rseq state, and boot-initialized `max_frame_size`. It integrates with `signal_32.c`, `signal_64.c`, FPU signal helpers, vDSO/vm86, pkeys, and generic signal code.

## Risks And Test Signals
Stack alignment, red-zone rules, PKRU restore on failure, dynamic xstate sizing, syscall IP rewinding, and debugger stepping are fragile ABI contracts. Test native 64-bit, IA32, x32, altstack/`SS_AUTODISARM`, PKU-protected stacks, AVX512/dynamic xstate, every `ERESTART*`, vm86, ptrace stepping, and bad-frame SIGSEGV paths.
