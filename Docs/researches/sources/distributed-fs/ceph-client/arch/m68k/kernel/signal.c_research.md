# sources/distributed-fs/ceph-client/arch/m68k/kernel/signal.c

## Purpose

`signal.c` implements m68k signal delivery and return, including legacy and realtime signal frames, exception-frame reshaping, FPU state save/restore, syscall restart handling, and user-mode resume work.

## Important APIs, Types, and Functions

Externally visible functions are `fixup_exception()` on MMU builds, `berr_040cleanup()` through trap integration, `do_sigreturn()`, `do_rt_sigreturn()`, and `do_notify_resume()`. Important internal types are `struct sigframe` and `struct rt_sigframe`. Helpers include `restore_fpu_state()`, `rt_restore_fpu_state()`, `save_fpu_state()`, `rt_save_fpu_state()`, `mangle_kernel_stack()`, `restore_sigcontext()`, `rt_restore_ucontext()`, `setup_sigcontext()`, `rt_setup_ucontext()`, `get_sigframe()`, `setup_frame()`, `setup_rt_frame()`, `handle_restart()`, and `handle_signal()`.

## Control Flow

On delivery, `do_notify_resume()` calls `do_signal()` when pending signal work exists. `do_signal()` handles syscall restart decisions, obtains a `ksignal`, and calls `handle_signal()`. `handle_signal()` builds either a legacy or realtime user frame on the normal or alt signal stack, copies any extra exception-frame words, stores register/FPU/sigmask/ucontext state, writes a small return trampoline or no-MMU return pointer, flushes the trampoline cache lines, adjusts `regs->stkadj` for complex frames, then sets USP and PC to invoke the user handler.

On signal return, `do_sigreturn()` and `do_rt_sigreturn()` validate and copy user frames, restore the blocked signal mask, restore GPRs, SR user bits, PC, USP, FPU state, altstack state, and call `mangle_kernel_stack()` to rebuild the hardware exception frame before returning to entry assembly.

## State and Persistence Behavior

The file mutates current task blocked signal mask, restart block, pt_regs, switch_stack, user stack contents, FPU hardware state, `current->thread.esp0`, and m68k exception-frame adjustment. It also clears or restores FPU state using CPU-specific instructions.

## Dependencies and Integration Points

It depends on entry assembly return paths, `struct frame` from traps, `traps.c::berr_040cleanup()`, exception table lookup, FPU emulator/hardware formats, ucontext ABI, cache flushing, altstack helpers, and generic signal core. `signal.h` exposes the entry points.

## Risks and Edge Cases

The ABI is highly sensitive: `siginfo_t` offsets are guarded by `BUILD_BUG_ON`, and frame sizes vary by CPU and exception format. User-supplied sigreturn frames can try to create invalid frame formats; `mangle_kernel_stack()` rejects negative/unknown sizes. Cache flushing is required because signal return code is written onto the user stack. Nested signals with adjusted exception frames rely on subtle `stkadj` behavior. FPU frame format validation differs for 68881/68882/040/060/ColdFire.

## Test Signals

Run signal ABI tests for legacy and realtime handlers, altstack, nested signals, syscall restart, ptrace single-step plus signals, sigreturn tampering, FPU state preservation, 040 bus-error writeback cleanup, and no-MMU return stubs.
