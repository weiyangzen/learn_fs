# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/signal.c

## Purpose
Saves and restores x86 FPU/xstate data in user signal frames, including legacy 32-bit layouts, XSAVE metadata, PKRU, and fault-tolerant direct user-memory operations.

## Important APIs, Types, And Functions
`copy_fpstate_to_sigframe()` writes current state to a signal frame. `fpu__restore_sig()` restores from sigreturn. `fpu__alloc_mathframe()` computes aligned frame placement. `fpu__get_fpstate_size()` reports maximum needed frame size. Helpers validate `_fpx_sw_bytes`, write magic fields, perform direct save/restore, and fold 32-bit fsave headers into FXSR data.

## Control Flow
Save first validates access, clears XSAVE header, ensures current FPU registers are loaded, attempts direct save with page faults disabled, faults in/clears user memory and retries if needed, writes 32-bit fsave headers where required, and appends XSAVE software bytes plus magic2. Restore validates frame size and optional IA32 FX layout, detects whether extended xstate is present, restores directly from user memory when possible, faults in pages on #PF, restores missing features from init state, preserves supervisor state, and clears user states on failure.

## State, Persistence, And Dependencies
State includes user signal-frame bytes, current task fpstate/register ownership, XFD state, xsave header feature bits, PKRU argument handling, and thread `TIF_NEED_FPU_LOAD`. It depends on FPU core, xstate helpers, legacy instruction wrappers, uaccess/fault-in helpers, compat signal layout, and CET/supervisor xstates.

## Integration Points
Called from signal delivery and sigreturn paths; it defines userspace ABI compatibility for old i387, FXSR, and XSAVE-aware applications.

## Risks
Signal frames are attacker-controlled on restore. The code must reject invalid magic/feature/MXCSR combinations, handle user page faults without corrupting registers, preserve supervisor xstate, and fall back to init state on failure.

## Test Signals
Signal stress should round-trip FP/SSE/AVX/PKRU/xstate data, handle 32-bit compat frames, reject malformed frames, fault safely on bad user buffers, and clear user FPU state after failed restore.
