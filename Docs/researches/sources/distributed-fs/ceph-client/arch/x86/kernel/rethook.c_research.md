# sources/distributed-fs/ceph-client/arch/x86/kernel/rethook.c

## Purpose
Implements the x86 architecture backend for generic rethook, replacing a probed function's return address with a trampoline that saves registers, invokes rethook handlers, and resumes at the original return address.

## APIs, Types, And Functions
Provides assembly `arch_rethook_trampoline`, callback `arch_rethook_trampoline_callback()`, `arch_rethook_fixup_return()`, and `arch_rethook_prepare()`. Functions are marked `NOKPROBE_SYMBOL` where recursion would be unsafe.

## Control Flow
`arch_rethook_prepare()` saves the original stack return address in `rethook_node`, records the frame pointer, and writes `arch_rethook_trampoline` to the return slot. On return, the trampoline pushes a fake return address for unwinding, saves pt_regs-compatible state, calls `arch_rethook_trampoline_callback()`, restores registers/flags, and returns. The callback normalizes pt_regs fields, passes the frame pointer to `rethook_trampoline_handler()`, and stores FLAGS into the pt_regs SS slot so trampoline stack fixup can pop correctly. `arch_rethook_fixup_return()` replaces the fake frame return address with the real one.

## State And Persistence
Per-hook state lives in `struct rethook_node` and the target stack's patched return address. No global mutable state is maintained.

## Dependencies And Integration
Depends on generic rethook, kprobes register save/restore macros, objtool unwind hints, frame-pointer unwinding conventions, and x86 pt_regs layout.

## Risks And Test Signals
Risks include corrupting the target stack, bad unwind metadata, recursion through probes, and incorrect 32/64-bit stack adjustment. Test signals include kretprobe/rethook selftests, stack unwinding through hooked functions, ftrace/kprobe coexistence, and stress with nested hooks.
