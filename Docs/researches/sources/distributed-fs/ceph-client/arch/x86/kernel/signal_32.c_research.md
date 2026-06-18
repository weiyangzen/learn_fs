# sources/distributed-fs/ceph-client/arch/x86/kernel/signal_32.c

## Purpose
`signal_32.c` implements i386 and IA32-compat signal-frame setup and return. It preserves classic and realtime 32-bit signal ABIs, restores segment registers, and asserts `siginfo32_t` layout invariants.

## Important APIs, Types, And Functions
Key functions are `ia32_setup_frame()`, `ia32_setup_rt_frame()`, `sigreturn`, `rt_sigreturn`, and `ia32_restore_sigcontext()`. Helpers include `fixup_rpl()`, `reload_segments()`, and `__unsafe_setup_sigcontext32()`. Important ABI types include `sigframe_ia32`, `rt_sigframe_ia32`, `sigcontext_32`, `compat_sigset_t`, and `compat_siginfo_t`.

## Control Flow
Sigreturn validates the frame, restores masks, general registers, segment selectors, FPU state, and altstack for realtime frames. Setup obtains a frame from `get_sigframe()`, chooses a vDSO or inline `int $0x80` restorer, writes sigcontext/masks/retcode markers/siginfo/ucontext, then sets handler registers according to i386 calling convention.

## State, Persistence, Dependencies, Integration
Persistent user ABI state is the exact frame and siginfo layout. Runtime state includes pt_regs, CS/SS/DS/ES/FS/GS, FPU state pointer, signal masks, and altstack. It depends on compat helpers, vDSO32 symbols, segment helpers, SMAP user access windows, and FPU restore. `signal.c` dispatches here for native x86-32 and IA32 emulation.

## Risks And Test Signals
Selector fixups must preserve nonzero null selectors while forcing RPL on real selectors. Static siginfo layout checks guard ABI drift. Test classic/realtime signals, `SA_RESTORER`, vDSO fallback, segment changes, bad sigreturn frames, FPU failures, altstack restore, and new `si_code` layout changes.
